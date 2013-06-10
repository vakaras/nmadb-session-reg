from django.db import models
from django.utils.translation import ugettext_lazy as _


class SessionGroup(models.Model):
    """ The session group. In most cases it will be section.
    """

    title = models.CharField(
            max_length=80,
            verbose_name=_(u'title'),
            unique=True,
            )

    description = models.TextField(
            blank=True,
            null=True,
            verbose_name=_(u'comment'),
            )

    class Meta(object):
        ordering = [u'title']
        verbose_name = _(u'session group')
        verbose_name_plural = _(u'session groups')
        app_label = 'nmadb_session_reg'

    def __unicode__(self):
        return self.title


class RegistrationInfoMixin(models.Model):
    """ Information entered by administrator. Session is section
    based.
    """

    assigned_session_group = models.ForeignKey(
            'nmadb_session_reg.SessionGroup',
            verbose_name=_(u'assigned session group'),
            blank=True,
            null=True,
            )

    class Meta(object):
        abstract = True
        ordering = [u'invitation',]
        verbose_name = _(u'registration info (section)')
        verbose_name_plural = _(u'registration infos (section)')
        app_label = 'nmadb_session_reg'

    def __unicode__(self):
        return u'<{0.id}> invitation: {0.invitation}'.format(self)
