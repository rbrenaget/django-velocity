"""
Tests for Authentication API endpoints.

These are integration tests that test the full HTTP request/response cycle.
"""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register/"""

    def test_register_creates_user(self, api_client):
        """Test successful user registration."""
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "securepass123",
                "first_name": "New",
                "last_name": "User",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["email"] == "newuser@example.com"
        assert response.data["user"]["first_name"] == "New"
        assert "access" in response.data
        assert "refresh" in response.data

    def test_register_validates_email(self, api_client):
        """Test email validation."""
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "invalid-email",
                "password": "securepass123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_validates_password_length(self, api_client):
        """Test password minimum length validation."""
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "short",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login/"""

    def test_login_returns_tokens(self, api_client, user):
        """Test successful login returns JWT tokens."""
        response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": "testpass123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data

    def test_login_invalid_credentials(self, api_client, user):
        """Test login with wrong password."""
        response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestChangePasswordEndpoint:
    """Tests for POST /api/v1/auth/change-password/"""

    def test_change_password_success(self, authenticated_client, user):
        """Test successful password change."""
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "current_password": "testpass123",
                "new_password": "newpass456",
            },
        )

        assert response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_current(self, authenticated_client):
        """Test password change with wrong current password."""
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "current_password": "wrongpassword",
                "new_password": "newpass456",
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
