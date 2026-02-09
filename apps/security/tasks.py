"""
Security Tasks - Celery tasks for security maintenance.
"""

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone

from apps.security.models import UserSession
from apps.security.services import user_export_data
from celery import shared_task

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task
def cleanup_expired_sessions() -> int:
    """
    Clean up inactive sessions.

    Marks sessions as inactive if they haven't been used
    within SESSION_INACTIVITY_TIMEOUT.

    Returns:
        Number of sessions cleaned up
    """
    timeout_seconds = getattr(settings, "SESSION_INACTIVITY_TIMEOUT", 604800)
    cutoff = timezone.now() - timezone.timedelta(seconds=timeout_seconds)

    inactive_sessions = UserSession.objects.filter(
        is_active=True,
        last_activity__lt=cutoff,
    )

    session_keys = list(inactive_sessions.values_list("session_key", flat=True))
    count = inactive_sessions.update(is_active=False)

    Session.objects.filter(pk__in=session_keys).delete()

    logger.info(f"Cleaned up {count} expired sessions")
    return count


@shared_task
def export_user_data_async(user_id: int) -> dict:
    """
    Export user data asynchronously for large datasets.

    Args:
        user_id: ID of the user to export data for

    Returns:
        Exported data dict
    """
    try:
        user = User.objects.get(pk=user_id)
        data = user_export_data(user=user)
        logger.info(f"Async data export completed for user {user.email}")
        return data
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for data export")
        return {}
