"""
URL configuration for velocity project.
"""

from django.contrib import admin
from django.urls import include, path

from apps.core.health import HealthCheckView, health_check_simple

urlpatterns = [
    # Health checks (before any auth middleware)
    path("health/", HealthCheckView.as_view(), name="health_check"),
    path("health/live/", health_check_simple, name="health_check_simple"),
    # Admin
    path("admin/", admin.site.urls),
    # API - DRF endpoints
    path("api/auth/", include("apps.authentication.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/permissions/", include("apps.permissions.urls")),
    path("api/security/", include("apps.security.urls")),
]
