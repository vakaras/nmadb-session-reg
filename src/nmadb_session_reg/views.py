from django.db import transaction
from django.contrib import admin
from django import shortcuts
from django.views.generic.simple import direct_to_template
from django.core import urlresolvers
from annoying.decorators import render_to
from django.contrib import messages
from django.utils.translation import ugettext as _

from nmadb_registration.conditions import check_condition
from nmadb_session_reg import models, forms
from nmadb_session_reg.config import info
from nmadb_automation import mail
from nmadb_automation import models as automation_models


@render_to('nmadb-session-reg/registration.html')
@transaction.commit_on_success
def register(request, uuid):
    """ Student registration view for session.
    """

    invitation = shortcuts.get_object_or_404(models.Invitation, uuid=uuid)
    base_info = invitation.base
    try:
        student_info = invitation.student_info
    except models.StudentInfo.DoesNotExist:
        pass
    else:
        if check_condition(u'send-confirmation-mail'):
            registration_info = student_info.registrationinfo
            template = automation_models.Email.objects.get(id=3)
            assert u'pasirinkimai' in template.subject
            mail.send_template_mail(
                    template,
                    (student_info.email,),
                    u'FIXME',
                    {
                        'base_info': base_info,
                        'student_info': student_info,
                        'registration_info': registration_info,
                        'info': info,
                    })
        return direct_to_template(
                request,
                template='nmadb-session-reg/registration-finished.html',
                extra_context={
                    'base_info': base_info,
                    'student_info': student_info,
                    'info': info,
                    },
                )

    if check_condition(u'registration-closed'):
        return direct_to_template(
                request,
                template='nmadb-session-reg/closed.html',
                extra_context={
                    'info': info,
                    },
                )

    if request.method == 'POST':
        form = forms.RegistrationFormSet(
                base_info, invitation, request.POST)
        if form.is_valid():
            form.save()
            return shortcuts.redirect(
                    'nmadb-session-reg-registration', uuid)
    else:
        form = forms.RegistrationFormSet(base_info, invitation)

    return {
            'info': info,
            'form': form,
            }


@admin.site.admin_view
@render_to('admin/file-form.html')
@transaction.commit_on_success
def import_base(request):
    """ Imports base info.
    """
    if request.method == 'POST':
        form = forms.ImportBaseInfoForm(request.POST, request.FILES)
        if form.is_valid():
            counter = 0
            for sheet in form.cleaned_data['spreadsheet']:
                for row in sheet:
                    base_info = models.BaseInfo()
                    for attr in row.keys():
                        setattr(base_info, attr, row[attr])
                    base_info.human_id = None
                    base_info.comment = None
                    base_info.generated_address = None
                    base_info.save()
                    counter += 1
            msg = _(u'{0} base infos about students successfully imported.'
                    ).format(counter)
            messages.success(request, msg)
            return shortcuts.redirect(
                    'admin:nmadb_session_reg_baseinfo_changelist')
    else:
        form = forms.ImportBaseInfoForm()
    return {
            'admin_index_url': urlresolvers.reverse('admin:index'),
            'app_url': urlresolvers.reverse(
                'admin:app_list',
                kwargs={'app_label': 'nmadb_session_reg'}),
            'app_label': _(u'NMADB Session Registration'),
            'form': form,
            }
