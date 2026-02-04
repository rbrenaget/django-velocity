"""
Factories for permission tests.

Uses Django's built-in Group model.
"""

import factory
from django.contrib.auth.models import Group
from faker import Faker

fake = Faker()


class GroupFactory(factory.django.DjangoModelFactory):
    """Factory for Django's Group model."""

    class Meta:
        model = Group

    name = factory.LazyAttribute(lambda _: fake.unique.word().title())
