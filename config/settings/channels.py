"""
Django Channels configuration settings.
"""

from config.env import env

# =============================================================================
# ASGI Application
# =============================================================================
ASGI_APPLICATION = "config.asgi.application"

# =============================================================================
# Channel Layers (Redis Backend)
# =============================================================================
# Uses a different Redis DB than Celery to avoid key collisions
CHANNEL_LAYERS_URL = env("CHANNEL_LAYERS_URL", default="redis://redis:6379/1")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [CHANNEL_LAYERS_URL],
        },
    },
}
