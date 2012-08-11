from django.contrib import admin

try:
    import dbinterface
except ImportError:
    import nmadb_session_reg.admin.standalone
else:
    import nmadb_session_reg.admin.module
