from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'nmadb_session_reg.views',
    url(r'^base/import/$', 'import_base',
        name='nmadb-session-reg-import-base-info',),
    url((
        r'(?P<uuid>'
        r'[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}'
        r')/$'
        ),
        'register',
        name='nmadb-session-reg-registration'),
    )
