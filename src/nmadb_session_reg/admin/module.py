import datetime

from django.db import transaction
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nmadb_session_reg import models

from nmadb_students import models as students
from nmadb_academics import models as academics
from nmadb_session import models as sessions
from nmadb_contacts import models as contacts
from django_db_utils.forms import (
        NamesValidator, SurnameValidator, EXTENDED_ALPHABET,
        PhoneNumberValidator, IdentityCodeValidator)


class BaseInfoAdmin(admin.ModelAdmin):
    """ Administration for BaseInfo.
    """

    list_display = (
            'first_name',
            'last_name',
            'email',
            'db_id',
            'section',
            )

    search_fields = (
            'first_name',
            'last_name',
            'email',
            'section',
            )


class StudentInfoAdmin(admin.ModelAdmin):
    """ Administration for StudentInfo.
    """

    list_display = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'school_class',
            'school',
            'create_timestamp',
            'payed',
            'chosen',
            )

    actions = [
            'migrate',
            ]

    search_fields = [
            'invitation__base__id',
            'first_name',
            'last_name',
            'email',
            ]

    select_related = True

    @transaction.commit_on_success
    def migrate(self, request, queryset):
        """ Copies to nmadb_session.
        """

        session = sessions.Session.objects.get(
                year=2012,
                session_type=u'Su',
                )
        last_time_used = session.begin - datetime.timedelta(days=10)
        phone_validator = PhoneNumberValidator(u'370')

        for student_info in queryset:

            if not student_info.chosen:
                continue

            invitation = student_info.invitation
            base_info = invitation.base
            payment = invitation.payment

            try:
                student = students.Student.objects.distinct().get(
                        email__address__iexact=base_info.email,
                        first_name=base_info.first_name,
                        last_name=base_info.last_name,
                        )
            except students.Student.DoesNotExist:
                self.message_user(
                        request,
                        _(u'Ignored: {0.first_name} {0.last_name}').format(
                            base_info))
            else:
                if base_info.section in (u'Filologija', u'filologija'):
                    base_info.section = u'Lietuvi\u0173 filologija'
                elif base_info.section in (u'fizika',):
                    base_info.section = u'Fizika ir Astronomija'
                #print base_info.section
                section = academics.Section.objects.get(
                        title__iexact=base_info.section)
                print student_info
                academic = student.academic_set.get(section=section)
                participation = sessions.AcademicParticipation()
                participation.academic = academic
                participation.session = session
                participation.payment = payment
                participation.save()

                try:
                    student.phone_set.get(number=student_info.phone_number)
                except contacts.Phone.DoesNotExist:
                    phone = contacts.Phone()
                    phone.human = student
                    phone.number = student_info.phone_number
                    phone.last_time_used = last_time_used
                    phone.save()

                try:
                    student.email_set.get(address=student_info.email)
                except contacts.Email.DoesNotExist:
                    print student_info, student_info.email
                    email = contacts.Email()
                    email.human = student
                    email.address = student_info.email
                    email.last_time_used = last_time_used
                    email.save()

                if (student_info.school_year - student_info.school_class !=
                        student.school_year - student.school_class):
                    self.message_user(
                            request,
                            _(u'Error: {0.first_name} {0.last_name}'
                                ).format(base_info))
                elif student.school_class < student_info.school_class:
                    student.school_class = student_info.school_class
                    student.school_year = student_info.school_year
                    student.save()

                if student.main_address is None:
                    self.message_user(
                            request,
                            _(u'No address: {0.first_name} {0.last_name}'
                                ).format(base_info))

                parents_exists = student.parents.exists()
                for parent_info in student_info.parents.all():
                    print parent_info
                    if parents_exists:
                        parent = student.parents.get(
                                first_name=parent_info.first_name,
                                last_name=parent_info.last_name,
                                )
                    else:
                        for human in contacts.Human.objects.filter(
                                first_name=parent_info.first_name,
                                last_name=parent_info.last_name):
                            self.message_user(
                                    request,
                                    _(u'{0.id} {0.first_name} '
                                    u'{0.last_name} '
                                    u'(birth date: {0.birth_date}) '
                                    u'already exists in database, but '
                                    u'creating a new one as '
                                    u'{1.id} {1.first_name} {1.last_name} '
                                    u'parent.'
                                    ).format(human, student))
                        parent = contacts.Human()
                        parent.first_name = parent_info.first_name
                        parent.last_name = parent_info.last_name
                        if parent_info.relation in (u'M', u'GM'):
                            parent.gender = u'F'
                        else:
                            parent.gender = u'M'
                        parent.save()
                        relation = students.ParentRelation()
                        relation.child = student
                        relation.parent = parent
                        if parent_info.relation in (u'M', u'T'):
                            relation.relation_type = u'P'
                        else:
                            relation.relation_type = u'T'
                        relation.save()
                    if (not parent.institution_set.exists() and
                            parent_info.job):
                        institution = contacts.Institution()
                        institution.human = parent
                        institution.title = parent_info.job
                        institution.save()
                    if parent_info.phone_number:
                        try:
                            contacts.Phone.objects.get(
                                    number=parent_info.phone_number)
                        except contacts.Phone.DoesNotExist:
                            phone = contacts.Phone()
                            phone.human = parent
                            phone.number = parent_info.phone_number
                            phone.last_time_used = last_time_used
                            phone.save()

                    if parent_info.email:
                        try:
                            contacts.Email.objects.get(
                                    address=parent_info.email)
                        except contacts.Email.DoesNotExist:
                            email = contacts.Email()
                            email.human = parent
                            email.address = parent_info.email
                            email.last_time_used = last_time_used
                            email.save()
                    parent.save()

        #raise Exception(u'STOP!')


class ParentInfoAdmin(admin.ModelAdmin):
    """ Administration for BaseInfo.
    """

    list_display = (
            'child',
            'relation',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'job',
            )

    search_fields = (
            'child__first_name',
            'child__last_name',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            )


admin.site.register(models.BaseInfo, BaseInfoAdmin)
admin.site.register(models.StudentInfo, StudentInfoAdmin)
admin.site.register(models.Invitation)
admin.site.register(models.ParentInfo, ParentInfoAdmin)
