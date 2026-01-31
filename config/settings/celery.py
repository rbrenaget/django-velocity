"""
Celery configuration settings.
"""

from config.env import env

# =============================================================================
# Celery Broker & Backend
# =============================================================================
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/0")

# =============================================================================
# Task Serialization
# =============================================================================
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"

# =============================================================================
# Task Execution
# =============================================================================
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# =============================================================================
# Celery Beat (Scheduled Tasks)
# =============================================================================
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
