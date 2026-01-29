"""
Tests for User Selectors.

These tests validate the read operations for users.
"""

import pytest

from apps.users import selectors


@pytest.mark.django_db
class TestUserGetById:
    """Tests for user_get_by_id selector."""

    def test_returns_user_when_exists(self, user):
        """Test fetching user by ID."""
        result = selectors.user_get_by_id(user_id=user.pk)

        assert result is not None
        assert result.pk == user.pk
        assert result.email == user.email

    def test_returns_none_when_not_found(self):
        """Test returns None for non-existent ID."""
        result = selectors.user_get_by_id(user_id=99999)

        assert result is None


@pytest.mark.django_db
class TestUserGetByEmail:
    """Tests for user_get_by_email selector."""

    def test_returns_user_when_exists(self, user):
        """Test fetching user by email."""
        result = selectors.user_get_by_email(email=user.email)

        assert result is not None
        assert result.email == user.email

    def test_case_insensitive_lookup(self, user):
        """Test email lookup is case insensitive."""
        result = selectors.user_get_by_email(email=user.email.upper())

        assert result is not None
        assert result.email == user.email

    def test_returns_none_when_not_found(self):
        """Test returns None for non-existent email."""
        result = selectors.user_get_by_email(email="nonexistent@example.com")

        assert result is None


@pytest.mark.django_db
class TestUserList:
    """Tests for user_list selector."""

    def test_returns_all_users(self, user, other_user):
        """Test fetching all users."""
        result = selectors.user_list()

        assert result.count() == 2

    def test_filters_by_active_status(self, user, other_user):
        """Test filtering by is_active."""
        other_user.is_active = False
        other_user.save()

        active_users = selectors.user_list(is_active=True)
        inactive_users = selectors.user_list(is_active=False)

        assert active_users.count() == 1
        assert inactive_users.count() == 1

    def test_filters_by_staff_status(self, user, admin_user):
        """Test filtering by is_staff."""
        staff_users = selectors.user_list(is_staff=True)
        non_staff_users = selectors.user_list(is_staff=False)

        assert staff_users.count() == 1
        assert non_staff_users.count() == 1


@pytest.mark.django_db
class TestUserListActive:
    """Tests for user_list_active selector."""

    def test_returns_only_active_users(self, user, other_user):
        """Test fetching only active users."""
        other_user.is_active = False
        other_user.save()

        result = selectors.user_list_active()

        assert result.count() == 1
        assert result.first() == user


@pytest.mark.django_db
class TestUserExists:
    """Tests for user_exists selector."""

    def test_returns_true_when_exists(self, user):
        """Test returns True for existing email."""
        assert selectors.user_exists(email=user.email) is True

    def test_returns_false_when_not_exists(self):
        """Test returns False for non-existent email."""
        assert selectors.user_exists(email="nonexistent@example.com") is False

    def test_case_insensitive(self, user):
        """Test email check is case insensitive."""
        assert selectors.user_exists(email=user.email.upper()) is True
