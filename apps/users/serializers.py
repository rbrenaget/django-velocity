"""
User Serializers - Input/Output schemas for User API.

Note: Authentication serializers are now in apps.authentication.
"""

from rest_framework import serializers

from .models import User


class UserOutputSerializer(serializers.ModelSerializer):
    """Serializer for User output (responses)."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserUpdateInputSerializer(serializers.Serializer):
    """Serializer for user profile update."""

    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)


class ChangePasswordInputSerializer(serializers.Serializer):
    """Serializer for authenticated password change."""

    current_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={"input_type": "password"},
    )
