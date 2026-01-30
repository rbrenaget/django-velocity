"""
Permissions App Configuration.
"""

from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    """Configuration for the permissions app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.permissions"
    verbose_name = "Permissions"
