"""
Tests for permission selectors.

Uses Django's built-in Group model with django-guardian.
"""

import pytest
from tests.factories import UserFactory

from apps.permissions import selectors, services
from apps.permissions.tests.factories import GroupFactory


@pytest.mark.django_db
class TestGroupGetById:
    """Tests for group_get_by_id selector."""

    def test_returns_group_when_exists(self):
        group = GroupFactory()

        result = selectors.group_get_by_id(group_id=group.id)

        assert result == group

    def test_returns_none_when_not_exists(self):
        result = selectors.group_get_by_id(group_id=99999)

        assert result is None


@pytest.mark.django_db
class TestGroupGetByName:
    """Tests for group_get_by_name selector."""

    def test_returns_group_case_insensitive(self):
        group = GroupFactory(name="Editors")

        result = selectors.group_get_by_name(name="editors")

        assert result == group


@pytest.mark.django_db
class TestGroupList:
    """Tests for group_list selector."""

    def test_returns_all_groups(self):
        GroupFactory.create_batch(3)

        result = selectors.group_list()

        assert result.count() == 3


@pytest.mark.django_db
class TestGroupListForUser:
    """Tests for group_list_for_user selector."""

    def test_returns_user_groups(self):
        user = UserFactory()
        group1 = GroupFactory()
        group2 = GroupFactory()
        user.groups.add(group1, group2)

        result = selectors.group_list_for_user(user=user)

        assert set(result) == {group1, group2}


@pytest.mark.django_db
class TestPermissionCheck:
    """Tests for permission_check selector."""

    def test_returns_true_when_user_has_permission(self):
        user = UserFactory()
        services.permission_assign(user=user, permission="view", obj=user)

        result = selectors.permission_check(user=user, permission="view", obj=user)

        assert result is True

    def test_returns_false_when_user_lacks_permission(self):
        user = UserFactory()

        result = selectors.permission_check(user=user, permission="view", obj=user)

        assert result is False


@pytest.mark.django_db
class TestPermissionListForUser:
    """Tests for permission_list_for_user selector."""

    def test_returns_all_permissions_on_object(self):
        user = UserFactory()
        services.permissions_assign_bulk(
            user=user, permissions=["view", "change"], obj=user
        )

        result = selectors.permission_list_for_user(user=user, obj=user)

        assert set(result) == {"view", "change"}


@pytest.mark.django_db
class TestUserInGroup:
    """Tests for user_in_group selector."""

    def test_returns_true_when_user_in_group(self):
        user = UserFactory()
        group = GroupFactory()
        user.groups.add(group)

        result = selectors.user_in_group(user=user, group=group)

        assert result is True

    def test_returns_false_when_user_not_in_group(self):
        user = UserFactory()
        group = GroupFactory()

        result = selectors.user_in_group(user=user, group=group)

        assert result is False
