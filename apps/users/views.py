"""
User API Views - DRF endpoints for User domain.

User profile and management endpoints.
Note: Authentication endpoints are now in apps.authentication.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import selectors, services
from .serializers import (
    ChangePasswordInputSerializer,
    UserOutputSerializer,
    UserUpdateInputSerializer,
)


class MeView(APIView):
    """
    Current user profile endpoint.

    GET /api/v1/users/me/ - Get current user
    PATCH /api/v1/users/me/ - Update current user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(
            UserOutputSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request) -> Response:
        serializer = UserUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = services.user_update(
            user=request.user,
            **serializer.validated_data,
        )

        return Response(
            UserOutputSerializer(user).data,
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.

    POST /api/v1/users/me/change-password/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ChangePasswordInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        services.user_change_password(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            new_password=serializer.validated_data["new_password"],
        )

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class UserListApi(APIView):
    """
    List all active users (admin only in production).

    GET /api/v1/users/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        users = selectors.user_list_active()
        return Response(
            UserOutputSerializer(users, many=True).data,
            status=status.HTTP_200_OK,
        )
