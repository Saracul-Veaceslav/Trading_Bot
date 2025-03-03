"""
Specialized metric collectors for different parts of the trading system.

This module provides specialized metric collectors that build on the base
PerformanceMetrics class to provide domain-specific monitoring for different
parts of the trading system.
"""

from typing import Dict, Any, Optional, List, Callable
import time
from functools import wraps
from abidance.monitoring.performance import PerformanceMetrics


class ExchangeMetrics(PerformanceMetrics):
    """
    Specialized metrics collector for exchange operations.
    
    This class extends PerformanceMetrics to provide specific monitoring
    for exchange-related operations like API calls, order placement, etc.
    """
    
    def __init__(self, window_size: int = 1000):
        """
        Initialize a new ExchangeMetrics instance.
        
        Args:
            window_size: Maximum number of timing values to keep per operation
        """
        super().__init__(window_size)
        
    def record_api_call(self, endpoint: str, duration: float) -> None:
        """
        Record duration of an API call to a specific endpoint.
        
        Args:
            endpoint: API endpoint that was called
            duration: Duration of the API call in seconds
        """
        operation = f"api_call:{endpoint}"
        self.record_timing(operation, duration)
        
    def record_order_placement(self, order_type: str, duration: float) -> None:
        """
        Record duration of an order placement.
        
        Args:
            order_type: Type of order that was placed (market, limit, etc.)
            duration: Duration of the order placement in seconds
        """
        operation = f"order_placement:{order_type}"
        self.record_timing(operation, duration)


class StrategyMetrics(PerformanceMetrics):
    """
    Specialized metrics collector for strategy operations.
    
    This class extends PerformanceMetrics to provide specific monitoring
    for strategy-related operations like signal generation, backtesting, etc.
    """
    
    def __init__(self, window_size: int = 1000):
        """
        Initialize a new StrategyMetrics instance.
        
        Args:
            window_size: Maximum number of timing values to keep per operation
        """
        super().__init__(window_size)
        
    def record_signal_generation(self, strategy_name: str, duration: float) -> None:
        """
        Record duration of signal generation for a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
            duration: Duration of the signal generation in seconds
        """
        operation = f"signal_generation:{strategy_name}"
        self.record_timing(operation, duration)
        
    def record_backtest(self, strategy_name: str, duration: float) -> None:
        """
        Record duration of a backtest for a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
            duration: Duration of the backtest in seconds
        """
        operation = f"backtest:{strategy_name}"
        self.record_timing(operation, duration)


def time_function(metrics: PerformanceMetrics, operation: str = None):
    """
    Decorator to time a function and record the duration.
    
    Args:
        metrics: PerformanceMetrics instance to record the timing
        operation: Name of the operation, defaults to the function name if None
        
    Returns:
        Decorated function
        
    Example:
        ```python
        metrics = PerformanceMetrics()
        
        @time_function(metrics)
        def my_function():
            # Function code here
            pass
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation or func.__name__
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                metrics.record_timing(op_name, duration)
        return wrapper
    return decorator 