"""Retry utilities with exponential backoff."""

from __future__ import annotations

import asyncio
import functools
import time
from typing import Any, Callable, TypeVar

from canvasapi.exceptions import CanvasException

T = TypeVar("T")


def with_retry(
    func: Callable[..., T],
    max_retries: int = 3,
    backoff_base: float = 1.0,
    retry_on: tuple[type[Exception], ...] = (CanvasException,),
) -> T:
    """
    Execute a function with retry and exponential backoff.

    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts
        backoff_base: Base time for exponential backoff (seconds)
        retry_on: Tuple of exception types to retry on

    Returns:
        Result of the function

    Raises:
        Last exception if all retries fail
    """
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except retry_on as e:
            last_exception = e

            # Check if it's a rate limit or server error
            if hasattr(e, "response"):
                status_code = getattr(e.response, "status_code", None)
                # Only retry on 429 (rate limit) and 5xx errors
                if status_code and status_code not in (429,) and not (500 <= status_code < 600):
                    raise

            if attempt < max_retries:
                backoff_time = backoff_base * (2**attempt)
                time.sleep(backoff_time)
            else:
                raise

    # Should never reach here, but satisfy type checker
    raise last_exception if last_exception else RuntimeError("Retry failed without exception")


async def with_retry_async(
    func: Callable[..., T],
    max_retries: int = 3,
    backoff_base: float = 1.0,
    retry_on: tuple[type[Exception], ...] = (CanvasException,),
) -> T:
    """
    Execute an async function with retry and exponential backoff.

    Args:
        func: Async function to execute
        max_retries: Maximum number of retry attempts
        backoff_base: Base time for exponential backoff (seconds)
        retry_on: Tuple of exception types to retry on

    Returns:
        Result of the function

    Raises:
        Last exception if all retries fail
    """
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            result = func()
            if asyncio.iscoroutine(result):
                return await result
            return result
        except retry_on as e:
            last_exception = e

            # Check if it's a rate limit or server error
            if hasattr(e, "response"):
                status_code = getattr(e.response, "status_code", None)
                # Only retry on 429 (rate limit) and 5xx errors
                if status_code and status_code not in (429,) and not (500 <= status_code < 600):
                    raise

            if attempt < max_retries:
                backoff_time = backoff_base * (2**attempt)
                await asyncio.sleep(backoff_time)
            else:
                raise

    # Should never reach here, but satisfy type checker
    raise last_exception if last_exception else RuntimeError("Retry failed without exception")


def retry(
    max_retries: int = 3,
    backoff_base: float = 1.0,
    retry_on: tuple[type[Exception], ...] = (CanvasException,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_base: Base time for exponential backoff (seconds)
        retry_on: Tuple of exception types to retry on

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return with_retry(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                backoff_base=backoff_base,
                retry_on=retry_on,
            )

        return wrapper

    return decorator
