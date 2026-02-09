"""
Security Services - Write operations for security domain.

Handles session management, IP allowlisting, and GDPR compliance.
"""

from __future__ import annotations

import contextlib
import logging
from typing import Any

from django.contrib.sessions.models import Session
from django.db.models import Model
from django.http import HttpRequest
from django.utils import timezone

from apps.core.exceptions import NotFound, PermissionDenied, ValidationError
from apps.core.services import service
from apps.users.models import User

from .models import AdminIPAllowlist, UserSession
from .selectors import session_get_by_key

logger = logging.getLogger(__name__)


def _parse_user_agent(user_agent: str) -> str:
    """
    Parse user agent string into a human-readable device description.

    Args:
        user_agent: Raw user agent string

    Returns:
        Simplified device description
    """
    ua_lower = user_agent.lower()

    browser = "Unknown Browser"
    if "chrome" in ua_lower and "edg" not in ua_lower:
        browser = "Chrome"
    elif "firefox" in ua_lower:
        browser = "Firefox"
    elif "safari" in ua_lower and "chrome" not in ua_lower:
        browser = "Safari"
    elif "edg" in ua_lower:
        browser = "Edge"

    os = "Unknown OS"
    if "windows" in ua_lower:
        os = "Windows"
    elif "mac os" in ua_lower or "macos" in ua_lower:
        os = "macOS"
    elif "linux" in ua_lower:
        os = "Linux"
    elif "android" in ua_lower:
        os = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        os = "iOS"

    return f"{browser} on {os}"


def _get_client_ip(request: HttpRequest) -> str | None:
    """
    Extract client IP from request headers.

    Args:
        request: The HTTP request

    Returns:
        Client IP address or None
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@service
def session_create(*, user: User, request: HttpRequest) -> UserSession:
    """
    Create a session record for tracking.

    Should be called after successful login.

    Args:
        user: The logged-in user
        request: The HTTP request

    Returns:
        Created UserSession instance
    """
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    user_agent = request.META.get("HTTP_USER_AGENT", "")
    ip_address = _get_client_ip(request)
    device_info = _parse_user_agent(user_agent)

    session, created = UserSession.objects.update_or_create(
        session_key=session_key,
        defaults={
            "user": user,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "device_info": device_info,
            "is_active": True,
        },
    )

    if created:
        logger.info(f"Session created for user {user.email} from {ip_address}")
    else:
        logger.info(f"Session updated for user {user.email}")

    return session


@service
def session_revoke(*, user: User, session_key: str) -> None:
    """
    Revoke a specific session.

    Args:
        user: The user revoking the session (must own it)
        session_key: The session key to revoke

    Raises:
        NotFound: If session doesn't exist
        PermissionDenied: If user doesn't own the session
    """
    session = session_get_by_key(session_key=session_key)

    if session is None:
        raise NotFound(message="Session not found.")

    if session.user_id != user.id:
        raise PermissionDenied(message="Cannot revoke another user's session.")

    session.is_active = False
    session.save(update_fields=["is_active", "updated_at"])

    # Attempt to delete the Django session too
    with contextlib.suppress(Exception):
        Session.objects.filter(pk=session_key).delete()

    logger.info(f"Session revoked for user {user.email}")


@service
def session_revoke_all(*, user: User, except_current: str | None = None) -> int:
    """
    Revoke all sessions for a user.

    Args:
        user: The user to revoke sessions for
        except_current: Session key to keep active (current session)

    Returns:
        Number of sessions revoked
    """
    sessions = UserSession.objects.filter(user=user, is_active=True)

    if except_current:
        sessions = sessions.exclude(session_key=except_current)

    session_keys = list(sessions.values_list("session_key", flat=True))
    count = sessions.update(is_active=False)

    Session.objects.filter(pk__in=session_keys).delete()

    logger.info(f"Revoked {count} sessions for user {user.email}")
    return count


@service
def ip_allowlist_add(
    *,
    ip_address: str,
    description: str = "",
    added_by: User | None = None,
) -> AdminIPAllowlist:
    """
    Add an IP address to the admin allowlist.

    Args:
        ip_address: The IP address to add
        description: Optional description
        added_by: User who added the entry

    Returns:
        Created AdminIPAllowlist instance

    Raises:
        ValidationError: If IP already exists
    """
    if AdminIPAllowlist.objects.filter(ip_address=ip_address).exists():
        raise ValidationError(
            message="IP address already in allowlist.",
            extra={"ip_address": ip_address},
        )

    entry = AdminIPAllowlist.objects.create(
        ip_address=ip_address,
        description=description,
        added_by=added_by,
        is_active=True,
    )

    logger.info(f"Added IP {ip_address} to admin allowlist")
    return entry


@service
def ip_allowlist_remove(*, ip_address: str) -> None:
    """
    Remove an IP address from the admin allowlist.

    Args:
        ip_address: The IP address to remove

    Raises:
        NotFound: If IP not in allowlist
    """
    try:
        entry = AdminIPAllowlist.objects.get(ip_address=ip_address)
        entry.delete()
        logger.info(f"Removed IP {ip_address} from admin allowlist")
    except AdminIPAllowlist.DoesNotExist:
        raise NotFound(message="IP address not in allowlist.") from None


@service
def ip_allowlist_toggle(*, ip_address: str, is_active: bool) -> AdminIPAllowlist:
    """
    Enable or disable an IP allowlist entry.

    Args:
        ip_address: The IP address to toggle
        is_active: Whether to enable or disable

    Returns:
        Updated AdminIPAllowlist

    Raises:
        NotFound: If IP not in allowlist
    """
    try:
        entry = AdminIPAllowlist.objects.get(ip_address=ip_address)
        entry.is_active = is_active
        entry.save(update_fields=["is_active", "updated_at"])
        return entry
    except AdminIPAllowlist.DoesNotExist:
        raise NotFound(message="IP address not in allowlist.") from None


def _serialize_model(obj: Model) -> dict[str, Any]:
    """Serialize a model instance to a dict for export."""
    data = {}
    for field in obj._meta.get_fields():
        if hasattr(field, "value_from_object"):
            value = field.value_from_object(obj)
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            data[field.name] = value
    return data


@service
def user_export_data(*, user: User) -> dict[str, Any]:
    """
    Export all user data for GDPR compliance.

    Args:
        user: The user requesting their data

    Returns:
        Dict containing all user data
    """
    export_data = {
        "exported_at": timezone.now().isoformat(),
        "user": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
        },
        "sessions": [],
        "permissions": {
            "groups": list(user.groups.values_list("name", flat=True)),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        },
    }

    for session in UserSession.objects.filter(user=user):
        export_data["sessions"].append(
            {
                "device_info": session.device_info,
                "ip_address": session.ip_address,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "is_active": session.is_active,
            }
        )

    logger.info(f"Data exported for user {user.email}")
    return export_data


@service
def user_delete_account(*, user: User, confirmation: str) -> None:
    """
    Permanently delete a user account and all associated data.

    Args:
        user: The user to delete
        confirmation: Must be the user's email to confirm deletion

    Raises:
        ValidationError: If confirmation doesn't match
    """
    if confirmation != user.email:
        raise ValidationError(
            message="Confirmation does not match email. Account not deleted.",
        )

    email = user.email

    UserSession.objects.filter(user=user).delete()

    user.delete()

    logger.warning(f"Account permanently deleted for user {email}")
