"""
Authentication Services - Allauth + SimpleJWT integration.

Uses django-allauth for registration/password flows and SimpleJWT for API tokens.
"""

from __future__ import annotations

from pathlib import Path

from allauth.account.models import EmailAddress
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import PermissionDenied, ValidationError
from apps.core.services import service
from apps.users.models import User
from apps.users.selectors import user_get_by_email
from django.contrib.auth import authenticate

# =============================================================================
# Email Template Utilities
# =============================================================================

EMAILS_DIR = Path(__file__).parent / "emails"


def _load_email_template(template_name: str, **context) -> str:
    """Load and render an email template from the emails directory."""
    template_path = EMAILS_DIR / template_name
    content = template_path.read_text()
    for key, value in context.items():
        content = content.replace("{{ " + key + " }}", str(value))
    return content


# =============================================================================
# JWT Token Generation
# =============================================================================


def generate_tokens_for_user(user: User) -> dict:
    """
    Generate JWT tokens for a user.

    Args:
        user: The User instance

    Returns:
        Dict with access and refresh tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# =============================================================================
# Registration Service
# =============================================================================


@service
def register_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> dict:
    """
    Register a new user using allauth and return JWT tokens.

    Args:
        email: User's email address (must be unique)
        password: Plain-text password (will be hashed)
        first_name: Optional first name
        last_name: Optional last name

    Returns:
        Dict with user and JWT tokens

    Raises:
        ValidationError: If email is already registered
    """
    existing_user = user_get_by_email(email=email)
    if existing_user is not None:
        raise ValidationError(
            message="A user with this email already exists.",
            extra={"email": email},
        )

    # Create user
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )

    # Create EmailAddress for allauth
    EmailAddress.objects.create(
        user=user,
        email=email,
        primary=True,
        verified=False,  # Set to True if you want to skip email verification
    )

    # Generate JWT tokens
    tokens = generate_tokens_for_user(user)

    return {
        "user": user,
        **tokens,
    }


# =============================================================================
# Login Service
# =============================================================================


def login_user(*, email: str, password: str) -> dict:
    """
    Authenticate user and return JWT tokens.

    Args:
        email: User's email address
        password: User's password

    Returns:
        Dict with user and JWT tokens

    Raises:
        ValidationError: If credentials are invalid
    """
    user = authenticate(email=email, password=password)

    if user is None:
        raise ValidationError(
            message="Invalid email or password.",
        )

    if not user.is_active:
        raise PermissionDenied(
            message="User account is disabled.",
        )

    tokens = generate_tokens_for_user(user)

    return {
        "user": user,
        **tokens,
    }


# =============================================================================
# Password Reset Services (using allauth)
# =============================================================================


def request_password_reset(*, email: str) -> bool:
    """
    Request a password reset using allauth.

    Sends a password reset email via allauth's built-in flow.
    Always returns True to prevent email enumeration attacks.

    Args:
        email: User's email address

    Returns:
        True (always, for security)
    """
    from allauth.account.forms import ResetPasswordForm

    from django.http import HttpRequest

    # Create a dummy request for allauth
    request = HttpRequest()
    request.META["HTTP_HOST"] = "localhost"

    form = ResetPasswordForm(data={"email": email})
    if form.is_valid():
        form.save(request)

    return True


@service
def confirm_password_reset(*, token: str, uid: str, new_password: str) -> User:
    """
    Confirm password reset with token from allauth.

    Args:
        token: The reset token
        uid: The user ID (base64 encoded)
        new_password: The new password to set

    Returns:
        The updated User instance

    Raises:
        ValidationError: If token is invalid or expired
    """
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode

    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, User.DoesNotExist):
        raise ValidationError(
            message="Invalid reset link.",
        ) from None

    if not default_token_generator.check_token(user, token):
        raise ValidationError(
            message="This reset link has expired or is invalid.",
        )

    if not user.is_active:
        raise PermissionDenied(
            message="User account is disabled.",
        )

    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])

    return user


# =============================================================================
# Email Verification (using allauth)
# =============================================================================


def verify_email(*, key: str) -> User:
    """
    Verify email address using allauth confirmation key.

    Args:
        key: The email confirmation key

    Returns:
        The User whose email was verified

    Raises:
        ValidationError: If key is invalid
    """
    from allauth.account.models import EmailConfirmationHMAC

    try:
        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation is None:
            raise ValidationError(message="Invalid verification link.")

        confirmation.confirm(request=None)
        return confirmation.email_address.user
    except Exception:
        raise ValidationError(message="Invalid or expired verification link.") from None
