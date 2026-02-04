"""
Project-wide pytest configuration and fixtures.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user(db) -> User:
    """Create a regular test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def other_user(db) -> User:
    """Create another test user."""
    return User.objects.create_user(
        email="other@example.com",
        password="testpass123",
        first_name="Other",
        last_name="User",
    )


@pytest.fixture
def admin_user(db) -> User:
    """Create a superuser for admin tests."""
    return User.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def authenticated_client(api_client: APIClient, user: User) -> APIClient:
    """API client authenticated as the test user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client: APIClient, admin_user: User) -> APIClient:
    """API client authenticated as admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client
