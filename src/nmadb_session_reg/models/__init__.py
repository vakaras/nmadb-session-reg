from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import validators

from nmadb_registration import models as registration_models
from nmadb_session_reg.config import info
from django_db_utils import models as utils_models


class BaseInfo(models.Model):
    """ Base information about student.
    """

    first_name = utils_models.FirstNameField(
            verbose_name=_(u'first name'),
            )

    last_name = utils_models.LastNameField(
            verbose_name=_(u'last name'),
            )

    email = models.EmailField(
            max_length=128,
            verbose_name=_(u'email address'),
            )

    human_id = models.IntegerField(        # Human.id from NMADB.
            blank=True,
            null=True,
            )

    section = models.ForeignKey(
            registration_models.Section,
            verbose_name=_(u'section'),
            )

    comment = models.TextField(
            verbose_name=_(u'comment'),
            blank=True,
            null=True,
            )

    payment = models.IntegerField(
            verbose_name=_(u'participant\'s payment'),
            )

    generated_address = models.CharField(
            max_length = 255,
            blank=True,
            null=True,
            )

    commit_timestamp = models.DateTimeField(
            verbose_name=_(u'commit timestamp'),
            auto_now_add=True,
            )

    class Meta(object):
        ordering = [u'last_name', u'first_name']
        verbose_name = _(u'base info')
        verbose_name_plural = _(u'base infos')

    def __unicode__(self):
        return u'<{0.id}> {0.first_name} {0.last_name}'.format(self)


class Invitation(models.Model):
    """ Invitation to session. This table is created, when invitation
    email is sent to pupil.
    """

    base = models.ForeignKey(
            BaseInfo,
            verbose_name=_(u'base info'),
            )

    uuid = utils_models.UUIDField(
            verbose_name=_(u'invitation identifier'))

    payment = models.IntegerField(
            verbose_name=_(u'participant\'s payment'),
            )

    commit_timestamp = models.DateTimeField(
            verbose_name=_(u'commit timestamp'),
            auto_now_add=True,
            )

    time_sent = models.DateTimeField(
            verbose_name=_(u'sent'),
            blank=True,
            null=True,
            )

    class Meta(object):
        ordering = [u'base',]
        verbose_name = _(u'invitation')
        verbose_name_plural = _(u'invitations')

    def __unicode__(self):
        return u'<{0.id}> base info: {0.base}'.format(self)


class StudentInfo(models.Model):
    """ All information that was entered by student.
    """

    invitation = models.OneToOneField(
            Invitation,
            related_name='student_info',
            verbose_name=_(u'invitation'),
            )

    first_name = utils_models.FirstNameField(
            verbose_name=_(u'first name'),
            )

    last_name = utils_models.LastNameField(
            verbose_name=_(u'last name'),
            )

    email = models.EmailField(
            max_length=128,
            verbose_name=_(u'email address'),
            )

    phone_number = utils_models.PhoneNumberField(
            verbose_name=_(u'personal phone number'),
            )

    school_class = models.PositiveSmallIntegerField(
            validators=[
                validators.MinValueValidator(6),
                validators.MaxValueValidator(12),
                ],
            verbose_name=_(u'class'),
            )

    school_year = models.IntegerField(
            validators=[
                validators.MinValueValidator(2005),
                validators.MaxValueValidator(2015),
                ],
            verbose_name=_(u'class update year'),
            help_text=_(
                u'This field value shows, at which year January 3 day '
                u'student was in school_class.'
                ),
            )

    school = models.ForeignKey(
            registration_models.School,
            verbose_name=_(u'school'),
            )

    home_address = models.ForeignKey(
            registration_models.Address,
            verbose_name=_(u'home address'),
            help_text=_(
                u'Null only if base_info.generated_address is present.'),
            blank=True,
            null=True,
            )

    commit_timestamp = models.DateTimeField(
            verbose_name=_(u'commit timestamp'),
            auto_now_add=True,
            )

    class Meta(object):
        ordering = [u'invitation',]
        verbose_name = _(u'student info')
        verbose_name_plural = _(u'student infos')

    def __unicode__(self):
        return u'<{0.id}> invitation: {0.invitation}'.format(self)

    def section(self):
        """ Returns the title of student's section.
        """
        return self.invitation.base.section.title
    section.short_description = _(u'section')


