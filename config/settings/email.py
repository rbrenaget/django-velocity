"""
Email configuration settings.
"""

import environ

env = environ.Env()

# =============================================================================
# Email Configuration
# =============================================================================
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")

# =============================================================================
# Frontend URL (for password reset links, etc.)
# =============================================================================
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")
