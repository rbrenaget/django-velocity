"""
Permission Admin Configuration.

Django's Group model is already registered in the admin by django.contrib.auth.
We don't need to register it again here.

For object-level permissions, django-guardian provides its own admin integration.
"""

# No custom admin needed - Django's Group admin is already available
# at /admin/auth/group/
#
# Guardian's UserObjectPermission and GroupObjectPermission can be viewed
# in the admin if you want to debug object-level permissions.
