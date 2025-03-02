"""
Fallback strategies for error recovery in the Abidance trading bot.

This module provides utilities for implementing fallback strategies
when operations fail, allowing the application to gracefully handle failures.
"""

import functools
import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

from . import AbidanceError
from .error_context import ErrorContext

# Type variables for function signatures
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R')

logger = logging.getLogger(__name__)


def fallback(
    default_value: Any = None,
    error_types: Union[Type[Exception], List[Type[Exception]]] = Exception,
    fallback_function: Optional[Callable[..., Any]] = None,
    log_error: bool = True,
    log_level: int = logging.ERROR
) -> Callable[[F], F]:
    """
    Decorator that applies a fallback strategy when a function fails.
    
    Args:
        default_value: Value to return if the function fails
        error_types: Exception type(s) that should trigger the fallback
        fallback_function: Alternative function to call if the main function fails
        log_error: Whether to log the error
        log_level: Logging level to use when logging errors
        
    Returns:
        Decorated function
    """
    if isinstance(error_types, type) and issubclass(error_types, Exception):
        error_types = [error_types]
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except tuple(error_types) as e:  # type: ignore
                if log_error:
                    if isinstance(e, AbidanceError) and hasattr(e, 'context'):
                        context_str = f" | Context: {getattr(e, 'context', {})}"
                    else:
                        context_str = ""
                    
                    # Get function name safely, handling the case of MagicMock objects which don't have __name__
                    func_name = getattr(func, '__name__', str(func))
                    
                    logger.log(
                        log_level, 
                        f"Error in {func_name}: {str(e)}{context_str}. Using fallback strategy."
                    )
                
                if fallback_function:
                    return fallback_function(*args, **kwargs)
                else:
                    return default_value
        
        return cast(F, wrapper)
    
    return decorator


class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to prevent cascading failures.
    
    The circuit breaker monitors for failures and automatically opens the circuit
    to prevent further calls when a threshold is reached. After a cooldown period, 
    the circuit transitions to half-open state to test if the underlying issue has
    been resolved.
    """
    
    # Circuit states
    CLOSED = 'closed'  # Normal operation, calls allowed
    OPEN = 'open'      # Circuit is open, calls are not allowed
    HALF_OPEN = 'half_open'  # Testing if the issue is resolved
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        error_types: Union[Type[Exception], List[Type[Exception]]] = Exception,
        fallback_value: Optional[Any] = None,
        fallback_function: Optional[Callable[..., Any]] = None,
        on_open: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Time in seconds to wait before testing recovery
            error_types: Exception type(s) that should count as failures
            fallback_value: Value to return when the circuit is open
            fallback_function: Function to call when the circuit is open
            on_open: Callback to execute when the circuit opens
            on_close: Callback to execute when the circuit closes
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        if isinstance(error_types, type) and issubclass(error_types, Exception):
            self.error_types = [error_types]
        else:
            self.error_types = error_types
            
        self.fallback_value = fallback_value
        self.fallback_function = fallback_function
        self.on_open = on_open
        self.on_close = on_close
        
        # Initialize state
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker")
    
    def __call__(self, func: F) -> F:
        """
        Decorate a function with circuit breaker functionality.
        
        Args:
            func: The function to protect with the circuit breaker
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self.execute(func, *args, **kwargs)
        
        return cast(F, wrapper)
    
    def execute(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        """
        Execute a function according to the circuit breaker state.
        
        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The function result or fallback value
            
        Raises:
            Exception: If the circuit is open and no fallback is provided
        """
        import time
        
        # Check if the circuit is open
        if self.state == self.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.logger.info("Circuit transitioning to half-open state")
                self.state = self.HALF_OPEN
            else:
                self.logger.debug("Circuit is open, using fallback")
                return self._handle_open_circuit(*args, **kwargs)
        
        try:
            result = func(*args, **kwargs)
            
            # If the call was successful in half-open state, reset the circuit
            if self.state == self.HALF_OPEN:
                self.logger.info("Success in half-open state, closing circuit")
                self._reset()
                if self.on_close:
                    self.on_close()
                
            return result
            
        except tuple(self.error_types) as e:  # type: ignore
            # Record the failure
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # Log the failure with a safe function name
            func_name = getattr(func, '__name__', str(func))
            self.logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold} in {func_name}: {str(e)}"
            )
            
            # If we've reached the threshold, open the circuit
            if self.state != self.OPEN and self.failure_count >= self.failure_threshold:
                self.logger.error(f"Circuit opened after {self.failure_count} failures")
                self.state = self.OPEN
                if self.on_open:
                    self.on_open()
            
            # If the circuit is now open, use the fallback
            if self.state == self.OPEN:
                return self._handle_open_circuit(*args, **kwargs)
            
            # Otherwise, propagate the exception
            raise
    
    def _handle_open_circuit(self, *args: Any, **kwargs: Any) -> Any:
        """
        Handle the case when the circuit is open.
        
        Args:
            *args: Original function arguments
            **kwargs: Original function keyword arguments
            
        Returns:
            Fallback value or fallback function result
            
        Raises:
            CircuitOpenError: If no fallback is provided
        """
        if self.fallback_function:
            return self.fallback_function(*args, **kwargs)
        elif self.fallback_value is not None:
            return self.fallback_value
        else:
            from . import CircuitOpenError
            raise CircuitOpenError("Circuit is open and no fallback was provided")
    
    def _reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0 