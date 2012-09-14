from django.db import transaction
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nmadb_session_reg import models


admin.site.register(models.BaseInfo)
admin.site.register(models.StudentInfo)
admin.site.register(models.Invitation)
admin.site.register(models.ParentInfo)
