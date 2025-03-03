"""
Performance metrics collection and analysis.

This module provides tools for tracking operation durations and calculating
performance statistics to help identify bottlenecks and monitor system health.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import time
from statistics import mean, median
from collections import deque
import threading
from contextlib import contextmanager


class PerformanceMetrics:
    """
    Collector for performance metrics.

    This class provides functionality to record operation durations and
    calculate statistics on those durations to help identify performance
    bottlenecks and track system health.

    Attributes:
        _metrics: Dictionary mapping operation names to deques of timing values
        _window_size: Maximum number of timing values to keep per operation
        _lock: Thread lock to ensure thread safety
    """

    def __init__(self, window_size: int = 1000):
        """
        Initialize a new PerformanceMetrics instance.

        Args:
            window_size: Maximum number of timing values to keep per operation
        """
        self._metrics: Dict[str, deque[float]] = {}
        self._window_size = window_size
        self._lock = threading.Lock()

    def record_timing(self, operation: str, duration: float) -> None:
        """
        Record operation duration.

        Args:
            operation: Name of the operation being timed
            duration: Duration of the operation in seconds
        """
        with self._lock:
            if operation not in self._metrics:
                self._metrics[operation] = deque(maxlen=self._window_size)
            self._metrics[operation].append(duration)

    def get_statistics(self, operation: str) -> Dict[str, float]:
        """
        Get timing statistics for an operation.

        Args:
            operation: Name of the operation to get statistics for

        Returns:
            Dictionary containing count, mean, median, min, and max values,
            or an empty dictionary if no metrics exist for the operation
        """
        with self._lock:
            if operation not in self._metrics:
                return {}

            values = list(self._metrics[operation])
            return {
                'count': len(values),
                'mean': mean(values),
                'median': median(values),
                'min': min(values),
                'max': max(values)
            }

    @contextmanager
    def timed_operation(self, operation: str):
        """
        Context manager for timing an operation.

        Args:
            operation: Name of the operation being timed

        Yields:
            None

        Example:
            ```python
            metrics = PerformanceMetrics()
            with metrics.timed_operation("database_query"):
                # Code to time goes here
                result = db.execute_query()
            ```
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_timing(operation, duration)

    def get_all_operations(self) -> List[str]:
        """
        Get a list of all operations that have been timed.

        Returns:
            List of operation names
        """
        with self._lock:
            return list(self._metrics.keys())

    def clear_metrics(self, operation: Optional[str] = None) -> None:
        """
        Clear metrics for a specific operation or all operations.

        Args:
            operation: Name of operation to clear metrics for, or None to clear all
        """
        with self._lock:
            if operation is None:
                self._metrics.clear()
            elif operation in self._metrics:
                del self._metrics[operation]