import datetime

from django.core import validators
from django import forms
from django.utils.translation import ugettext as _
from django.utils.functional import lazy

from db_utils.validators.name import (
        NamesValidator, SurnameValidator, ALPHABET_LT)
from django_db_utils.forms import SpreadSheetField
from pysheets.sheet import Sheet
from nmadb_session_reg import models
from nmadb_registration.forms import ImportValidateRow
from nmadb_registration.models import Section as SectionModel
from nmadb_registration import forms as registration_forms


def once(func):
    """ Per object once routine decorator. (In Eiffel sence.)
    """
    cached_value_name = '_' + func.func_name
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, cached_value_name):
            setattr(self, cached_value_name, func(self, *args, **kwargs))
        return getattr(self, cached_value_name)
    return wrapper


class StudentInfoForm(forms.ModelForm):
    """ Form for entering student info.
    """

    class Meta(object):
        model = models.RegistrationInfo
        exclude = (
                # StudentInfo
                'invitation',
                'school_year',
                'home_address',
                'session_programs_ratings',
                'commit_timestamp',
                # RegistrationInfo
                'payed',
                'chosen',
                'comment',
                'assigned_session_program',
                )


class ParentInfoForm(forms.ModelForm):
    """ Form for entering parent info.
    """

    relation = forms.ChoiceField(
            choices=models.ParentInfo.PARENT_CHILD_RELATIONS,
            label=_(u'Relation'),
            help_text=_(
                u'If there is only one of the parents, then '
                u'please fill information only about him and '
                u'in other form choose \u201cnone\u201d'
                ),
            widget=forms.Select(
                attrs={'class': 'parent-relation'},
                )
            )

    class Meta(object):
        model = models.ParentInfo
        exclude = ('child',)


def get_rating_choices():
    """ Generates possible rating choices.
    """
    max_value = models.SessionProgram.objects.count() + 1
    return tuple(zip(range(1, max_value), range(1, max_value)))

class SessionProgramRatingForm(forms.ModelForm):
    """ From for selecting program.
    """

    rating = forms.ChoiceField(
            choices=lazy(get_rating_choices, tuple)(),
            label=_(u'Rating'),
            widget=forms.Select(
                attrs={'class': 'program-rating'},
                ),
            required=True,
            )

    comment = forms.CharField(
            label=_(u'Comment'),
            widget=forms.Textarea(
                attrs={'class': 'program-rating', 'rows': 3,},
                ),
            required=False,
            )

    class Meta(object):
        model = models.SessionProgramRating
        exclude = ('student', 'program',)


class RegistrationFormSet(object):
    """ Formset that encapsulates checking of all registration
    forms.
    """

    def __init__(self, base_info, invitation, POST=None):

        self.POST = POST
        self.base_info = base_info
        self.invitation = invitation
        self.errors = []

    @once
    def is_valid(self):
        """ Checks if all forms are valid.
        """

        valid = True

        if not self.student_form.is_valid():
            self.errors.append(_(u'Fix errors in the student form.'))
            valid = False

        if not self.address_form.is_valid():
            self.errors.append(_(u'Fix errors in the address form.'))
            valid = False

        self.parent_forms_valid = []
        parent_error_added = False
        for i, parent_form in enumerate(self.parent_forms):
            if self.POST.get(
                    parent_form['relation'].html_name, u'') != u'N':
                if not parent_form.is_valid():
                    if not parent_error_added:
                        self.errors.append(_(
                            u'Fix errors in parent forms.'))
                        parent_error_added = True
                else:
                    self.parent_forms_valid.append(parent_form)
            else:
                self.parent_forms[i] = ParentInfoForm(
                        prefix=u'parent_info_{0}'.format(i),
                        initial={'relation': u'N'},
                        )
        if not self.parent_forms_valid and not parent_error_added:
            self.errors.append(_(u'Fill parent forms.'))
            parent_error_added = True
        valid = valid and not parent_error_added

        ratings = set()
        if self.rating_forms:
            for rating_form in self.rating_forms:
                if not rating_form.is_valid():
                    valid = False
                    self.errors.append(_(u'Fix errors in rating forms.'))
                else:
                    ratings.add(rating_form.cleaned_data['rating'])
        if len(ratings) != len(self.rating_forms):
            valid = False
            self.errors.append(_(
                u'Assign different values to different programs.'))

        return valid

    @property
    @once
    def student_form(self):
        """ Student form factory.
        """
        if self.POST is None:
            return StudentInfoForm(
                    prefix=u'student_info',
                    initial={
                        'first_name': self.base_info.first_name,
                        'last_name': self.base_info.last_name,
                        'email': self.base_info.email,
                        'phone_number': '+370',
                        },
                    )
        else:
            return StudentInfoForm(self.POST, prefix=u'student_info')

    @property
    @once
    def address_form(self):
        """ Address form factory.
        """
        if self.POST is None:
            return registration_forms.AddressForm(prefix=u'address_form')
        else:
            return registration_forms.AddressForm(
                    self.POST,
                    prefix=u'address_form')


    @property
    @once
    def parent_forms(self):
        """ Parent forms list factory.
        """
        if self.POST is None:
            return [
                    ParentInfoForm(
                        prefix=u'parent_info_' + unicode(index),
                        initial={
                            'relation': relation,
                            'job_phone_number': '+370',
                            'phone_number': '+370',
                            }
                        )
                    for index, relation in enumerate((u'M', u'T'))
                    ]
        else:
            return [
                    ParentInfoForm(
                        self.POST,
                        prefix=u'parent_info_' + unicode(index),
                        )
                    for index in range(2)
                    ]

    @property
    @once
    def rating_forms(self):
        """ Rating forms list factory.
        """
        self.ratings = []
        for program in models.SessionProgram.objects.all():
            rating = models.SessionProgramRating()
            rating.program = program
            self.ratings.append(rating)
        if self.POST is None:
            return [
                    SessionProgramRatingForm(
                        instance=rating,
                        prefix=u'rating_' + unicode(rating.program.id))
                    for rating in self.ratings
                    ]
        else:
            return [
                    SessionProgramRatingForm(
                        self.POST,
                        instance=rating,
                        prefix=u'rating_' + unicode(rating.program.id))
                    for rating in self.ratings
                    ]

    def save(self):
        """ Saves all forms.
        """
        today = datetime.date.today()

        address = self.address_form.save()

        student = self.student_form.save(commit=False)
        student.invitation = self.invitation
        student.school_year = today.year + int(today.month >= 9)
        student.home_address = address
        student.save()

        self.base_info.generated_address = unicode(address)
        self.base_info.save()

        for rating in self.ratings:
            rating.student = student
            rating.save()

        for parent_form in self.parent_forms_valid:
            parent = parent_form.save(commit=False)
            parent.child = student
            parent.save()


