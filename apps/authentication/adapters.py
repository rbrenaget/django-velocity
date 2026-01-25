"""
Authentication Adapters - Custom allauth adapter for our User model.
"""

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for django-allauth.

    Handles custom user creation and email sending to work with our
    email-based User model and service layer.
    """

    def get_login_redirect_url(self, request):
        """
        Return the URL to redirect to after login.
        For API-only apps, this is typically not used.
        """
        return settings.LOGIN_REDIRECT_URL

    def save_user(self, request, user, form, commit=True):
        """
        Save a new user with email as the primary identifier.
        """
        user = super().save_user(request, user, form, commit=False)
        # Ensure username is not set (we use email-only auth)
        user.username = None
        if commit:
            user.save()
        return user

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Return the URL for email confirmation.
        Points to frontend for API-based apps.
        """
        return f"{settings.FRONTEND_URL}/verify-email?key={emailconfirmation.key}"

    def send_mail(self, template_prefix, email, context):
        """
        Send email using allauth's templates.
        """
        super().send_mail(template_prefix, email, context)
