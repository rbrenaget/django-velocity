"""
User URL Configuration.

User profile and management endpoints.
Note: Authentication endpoints are now in apps.authentication.
"""

from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Current user profile
    path("me/", views.MeView.as_view(), name="me"),
    path(
        "me/change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password",
    ),
    # User listing (admin)
    path("", views.UserListApi.as_view(), name="list"),
]
