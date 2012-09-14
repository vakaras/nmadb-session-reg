from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'nmadb_session_reg.views',
    url((
        r'(?P<uuid>'
        r'[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}'
        r')/$'
        ),
        'register',
        name='nmadb-session-reg-registration'),
    url(r'invitations/(?P<queryset>\d+(,\d+)*)/$',
        'send_invitations', name='nmadb-session-reg-send-invitation'),
    url(r'^mail/(?P<queryset>\d+(,\d+)*)/$',
        'send_mail', name='nma-session-reg-send-mail',),
    )
