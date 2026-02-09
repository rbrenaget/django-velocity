"""
Tests for security middleware.
"""

import pytest

from apps.security.middleware import (
    AdminIPRestrictionMiddleware,
    SecurityHeadersMiddleware,
)
from apps.security.models import AdminIPAllowlist
from django.test import RequestFactory, override_settings


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def get_response():
    """Mock get_response function."""

    def _get_response(request):
        from django.http import HttpResponse

        return HttpResponse("OK")

    return _get_response


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware."""

    def test_adds_security_headers(self, request_factory, get_response):
        """Should add security headers to response."""
        middleware = SecurityHeadersMiddleware(get_response)
        request = request_factory.get("/")

        response = middleware(request)

        assert response["X-Content-Type-Options"] == "nosniff"
        assert response["X-Frame-Options"] == "DENY"
        assert response["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "Permissions-Policy" in response

    @override_settings(SECURITY_HEADERS_ENABLED=False)
    def test_disabled_does_not_add_headers(self, request_factory, get_response):
        """Should not add headers when disabled."""
        middleware = SecurityHeadersMiddleware(get_response)
        request = request_factory.get("/")

        response = middleware(request)

        assert "X-Content-Type-Options" not in response

    @override_settings(SECURITY_CSP_POLICY="default-src 'self'")
    def test_adds_csp_header_when_configured(self, request_factory, get_response):
        """Should add CSP header when configured."""
        middleware = SecurityHeadersMiddleware(get_response)
        request = request_factory.get("/")

        response = middleware(request)

        assert response["Content-Security-Policy"] == "default-src 'self'"


class TestAdminIPRestrictionMiddleware:
    """Tests for AdminIPRestrictionMiddleware."""

    def test_allows_when_no_allowlist_entries(self, request_factory, get_response, db):
        """Should allow access when allowlist is empty."""
        middleware = AdminIPRestrictionMiddleware(get_response)
        request = request_factory.get("/admin/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        response = middleware(request)

        assert response.status_code == 200

    def test_allows_when_ip_in_allowlist(self, request_factory, get_response, db):
        """Should allow access when IP is in allowlist."""
        AdminIPAllowlist.objects.create(ip_address="192.168.1.100", is_active=True)
        middleware = AdminIPRestrictionMiddleware(get_response)
        request = request_factory.get("/admin/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        response = middleware(request)

        assert response.status_code == 200

    def test_denies_when_ip_not_in_allowlist(self, request_factory, get_response, db):
        """Should deny access when IP is not in allowlist."""
        AdminIPAllowlist.objects.create(ip_address="192.168.1.100", is_active=True)
        middleware = AdminIPRestrictionMiddleware(get_response)
        request = request_factory.get("/admin/")
        request.META["REMOTE_ADDR"] = "192.168.1.200"

        response = middleware(request)

        assert response.status_code == 403

    def test_allows_non_admin_paths(self, request_factory, get_response, db):
        """Should allow non-admin paths even when IP not in allowlist."""
        AdminIPAllowlist.objects.create(ip_address="192.168.1.100", is_active=True)
        middleware = AdminIPRestrictionMiddleware(get_response)
        request = request_factory.get("/api/v1/users/")
        request.META["REMOTE_ADDR"] = "192.168.1.200"

        response = middleware(request)

        assert response.status_code == 200

    @override_settings(ADMIN_IP_RESTRICTION_ENABLED=False)
    def test_disabled_allows_all(self, request_factory, get_response, db):
        """Should allow access when disabled even with allowlist entries."""
        AdminIPAllowlist.objects.create(ip_address="192.168.1.100", is_active=True)
        middleware = AdminIPRestrictionMiddleware(get_response)
        request = request_factory.get("/admin/")
        request.META["REMOTE_ADDR"] = "192.168.1.200"

        response = middleware(request)

        assert response.status_code == 200
