"""
Factories for permission tests.

Uses Django's built-in Group model.
"""

import factory
from faker import Faker

from django.contrib.auth.models import Group

fake = Faker()


class GroupFactory(factory.django.DjangoModelFactory):
    """Factory for Django's Group model."""

    class Meta:
        model = Group

    name = factory.LazyAttribute(lambda _: fake.unique.word().title())
