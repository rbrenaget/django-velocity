"""
Security app configuration.
"""

from django.apps import AppConfig


class SecurityConfig(AppConfig):
    """Security app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.security"
    verbose_name = "Security"

    def ready(self) -> None:
        """Import signals when app is ready."""
        pass
