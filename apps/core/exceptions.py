"""
Core Exceptions - Business Logic Error Hierarchy.

All business logic exceptions should inherit from ApplicationError.
The API layer catches these and transforms them into appropriate HTTP responses.

Usage:
    from apps.core.exceptions import ValidationError, NotFound

    def user_create(*, email: str) -> User:
        if user_exists(email):
            raise ValidationError("User with this email already exists.")
        ...
"""

from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class ApplicationError(Exception):
    """
    Base exception for all business logic errors.

    Attributes:
        message: Human-readable error description
        extra: Additional context data for debugging
        status_code: HTTP status code for API responses
    """

    status_code: ClassVar[int] = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        message: str = "An error occurred",
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.extra = extra or {}

    def __str__(self) -> str:
        return self.message


class ValidationError(ApplicationError):
    """
    Input validation failed.

    Raised when user input doesn't meet business rules.
    Maps to HTTP 400 Bad Request.
    """

    status_code = status.HTTP_400_BAD_REQUEST


class NotFound(ApplicationError):
    """
    Resource not found.

    Raised when a requested resource doesn't exist.
    Maps to HTTP 404 Not Found.
    """

    status_code = status.HTTP_404_NOT_FOUND


class PermissionDenied(ApplicationError):
    """
    User lacks permission for this action.

    Raised when authentication succeeds but authorization fails.
    Maps to HTTP 403 Forbidden.
    """

    status_code = status.HTTP_403_FORBIDDEN


class Conflict(ApplicationError):
    """
    Operation conflicts with current state.

    Raised for duplicate entries, concurrent modifications, etc.
    Maps to HTTP 409 Conflict.
    """

    status_code = status.HTTP_409_CONFLICT


class ServiceUnavailable(ApplicationError):
    """
    External service is unavailable.

    Raised when external API calls fail.
    Maps to HTTP 503 Service Unavailable.
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """
    Custom DRF exception handler that catches ApplicationError.

    Transforms business logic exceptions into standardized JSON responses.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    # Handle our custom ApplicationError hierarchy
    if isinstance(exc, ApplicationError):
        return Response(
            {
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "extra": exc.extra,
                }
            },
            status=exc.status_code,
        )

    return response
