REGISTRATION_MODULES = (
        'nmadb_session_reg',
        'nmadb_registration',
        )
DATABASE_NAME = 'session-reg'

class SessionRegRouter(object):
    """
    """

    def db_for_read(self, model, **hints):
        """ Point all operations on REGISTRATION_MODULES models to
        DATABASE_NAME.
        """
        if model._meta.app_label in REGISTRATION_MODULES:
            return DATABASE_NAME
        return None

    def db_for_write(self, model, **hints):
        """ Point all operations on REGISTRATION_MODULES models to
        DATABASE_NAME.
        """
        if model._meta.app_label in REGISTRATION_MODULES:
            return DATABASE_NAME
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_syncdb(self, db, model):
        """ Do not allow syncing module databases.
        """
        if model._meta.app_label in REGISTRATION_MODULES:
            return False
        else:
            return None
