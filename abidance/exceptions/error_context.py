"""
Error context utilities for the Abidance trading bot.

This module provides utilities for enriching exceptions with context information
and implementing standardized error handling patterns.
"""

from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast
import functools
import time
import traceback


from .base import AbidanceError

# Type variables for function signatures
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class ErrorContext:
    """
    Class for storing and retrieving context information for exceptions.

    This class provides methods for enriching exceptions with additional context
    information, making debugging and error handling more effective.
    """

    def __init__(self,
                context: Optional[Dict[str, Any]] = None,
                source: Optional[str] = None,
                operation: Optional[str] = None):
        """
        Initialize the error context.

        Args:
            context: Initial context information as a dictionary
            source: Name of the component or module where the error occurred
            operation: Name of the operation being performed when the error occurred
        """
        self.context = context or {}
        self.source = source
        self.operation = operation
        self.stack_trace = None

    def add_context(self, key: str, value: Any) -> 'ErrorContext':
        """
        Add a context item to the error context.

        Args:
            key: Context item key
            value: Context item value

        Returns:
            Self for method chaining
        """
        self.context[key] = value
        return self

    def update_context(self, context_dict: Dict[str, Any]) -> 'ErrorContext':
        """
        Update the context with multiple items.

        Args:
            context_dict: Dictionary of context items to add

        Returns:
            Self for method chaining
        """
        self.context.update(context_dict)
        return self

    def set_source(self, source: str) -> 'ErrorContext':
        """
        Set the source of the error.

        Args:
            source: Name of the component or module

        Returns:
            Self for method chaining
        """
        self.source = source
        return self

    def set_operation(self, operation: str) -> 'ErrorContext':
        """
        Set the operation being performed when the error occurred.

        Args:
            operation: Name of the operation

        Returns:
            Self for method chaining
        """
        self.operation = operation
        return self

    def capture_stack_trace(self) -> 'ErrorContext':
        """
        Capture the current stack trace.

        Returns:
            Self for method chaining
        """
        self.stack_trace = traceback.format_exc()
        return self

    def enrich_exception(self, exception: AbidanceError) -> AbidanceError:
        """
        Enrich an exception with the context information.

        Args:
            exception: The exception to enrich

        Returns:
            The enriched exception
        """
        if not hasattr(exception, 'context'):
            setattr(exception, 'context', {})

        exception.context = self.context.copy()  # type: ignore

        if self.source:
            exception.source = self.source  # type: ignore

        if self.operation:
            exception.operation = self.operation  # type: ignore

        if self.stack_trace:
            exception.stack_trace = self.stack_trace  # type: ignore

        return exception


@contextmanager
def error_boundary(
    error_types: Union[Type[Exception], List[Type[Exception]]] = Exception,
    source: Optional[str] = None,
    operation: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    reraise: bool = True,
    transform_exception: Optional[Callable[[Exception, ErrorContext], Exception]] = None
):
    """
    Context manager for handling errors with consistent behavior.

    This context manager captures exceptions of specified types and enriches them
    with context information before reraising or handling them.

    Args:
        error_types: Exception type(s) to catch
        source: Name of the component or module where the error occurred
        operation: Name of the operation being performed
        context: Initial context information as a dictionary
        reraise: Whether to reraise the exception after processing
        transform_exception: Optional function to transform the caught exception

    Yields:
        ErrorContext object that can be used to add more context

    Raises:
        The caught exception, possibly transformed, if reraise is True
    """
    if isinstance(error_types, type) and issubclass(error_types, Exception):
        error_types = [error_types]

    error_ctx = ErrorContext(context=context, source=source, operation=operation)

    try:
        yield error_ctx
    except tuple(error_types) as e:  # type: ignore
        error_ctx.capture_stack_trace()

        if isinstance(e, AbidanceError):
            enriched_error = error_ctx.enrich_exception(e)
        else:
            # If it's not an AbidanceError, wrap it in one
            abidance_error = AbidanceError(str(e))
            enriched_error = error_ctx.enrich_exception(abidance_error)
            enriched_error.__cause__ = e

        if transform_exception:
            transformed_error = transform_exception(enriched_error, error_ctx)
            if reraise:
                raise transformed_error from e
        elif reraise:
            raise enriched_error from e


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    error_types: Union[Type[Exception], List[Type[Exception]]] = Exception,
    should_retry: Optional[Callable[[Exception, int], bool]] = None
) -> Callable[[F], F]:
    """
    Decorator for retrying a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor by which the delay increases with each retry
        error_types: Exception type(s) that should trigger a retry
        should_retry: Optional function that decides if a retry should be performed

    Returns:
        Decorated function
    """
    if isinstance(error_types, type) and issubclass(error_types, Exception):
        error_types = [error_types]

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            current_delay = delay

            while True:
                try:
                    return func(*args, **kwargs)
                except tuple(error_types) as e:  # type: ignore
                    # Check if we've reached max attempts
                    if attempt >= max_attempts:
                        raise

                    # Check if we should retry based on custom logic
                    if should_retry and not should_retry(e, attempt):
                        raise

                    # Wait before retrying
                    time.sleep(current_delay)

                    # Increase delay for next attempt
                    current_delay *= backoff_factor
                    attempt += 1

        return cast(F, wrapper)

    return decorator
