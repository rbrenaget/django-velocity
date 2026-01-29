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
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from django.db import transaction
from django.db.models import Model

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")
M = TypeVar("M", bound=Model)


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
    model_class: type[M],
    exception_class: type[Exception],
    message: str,
    **lookup_kwargs: Any,
) -> M:
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

    try:
        return model_class.objects.get(**lookup_kwargs)
    except model_class.DoesNotExist as e:
        raise exception_class(message) from e
