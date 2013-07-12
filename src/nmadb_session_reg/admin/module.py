import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.contrib import admin

from nmadb_session_reg import models
from nmadb_utils import admin as utils
from nmadb_session_reg.config import info

from nmadb_contacts import models as contacts
from nmadb_academics import models as academics
from nmadb_students import models as students
from nmadb_session import models as sessions


class HumanUpdater(object):
    """ Util object that helps to update info about human.
    """

    def __init__(self, human, session, message_user):
        self.human = human
        self.session = session
        self.last_time_used = session.begin - datetime.timedelta(days=10)
        self.message_user = message_user

    def update_phone(self, phone_number):
        """ If the phone number does not exist, then adds.
        """
        try:
            contacts.Phone.objects.get(number=phone_number)
        except contacts.Phone.DoesNotExist:
            phone = contacts.Phone()
            phone.human = self.human
            phone.number = phone_number
            phone.last_time_used = self.last_time_used
            phone.save()
            self.notify_create('phone', phone.number)

    def update_email(self, address):
        """ If the email does not exist, then adds.
        """
        try:
            contacts.Email.objects.get(address=address)
        except contacts.Email.DoesNotExist:
            email = contacts.Email()
            email.human = self.human
            email.address = address
            email.last_time_used = self.last_time_used
            email.save()
            self.notify_create('email', email.address)

    def message(self, frmt, *args, **kwargs):
        """ Shows a message to user.
        """
        self.message_user(frmt.format(*args, **kwargs))

    def notify_update(self, field, old_value, new_value):
        """ Shows a notification message about update.
        """
        self.message(
                _(
                    u'Updated ({0.id} {0.first_name} {0.last_name}) '
                    u'{1}: \u201e{2}\u201c \u2192 \u201e{3}\u201c'
                    ),
                self.human, field, old_value, new_value)

    def notify_create(self, field, value):
        """ Shows a notification message about update.
        """
        self.message(
                _(
                    u'Created ({0.id} {0.first_name} {0.last_name}) '
                    u'{1}: \u201e{2}\u201c'
                    ),
                self.human, field, value)


class StudentUpdater(HumanUpdater):
    """ Util object that helps to update info about student.
    """

    def __init__(self, student, session, message_user):
        super(StudentUpdater, self).__init__(
                student, session, message_user)
        self.student = student

    def update_school_year(self, school_year, school_class):
        """ Checks if info is correct and updates.
        """
        if (
                school_year - school_class !=
                self.student.school_year - self.student.school_class):
            self.message(
                    _(u'Error: {0.first_name} {0.last_name}'),
                    self.student)
        elif self.student.school_class < school_class:
            self.notify_update(
                    u'class',
                    self.student.school_class,
                    school_class)
            self.student.school_class = school_class
            self.student.school_year = school_year
            self.student.save()

    def update_main_address(self, address):
        """ Only shows a notification.
        """
        if self.student.main_address is None:
            self.message(
                    _(u'No address: {0.first_name} {0.last_name}'),
                    self.student)

    def update_parents(self, parents, session):
        """ Updates information about parents.
        """
        parents_exists = self.student.parents.exists()
        for parent_info in parents:
            print parent_info
            if parent_info.relation == u'N':
                raise Exception("Internal error!")
            if parents_exists:
                parent = self.student.parents.get(
                        first_name=parent_info.first_name,
                        last_name=parent_info.last_name,
                        )
            else:
                for human in contacts.Human.objects.filter(
                        first_name=parent_info.first_name,
                        last_name=parent_info.last_name):
                    self.message(
                            _(u'{0.id} {0.first_name} '
                            u'{0.last_name} '
                            u'(birth date: {0.birth_date}) '
                            u'already exists in database, but '
                            u'creating a new one as '
                            u'{1.id} {1.first_name} {1.last_name} '
                            u'parent.'),
                            human,
                            self.student)
                parent = contacts.Human()
                parent.first_name = parent_info.first_name
                parent.last_name = parent_info.last_name
                if parent_info.relation in (u'M', u'GM'):
                    parent.gender = u'F'
                else:
                    parent.gender = u'M'
                parent.save()
                relation = students.ParentRelation()
                relation.child = self.student
                relation.parent = parent
                if parent_info.relation in (u'M', u'T'):
                    relation.relation_type = u'P'
                else:
                    relation.relation_type = u'T'
                relation.save()
                self.message(
                        _(u'Added parent: '
                        u'{0.id} {0.first_name} {0.last_name} '
                        u'(child: {1.id} {1.first_name} {1.last_name})'),
                        parent,
                        self.student)
            parent_updater = HumanUpdater(
                    parent, session, self.message_user)
            parent_updater.update_phone(parent_info.phone_number)
            parent_updater.update_email(parent_info.email)
            parent.save()


