class SessionRegRouter(object):
    """
    """

    def db_for_read(self, model, **hints):
        """ Point all operations on nmadb_session_reg models to
        'session-reg'.
        """
        if model._meta.app_label == 'nmadb_session_reg':
            return 'session-reg'
        return None

    def db_for_write(self, model, **hints):
        """ Point all operations on nmadb_session_reg models to
        'session-reg'.
        """
        if model._meta.app_label == 'nmadb_session_reg':
            return 'session-reg'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_syncdb(self, db, model):
        if db == 'session-reg':
            return model._meta.app_label == 'nmadb_session_reg'
        elif model._meta.app_label == 'nmadb_session_reg':
            return False
        return None
