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

    # User listing (admin)
    path("", views.user_list_view, name="list"),
]


