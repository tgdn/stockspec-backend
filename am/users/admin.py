from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

UserAdmin.fieldsets = (
    (None, {"fields": ("username", "password", "picture_url")}),
    (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
    (
        _("Permissions"),
        {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        },
    ),
    (_("Important dates"), {"fields": ("last_login", "date_joined")}),
)

admin.site.register(User, UserAdmin)
