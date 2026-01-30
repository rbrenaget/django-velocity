"""
Permission Selectors - Read operations for permissions.

Uses Django's built-in Group/Permission models with django-guardian
for object-level permission queries.
"""

from guardian.shortcuts import (
    get_groups_with_perms,
    get_objects_for_user,
    get_perms,
    get_users_with_perms,
)

from apps.users.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet


def group_get_by_id(*, group_id: int) -> Group | None:
    """Get a group by its primary key."""
    return Group.objects.filter(pk=group_id).first()


def group_get_by_name(*, name: str) -> Group | None:
    """Get a group by its name (case-insensitive)."""
    return Group.objects.filter(name__iexact=name).first()


def group_list() -> QuerySet[Group]:
    """Get all groups."""
    return Group.objects.all()


def group_list_for_user(*, user: User) -> QuerySet[Group]:
    """Get all groups a user belongs to."""
    return user.groups.all()


def permission_check(
    *,
    user: User,
    permission: str,
    obj: Model,
) -> bool:
    """
    Check if a user has a specific permission on an object.

    Args:
        user: The user to check
        permission: Permission codename (e.g., 'view', 'change')
        obj: The object to check

    Returns:
        True if user has the permission, False otherwise
    """
    return user.has_perm(permission, obj)


def permission_list_for_user(
    *,
    user: User,
    obj: Model,
) -> list[str]:
    """
    Get all permissions a user has on an object.

    Args:
        user: The user to check
        obj: The object to check

    Returns:
        List of permission codenames
    """
    return get_perms(user, obj)


def user_list_with_permission(
    *,
    obj: Model,
    permission: str | None = None,
) -> list[User]:
    """
    Get all users with permissions on an object.

    Args:
        obj: The object to check
        permission: Optional specific permission to filter by

    Returns:
        List of User instances with permissions
    """
    if permission:
        return list(get_users_with_perms(obj, only_with_perms_in=[permission]))
    return list(get_users_with_perms(obj))


def group_list_with_permission(
    *,
    obj: Model,
    permission: str | None = None,
) -> list[Group]:
    """
    Get all groups with permissions on an object.

    Args:
        obj: The object to check
        permission: Optional specific permission to filter by

    Returns:
        List of Group instances with permissions
    """
    if permission:
        return list(get_groups_with_perms(obj, only_with_perms_in=[permission]))
    return list(get_groups_with_perms(obj))


def object_list_for_user(
    *,
    user: User,
    model_class: type[Model],
    permission: str,
) -> QuerySet:
    """
    Get all objects of a model that a user has a specific permission on.

    Args:
        user: The user to check
        model_class: The model class to query
        permission: The permission codename to check

    Returns:
        QuerySet of objects the user has permission on
    """
    return get_objects_for_user(
        user,
        permission,
        klass=model_class,
    )


def user_in_group(*, user: User, group: Group) -> bool:
    """Check if a user is in a specific group."""
    return user.groups.filter(pk=group.pk).exists()


def permission_exists(*, codename: str) -> bool:
    """Check if a permission with the given codename exists."""
    return Permission.objects.filter(codename=codename).exists()


def permission_list_for_content_type(
    *,
    model_class: type[Model],
) -> QuerySet[Permission]:
    """Get all permissions for a specific model."""
    content_type = ContentType.objects.get_for_model(model_class)
    return Permission.objects.filter(content_type=content_type)
