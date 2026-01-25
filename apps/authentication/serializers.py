"""
Authentication Serializers - Input/Output schemas for auth API.
"""

from rest_framework import serializers

from apps.users.serializers import UserOutputSerializer


class RegisterInputSerializer(serializers.Serializer):
    """Serializer for user registration."""

    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={"input_type": "password"},
    )
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")


class RegisterOutputSerializer(serializers.Serializer):
    """Serializer for registration response with tokens."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserOutputSerializer(read_only=True)


class LoginInputSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )


class TokenOutputSerializer(serializers.Serializer):
    """Serializer for JWT token output."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserOutputSerializer(read_only=True)


class ForgotPasswordInputSerializer(serializers.Serializer):
    """Serializer for forgot password request."""

    email = serializers.EmailField()


class ResetPasswordInputSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={"input_type": "password"},
    )


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


class VerifyEmailInputSerializer(serializers.Serializer):
    """Serializer for email verification."""

    key = serializers.CharField()
