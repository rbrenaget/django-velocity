"""
Security Admin - Unfold-compatible admin for security models.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import AdminIPAllowlist, UserSession


@admin.register(UserSession)
class UserSessionAdmin(ModelAdmin):
    """Admin for user sessions."""

    list_display = ["user", "device_info", "ip_address", "last_activity", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["user__email", "ip_address", "device_info"]
    readonly_fields = ["session_key", "user_agent", "ip_address", "created_at"]
    ordering = ["-last_activity"]

    def has_add_permission(self, request):
        return False


@admin.register(AdminIPAllowlist)
class AdminIPAllowlistAdmin(ModelAdmin):
    """Admin for IP allowlist."""

    list_display = ["ip_address", "description", "is_active", "added_by", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["ip_address", "description"]
    readonly_fields = ["added_by", "created_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
