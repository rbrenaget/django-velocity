"""
Authentication API Views - DRF endpoints using allauth + SimpleJWT.

Thin views delegating to authentication services.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import UserOutputSerializer

from . import services
from .serializers import (
    RegisterInputSerializer,
    RegisterOutputSerializer,
    LoginInputSerializer,
    TokenOutputSerializer,
    ForgotPasswordInputSerializer,
    ResetPasswordInputSerializer,
    ChangePasswordInputSerializer,
    VerifyEmailInputSerializer,
)


class RegisterView(APIView):
    """
    User registration endpoint.

    POST /api/v1/auth/register/
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = services.register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
        )

        return Response(
            RegisterOutputSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    User login endpoint - returns JWT tokens.

    POST /api/v1/auth/login/
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = services.login_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        return Response(
            TokenOutputSerializer(result).data,
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    """
    Request password reset endpoint (uses allauth).

    POST /api/v1/auth/forgot-password/
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ForgotPasswordInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        services.request_password_reset(
            email=serializer.validated_data["email"],
        )

        return Response(
            {"message": "If an account exists with this email, you will receive a password reset link."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    """
    Confirm password reset endpoint.

    POST /api/v1/auth/reset-password/
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ResetPasswordInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        services.confirm_password_reset(
            uid=serializer.validated_data["uid"],
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )

        return Response(
            {"message": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.

    POST /api/v1/auth/change-password/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ChangePasswordInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.users.services import user_change_password

        user_change_password(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            new_password=serializer.validated_data["new_password"],
        )

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(APIView):
    """
    Email verification endpoint (uses allauth).

    POST /api/v1/auth/verify-email/
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = VerifyEmailInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = services.verify_email(
            key=serializer.validated_data["key"],
        )

        return Response(
            {"message": "Email verified successfully.", "user": UserOutputSerializer(user).data},
            status=status.HTTP_200_OK,
        )
