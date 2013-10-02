from django.forms.models import model_to_dict


class Info(object):
    """ Session information object.
    """

    def __init__(self):
        self.session_is_program_based = True
        self._info_object = None

    def as_dict(self):
        """ Returns data as Python dictionary.
        """
        return model_to_dict(self._info, fields=[], exclude=[])

    def __getattr__(self, name):
        return getattr(self._info, name)

    @property
    def _info(self):
        """ Returns the info object.
        """
        if self._info_object is None:
            self._info_object = self._get_info_object()
        return self._info_object

    def _get_info_object(self):
        """ Gets or crates the info object.
        """
        from nmadb_session_reg.models import Info

        try:
            info = Info.objects.all()[0]
        except IndexError:
            import datetime
            info = Info()
            info.year = 2013
            info.session_type = u'Su'   # Vasaros
            info.session = u'2013 met\u0173 vasaros'
            info.manager_name_dative = u'Giedrei'
            info.manager_email = u'info@nmakademija.lt'
            info.manager_phone = u'+370 677 68 899'
            info.admin_email = u'atranka@nmakademija.lt'
            info.confirmation_deadline = datetime.date(2013, 7, 3)
            info.session_is_program_based = self.session_is_program_based
            info.save()
        finally:
            del Info
            return info


info = Info()
