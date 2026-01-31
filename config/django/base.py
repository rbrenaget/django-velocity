"""
Django settings for velocity project - Base Configuration.
All settings are loaded from environment variables via django-environ.
"""

from config.env import BASE_DIR, env

# =============================================================================
# Core Settings
# =============================================================================
DEBUG = env("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=[])

# =============================================================================
# Application Definition
# =============================================================================
DJANGO_APPS = [
    "unfold",  # Must be before django.contrib.admin
    "unfold.contrib.filters",  # Optional: enhanced filters
    "unfold.contrib.forms",  # Optional: enhanced form elements
    "unfold.contrib.inlines",  # Optional: enhanced inlines
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "tailwind",
    "rest_framework",
    "rest_framework_simplejwt",
    "ninja",
    "guardian",
    "django_celery_beat",
    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
]

LOCAL_APPS = [
    "apps.theme",
    "apps.core",
    "apps.authentication",
    "apps.users",
    "apps.permissions",
    "apps.tasks",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# Middleware
# =============================================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =============================================================================
# URL Configuration
# =============================================================================
ROOT_URLCONF = "config.urls"

# =============================================================================
# Templates
# =============================================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =============================================================================
# WSGI / ASGI
# =============================================================================
WSGI_APPLICATION = "config.wsgi.application"

# =============================================================================
# Database
# =============================================================================
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}

# =============================================================================
# Authentication
# =============================================================================
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =============================================================================
# Internationalization
# =============================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Supported languages - uncomment the languages you want to support
LANGUAGES = [
    ("en", "English"),
    # ("fr", "Français"),
    # ("es", "Español"),
    # ("de", "Deutsch"),
    # ("it", "Italiano"),
    # ("pt", "Português"),
    # ("nl", "Nederlands"),
    # ("pl", "Polski"),
    # ("ru", "Русский"),
    # ("zh-hans", "简体中文"),
    # ("ja", "日本語"),
    # ("ko", "한국어"),
    # ("ar", "العربية"),
]

# Path to translation files
LOCALE_PATHS = [BASE_DIR / "locale"]

# =============================================================================
# Static Files
# =============================================================================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =============================================================================
# Default Primary Key
# =============================================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# Third-Party Settings (imported from config/settings/)
# =============================================================================
from config.settings.allauth import *  # noqa: F401, F403, E402
from config.settings.celery import *  # noqa: F401, F403, E402
from config.settings.email import *  # noqa: F401, F403, E402
from config.settings.guardian import *  # noqa: F401, F403, E402
from config.settings.jwt import *  # noqa: F401, F403, E402
from config.settings.rest_framework import *  # noqa: F401, F403, E402
from config.settings.tailwind import *  # noqa: F401, F403, E402
from config.settings.unfold import *  # noqa: F401, F403, E402
