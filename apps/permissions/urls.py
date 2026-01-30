"""
Permission URL Configuration.

Uses Django's built-in Group/Permission models with django-guardian.
"""

from django.urls import path

from . import views

app_name = "permissions"

urlpatterns = [
    # Group (role) management
    path("groups/", views.GroupListCreateApi.as_view(), name="group-list-create"),
    path("groups/<int:group_id>/", views.GroupDetailApi.as_view(), name="group-detail"),
    path(
        "groups/members/", views.GroupMembershipApi.as_view(), name="group-membership"
    ),
    # Permission management
    path("assign/", views.PermissionAssignApi.as_view(), name="assign"),
    path("assign-bulk/", views.PermissionAssignBulkApi.as_view(), name="assign-bulk"),
    path("revoke/", views.PermissionRevokeApi.as_view(), name="revoke"),
    # Permission checking
    path("check/", views.PermissionCheckApi.as_view(), name="check"),
    # User permissions on object
    path(
        "users/<int:user_id>/objects/<str:content_type>/<int:object_id>/",
        views.UserPermissionsApi.as_view(),
        name="user-permissions",
    ),
]
