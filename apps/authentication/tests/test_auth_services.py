"""
Tests for Authentication Services.

These tests validate the authentication business logic.
"""

import pytest

from apps.authentication import services
from apps.core.exceptions import ValidationError


@pytest.mark.django_db
class TestRegisterUser:
    """Tests for register_user service."""

    def test_creates_user_successfully(self):
        """Test creating a new user with valid data."""
        result = services.register_user(
            email="new@example.com",
            password="securepass123",
            first_name="New",
            last_name="User",
        )

        assert result["user"].pk is not None
        assert result["user"].email == "new@example.com"
        assert result["user"].first_name == "New"
        assert result["user"].last_name == "User"
        assert result["user"].is_active is True
        assert result["user"].check_password("securepass123")
        assert "access" in result
        assert "refresh" in result

    def test_raises_on_duplicate_email(self, user):
        """Test that creating a user with existing email raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            services.register_user(
                email=user.email,
                password="anotherpass123",
            )

        assert "already exists" in str(exc_info.value.message)


@pytest.mark.django_db
class TestLoginUser:
    """Tests for login_user service."""

    def test_authenticates_valid_credentials(self, user):
        """Test authentication with valid credentials returns tokens."""
        result = services.login_user(
            email=user.email,
            password="testpass123",
        )

        assert "access" in result
        assert "refresh" in result
        assert "user" in result
        assert result["user"] == user

    def test_raises_on_invalid_email(self):
        """Test that invalid email raises ValidationError."""
        with pytest.raises(ValidationError):
            services.login_user(
                email="nonexistent@example.com",
                password="anypassword",
            )

    def test_raises_on_invalid_password(self, user):
        """Test that wrong password raises ValidationError."""
        with pytest.raises(ValidationError):
            services.login_user(
                email=user.email,
                password="wrongpassword",
            )

    def test_raises_on_inactive_user(self, user):
        """Test that inactive user cannot authenticate.

        Note: Django's authenticate() returns None for inactive users,
        so we get ValidationError (invalid credentials) rather than PermissionDenied.
        """
        user.is_active = False
        user.save()

        with pytest.raises(ValidationError):
            services.login_user(
                email=user.email,
                password="testpass123",
            )
