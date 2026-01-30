"""
Permission Serializers - Input/Output serializers for permission APIs.

Uses Django's built-in Group and Permission models.
"""

from rest_framework import serializers


class GroupOutputSerializer(serializers.Serializer):
    """Output serializer for Group."""

    id = serializers.IntegerField()
    name = serializers.CharField()


class GroupDetailOutputSerializer(serializers.Serializer):
    """Detailed output serializer for Group with permissions."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj) -> list[str]:
        return list(obj.permissions.values_list("codename", flat=True))


class GroupInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating Group."""

    name = serializers.CharField(max_length=150)
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="List of permission codenames to assign to the group",
    )


class PermissionAssignInputSerializer(serializers.Serializer):
    """Input for assigning a permission to a user on an object."""

    user_id = serializers.IntegerField()
    permission = serializers.CharField(
        help_text="Permission codename, e.g. 'view', 'change', 'delete'"
    )
    content_type = serializers.CharField(
        help_text="App label and model, e.g. 'myapp.mymodel'"
    )
    object_id = serializers.IntegerField()


class PermissionAssignBulkInputSerializer(serializers.Serializer):
    """Input for assigning multiple permissions to a user on an object."""

    user_id = serializers.IntegerField()
    permissions = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of permission codenames",
    )
    content_type = serializers.CharField()
    object_id = serializers.IntegerField()


class PermissionCheckInputSerializer(serializers.Serializer):
    """Input for checking a permission."""

    user_id = serializers.IntegerField()
    permission = serializers.CharField()
    content_type = serializers.CharField()
    object_id = serializers.IntegerField()


class PermissionCheckOutputSerializer(serializers.Serializer):
    """Output for permission check."""

    has_permission = serializers.BooleanField()
    user_id = serializers.IntegerField()
    permission = serializers.CharField()


class UserPermissionsOutputSerializer(serializers.Serializer):
    """Output for listing user's permissions on an object."""

    user_id = serializers.IntegerField()
    permissions = serializers.ListField(child=serializers.CharField())


class GroupMembershipInputSerializer(serializers.Serializer):
    """Input for adding/removing user from group."""

    user_id = serializers.IntegerField()
    group_id = serializers.IntegerField()
