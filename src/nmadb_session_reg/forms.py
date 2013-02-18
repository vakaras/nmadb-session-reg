from django.core import validators
from django import forms
from django.utils.translation import ugettext as _

from db_utils.validators.name import (
        NamesValidator, SurnameValidator, ALPHABET_LT)
from django_db_utils.forms import SpreadSheetField
from pysheets.sheet import Sheet
from nmadb_session_reg import models
from nmadb_registration.forms import ImportValidateRow
from nmadb_registration.models import Section as SectionModel


def once(func):
    """ Per object once routine decorator. (In Eiffel sence.)
    """
    cached_value_name = '_' + func.func_name
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, cached_value_name):
            setattr(self, cached_value_name, func(*args, **kwargs))
        return getattr(self, cached_value_name)
    return wrapper


class StudentInfoForm(forms.ModelForm):
    """ Form for entering student info.
    """

    class Meta(object):
        model = models.StudentInfo
        exclude = (
                'invitation',
                'school_year',
                'home_address',
                'session_programs_ratings',
                'commit_timestamp',
                )


class RegistrationFormSet(object):
    """ Formset that encapsulates checking of all registration
    forms.
    """

    def __init__(self, base_info, POST=None):

        self.POST = POST
        self.base_info = base_info

    @property
    @once
    def student_form(self):
        """ Student form factory.
        """
        if self.POST is None:
            today = datetime.date.today()
            return StudentInfoForm(
                    prefix=u'student_info',
                    initial={
                        'first_name': self.base_info.first_name,
                        'last_name': self.base_info.last_name,
                        'email': self.base_info.email,
                        'phone_number': '+370',
                        'school_year': today.year + int(today.month >= 9),
                        },
                    )
        else:
            return StudentInfoForm(self.POST, prefix=u'student_info')


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
