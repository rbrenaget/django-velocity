"""
Test Factories - FactoryBoy factories for generating test data.

Usage:
    from tests.factories import UserFactory

    def test_something():
        user = UserFactory()  # Creates a user in DB
        user = UserFactory.build()  # Creates a user without saving
"""

import factory

from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating User instances in tests.
    """

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override the default _create method to use create_user for proper password hashing.
        """
        password = kwargs.pop("password", "testpass123")
        obj = super()._create(model_class, *args, **kwargs)
        obj.set_password(password)
        obj.save()
        return obj


class AdminUserFactory(UserFactory):
    """
    Factory for creating admin User instances.
    """

    is_staff = True
    is_superuser = True
