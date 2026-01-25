"""
Core Services - Base utilities for service layer.

Services are responsible for:
- Business logic orchestration
- Write operations (Create, Update, Delete)
- External API calls
- Transaction management

Usage:
    from apps.core.services import service

    @service
    def order_create(*, user: User, items: list[dict]) -> Order:
        # Business logic here
        ...
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, ParamSpec, TypeVar

from django.db import transaction

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def service(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that marks a function as a service.

    Features:
    - Wraps the function in a database transaction
    - Logs service calls for debugging
    - Provides consistent error handling

    Usage:
        @service
        def user_create(*, email: str, password: str) -> User:
            ...
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        service_name = f"{func.__module__}.{func.__name__}"
        logger.debug(f"Service called: {service_name}")

        try:
            with transaction.atomic():
                result = func(*args, **kwargs)
            logger.debug(f"Service completed: {service_name}")
            return result
        except Exception as e:
            logger.exception(f"Service failed: {service_name} - {e}")
            raise

    return wrapper


def get_object_or_raise(
    model_class: type,
    exception_class: type[Exception],
    message: str,
    **lookup_kwargs: Any,
) -> Any:
    """
    Get an object or raise a custom exception.

    Usage:
        user = get_object_or_raise(
            User,
            NotFound,
            "User not found",
            pk=user_id
        )
    """
    from apps.core.exceptions import NotFound

    try:
        return model_class.objects.get(**lookup_kwargs)
    except model_class.DoesNotExist:
        raise exception_class(message)
