"""
Core Type Definitions.

Common types used across the application.
"""

from __future__ import annotations

from typing import Any, TypeAlias, TypeVar

from django.db.models import Model, QuerySet

# Generic model type variable
ModelType = TypeVar("ModelType", bound=Model)

# Common type aliases
JsonDict: TypeAlias = dict[str, Any]
JsonList: TypeAlias = list[JsonDict]

# QuerySet with generic type support
TypedQuerySet: TypeAlias = QuerySet[ModelType]
