from django.db import models

from nmadb_session_reg.models import StudentInfo
from django.utils.translation import ugettext_lazy as _


class SessionProgram(models.Model):
    """ Program for student to select from.
    """

    title = models.CharField(
            max_length=80,
            verbose_name=_(u'title'),
            unique=True,
            )

    description = models.TextField(
            blank=True,
            null=True,
            verbose_name=_(u'description'),
            )

    ratings = models.ManyToManyField(
            StudentInfo,
            through='SessionProgramRating',
            related_name='session_programs_ratings',
            verbose_name=_(u'ratings of the session programs')
            )

    class Meta(object):
        ordering = [u'title']
        verbose_name = _(u'session program')
        verbose_name_plural = _(u'session programs')

    def __unicode__(self):
        return self.title


class RegistrationInfoMixin:
    """ Information entered by administrator. Session is program
    based.
    """

    assigned_session_program = models.ForeignKey(
            SessionProgram,
            verbose_name=_(u'assigned session program'),
            blank=True,
            null=True,
            )

    class Meta(object):
        ordering = [u'invitation',]
        verbose_name = _(u'registration info (program)')
        verbose_name_plural = _(u'registration infos (program)')

    def __unicode__(self):
        return u'<{0.id}> invitation: {0.invitation}'.format(self)

    def selection(self, index):
        """ Student selection with given index.
        """
        ratings = SessionProgramRating.objects.filter(
                student=self).order_by('-rating')
        try:
            rating = ratings[index]
        except IndexError:
            return None
        else:
            return u'{0.id} {0.title} ({1})'.format(
                    rating.program, rating.rating)

    def first_selection(self):
        """ Session program that student assigned a highest rating.
        """
        return self.selection(0)

    def second_selection(self):
        """ Session program that student assigned a second highest rating.
        """
        return self.selection(1)

    def third_selection(self):
        """ Session program that student assigned a third highest rating.
        """
        return self.selection(2)


class SessionProgramRating(models.Model):
    """ Student rating of the session program.
    """

    student = models.ForeignKey(
            StudentInfo,
            verbose_name=_(u'student'),
            )

    program = models.ForeignKey(
            SessionProgram,
            verbose_name=_(u'program')
            )

    rating = models.PositiveSmallIntegerField(
            verbose_name=_(u'rating'),
            help_text=_(
                u'The bigger the number, the more you want to '
                u'participate in that program.'),
            )

    comment = models.TextField(
            blank=True,
            null=True,
            verbose_name=_(u'Motivation'),
            )

    class Meta(object):
        ordering = [u'student', u'program',]
        verbose_name = u'session program rating'
        verbose_name_plural = u'session program ratings'
