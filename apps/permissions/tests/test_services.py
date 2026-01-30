"""
Tests for permission services.

Uses Django's built-in Group model with django-guardian.
"""

import pytest
from tests.factories import UserFactory

from apps.core.exceptions import ValidationError
from apps.permissions import services
from apps.permissions.tests.factories import GroupFactory
from django.contrib.auth.models import Group


@pytest.mark.django_db
class TestGroupCreate:
    """Tests for group_create service."""

    def test_creates_group_with_valid_data(self):
        group = services.group_create(name="Editors")

        assert group.name == "Editors"
        assert Group.objects.filter(name="Editors").exists()

    def test_raises_validation_error_for_duplicate_name(self):
        services.group_create(name="Editors")

        with pytest.raises(ValidationError) as exc_info:
            services.group_create(name="editors")  # Case-insensitive

        assert "already exists" in exc_info.value.message


@pytest.mark.django_db
class TestGroupUpdate:
    """Tests for group_update service."""

    def test_updates_group_name(self):
        group = GroupFactory(name="OldName")

        updated = services.group_update(group=group, name="NewName")

        assert updated.name == "NewName"

    def test_raises_validation_error_for_duplicate_name(self):
        GroupFactory(name="ExistingGroup")
        group = GroupFactory(name="MyGroup")

        with pytest.raises(ValidationError):
            services.group_update(group=group, name="ExistingGroup")


@pytest.mark.django_db
class TestGroupDelete:
    """Tests for group_delete service."""

    def test_deletes_group(self):
        group = GroupFactory()
        group_id = group.id

        services.group_delete(group=group)

        assert not Group.objects.filter(id=group_id).exists()


@pytest.mark.django_db
class TestPermissionAssign:
    """Tests for permission_assign service."""

    def test_assigns_permission_to_user(self):
        user = UserFactory()

        # Assign permission on user object itself (for testing)
        services.permission_assign(user=user, permission="view", obj=user)

        # Check via guardian
        assert user.has_perm("view", user)


@pytest.mark.django_db
class TestPermissionRevoke:
    """Tests for permission_revoke service."""

    def test_revokes_permission_from_user(self):
        user = UserFactory()

        services.permission_assign(user=user, permission="view", obj=user)
        assert user.has_perm("view", user)

        services.permission_revoke(user=user, permission="view", obj=user)
        assert not user.has_perm("view", user)


@pytest.mark.django_db
class TestUserGroupMembership:
    """Tests for user group membership services."""

    def test_add_user_to_group(self):
        user = UserFactory()
        group = GroupFactory()

        services.user_add_to_group(user=user, group=group)

        assert user.groups.filter(pk=group.pk).exists()

    def test_remove_user_from_group(self):
        user = UserFactory()
        group = GroupFactory()
        user.groups.add(group)

        services.user_remove_from_group(user=user, group=group)

        assert not user.groups.filter(pk=group.pk).exists()


@pytest.mark.django_db
class TestBulkPermissions:
    """Tests for bulk permission operations."""

    def test_assigns_multiple_permissions(self):
        user = UserFactory()

        services.permissions_assign_bulk(
            user=user,
            permissions=["view", "change"],
            obj=user,
        )

        assert user.has_perm("view", user)
        assert user.has_perm("change", user)

    def test_revokes_multiple_permissions(self):
        user = UserFactory()
        services.permissions_assign_bulk(
            user=user, permissions=["view", "change"], obj=user
        )

        services.permissions_revoke_bulk(
            user=user,
            permissions=["view", "change"],
            obj=user,
        )

        assert not user.has_perm("view", user)
        assert not user.has_perm("change", user)
