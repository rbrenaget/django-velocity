"""
User Services - Write operations for User domain.

User profile management operations.
Note: Authentication services are now in apps.authentication.
"""

from __future__ import annotations

from apps.core.exceptions import PermissionDenied
from apps.core.services import service

from .models import User


@service
def user_update(
    *,
    user: User,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    """
    Update user profile information.

    Args:
        user: The User instance to update
        first_name: Optional new first name
        last_name: Optional new last name

    Returns:
        The updated User instance
    """
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name

    user.save(update_fields=["first_name", "last_name", "updated_at"])
    return user


@service
def user_change_password(
    *,
    user: User,
    current_password: str,
    new_password: str,
) -> User:
    """
    Change user's password.

    Args:
        user: The User instance
        current_password: Current password for verification
        new_password: New password to set

    Returns:
        The updated User instance

    Raises:
        PermissionDenied: If current password is incorrect
    """
    if not user.check_password(current_password):
        raise PermissionDenied(
            message="Current password is incorrect.",
        )

    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])

    return user


@service
def user_deactivate(*, user: User) -> User:
    """
    Deactivate a user account (soft delete).

    Args:
        user: The User instance to deactivate

    Returns:
        The deactivated User instance
    """
    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])

    return user
