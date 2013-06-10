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
                'commit_timestamp',
                # RegistrationInfo
                'payed',
                'chosen',
                'comment',
                'assigned_session_group',
                )
