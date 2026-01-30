"""
Permission Services - Write operations for role-based permissions.

Uses Django's built-in Group/Permission models with django-guardian
for object-level permissions.
"""

import logging
from collections.abc import Sequence

from guardian.models import GroupObjectPermission, UserObjectPermission

from apps.core.exceptions import ValidationError
from apps.core.services import service
from apps.users.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

logger = logging.getLogger(__name__)


def _get_or_create_permission(codename: str, content_type: ContentType) -> Permission:
    """
    Get or create a Permission object.

    This allows creating custom permissions on-the-fly without requiring
    them to be defined in model Meta.permissions.

    Args:
        codename: The permission codename (e.g., 'view', 'edit', 'approve')
        content_type: The ContentType for the object

    Returns:
        The Permission object
    """
    permission, created = Permission.objects.get_or_create(
        codename=codename,
        content_type=content_type,
        defaults={"name": f"Can {codename} {content_type.model}"},
    )
    if created:
        logger.info(f"Created permission: {codename} for {content_type}")
    return permission


def _assign_object_permission(
    perm: str,
    user_or_group: User | Group,
    obj: Model,
) -> None:
    """
    Assign a permission to a user or group for a specific object.

    Creates the Permission object if it doesn't exist.
    """
    content_type = ContentType.objects.get_for_model(obj)
    permission = _get_or_create_permission(perm, content_type)

    if isinstance(user_or_group, User):
        UserObjectPermission.objects.get_or_create(
            user=user_or_group,
            permission=permission,
            content_type=content_type,
            object_pk=str(obj.pk),
        )
    else:
        GroupObjectPermission.objects.get_or_create(
            group=user_or_group,
            permission=permission,
            content_type=content_type,
            object_pk=str(obj.pk),
        )


def _revoke_object_permission(
    perm: str,
    user_or_group: User | Group,
    obj: Model,
) -> None:
    """
    Revoke a permission from a user or group for a specific object.
    """
    content_type = ContentType.objects.get_for_model(obj)

    try:
        permission = Permission.objects.get(codename=perm, content_type=content_type)
    except Permission.DoesNotExist:
        logger.debug(f"Permission {perm} doesn't exist, nothing to revoke")
        return

    if isinstance(user_or_group, User):
        UserObjectPermission.objects.filter(
            user=user_or_group,
            permission=permission,
            content_type=content_type,
            object_pk=str(obj.pk),
        ).delete()
    else:
        GroupObjectPermission.objects.filter(
            group=user_or_group,
            permission=permission,
            content_type=content_type,
            object_pk=str(obj.pk),
        ).delete()


@service
def group_create(
    *,
    name: str,
    permissions: list[str] | None = None,
) -> Group:
    """
    Create a new group (role).

    Args:
        name: Unique group name
        permissions: Optional list of permission codenames to add

    Returns:
        The created Group instance

    Raises:
        ValidationError: If group name already exists
    """
    if Group.objects.filter(name__iexact=name).exists():
        raise ValidationError(
            message="Group with this name already exists.",
            extra={"name": name},
        )

    group = Group.objects.create(name=name)

    if permissions:
        _add_permissions_to_group(group, permissions)

    return group


@service
def group_update(
    *,
    group: Group,
    name: str | None = None,
    permissions: list[str] | None = None,
) -> Group:
    """
    Update a group's attributes.

    Args:
        group: The Group instance to update
        name: New group name (optional)
        permissions: New list of permissions (replaces existing)

    Returns:
        The updated Group instance
    """
    if name is not None:
        if Group.objects.filter(name__iexact=name).exclude(pk=group.pk).exists():
            raise ValidationError(
                message="Group with this name already exists.",
                extra={"name": name},
            )
        group.name = name
        group.save()

    if permissions is not None:
        group.permissions.clear()
        _add_permissions_to_group(group, permissions)

    return group


@service
def group_delete(*, group: Group) -> None:
    """
    Delete a group.

    Args:
        group: The Group instance to delete
    """
    group.delete()


@service
def permission_assign(
    *,
    user: User,
    permission: str,
    obj: Model,
) -> None:
    """
    Assign a permission to a user for a specific object.

    Args:
        user: The user to grant permission to
        permission: Permission codename (e.g., 'view', 'change', 'delete')
        obj: The object to grant permission on
    """
    _assign_object_permission(permission, user, obj)


@service
def permission_assign_group(
    *,
    group: Group,
    permission: str,
    obj: Model,
) -> None:
    """
    Assign a permission to a group for a specific object.

    Args:
        group: The group to grant permission to
        permission: Permission codename
        obj: The object to grant permission on
    """
    _assign_object_permission(permission, group, obj)


@service
def permission_revoke(
    *,
    user: User,
    permission: str,
    obj: Model,
) -> None:
    """
    Revoke a permission from a user for a specific object.

    Args:
        user: The user to revoke permission from
        permission: Permission codename
        obj: The object to revoke permission on
    """
    _revoke_object_permission(permission, user, obj)


@service
def permission_revoke_group(
    *,
    group: Group,
    permission: str,
    obj: Model,
) -> None:
    """
    Revoke a permission from a group for a specific object.

    Args:
        group: The group to revoke permission from
        permission: Permission codename
        obj: The object to revoke permission on
    """
    _revoke_object_permission(permission, group, obj)


@service
def user_add_to_group(*, user: User, group: Group) -> None:
    """
    Add a user to a group.

    Args:
        user: The user to add
        group: The group to add the user to
    """
    user.groups.add(group)


@service
def user_remove_from_group(*, user: User, group: Group) -> None:
    """
    Remove a user from a group.

    Args:
        user: The user to remove
        group: The group to remove the user from
    """
    user.groups.remove(group)


@service
def permissions_assign_bulk(
    *,
    user: User,
    permissions: Sequence[str],
    obj: Model,
) -> None:
    """
    Assign multiple permissions to a user for an object.

    Args:
        user: The user to grant permissions to
        permissions: List of permission codenames
        obj: The object to grant permissions on
    """
    for perm in permissions:
        _assign_object_permission(perm, user, obj)


@service
def permissions_revoke_bulk(
    *,
    user: User,
    permissions: Sequence[str],
    obj: Model,
) -> None:
    """
    Revoke multiple permissions from a user for an object.

    Args:
        user: The user to revoke permissions from
        permissions: List of permission codenames
        obj: The object to revoke permissions on
    """
    for perm in permissions:
        _revoke_object_permission(perm, user, obj)


def _add_permissions_to_group(group: Group, permission_codenames: list[str]) -> None:
    """Helper to add permissions to a group by codename."""
    for codename in permission_codenames:
        try:
            perm = Permission.objects.get(codename=codename)
            group.permissions.add(perm)
        except Permission.DoesNotExist:
            logger.warning(f"Permission '{codename}' not found, skipping")
