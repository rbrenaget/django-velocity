"""
Security Settings - Configurable security options.
"""

from config.env import env

# =============================================================================
# Security Headers
# =============================================================================
SECURITY_HEADERS_ENABLED = env("SECURITY_HEADERS_ENABLED", default=True)

# Content Security Policy - customize based on your app's needs
SECURITY_CSP_POLICY = env(
    "SECURITY_CSP_POLICY",
    default=(
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
)

# HSTS - Only applies to HTTPS requests
# 31536000 = 1 year (recommended for production)
SECURITY_HSTS_SECONDS = env("SECURITY_HSTS_SECONDS", default=31536000)

# =============================================================================
# Admin IP Restriction
# =============================================================================
ADMIN_IP_RESTRICTION_ENABLED = env("ADMIN_IP_RESTRICTION_ENABLED", default=True)
ADMIN_URL_PREFIX = "/admin/"

# =============================================================================
# Password Breach Check
# =============================================================================
# Enable/disable Have I Been Pwned API check
PASSWORD_BREACH_CHECK_ENABLED = env("PASSWORD_BREACH_CHECK_ENABLED", default=True)

# Minimum breach count to reject password (1 = reject any breached password)
PASSWORD_BREACH_THRESHOLD = env("PASSWORD_BREACH_THRESHOLD", default=1)

# =============================================================================
# Session Management
# =============================================================================
# Cleanup sessions inactive for more than this duration (in seconds)
# 7 days = 604800 seconds
SESSION_INACTIVITY_TIMEOUT = env("SESSION_INACTIVITY_TIMEOUT", default=604800)
