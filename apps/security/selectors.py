"""
Security Selectors - Read operations for security domain.
"""

from __future__ import annotations

from django.contrib.sessions.models import Session
from django.db.models import QuerySet
from django.utils import timezone

from apps.users.models import User

from .models import AdminIPAllowlist, UserSession


def session_list_for_user(
    *, user: User, active_only: bool = True
) -> QuerySet[UserSession]:
    """
    Get all sessions for a user.

    Args:
        user: The user to get sessions for
        active_only: Whether to filter to active sessions only

    Returns:
        QuerySet of UserSession objects
    """
    qs = UserSession.objects.filter(user=user)
    if active_only:
        qs = qs.filter(is_active=True)
    return qs.order_by("-last_activity")


def session_get_by_key(*, session_key: str) -> UserSession | None:
    """
    Get a session by its key.

    Args:
        session_key: The Django session key

    Returns:
        UserSession or None if not found
    """
    try:
        return UserSession.objects.get(session_key=session_key)
    except UserSession.DoesNotExist:
        return None


def session_is_current(*, session_key: str, request_session_key: str) -> bool:
    """
    Check if a session is the current request's session.

    Args:
        session_key: The session key to check
        request_session_key: The current request's session key

    Returns:
        True if this is the current session
    """
    return session_key == request_session_key


def ip_is_allowed(*, ip_address: str) -> bool:
    """
    Check if an IP address is in the admin allowlist.

    If no active entries exist, all IPs are allowed.

    Args:
        ip_address: The IP address to check

    Returns:
        True if allowed (or if allowlist is empty)
    """
    active_entries = AdminIPAllowlist.objects.filter(is_active=True)

    if not active_entries.exists():
        return True

    return active_entries.filter(ip_address=ip_address).exists()


def ip_allowlist_list(*, active_only: bool = True) -> QuerySet[AdminIPAllowlist]:
    """
    Get all IP allowlist entries.

    Args:
        active_only: Whether to filter to active entries only

    Returns:
        QuerySet of AdminIPAllowlist objects
    """
    qs = AdminIPAllowlist.objects.all()
    if active_only:
        qs = qs.filter(is_active=True)
    return qs


def session_exists_in_django(*, session_key: str) -> bool:
    """
    Check if a Django session still exists.

    Args:
        session_key: The session key to check

    Returns:
        True if the session exists and hasn't expired
    """
    try:
        session = Session.objects.get(pk=session_key)
        return session.expire_date > timezone.now()
    except Session.DoesNotExist:
        return False