class RegistrationInfoMixin(models.Model):
    """ Information entered by administrator mixin.
    """

    payed = models.BooleanField(
            verbose_name=_(u'payed'),
            blank=True,
            help_text=_(u'True, if pupil have payed registration fee.'),
            )

    chosen = models.BooleanField(
            verbose_name=_(u'chosen'),
            help_text=_(u'Student was chosen.'),
            blank=True,
            )

    comment = models.TextField(
            verbose_name=_(u'comment'),
            blank=True,
            null=True,
            )

    class Meta(object):
        abstract = True


if info.session_is_program_based:
    from nmadb_session_reg.models.program_based import (
            SessionProgram,
            SessionProgramRating,
            )
    from nmadb_session_reg.models import program_based
    class RegistrationInfo(
            StudentInfo,
            RegistrationInfoMixin,
            program_based.RegistrationInfoMixin):
        """ Information entered by administrator.
        """
else:
    from nmadb_session_reg.models.section_based import (
            SessionGroup,
            )
    from nmadb_session_reg.models import section_based
    class RegistrationInfo(
            StudentInfo,
            RegistrationInfoMixin,
            section_based.RegistrationInfoMixin):
        """ Information entered by administrator.
        """


class ParentInfo(models.Model):
    """ Parent information.
    """

    PARENT_CHILD_RELATIONS = (
            (u'M', _(u'mother')),
            (u'T', _(u'father')),
            (u'GM', _(u'tutoress')),
            (u'GT', _(u'tutor')),
            (u'N', _(u'none')),
            )

    child = models.ForeignKey(
            StudentInfo,
            verbose_name=_(u'child'),
            )

    relation = models.CharField(
            max_length=2,
            choices=PARENT_CHILD_RELATIONS,
            verbose_name=_(u'relation'),
            )

    first_name = utils_models.FirstNameField(
            verbose_name=_(u'first name'),
            )

    last_name = utils_models.LastNameField(
            verbose_name=_(u'last name'),
            )

    phone_number = utils_models.PhoneNumberField(
            verbose_name=_(u'phone number'),
            )

    email = models.EmailField(
            max_length=128,
            verbose_name=_(u'email address'),
            )

    class Meta(object):
        ordering = [u'last_name', u'first_name',]
        verbose_name = _(u'parent info')
        verbose_name_plural = _(u'parent infos')

    def __unicode__(self):
        return u'<{0.child}> {0.first_name} {0.last_name}'.format(self)


class Info(models.Model):
    """ Session system information.
    """

    SESSION_TYPE = (
            (u'Wi', _(u'winter'),),
            (u'Sp', _(u'spring'),),
            (u'Su', _(u'summer'),),
            (u'Au', _(u'autumn'),),
            )

    year = models.PositiveSmallIntegerField(
            verbose_name=_(u'year'),
            )

    session_type = models.CharField(
            max_length=3,
            choices=SESSION_TYPE,
            verbose_name=_(u'session type'),
            )

    session = models.CharField(
            max_length=128,
            verbose_name=_(u'session'),
            )

    manager_name_dative = models.CharField(
            max_length=128,
            verbose_name=_(u'manager name dative'),
            )

    manager_email = models.EmailField(
            verbose_name=_(u'manager email'),
            )

    manager_phone = utils_models.PhoneNumberField(
            verbose_name=_(u'manager phone'),
            )

    admin_email = models.EmailField(
            verbose_name=_(u'administrator email'),
            )

    confirmation_deadline = models.DateField(
            verbose_name=_(u'confirmation deadline'),
            )

    session_is_program_based = models.BooleanField(
            verbose_name=_(u'session is program based'),
            editable=False,
            )

    root_page_redirect_address = models.URLField(
            verbose_name=_(u'root page redirect address'),
            )
