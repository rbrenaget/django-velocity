"""
Permission Models - Extends Django's built-in permission system.

We use Django's built-in Group and Permission models directly,
along with django-guardian for object-level permissions.

No custom models are needed as django-guardian provides:
- UserObjectPermission: per-user object permissions
- GroupObjectPermission: per-group object permissions

This module is intentionally minimal. Use:
- django.contrib.auth.models.Group for role groupings
- django.contrib.auth.models.Permission for permission definitions
- guardian.shortcuts for object-level permission management
"""

# No custom models needed - we use Django's built-in models:
# - django.contrib.auth.models.Group (for roles)
# - django.contrib.auth.models.Permission (for permissions)
# - guardian.models.UserObjectPermission (for object-level user perms)
# - guardian.models.GroupObjectPermission (for object-level group perms)
