from nmadb_session_reg.models import Info


try:
    info = Info.objects.all()[0]
except IndexError:
    import datetime
    info = Info()
    info.year = 2013
    info.session = u'2013 met\u0173 pavasario'
    info.admin_email = u'atranka@nmakademija.lt'
    info.manager_name_dative = u'Giedrei'
    info.manager_phone = u'+370 677 68 899'
    info.manager_email = u'info@nmakademija.lt'
    info.confirmation_deadline = datetime.date(2013, 3, 28)
    info.save()
finally:
    del Info