class BaseInfoAdmin(utils.ModelAdmin):
    """ Administration for BaseInfo.
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
            'section',
            )

    list_filter = (
            'school_class',
            'assigned_session_program',
            'payed',
            'chosen',
            )

    search_fields = (
            'id',
            'first_name',
            'last_name',
            'school__title',
            'invitation__base__section__title',
            )

    raw_id_fields = (
            'invitation',
            'school',
            'home_address',
            )

    readonly_fields = (
            'commit_timestamp',
            )

    actions = utils.ModelAdmin.actions + [
            'update',
            'create',
            'show_message',
            ]

    list_per_page = 20

    def _update_db_info_about_students(
            self, request, registration_infos, session):
        """ Updates info about each student.
        """
        for registration_info in registration_infos:
            invitation = registration_info.invitation
            base_info = invitation.base
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
                section = academics.Section.objects.get(
                        title__iexact=base_info.section)
                print registration_info
                student_updater = StudentUpdater(
                        student,
                        session,
                        lambda x: self.message_user(request, x)
                        )
                student_updater.update_phone(
                        registration_info.phone_number)
                student_updater.update_email(
                        registration_info.email)
                student_updater.update_school_year(
                        registration_info.school_year,
                        registration_info.school_class)
                student_updater.update_main_address(None)
                student_updater.update_parents(
                        registration_info.parentinfo_set.all(),
                        session)
                student.save()

    def _get_section(self, title):
        """ Returns the section by title.
        """
        section = academics.Section.objects.get(title__iexact=title)
        return section

    def _create_session_participation_entries(
            self, request, registration_infos, session):
        """ Creates participation entries.
        """
        def generate_key(program):
            """ Generates key for session program.
            """
            return u'{0.id} - {0.title}'.format(program)
        groups = {}
        for program in models.SessionProgram.objects.all():
            key = generate_key(program)
            try:
                group = sessions.Group.objects.get(comment=key)
            except sessions.Group.DoesNotExist:
                group = sessions.Group()
                group.session = session
                group.comment = key
                group.save()
                self.message_user(
                        request,
                        _(u'Created group: {0.id} {0.session} {0.comment}'
                            ).format(group))
            groups[key] = group

        for registration_info in registration_infos:
            if not registration_info.chosen:
                continue
            invitation = registration_info.invitation
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
                section = self._get_section(base_info.section)
                print registration_info
                academic = student.academic_set.get(section=section)
                try:
                    participation = (
                            sessions.AcademicParticipation.objects.get(
                                academic = academic,
                                session = session,
                                ))
                except sessions.AcademicParticipation.DoesNotExist:
                    participation = sessions.AcademicParticipation()
                    participation.academic = academic
                    participation.session = session
                    participation.payment = payment
                    participation.save()
                    key = generate_key(
                            registration_info.assigned_session_program)
                    group = groups[key]
                    group.academics.add(participation)
                    self.message_user(
                            request,
                            _(
                                u'Created participation '
                                u'({0.id} {0.first_name} {0.last_name}) '
                                u'{1} '
                                u'and added to {2.id} {2.comment}'
                                ).format(student, session, group))

    def show_message(self, request, queryset):
        """ For testing messaging framework.
        """
        self.message_user(
                request,
                _(u'Selected {0} entries.').format(
                    queryset.count()))

    def _get_session(self):
        """ Returns the current session object.
        """
        year = info.year
        if info.session.endswith(u'pavasario'):
            # Assuming that session type is program based.
            session_type = u'Sp'
        else:
            raise Exception(u'Uknown session type')

        session = sessions.Session.objects.get(
                year=year,
                session_type=session_type,
                )
        return session

    @transaction.commit_on_success
    def update(self, request, queryset):
        """ Copies to nmadb_session.
        """
        session = self._get_session()

        self._update_db_info_about_students(
                request,
                queryset,
                #models.RegistrationInfo.objects.all(),
                session)
    update.short_description = _(
            u'Update NMADB info with collected data.')

    @transaction.commit_on_success
    def create(self, request, queryset):
        """ Creates participation entries.
        """
        session = self._get_session()

        self._create_session_participation_entries(
                request,
                queryset,
                #models.RegistrationInfo.objects.all(),
                session)
    create.short_description = _(
            u'Create participation entries.')


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


#admin.site.register(models.BaseInfo, BaseInfoAdmin)
#admin.site.register(models.RegistrationInfo, RegistrationInfoAdmin)
#admin.site.register(models.ParentInfo, ParentInfoAdmin)
