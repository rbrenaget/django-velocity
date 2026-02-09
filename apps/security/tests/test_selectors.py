"""
Tests for security selectors.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.security import selectors
from apps.security.models import AdminIPAllowlist, UserSession

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
    )


class TestSessionListForUser:
    """Tests for session_list_for_user selector."""

    def test_returns_active_sessions(self, user, db):
        """Should return only active sessions."""
        UserSession.objects.create(user=user, session_key="active-1", is_active=True)
        UserSession.objects.create(user=user, session_key="active-2", is_active=True)
        UserSession.objects.create(user=user, session_key="inactive", is_active=False)

        sessions = selectors.session_list_for_user(user=user, active_only=True)

        assert sessions.count() == 2

    def test_returns_all_sessions_when_active_only_false(self, user, db):
        """Should return all sessions when active_only is False."""
        UserSession.objects.create(user=user, session_key="active", is_active=True)
        UserSession.objects.create(user=user, session_key="inactive", is_active=False)

        sessions = selectors.session_list_for_user(user=user, active_only=False)

        assert sessions.count() == 2


class TestSessionGetByKey:
    """Tests for session_get_by_key selector."""

    def test_returns_session_by_key(self, user, db):
        """Should return session by key."""
        UserSession.objects.create(user=user, session_key="test-key")

        session = selectors.session_get_by_key(session_key="test-key")

        assert session is not None
        assert session.session_key == "test-key"

    def test_returns_none_for_missing_session(self, db):
        """Should return None for non-existent session."""
        session = selectors.session_get_by_key(session_key="nonexistent")

        assert session is None


class TestIPIsAllowed:
    """Tests for ip_is_allowed selector."""

    def test_allows_all_when_no_entries(self, db):
        """Should allow all IPs when allowlist is empty."""
        assert selectors.ip_is_allowed(ip_address="192.168.1.1") is True

    def test_allows_listed_ip(self, db):
        """Should allow IP in allowlist."""
        AdminIPAllowlist.objects.create(ip_address="192.168.1.100", is_active=True)

        assert selectors.ip_is_allowed(ip_address="192.168.1.100") is True

    def test_denies_unlisted_ip(self, db):
        """Should deny IP not in allowlist."""
        AdminIPAllowlist.objects.create(ip_address="192.168.1.100", is_active=True)

        assert selectors.ip_is_allowed(ip_address="192.168.1.200") is False

    def test_ignores_inactive_entries(self, db):
        """Should ignore inactive allowlist entries."""
        AdminIPAllowlist.objects.create(ip_address="192.168.1.100", is_active=False)

        # Empty active list = allow all
        assert selectors.ip_is_allowed(ip_address="192.168.1.200") is True
