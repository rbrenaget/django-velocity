"""
Core Utilities - Shared helpers used across multiple apps.

These are pure utility functions with no business logic.
"""

from __future__ import annotations

from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> str | None:
    """
    Extract client IP address from request headers.

    Handles X-Forwarded-For for proxied requests.

    Args:
        request: The HTTP request

    Returns:
        Client IP address or None
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
