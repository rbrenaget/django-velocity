"""
Core Models - Abstract base classes for all domain models.

Usage:
    from apps.core.models import BaseModel

    class Product(BaseModel):
        name = models.CharField(max_length=255)
        # Automatically includes: created_at, updated_at
"""

from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model with timestamp tracking.

    All domain models should inherit from this class.

    Attributes:
        created_at: Auto-set on creation
        updated_at: Auto-updated on every save
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the record was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} pk={self.pk}>"
