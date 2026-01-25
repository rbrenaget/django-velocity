"""
URL configuration for velocity project.
"""

from django.contrib import admin
from django.urls import path, include

from apps.core.api import api as core_api

urlpatterns = [
    path("admin/", admin.site.urls),

    # API v1 - DRF endpoints
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/users/", include("apps.users.urls")),

    # API - Django Ninja (optional alternative)
    path("api/ninja/", core_api.urls),
]

