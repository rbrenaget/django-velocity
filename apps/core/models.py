"""
Core Models - Abstract base classes for all domain models.

Usage:
    from apps.core.models import BaseModel

    class Product(BaseModel):
        name = models.CharField(max_length=255)
        # Automatically includes: created_at, updated_at
"""

from typing import Any

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

    def save_partial(
        self,
        *,
        update_fields: list[str],
        using: str | None = None,
        **kwargs: Any,
    ):
        """
        Saves specific fields to the database while ensuring 'updated_at' is included.

        This method is a safety wrapper around Django's native save(update_fields=...).
        It prevents the common bug where 'updated_at' is not refreshed during
        partial updates.

        Args:
            update_fields: List of field names to be updated in the database.
            using: Name of the database alias to use.
            **kwargs: Additional arguments passed to the native save() method
                (e.g., force_insert, force_update).

        Example:
            >>> task.title = "New Title"
            >>> task.save_fields(update_fields=["title"])
        """
        if "updated_at" not in update_fields:
            # Use a copy to avoid using the original list
            update_fields = list(update_fields) + ["updated_at"]

        super().save(update_fields=update_fields, **kwargs)
