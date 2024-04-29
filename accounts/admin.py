from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (_("Custom Fields"), {"fields": ("is_core_admin", "is_client_admin")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            _("Custom Fields"),
            {
                "classes": ("wide",),
                "fields": ("is_core_admin", "is_client_admin"),
            },
        ),
    )
