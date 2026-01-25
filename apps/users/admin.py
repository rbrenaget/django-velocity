"""
User Admin Configuration.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model with email-based authentication.
    """

    list_display = ["email", "first_name", "last_name", "is_staff", "is_active", "created_at"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]

    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal Info", {"fields": ["first_name", "last_name"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ],
            },
        ),
        ("Important Dates", {"fields": ["last_login", "created_at", "updated_at"]}),
    ]
    readonly_fields = ["created_at", "updated_at", "last_login"]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
