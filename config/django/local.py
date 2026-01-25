"""
Local development settings.
"""

from .base import *  # noqa: F401, F403

# =============================================================================
# Debug Settings
# =============================================================================
DEBUG = True

# =============================================================================
# Email Backend (Console for development)
# =============================================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# Django Debug Toolbar (optional)
# =============================================================================
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1"]

# =============================================================================
# CORS (for local frontend development)
# =============================================================================
# CORS_ALLOW_ALL_ORIGINS = True

# =============================================================================
# Logging
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
