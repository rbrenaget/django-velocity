"""
Security URL Configuration.
"""

from django.urls import path

from . import views

app_name = "security"

urlpatterns = [
    # Session Management
    path("sessions/", views.SessionListApi.as_view(), name="session-list"),
    path(
        "sessions/<str:session_key>/",
        views.SessionRevokeApi.as_view(),
        name="session-revoke",
    ),
    path(
        "sessions/revoke-all/",
        views.SessionRevokeAllApi.as_view(),
        name="session-revoke-all",
    ),
    # GDPR Compliance
    path("gdpr/export/", views.DataExportApi.as_view(), name="gdpr-export"),
    path(
        "gdpr/delete-account/",
        views.DeleteAccountApi.as_view(),
        name="gdpr-delete-account",
    ),
    # IP Allowlist (Admin only)
    path(
        "ip-allowlist/",
        views.IPAllowlistListCreateApi.as_view(),
        name="ip-allowlist-list",
    ),
    path(
        "ip-allowlist/<str:ip_address>/",
        views.IPAllowlistDetailApi.as_view(),
        name="ip-allowlist-detail",
    ),
]
