"""
Tests for User Services.

These tests validate the business logic in services.
They do NOT test through the HTTP layer - that's for integration tests.

Note: Authentication services (register, login) are tested in apps.authentication.
"""

import pytest

from apps.core.exceptions import PermissionDenied
from apps.users import services


@pytest.mark.django_db
class TestUserUpdate:
    """Tests for user_update service."""

    def test_updates_first_name(self, user):
        """Test updating user's first name."""
        updated_user = services.user_update(
            user=user,
            first_name="Updated",
        )

        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == user.last_name  # unchanged

    def test_updates_last_name(self, user):
        """Test updating user's last name."""
        updated_user = services.user_update(
            user=user,
            last_name="NewLastName",
        )

        assert updated_user.last_name == "NewLastName"

    def test_updates_multiple_fields(self, user):
        """Test updating multiple fields at once."""
        updated_user = services.user_update(
            user=user,
            first_name="NewFirst",
            last_name="NewLast",
        )

        assert updated_user.first_name == "NewFirst"
        assert updated_user.last_name == "NewLast"


@pytest.mark.django_db
class TestUserChangePassword:
    """Tests for user_change_password service."""

    def test_changes_password_successfully(self, user):
        """Test changing password with correct current password."""
        services.user_change_password(
            user=user,
            current_password="testpass123",
            new_password="newpass456",
        )

        user.refresh_from_db()
        assert user.check_password("newpass456")
        assert not user.check_password("testpass123")

    def test_raises_on_wrong_current_password(self, user):
        """Test that wrong current password raises PermissionDenied."""
        with pytest.raises(PermissionDenied) as exc_info:
            services.user_change_password(
                user=user,
                current_password="wrongpassword",
                new_password="newpass456",
            )

        assert "incorrect" in str(exc_info.value.message)


@pytest.mark.django_db
class TestUserDeactivate:
    """Tests for user_deactivate service."""

    def test_deactivates_user(self, user):
        """Test deactivating a user."""
        assert user.is_active is True

        deactivated_user = services.user_deactivate(user=user)

        assert deactivated_user.is_active is False
