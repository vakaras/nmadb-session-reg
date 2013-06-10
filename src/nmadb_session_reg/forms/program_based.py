from django import forms
from django.utils.translation import ugettext as _

from nmadb_session_reg import models


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
