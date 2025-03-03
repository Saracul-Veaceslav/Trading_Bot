"""
Metrics collection system for the Abidance trading bot.

This module provides a framework for collecting, storing, and retrieving
metrics about the application's performance and behavior.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, Any, Optional, List, Union, Callable
import threading

import statistics



class AggregationType(Enum):
    """Types of aggregation for metrics data."""
    SUM = auto()
    AVG = auto()
    MIN = auto()
    MAX = auto()
    COUNT = auto()
    LAST = auto()
    FIRST = auto()


class MetricsCollector:
    """
    Collector for application metrics.

    This class provides methods for recording metric values and retrieving
    historical metric data with optional time-based filtering.
    """

    def __init__(self):
        """Initialize the metrics collector with empty metrics storage."""
        self._metrics: Dict[str, Dict[datetime, Any]] = defaultdict(dict)
        self._lock = threading.Lock()

    def record(self, metric_name: str, value: Any) -> None:
        """
        Record a metric value with the current timestamp.

        Args:
            metric_name: The name of the metric to record
            value: The value to record
        """
        with self._lock:
            self._metrics[metric_name][datetime.now()] = value

    def record_with_timestamp(self, metric_name: str, value: Any, timestamp: datetime) -> None:
        """
        Record a metric value with a specific timestamp.

        Args:
            metric_name: The name of the metric to record
            value: The value to record
            timestamp: The timestamp to associate with the value
        """
        with self._lock:
            self._metrics[metric_name][timestamp] = value

    def get_metric(self, metric_name: str,
                  since: Optional[datetime] = None,
                  until: Optional[datetime] = None) -> Dict[datetime, Any]:
        """
        Get recorded values for a metric with optional time filtering.

        Args:
            metric_name: The name of the metric to retrieve
            since: Optional start time for filtering (inclusive)
            until: Optional end time for filtering (inclusive)

        Returns:
            A dictionary mapping timestamps to metric values
        """
        with self._lock:
            data = self._metrics.get(metric_name, {})
            filtered_data = {}

            for ts, val in data.items():
                if since and ts < since:
                    continue
                if until and ts > until:
                    continue
                filtered_data[ts] = val

            return filtered_data

    def get_metrics_list(self, metric_names: List[str],
                        since: Optional[datetime] = None,
                        until: Optional[datetime] = None) -> Dict[str, Dict[datetime, Any]]:
        """
        Get recorded values for multiple metrics with optional time filtering.

        Args:
            metric_names: List of metric names to retrieve
            since: Optional start time for filtering (inclusive)
            until: Optional end time for filtering (inclusive)

        Returns:
            A dictionary mapping metric names to dictionaries of timestamp-value pairs
        """
        result = {}
        for name in metric_names:
            result[name] = self.get_metric(name, since, until)
        return result

    def get_latest(self, metric_name: str) -> Optional[Any]:
        """
        Get the most recent value for a metric.

        Args:
            metric_name: The name of the metric to retrieve

        Returns:
            The most recent value, or None if no values exist
        """
        with self._lock:
            data = self._metrics.get(metric_name, {})
            if not data:
                return None

            latest_ts = max(data.keys())
            return data[latest_ts]

    def aggregate(self, metric_name: str,
                 aggregation_type: AggregationType,
                 since: Optional[datetime] = None,
                 until: Optional[datetime] = None) -> Optional[Any]:
        """
        Aggregate metric values using the specified aggregation type.

        Args:
            metric_name: The name of the metric to aggregate
            aggregation_type: The type of aggregation to perform
            since: Optional start time for filtering (inclusive)
            until: Optional end time for filtering (inclusive)

        Returns:
            The aggregated value, or None if no values exist
        """
        data = self.get_metric(metric_name, since, until)
        values = list(data.values())

        if not values:
            return None

        if aggregation_type == AggregationType.SUM:
            return sum(values)
        if aggregation_type == AggregationType.AVG:
            return statistics.mean(values)
        if aggregation_type == AggregationType.MIN:
            return min(values)
        if aggregation_type == AggregationType.MAX:
            return max(values)
        if aggregation_type == AggregationType.COUNT:
            return len(values)
        if aggregation_type == AggregationType.LAST:
            latest_ts = max(data.keys())
            return data[latest_ts]
        if aggregation_type == AggregationType.FIRST:
            earliest_ts = min(data.keys())
            return data[earliest_ts]

        return None

    def clear(self, metric_name: Optional[str] = None) -> None:
        """
        Clear metrics data.

        Args:
            metric_name: Optional name of the metric to clear.
                         If None, all metrics are cleared.
        """
        with self._lock:
            if metric_name:
                if metric_name in self._metrics:
                    del self._metrics[metric_name]
            else:
                self._metrics.clear()
