"""
Django Allauth settings.
"""

# =============================================================================
# Django Sites Framework (required by allauth)
# =============================================================================
SITE_ID = 1

# =============================================================================
# Authentication Backends
# =============================================================================
AUTHENTICATION_BACKENDS = [
    # Django default
    "django.contrib.auth.backends.ModelBackend",
    # django-allauth
    "allauth.account.auth_backends.AuthenticationBackend",
    # django-guardian object permissions
    "guardian.backends.ObjectPermissionBackend",
]

# =============================================================================
# Django-Allauth Configuration
# =============================================================================
ACCOUNT_LOGIN_METHODS = {"email"}  # Email-only authentication
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"  # "mandatory", "optional", or "none"
ACCOUNT_UNIQUE_EMAIL = True

# Allauth adapter for custom user model
ACCOUNT_ADAPTER = "apps.authentication.adapters.AccountAdapter"

# Login/Logout redirects (for web-based auth if needed)
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Email subject prefix
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Velocity] "
