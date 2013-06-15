from django.db import transaction
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from nmadb_session_reg import models
from nmadb_utils import admin as utils
from nmadb_utils import actions
from nmadb_utils.pdf import render_to_pdf
from nmadb_automation import mail
from nmadb_session_reg.config import info
from django.conf import settings


class SendMailMixin(object):
    """ Admin actions for sending mail.
    """

    def send_mail(self, request, queryset):
        """ Allows to send email.
        """
        return mail.send_mail_admin_action(
                lambda obj: [(obj.email, {'obj': obj, 'info': info})],
                request,
                queryset)
    send_mail.short_description = _(u'send email')


    def send_sync_template_mail(self, request, queryset):
        """ Sends template email synchronously.
        """
        return mail.send_template_mail_admin_action(
                lambda obj: [(obj.email, {'obj': obj, 'info': info})],
                False, request, queryset)
    send_sync_template_mail.short_description = _(
            u'send template mail synchronously')


    def send_async_template_mail(self, request, queryset):
        """ Sends template email asynchronously.
        """
        return mail.send_template_mail_admin_action(
                lambda obj: [(obj.email, {'obj': obj, 'info': info})],
                True, request, queryset)
    send_async_template_mail.short_description = _(
            u'send template mail asynchronously')


class SessionProgramAdmin(utils.ModelAdmin):
    """ Administration for session program.
    """

    list_display = (
            'id',
            'title',
            'description',
            )


class SessionGroupAdmin(utils.ModelAdmin):
    """ Administration for session group.
    """

    list_display = (
            'id',
            'title',
            'description',
            )


class BaseInfoAdmin(utils.ModelAdmin, SendMailMixin):
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

    actions = utils.ModelAdmin.actions + [
            'send_mail',
            'send_sync_template_mail',
            'send_async_template_mail',
            'send_invitations',
            ]

    def send_invitations(self, request, queryset):
        """ Sends invitations.
        """
        def create_context(base_info):
            """ Creates invitation object and returns context.
            """
            invitation = models.Invitation()
            invitation.base = base_info
            invitation.payment = base_info.payment
            invitation.save()
            return [(base_info.email, {
                'base_info': base_info,
                'info': info.as_dict(),
                'invitation': invitation,
                'invitation_id': invitation.id,
                'current_site': unicode(Site.objects.get_current()),
                })]
        def send_handler(to, from_email, context):
            """ Handles mail sent event.
            """
            from django.utils import timezone
            from nmadb_session_reg.models import Invitation
            invitation = Invitation.objects.get(
                    id=context['invitation_id'])
            invitation.time_sent = timezone.now()
            invitation.save()
        return mail.send_template_mail_admin_action(
                create_context, True, request, queryset,
                callback=send_handler,
                action=u'send_invitations')
    send_invitations.short_description = _(u'send invitations')


class InvitationAdmin(utils.ModelAdmin):
    """ Administration for invitation.
    """

    list_display = (
            'id',
            'base',
            'uuid',
            'payment',
            'time_sent',
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
            'section',
            )

    list_filter = (
            'school_class',
            )

    search_fields = (
            'id',
            'first_name',
            'last_name',
            'school__title',
            'invitation__base__section__title',
            )

    readonly_fields = (
            'commit_timestamp',
            )

    raw_id_fields = (
            'invitation',
            'school',
            'home_address',
            )

    list_per_page = 20


