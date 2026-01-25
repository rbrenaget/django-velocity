"""
User API Views - DRF endpoints for User domain.

User profile and management endpoints.
Note: Authentication endpoints are now in apps.authentication.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services, selectors
from .serializers import (
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_list_view(request: Request) -> Response:
    """
    List all active users (admin only in production).

    GET /api/v1/users/
    """
    users = selectors.user_list_active()
    return Response(
        UserOutputSerializer(users, many=True).data,
        status=status.HTTP_200_OK,
    )
