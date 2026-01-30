"""
Django Guardian settings for object-level permissions.
"""

# Disable anonymous user (guardian requires this setting)
ANONYMOUS_USER_NAME = None

# Permission behavior settings
GUARDIAN_RAISE_403 = True  # Raise PermissionDenied instead of redirect
GUARDIAN_RENDER_403 = False
