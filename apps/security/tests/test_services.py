"""
Tests for security services.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.core.exceptions import NotFound, PermissionDenied, ValidationError
from apps.security import services
from apps.security.models import AdminIPAllowlist, UserSession
from django.test import RequestFactory

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def other_user(db):
    """Create another test user."""
    return User.objects.create_user(
        email="other@example.com",
        password="testpass123",
    )


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


class TestSessionCreate:
    """Tests for session_create service."""

    def test_creates_session_for_user(self, user, request_factory, db):
        """Should create a new session record."""
        request = request_factory.get("/")
        request.session = type(
            "MockSession",
            (),
            {
                "session_key": "test-session-key-123",
                "create": lambda: None,
            },
        )()
        request.META["HTTP_USER_AGENT"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        )
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        session = services.session_create(user=user, request=request)

        assert session.user == user
        assert session.session_key == "test-session-key-123"
        assert session.ip_address == "192.168.1.1"
        assert "Chrome" in session.device_info
        assert "Windows" in session.device_info
        assert session.is_active is True


class TestSessionRevoke:
    """Tests for session_revoke service."""

    def test_revokes_own_session(self, user, db):
        """Should revoke a session owned by the user."""
        session = UserSession.objects.create(
            user=user,
            session_key="session-to-revoke",
            ip_address="192.168.1.1",
            is_active=True,
        )

        services.session_revoke(user=user, session_key="session-to-revoke")

        session.refresh_from_db()
        assert session.is_active is False

    def test_raises_not_found_for_missing_session(self, user, db):
        """Should raise NotFound for non-existent session."""
        with pytest.raises(NotFound):
            services.session_revoke(user=user, session_key="nonexistent")

    def test_raises_permission_denied_for_other_user_session(
        self, user, other_user, db
    ):
        """Should raise PermissionDenied when trying to revoke another user's session."""
        UserSession.objects.create(
            user=other_user,
            session_key="other-user-session",
            ip_address="192.168.1.1",
            is_active=True,
        )

        with pytest.raises(PermissionDenied):
            services.session_revoke(user=user, session_key="other-user-session")


class TestSessionRevokeAll:
    """Tests for session_revoke_all service."""

    def test_revokes_all_sessions(self, user, db):
        """Should revoke all sessions for the user."""
        UserSession.objects.create(user=user, session_key="session-1", is_active=True)
        UserSession.objects.create(user=user, session_key="session-2", is_active=True)

        count = services.session_revoke_all(user=user)

        assert count == 2
        assert UserSession.objects.filter(user=user, is_active=True).count() == 0

    def test_keeps_current_session(self, user, db):
        """Should keep current session when except_current is provided."""
        UserSession.objects.create(user=user, session_key="current", is_active=True)
        UserSession.objects.create(user=user, session_key="other", is_active=True)

        count = services.session_revoke_all(user=user, except_current="current")

        assert count == 1
        assert UserSession.objects.get(session_key="current").is_active is True
        assert UserSession.objects.get(session_key="other").is_active is False


class TestIPAllowlistAdd:
    """Tests for ip_allowlist_add service."""

    def test_adds_ip_to_allowlist(self, user, db):
        """Should add IP to allowlist."""
        entry = services.ip_allowlist_add(
            ip_address="192.168.1.100",
            description="Office VPN",
            added_by=user,
        )

        assert entry.ip_address == "192.168.1.100"
        assert entry.description == "Office VPN"
        assert entry.added_by == user
        assert entry.is_active is True

    def test_raises_for_duplicate_ip(self, user, db):
        """Should raise ValidationError for duplicate IP."""
        services.ip_allowlist_add(ip_address="192.168.1.100")

        with pytest.raises(ValidationError):
            services.ip_allowlist_add(ip_address="192.168.1.100")


class TestIPAllowlistRemove:
    """Tests for ip_allowlist_remove service."""

    def test_removes_ip_from_allowlist(self, db):
        """Should remove IP from allowlist."""
        AdminIPAllowlist.objects.create(ip_address="192.168.1.100")

        services.ip_allowlist_remove(ip_address="192.168.1.100")

        assert not AdminIPAllowlist.objects.filter(ip_address="192.168.1.100").exists()

    def test_raises_not_found_for_missing_ip(self, db):
        """Should raise NotFound for non-existent IP."""
        with pytest.raises(NotFound):
            services.ip_allowlist_remove(ip_address="192.168.1.100")


class TestUserExportData:
    """Tests for user_export_data service."""

    def test_exports_user_data(self, user, db):
        """Should export all user data."""
        UserSession.objects.create(
            user=user,
            session_key="test-session",
            device_info="Chrome on Windows",
            ip_address="192.168.1.1",
        )

        data = services.user_export_data(user=user)

        assert "exported_at" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["first_name"] == "Test"
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["device_info"] == "Chrome on Windows"


class TestUserDeleteAccount:
    """Tests for user_delete_account service."""

    def test_deletes_account_with_correct_confirmation(self, user, db):
        """Should delete account when confirmation matches."""
        user_id = user.id

        services.user_delete_account(user=user, confirmation="test@example.com")

        assert not User.objects.filter(id=user_id).exists()

    def test_raises_for_wrong_confirmation(self, user, db):
        """Should raise ValidationError for wrong confirmation."""
        with pytest.raises(ValidationError):
            services.user_delete_account(user=user, confirmation="wrong@email.com")
