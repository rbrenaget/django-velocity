"""
Core Type Definitions.

Common types used across the application.
"""

from __future__ import annotations

from typing import Any, TypeVar

from django.db.models import Model, QuerySet

# Generic model type variable
ModelType = TypeVar("ModelType", bound=Model)

# Common type aliases
type JsonDict = dict[str, Any]
type JsonList = list[JsonDict]

# QuerySet with generic type support
type TypedQuerySet[T] = QuerySet[T]