class RegistrationInfoAdminBase(utils.ModelAdmin, SendMailMixin):
    """ Administration for registration info base.
    """

    list_display = (
            'id',
            'first_name',
            'last_name',
            'school',
            'school_class',
            'payed',
            'chosen',
            'section',
            )

    search_fields = (
            'id',
            'first_name',
            'last_name',
            'school__title',
            'invitation__base__section__title',
            )

    readonly_fields = (
            'commit_timestamp',
            )

    list_editable = (
            'payed',
            'chosen',
            )

    actions = utils.ModelAdmin.actions + [
            'send_mail',
            'send_sync_template_mail',
            'send_async_template_mail',
            'download_registration_sheet',
            'download_lecturer_sheet',
            ]

    raw_id_fields = (
            'invitation',
            'school',
            'home_address',
            )

    list_per_page = 20


    def download_sheet(self, request, queryset, default_div, template):
        """ Download registration sheet as pdf.
        """
        from collections import defaultdict
        groups = defaultdict(list)
        if not info.session_is_program_based:
            def add(student):
                if student.assigned_session_group:
                    title = student.assigned_session_group.title
                else:
                    title = _(u'Unknown')
                groups[title].append(student)

        else:
            raise NotImplemented
        for student in queryset:
            add(student)
        sorted_groups = {}
        for title, group in sorted(groups.items()):
            students = list(enumerate(sorted(
                    group,
                    key=lambda x: (x.last_name, x.first_name))))
            length = len(students)
            div = default_div
            if length > div:
                while 0 < (length % div) < 3:
                    div -= 1
            sgroup = []
            for i in range(0, length, div):
                sgroup.append(students[i:i+div])
            sorted_groups[title] = sgroup
        return render_to_pdf(
                template,
                {
                    'info': info,
                    'logo_path': settings.NMA_LOGO_IMAGE,
                    'font_path': settings.UBUNTU_FONT,
                    'pagesize':'A4',
                    'students': queryset,
                    'groups': sorted_groups,
                })

    def download_registration_sheet(self, request, queryset):
        """ Download registration sheet as pdf.
        """
        return self.download_sheet(
                request,
                queryset,
                14,
                'nmadb-session-reg/registration-sheet.html',
                )
    download_registration_sheet.short_description = _(
            u'download registration sheet as pdf')

    def download_lecturer_sheet(self, request, queryset):
        """ Download sheet for lecturer as pdf.
        """
        return self.download_sheet(
                request,
                queryset,
                14,
                'nmadb-session-reg/lecturer-sheet.html',
                )
    download_lecturer_sheet.short_description = _(
            u'download lecturer sheet as pdf')


class RegistrationInfoSectionAdmin(RegistrationInfoAdminBase):
    """ Administration for registration info.
    """

    list_display = RegistrationInfoAdminBase.list_display + (
            'assigned_session_group',
            )

    list_filter = (
            'school_class',
            'assigned_session_group',
            'payed',
            'chosen',
            )

    list_editable = RegistrationInfoAdminBase.list_editable + (
            'assigned_session_group',
            )


class RegistrationInfoProgramAdmin(RegistrationInfoAdminBase):
    """ Administration for registration info.
    """

    list_display = RegistrationInfoAdminBase.list_display + (
            'assigned_session_program',
            'first_selection',
            'second_selection',
            'third_selection',
            )

    list_filter = (
            'school_class',
            'assigned_session_program',
            )

    list_editable = RegistrationInfoAdminBase.list_editable + (
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


actions.register(
        'nmadb-session-reg-import-base-info',
        _(u'Import student base info'),
        'nmadb-session-reg-import-base-info')


if info.session_is_program_based:
    admin.site.register(models.SessionProgram, SessionProgramAdmin)
    admin.site.register(models.SessionProgramRating)
    admin.site.register(
            models.RegistrationInfo,
            RegistrationInfoProgramAdmin)
else:
    actions.unregister('nmadb-registration-import-sections')
    actions.register(
            'nmadb-registration-import-sections',
            _(u'Import sections and groups'),
            'nmadb-registration-import-sections-and-groups')
    admin.site.register(models.SessionGroup, SessionGroupAdmin)
    admin.site.register(
            models.RegistrationInfo,
            RegistrationInfoSectionAdmin)
admin.site.register(models.BaseInfo, BaseInfoAdmin)
admin.site.register(models.StudentInfo, StudentInfoAdmin)
admin.site.register(models.Invitation, InvitationAdmin)
admin.site.register(models.ParentInfo, ParentInfoAdmin)
admin.site.register(models.Info)
