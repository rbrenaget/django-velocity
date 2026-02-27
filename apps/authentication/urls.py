"""
Authentication URL Configuration.

All authentication-related API endpoints using allauth + SimpleJWT.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "authentication"

urlpatterns = [
    # Registration & Login
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Password Management
    path(
        "forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    # Email Verification
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
]
