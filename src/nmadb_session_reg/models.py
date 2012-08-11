# -*- coding: utf-8 -*-


from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from db_utils.validators.name import (
        NamesValidator, SurnameValidator, ALPHABET_LT)
from db_utils.validators.phone_number import PhoneNumberValidator


from nmadb_session_reg.config import INFO


class School(models.Model):
    """
    """

    title = models.CharField(
            max_length=80,
            blank=False,
            verbose_name=u'Pavadinimas',
            unique=True,
            )

    class Meta(object):
        db_table = u'nma_reg_common_school'
        ordering = [u'title']
        verbose_name = u'Mokykla'
        verbose_name_plural = u'Mokyklos'

    def __unicode__(self):
        return self.title


class BaseInfo(models.Model):
    """ Base information about student.
    """

    first_name = models.CharField(
            max_length=45,
            verbose_name=u'Vardas',
            validators=[
                NamesValidator(
                    ALPHABET_LT,
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),],
            )

    last_name = models.CharField(
            max_length=45,
            verbose_name=u'Pavardė',
            validators=[
                SurnameValidator(
                    ALPHABET_LT,
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),],
            )

    email = models.EmailField(
            max_length=128,
            verbose_name=u'Elektroninio pašto adresas',
            )

    db_id = models.IntegerField(        # ZmogusId iš NMADB.
            blank=True,
            null=True,
            )

    section = models.CharField(
            max_length=20,
            verbose_name=u'Sekcija',
            )

    comment = models.TextField(
            blank=True,
            null=True,
            verbose_name=u'Pastabos',
            )

    payment = models.IntegerField(
            verbose_name=u'Dalyvio mokestis',
            )

    class Meta(object):
        db_table = u'session_reg_baseinfo'
        ordering = [u'last_name', u'first_name',]
        verbose_name = u'Bazinė informacija'
        verbose_name_plural = u'Bazinės informacijos'

    def __unicode__(self):
        return u'<{0.id}> {0.first_name} {0.last_name}'.format(self)


class Invitation(models.Model):
    """ Invitation to session. Actually this table is created, when
    invitation email is sent to pupil.
    """

    base = models.ForeignKey(
            BaseInfo,
            related_name='invitations',
            verbose_name=u'Bazinė informacija',
            )

    uuid = models.CharField(
            max_length=36,
            unique=True,
            verbose_name=u'Kvietimo identifikatorius',
            )

    payment = models.IntegerField(
            verbose_name=u'Dalyvio mokestis',
            )

    create_timestamp = models.DateTimeField(
            verbose_name=u'Kvietimo sukūrimo data',
            auto_now_add=True)

    class Meta(object):
        db_table = u'session_reg_invitation'
        ordering = [u'base',]
        verbose_name = u'Kvietimas'
        verbose_name_plural = u'Kvietimai'

    def __unicode__(self):
        return u'<{0.id}> bazinė anketa: {0.base}'.format(self)


class StudentInfo(models.Model):
    """ All information, which was entered by student.
    """

    invitation = models.OneToOneField(
            Invitation,
            related_name='student_info',
            verbose_name=u'Kvietimas',
            )

    first_name = models.CharField(
            max_length=45,
            verbose_name=u'Vardas',
            validators=[
                NamesValidator(
                    ALPHABET_LT,
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),],
            )

    last_name = models.CharField(
            max_length=45,
            verbose_name=u'Pavardė',
            validators=[
                SurnameValidator(
                    ALPHABET_LT,
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),],
            )

    email = models.EmailField(
            max_length=128,
            verbose_name=u'Dabartinio elektroninio pašto adresas',
            )

    phone_number = models.CharField(
            max_length=16,
            verbose_name=u'Asmeninis telefono numeris',
            validators=[
                PhoneNumberValidator(
                    u'370',
                    validation_exception_type=ValidationError,
                    convert=False,
                    )
                ],
            )

    school_class = models.PositiveSmallIntegerField(
            verbose_name=u'Klasė',
            validators=[
                validators.MaxValueValidator(12),
                validators.MinValueValidator(6),
                ])

    school_year = models.IntegerField(
            verbose_name=u'Klasės atnaujinimo metai',
            help_text=(
                u'Nurodo kurių metų sausio 3 dieną buvo '
                u'„school_class“ klasėje.'),
            )

    school = models.ForeignKey(
            School,
            verbose_name=u'Mokykla',
            )

    home_address = models.CharField(max_length=90,
            verbose_name=u'Namų adresas',
            help_text=(
                u'Pavyzdžiui: „Subačiaus g. 120, LT-11345 Vilnius.“ '
                u'arba „Antagavės k., Ignalinos pšt., '
                u'LT-30148 Ignalinos r. sav.“'
                ),
            )

    create_timestamp = models.DateTimeField(
            verbose_name=u'Užpildymo laikas',
            auto_now_add=True,
            )

    # Information entered by administrator:

    payed = models.BooleanField(
            verbose_name=u'Susimokėjo',
            help_text=u'Mokinys susimokėjo registracijos mokestį.',
            blank=True,
            )

    chosen = models.BooleanField(
            verbose_name=u'Priimtas',
            help_text=u'Mokinys priimtas į sesiją.',
            blank=True,
            )

    comment = models.TextField(
            blank=True,
            null=True,
            verbose_name=u'Pastabos',
            )

    class Meta(object):
        db_table = u'session_reg_studentinfo'
        ordering = [u'invitation',]
        verbose_name = u'Akademiko informacija'
        verbose_name_plural = u'Akademikų informacijos'

    def __unicode__(self):
        return u'<{0.id}> kvietimas: {0.invitation}'.format(self)


class ParentInfo(models.Model):
    """ Parent information.
    """

    child = models.ForeignKey(
            StudentInfo,
            related_name='parents',
            verbose_name=u'Vaikas',
            )

    relation = models.CharField(
            max_length=2,
            choices=INFO['parent_child_relations'],
            verbose_name=u'Ryšys',
            )

    first_name = models.CharField(
            max_length=45,
            verbose_name=u'Vardas',
            validators=[
                NamesValidator(
                    ALPHABET_LT,
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),],
            )

    last_name = models.CharField(
            max_length=45,
            verbose_name=u'Pavardė',
            validators=[
                SurnameValidator(
                    ALPHABET_LT,
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),],
            )

    job = models.CharField(
            max_length=128,
            blank=True,
            verbose_name=u'Darbovietė',
            )

    job_phone_number = models.CharField(
            max_length=16,
            verbose_name=u'Darbo telefono numeris',
            help_text=(
                u'Arba įveskite teisingą numerį, arba palikite laukelį '
                u'visiškai tuščią.'
                ),
            validators=[
                PhoneNumberValidator(
                    u'370',
                    validation_exception_type=ValidationError,
                    convert=False,
                    )
                ],
            blank=True,
            )

    job_position = models.CharField(
            max_length=128,
            blank=True,
            verbose_name=u'Pareigos',
            )

    phone_number = models.CharField(
            max_length=16,
            verbose_name=u'Mobiliojo telefono numeris',
            validators=[
                PhoneNumberValidator(
                    u'370',
                    validation_exception_type=ValidationError,
                    convert=False,
                    )
                ],
            )

    email = models.EmailField(
            max_length=128,
            verbose_name=u'Elektroninio pašto adresas',
            )

    class Meta(object):
        db_table = u'session_reg_parentinfo'
        ordering = [u'last_name', u'first_name',]
        verbose_name = u'Tėvo informacija'
        verbose_name_plural = u'Tėvų informacijos'

    def __unicode__(self):
        return u'<{0.child}> {0.first_name} {0.last_name}'.format(self)
