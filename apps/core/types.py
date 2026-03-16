"""
Core Type Definitions.

Common types used across the application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from django.db.models import Model, QuerySet
from rest_framework.request import Request

if TYPE_CHECKING:
    from apps.users.models import User


# Define a Request where .user is guaranteed to be our User model
class AuthenticatedRequest(Request):
    user: User


# Generic model type variable
ModelType = TypeVar("ModelType", bound=Model)

# Common type aliases
type JsonDict = dict[str, Any]
type JsonList = list[JsonDict]

# QuerySet with generic type support
type TypedQuerySet[T] = QuerySet[T]
