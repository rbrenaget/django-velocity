"""
Test settings - Fast tests with in-memory SQLite.
"""

from .base import *  # noqa: F401, F403
from .base import REST_FRAMEWORK  # noqa: F401

# =============================================================================
# Test-Optimized Settings
# =============================================================================
DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

# =============================================================================
# Faster Password Hashing for Tests
# =============================================================================
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# =============================================================================
# In-Memory Database
# =============================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# =============================================================================
# Disable Throttling for Tests
# =============================================================================
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}

# =============================================================================
# Email Backend
# =============================================================================
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
