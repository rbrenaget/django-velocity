"""
URL configuration for velocity project.
"""

from django.contrib import admin
from django.urls import include, path

from apps.core.api import api as core_api
from apps.core.health import HealthCheckView, health_check_simple

urlpatterns = [
    # Health checks (before any auth middleware)
    path("health/", HealthCheckView.as_view(), name="health_check"),
    path("health/live/", health_check_simple, name="health_check_simple"),
    # Admin
    path("admin/", admin.site.urls),
    # API v1 - DRF endpoints
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/permissions/", include("apps.permissions.urls")),
    path("api/v1/security/", include("apps.security.urls")),
    # API - Django Ninja (optional alternative)
    path("api/ninja/", core_api.urls),
]
