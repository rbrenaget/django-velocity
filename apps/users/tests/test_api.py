"""
Tests for User API endpoints.

These are integration tests that test the full HTTP request/response cycle.

Note: Authentication endpoints (register, login, change-password) are tested in apps.authentication.
"""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestMeEndpoint:
    """Tests for /api/v1/users/me/"""

    def test_get_me_returns_current_user(self, authenticated_client, user):
        """Test GET /me returns current user."""
        response = authenticated_client.get("/api/v1/users/me/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_get_me_requires_auth(self, api_client):
        """Test GET /me requires authentication."""
        response = api_client.get("/api/v1/users/me/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_me_updates_profile(self, authenticated_client, user):
        """Test PATCH /me updates user profile."""
        response = authenticated_client.patch(
            "/api/v1/users/me/",
            {"first_name": "Updated"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"


@pytest.mark.django_db
class TestChangePasswordEndpoint:
    """Tests for POST /api/v1/users/me/change-password/"""

    def test_change_password_success(self, authenticated_client, user):
        """Test successful password change."""
        response = authenticated_client.post(
            "/api/v1/users/me/change-password/",
            {
                "current_password": "testpass123",
                "new_password": "newpass456",
            },
        )

        assert response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_current(self, authenticated_client):
        """Test password change with wrong current password."""
        response = authenticated_client.post(
            "/api/v1/users/me/change-password/",
            {
                "current_password": "wrongpassword",
                "new_password": "newpass456",
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
