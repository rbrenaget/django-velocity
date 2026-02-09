"""
Security Serializers - Input/Output for security APIs.
"""

from rest_framework import serializers


class SessionOutputSerializer(serializers.Serializer):
    """Output serializer for session data."""

    session_key = serializers.CharField()
    device_info = serializers.CharField()
    ip_address = serializers.IPAddressField(allow_null=True)
    last_activity = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    is_current = serializers.BooleanField()


class SessionRevokeInputSerializer(serializers.Serializer):
    """Input for revoking a specific session."""

    session_key = serializers.CharField(max_length=40)


class SessionRevokeAllInputSerializer(serializers.Serializer):
    """Input for revoking all sessions."""

    keep_current = serializers.BooleanField(default=True)


class DataExportOutputSerializer(serializers.Serializer):
    """Output serializer for GDPR data export."""

    exported_at = serializers.DateTimeField()
    user = serializers.DictField()
    sessions = serializers.ListField()
    permissions = serializers.DictField()


class DeleteAccountInputSerializer(serializers.Serializer):
    """Input for account deletion confirmation."""

    confirmation = serializers.EmailField(
        help_text="Enter your email address to confirm account deletion."
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Enter your password to confirm.",
    )


class IPAllowlistOutputSerializer(serializers.Serializer):
    """Output serializer for IP allowlist entries."""

    ip_address = serializers.IPAddressField()
    description = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class IPAllowlistInputSerializer(serializers.Serializer):
    """Input for adding IP to allowlist."""

    ip_address = serializers.IPAddressField()
    description = serializers.CharField(max_length=255, required=False, default="")
