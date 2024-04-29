from django.contrib import admin

from .models import ScormAsset, ScormResponse, ScormAssignment, UserScormMapping

admin.site.register(ScormAsset)
admin.site.register(ScormResponse)
admin.site.register(ScormAssignment)
admin.site.register(UserScormMapping)