IMPORT_BASE_INFO_REQUIRED_COLUMNS = {
        u'first_name': _(u'First name'),
        u'last_name': _(u'Last name'),
        u'email': _(u'Email'),
        u'section': _(u'Section title'),
        u'payment': _(u'Payment'),
        }
#IMPORT_BASE_INFO_OPTIONAL_COLUMNS = { FIXME: Not used.
        #u'human_id': _(u'NMADB human id'),
        #u'comment': _(u'Comment'),
        #u'generated_address': _(u'Generated address'),
        #}

NAME_VALIDATOR = NamesValidator(
    ALPHABET_LT,
    validation_exception_type=forms.ValidationError,
    )

SURNAME_VALIDATOR = SurnameValidator(
    ALPHABET_LT,
    validation_exception_type=forms.ValidationError,
    )

def base_info_import_validate_row(sheet, row):
    """ Checks if row is valid.
    """
    print 'V1'
    row[u'first_name'] = NAME_VALIDATOR(row[u'first_name'])
    row[u'last_name'] = SURNAME_VALIDATOR(row[u'last_name'])
    validators.validate_email(row[u'email'])
    if row[u'payment'] < 0:
        raise forms.ValidationError(
                _(u'Payment cannot be negative!'))
    print 'V2'
    try:
        section = SectionModel.objects.get(
                title=row[u'section'])
    except SectionModel.DoesNotExist:
        raise forms.ValidationError(
                _(u'Unknown section \u201c{0}\u201d.').format(
                    row[u'section']))
    else:
        row[u'section'] = section
    print 'V3'
    return row

def base_info_import_validate_sheet(spreadsheet, name, sheet):
    """ Creates sheet with correct columns.
    """
    sheet = Sheet(
            captions=(list(IMPORT_BASE_INFO_REQUIRED_COLUMNS.keys())))
    sheet.add_validator(
            ImportValidateRow(
                IMPORT_BASE_INFO_REQUIRED_COLUMNS,
                (u'payment',),
                (),
                (u'first_name', u'last_name', u'email', u'section',
                    u'payment'),
                ),
            'insert')
    sheet.add_validator(base_info_import_validate_row, 'insert')
    return sheet, name

class ImportBaseInfoForm(forms.Form):
    """ Form for importing base info data.
    """

    spreadsheet = SpreadSheetField(
            sheet_name=_(u'Base info'),
            spreadsheet_constructor_args={
                'validators': {
                    'spreadsheet': [
                        (base_info_import_validate_sheet, 'add_sheet'),
                        ],
                    },
                },
            label=_(u'Spreadsheet document'),
            required=True,
            help_text=_(
                u'Please select spreadsheet file. '
                u'Required columns are: {0}.').format(
                    u','.join(
                        _(u'\u201c{0}\u201d').format(caption)
                        for caption in
                        IMPORT_BASE_INFO_REQUIRED_COLUMNS.values()))
            )
