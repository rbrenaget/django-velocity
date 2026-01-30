"""
Permission API Views - RESTful endpoints for permissions.

Uses Django's built-in Group/Permission models with django-guardian.
"""

from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import NotFound
from apps.users import selectors as user_selectors
from django.apps import apps

from . import selectors, services
from .serializers import (
    GroupDetailOutputSerializer,
    GroupInputSerializer,
    GroupMembershipInputSerializer,
    GroupOutputSerializer,
    PermissionAssignBulkInputSerializer,
    PermissionAssignInputSerializer,
    PermissionCheckInputSerializer,
    PermissionCheckOutputSerializer,
    UserPermissionsOutputSerializer,
)


class GroupListCreateApi(APIView):
    """
    GET  /api/v1/permissions/groups/ - List all groups
    POST /api/v1/permissions/groups/ - Create a new group
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request) -> Response:
        groups = selectors.group_list()
        return Response(
            GroupOutputSerializer(groups, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = GroupInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = services.group_create(**serializer.validated_data)

        return Response(
            GroupDetailOutputSerializer(group).data,
            status=status.HTTP_201_CREATED,
        )


class GroupDetailApi(APIView):
    """
    GET    /api/v1/permissions/groups/<id>/ - Get group detail
    PUT    /api/v1/permissions/groups/<id>/ - Update group
    DELETE /api/v1/permissions/groups/<id>/ - Delete group
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request, group_id: int) -> Response:
        group = selectors.group_get_by_id(group_id=group_id)
        if group is None:
            raise NotFound(message="Group not found.")

        return Response(
            GroupDetailOutputSerializer(group).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request: Request, group_id: int) -> Response:
        group = selectors.group_get_by_id(group_id=group_id)
        if group is None:
            raise NotFound(message="Group not found.")

        serializer = GroupInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = services.group_update(group=group, **serializer.validated_data)

        return Response(
            GroupDetailOutputSerializer(group).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, group_id: int) -> Response:
        group = selectors.group_get_by_id(group_id=group_id)
        if group is None:
            raise NotFound(message="Group not found.")

        services.group_delete(group=group)

        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupMembershipApi(APIView):
    """
    POST   /api/v1/permissions/groups/members/ - Add user to group
    DELETE /api/v1/permissions/groups/members/ - Remove user from group
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request: Request) -> Response:
        serializer = GroupMembershipInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = user_selectors.user_get_by_id(user_id=data["user_id"])
        if user is None:
            raise NotFound(message="User not found.")

        group = selectors.group_get_by_id(group_id=data["group_id"])
        if group is None:
            raise NotFound(message="Group not found.")

        services.user_add_to_group(user=user, group=group)

        return Response(
            {"message": f"User added to group '{group.name}'"},
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request) -> Response:
        serializer = GroupMembershipInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = user_selectors.user_get_by_id(user_id=data["user_id"])
        if user is None:
            raise NotFound(message="User not found.")

        group = selectors.group_get_by_id(group_id=data["group_id"])
        if group is None:
            raise NotFound(message="Group not found.")

        services.user_remove_from_group(user=user, group=group)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PermissionAssignApi(APIView):
    """
    POST /api/v1/permissions/assign/ - Assign permission to user on object
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request: Request) -> Response:
        serializer = PermissionAssignInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = user_selectors.user_get_by_id(user_id=data["user_id"])
        if user is None:
            raise NotFound(message="User not found.")

        obj = _get_object_from_content_type(
            data["content_type"],
            data["object_id"],
        )

        services.permission_assign(
            user=user,
            permission=data["permission"],
            obj=obj,
        )

        return Response(
            {"message": f"Permission '{data['permission']}' assigned to user"},
            status=status.HTTP_201_CREATED,
        )


class PermissionRevokeApi(APIView):
    """
    POST /api/v1/permissions/revoke/ - Revoke permission from user on object
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request: Request) -> Response:
        serializer = PermissionAssignInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = user_selectors.user_get_by_id(user_id=data["user_id"])
        if user is None:
            raise NotFound(message="User not found.")

        obj = _get_object_from_content_type(
            data["content_type"],
            data["object_id"],
        )

        services.permission_revoke(
            user=user,
            permission=data["permission"],
            obj=obj,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class PermissionAssignBulkApi(APIView):
    """
    POST /api/v1/permissions/assign-bulk/ - Assign multiple permissions
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request: Request) -> Response:
        serializer = PermissionAssignBulkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = user_selectors.user_get_by_id(user_id=data["user_id"])
        if user is None:
            raise NotFound(message="User not found.")

        obj = _get_object_from_content_type(
            data["content_type"],
            data["object_id"],
        )

        services.permissions_assign_bulk(
            user=user,
            permissions=data["permissions"],
            obj=obj,
        )

        return Response(
            {"message": f"Assigned {len(data['permissions'])} permissions"},
            status=status.HTTP_201_CREATED,
        )


class PermissionCheckApi(APIView):
    """
    POST /api/v1/permissions/check/ - Check if user has permission
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = PermissionCheckInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = user_selectors.user_get_by_id(user_id=data["user_id"])
        if user is None:
            raise NotFound(message="User not found.")

        obj = _get_object_from_content_type(
            data["content_type"],
            data["object_id"],
        )

        has_perm = selectors.permission_check(
            user=user,
            permission=data["permission"],
            obj=obj,
        )

        return Response(
            PermissionCheckOutputSerializer(
                {
                    "has_permission": has_perm,
                    "user_id": user.id,
                    "permission": data["permission"],
                }
            ).data,
            status=status.HTTP_200_OK,
        )


class UserPermissionsApi(APIView):
    """
    GET /api/v1/permissions/users/<user_id>/objects/<content_type>/<object_id>/
    List all permissions a user has on an object.
    """

    permission_classes = [IsAuthenticated]

    def get(
        self,
        request: Request,
        user_id: int,
        content_type: str,
        object_id: int,
    ) -> Response:
        user = user_selectors.user_get_by_id(user_id=user_id)
        if user is None:
            raise NotFound(message="User not found.")

        obj = _get_object_from_content_type(content_type, object_id)

        permissions = selectors.permission_list_for_user(user=user, obj=obj)

        return Response(
            UserPermissionsOutputSerializer(
                {
                    "user_id": user.id,
                    "permissions": permissions,
                }
            ).data,
            status=status.HTTP_200_OK,
        )


def _get_object_from_content_type(content_type_str: str, object_id: int):
    """Helper to fetch an object from content_type string and ID."""
    try:
        app_label, model = content_type_str.split(".")
        model_class = apps.get_model(app_label, model)
    except (ValueError, LookupError) as e:
        raise NotFound(
            message=f"Invalid content type: {content_type_str}",
        ) from e

    try:
        return model_class.objects.get(pk=object_id)
    except model_class.DoesNotExist as e:
        raise NotFound(
            message=f"Object not found: {content_type_str} #{object_id}",
        ) from e
