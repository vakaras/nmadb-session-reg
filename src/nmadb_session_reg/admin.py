from django.contrib import admin

from nmadb_session_reg import models


admin.site.register(models.SessionProgram)
admin.site.register(models.BaseInfo)
admin.site.register(models.StudentInfo)
admin.site.register(models.SessionProgramRating)
admin.site.register(models.ParentInfo)
