"""
Security Views - API endpoints for security features.
"""

from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import PermissionDenied

from . import selectors, services
from .serializers import (
    DataExportOutputSerializer,
    DeleteAccountInputSerializer,
    IPAllowlistInputSerializer,
    IPAllowlistOutputSerializer,
    SessionOutputSerializer,
    SessionRevokeAllInputSerializer,
)


class SessionListApi(APIView):
    """
    GET /api/v1/security/sessions/
    List all active sessions for the current user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        sessions = selectors.session_list_for_user(user=request.user, active_only=True)

        data = []
        for session in sessions:
            data.append(
                {
                    "session_key": session.session_key,
                    "device_info": session.device_info,
                    "ip_address": session.ip_address,
                    "last_activity": session.last_activity,
                    "created_at": session.created_at,
                    "is_current": session.session_key == request.session.session_key,
                }
            )

        serializer = SessionOutputSerializer(data, many=True)
        return Response(serializer.data)


class SessionRevokeApi(APIView):
    """
    DELETE /api/v1/security/sessions/<session_key>/
    Revoke a specific session.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, session_key: str) -> Response:
        if session_key == request.session.session_key:
            raise PermissionDenied(
                message="Cannot revoke your current session. Use logout instead."
            )

        services.session_revoke(user=request.user, session_key=session_key)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionRevokeAllApi(APIView):
    """
    POST /api/v1/security/sessions/revoke-all/
    Revoke all sessions except optionally the current one.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = SessionRevokeAllInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        keep_current = serializer.validated_data.get("keep_current", True)
        except_current = request.session.session_key if keep_current else None

        count = services.session_revoke_all(
            user=request.user,
            except_current=except_current,
        )

        return Response({"revoked_count": count})


class DataExportApi(APIView):
    """
    POST /api/v1/security/gdpr/export/
    Export all user data for GDPR compliance.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        data = services.user_export_data(user=request.user)
        serializer = DataExportOutputSerializer(data)
        return Response(serializer.data)


class DeleteAccountApi(APIView):
    """
    POST /api/v1/security/gdpr/delete-account/
    Permanently delete user account.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = DeleteAccountInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["password"]):
            raise PermissionDenied(message="Invalid password.")

        services.user_delete_account(
            user=user,
            confirmation=serializer.validated_data["confirmation"],
        )

        return Response(
            {"message": "Account deleted successfully."},
            status=status.HTTP_200_OK,
        )


class IPAllowlistListCreateApi(APIView):
    """
    GET  /api/v1/security/ip-allowlist/ - List IP allowlist
    POST /api/v1/security/ip-allowlist/ - Add IP to allowlist
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request) -> Response:
        entries = selectors.ip_allowlist_list(active_only=False)
        serializer = IPAllowlistOutputSerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = IPAllowlistInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entry = services.ip_allowlist_add(
            ip_address=serializer.validated_data["ip_address"],
            description=serializer.validated_data.get("description", ""),
            added_by=request.user,
        )

        return Response(
            IPAllowlistOutputSerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class IPAllowlistDetailApi(APIView):
    """
    DELETE /api/v1/security/ip-allowlist/<ip_address>/
    Remove IP from allowlist.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request: Request, ip_address: str) -> Response:
        services.ip_allowlist_remove(ip_address=ip_address)
        return Response(status=status.HTTP_204_NO_CONTENT)
