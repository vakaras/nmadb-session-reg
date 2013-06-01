from django.contrib import admin

try:
    import nmadb_contacts
except ImportError:
    import nmadb_session_reg.admin.standalone
else:
    import nmadb_session_reg.admin.module
