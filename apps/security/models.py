"""
Security Models - Session tracking and IP allowlisting.
"""

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class UserSession(BaseModel):
    """
    Track active user sessions for session management.

    Allows users to view all their active sessions and revoke them remotely.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    session_key = models.CharField(
        max_length=40,
        unique=True,
        db_index=True,
        help_text="Django session key",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address at login",
    )
    user_agent = models.TextField(
        blank=True,
        default="",
        help_text="Browser user agent string",
    )
    device_info = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Parsed device info (browser, OS)",
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether session is still valid",
    )

    class Meta:
        verbose_name = "user session"
        verbose_name_plural = "user sessions"
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.device_info or 'Unknown device'}"


class AdminIPAllowlist(BaseModel):
    """
    IP addresses allowed to access the admin panel.

    If no entries exist, admin is accessible from any IP.
    """

    ip_address = models.GenericIPAddressField(
        unique=True,
        help_text="IPv4 or IPv6 address",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Description (e.g., 'Office VPN')",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this IP is currently allowed",
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ip_allowlist_entries",
    )

    class Meta:
        verbose_name = "admin IP allowlist"
        verbose_name_plural = "admin IP allowlist"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.ip_address} - {self.description}"
