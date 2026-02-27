"""
Security Middleware - Headers, IP restriction, and session tracking.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils import timezone

from apps.core.utils import get_client_ip

from .models import UserSession
from .selectors import ip_is_allowed

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.

    Configurable via settings:
    - SECURITY_HEADERS_ENABLED: bool (default True)
    - SECURITY_CSP_POLICY: str (Content-Security-Policy)
    - SECURITY_HSTS_SECONDS: int (Strict-Transport-Security)
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if not getattr(settings, "SECURITY_HEADERS_ENABLED", True):
            return response

        response["X-Content-Type-Options"] = "nosniff"

        response["X-Frame-Options"] = "DENY"

        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        response["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )

        csp = getattr(settings, "SECURITY_CSP_POLICY", None)
        if csp:
            response["Content-Security-Policy"] = csp

        hsts_seconds = getattr(settings, "SECURITY_HSTS_SECONDS", 0)
        if hsts_seconds > 0 and request.is_secure():
            response["Strict-Transport-Security"] = (
                f"max-age={hsts_seconds}; includeSubDomains; preload"
            )

        return response


class AdminIPRestrictionMiddleware:
    """
    Restrict admin access to allowed IP addresses.

    If AdminIPAllowlist has no active entries, all IPs are allowed.

    Configurable via settings:
    - ADMIN_IP_RESTRICTION_ENABLED: bool (default True)
    - ADMIN_URL_PREFIX: str (default '/admin/')
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not getattr(settings, "ADMIN_IP_RESTRICTION_ENABLED", True):
            return self.get_response(request)

        admin_prefix = getattr(settings, "ADMIN_URL_PREFIX", "/admin/")

        if not request.path.startswith(admin_prefix):
            return self.get_response(request)

        ip_address = get_client_ip(request) or ""

        if not ip_is_allowed(ip_address=ip_address):
            logger.warning(f"Admin access denied for IP {ip_address} at {request.path}")
            return HttpResponseForbidden(
                "Access denied. Your IP is not in the allowlist."
            )

        return self.get_response(request)


class SessionTrackingMiddleware:
    """
    Track session activity for authenticated users.

    Updates last_activity timestamp on each request.
    Creates session record if not exists.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if not request.user.is_authenticated:
            return response

        session_key = request.session.session_key
        if not session_key:
            return response

        UserSession.objects.filter(
            session_key=session_key,
            user=request.user,
            is_active=True,
        ).update(last_activity=timezone.now())

        return response
