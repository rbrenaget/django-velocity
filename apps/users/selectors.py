"""
User Selectors - Read operations for User domain.

Selectors are responsible for:
- Fetching data from the database
- Complex filtering and aggregations
- Returning QuerySets or single objects

IMPORTANT: Selectors should NEVER modify data.
"""

from __future__ import annotations

from django.db.models import QuerySet

from .models import User


def user_get_by_id(*, user_id: int) -> User | None:
    """
    Get a user by their primary key.

    Args:
        user_id: The user's ID

    Returns:
        User instance or None if not found
    """
    return User.objects.filter(pk=user_id).first()


def user_get_by_email(*, email: str) -> User | None:
    """
    Get a user by their email address.

    Args:
        email: The user's email address

    Returns:
        User instance or None if not found
    """
    return User.objects.filter(email__iexact=email).first()


def user_list(
    *,
    is_active: bool | None = None,
    is_staff: bool | None = None,
) -> QuerySet[User]:
    """
    Get a filtered queryset of users.

    Args:
        is_active: Filter by active status (optional)
        is_staff: Filter by staff status (optional)

    Returns:
        QuerySet of User instances
    """
    queryset = User.objects.all()

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if is_staff is not None:
        queryset = queryset.filter(is_staff=is_staff)

    return queryset


def user_list_active() -> QuerySet[User]:
    """
    Get all active users.

    Returns:
        QuerySet of active User instances
    """
    return user_list(is_active=True)


def user_exists(*, email: str) -> bool:
    """
    Check if a user with the given email exists.

    Args:
        email: The email to check

    Returns:
        True if user exists, False otherwise
    """
    return User.objects.filter(email__iexact=email).exists()
