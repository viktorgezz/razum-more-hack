from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Дополнительные поля",
            {"fields": ("role", "city", "birth_date", "avatar", "is_verified")},
        ),
    )
    list_display = (
        "id",
        "username",
        "email",
        "role",
        "is_verified",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_verified", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name", "city")
