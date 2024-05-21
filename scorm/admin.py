from django.contrib import admin

from .models import ScormAsset, ScormResponse, ScormAssignment, UserScormMapping, Course, Module

admin.site.register(ScormAsset)
admin.site.register(ScormResponse)
admin.site.register(ScormAssignment)
admin.site.register(UserScormMapping)
admin.site.register(Course)
admin.site.register(Module)
