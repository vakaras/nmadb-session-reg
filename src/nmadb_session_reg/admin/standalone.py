from django.db import transaction
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nmadb_session_reg import models
from nmadb_utils import admin as utils
from nmadb_utils import actions


class SessionProgramAdmin(utils.ModelAdmin):
    """ Administration for session program.
    """

    list_display = (
            'id',
            'title',
            'description',
            )


class BaseInfoAdmin(utils.ModelAdmin):
    """ Administration for base info.
    """

    list_display = (
            'id',
            'first_name',
            'last_name',
            'email',
            'human_id',
            'section',
            'payment',
            'generated_address',
            )

    list_filter = (
            'section',
            )

    search_fields = (
            'id',
            'first_name',
            'last_name',
            )

    readonly_fields = (
            'commit_timestamp',
            )


class InvitationAdmin(utils.ModelAdmin):
    """ Administration for invitation.
    """

    list_display = (
            'id',
            'base',
            'uuid',
            'payment',
            'commit_timestamp',
            )

    search_fields = (
            'id',
            'uuid',
            'base__first_name',
            'base__last_name',
            'payment',
            )

    readonly_fields = (
            'commit_timestamp',
            )


class StudentInfoAdmin(utils.ModelAdmin):
    """ Administration for base info.
    """

    list_display = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'school_class',
            'school',
            )

    list_filter = (
            'school_class',
            )

    search_fields = (
            'id',
            'first_name',
            'last_name',
            'school__title',
            )

    readonly_fields = (
            'commit_timestamp',
            )


class RegistrationInfoAdmin(utils.ModelAdmin):
    """ Administration for registration info.
    """

    list_display = (
            'id',
            'first_name',
            'last_name',
            'school',
            'school_class',
            'payed',
            'chosen',
            'assigned_session_program',
            )

    list_filter = (
            'school_class',
            'assigned_session_program',
            )

    search_fields = (
            'id',
            'first_name',
            'last_name',
            'school__title',
            )

    readonly_fields = (
            'commit_timestamp',
            )

    list_editable = (
            'payed',
            'chosen',
            'assigned_session_program',
            )


class ParentInfoAdmin(utils.ModelAdmin):
    """ Administration for parent info.
    """

    list_display = (
            'id',
            'first_name',
            'last_name',
            'child',
            'relation',
            'phone_number',
            'email',
            )

    search_fields = (
            'id',
            'first_name',
            'last_name',
            'child__first_name',
            'child__last_name',
            )


actions.register(_(u'Import student base info'),
    'nmadb-session-reg-import-base-info')


admin.site.register(models.SessionProgram, SessionProgramAdmin)
admin.site.register(models.BaseInfo, BaseInfoAdmin)
admin.site.register(models.StudentInfo, StudentInfoAdmin)
admin.site.register(models.Invitation, InvitationAdmin)
admin.site.register(models.RegistrationInfo, RegistrationInfoAdmin)
admin.site.register(models.ParentInfo, ParentInfoAdmin)
admin.site.register(models.SessionProgramRating)
