"""
CORS Headers Settings - Cross-Origin Resource Sharing configuration.
"""

from config.env import env

# =============================================================================
# CORS Configuration
# =============================================================================

# Allow all origins in development, restrict in production
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Allow all origins (use only in development)
CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL_ORIGINS", default=False)

# Allow credentials (cookies, authorization headers)
CORS_ALLOW_CREDENTIALS = env("CORS_ALLOW_CREDENTIALS", default=True)

# Allowed HTTP methods
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Allowed headers
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Expose headers to frontend
CORS_EXPOSE_HEADERS = [
    "content-disposition",
]

# Preflight cache duration (in seconds)
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours
