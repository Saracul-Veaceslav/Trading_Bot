"""
Tests for the performance metrics module.

This module contains tests for the PerformanceMetrics class and related functionality.
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from abidance.monitoring.performance import PerformanceMetrics
from abidance.monitoring.collectors import ExchangeMetrics, StrategyMetrics, time_function


class TestPerformanceMetrics:
    """Tests for the PerformanceMetrics class."""

    def test_record_timing(self):
        """Test that timing recording works correctly."""
        # Given
        metrics = PerformanceMetrics()
        operation = "test_operation"
        duration = 0.1
        
        # When
        metrics.record_timing(operation, duration)
        
        # Then
        stats = metrics.get_statistics(operation)
        assert stats["count"] == 1
        assert stats["mean"] == duration
        assert stats["median"] == duration
        assert stats["min"] == duration
        assert stats["max"] == duration
        
    def test_get_statistics_empty(self):
        """Test that get_statistics returns an empty dict for unknown operations."""
        # Given
        metrics = PerformanceMetrics()
        
        # When
        stats = metrics.get_statistics("unknown_operation")
        
        # Then
        assert stats == {}
        
    def test_get_statistics_multiple_values(self):
        """Test that statistics are calculated correctly for multiple values."""
        # Given
        metrics = PerformanceMetrics()
        operation = "test_operation"
        durations = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # When
        for duration in durations:
            metrics.record_timing(operation, duration)
        
        # Then
        stats = metrics.get_statistics(operation)
        assert stats["count"] == len(durations)
        assert stats["mean"] == sum(durations) / len(durations)
        assert stats["median"] == 0.3
        assert stats["min"] == min(durations)
        assert stats["max"] == max(durations)
        
    def test_window_size_limiting(self):
        """Test that the window size limits the number of recorded values."""
        # Given
        window_size = 5
        metrics = PerformanceMetrics(window_size=window_size)
        operation = "test_operation"
        
        # When
        for i in range(10):
            metrics.record_timing(operation, float(i))
        
        # Then
        stats = metrics.get_statistics(operation)
        assert stats["count"] == window_size
        assert stats["min"] == 5.0
        assert stats["max"] == 9.0
        
    def test_concurrent_access(self):
        """Test that concurrent access to the metrics is thread-safe."""
        # Given
        metrics = PerformanceMetrics()
        operation = "test_operation"
        num_threads = 10
        iterations_per_thread = 100
        
        # When
        def worker():
            for _ in range(iterations_per_thread):
                metrics.record_timing(operation, 0.1)
                
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_threads)]
            for future in futures:
                future.result()
        
        # Then
        stats = metrics.get_statistics(operation)
        assert stats["count"] == num_threads * iterations_per_thread
        
    def test_timed_operation_context_manager(self):
        """Test that the timed_operation context manager records timings."""
        # Given
        metrics = PerformanceMetrics()
        operation = "test_operation"
        sleep_time = 0.01
        
        # When
        with metrics.timed_operation(operation):
            time.sleep(sleep_time)
        
        # Then
        stats = metrics.get_statistics(operation)
        assert stats["count"] == 1
        assert stats["min"] >= sleep_time
        
    def test_get_all_operations(self):
        """Test that get_all_operations returns all recorded operations."""
        # Given
        metrics = PerformanceMetrics()
        operations = ["op1", "op2", "op3"]
        
        # When
        for op in operations:
            metrics.record_timing(op, 0.1)
        
        # Then
        all_ops = metrics.get_all_operations()
        assert set(all_ops) == set(operations)
        
    def test_clear_metrics_specific_operation(self):
        """Test that clear_metrics clears metrics for a specific operation."""
        # Given
        metrics = PerformanceMetrics()
        operations = ["op1", "op2", "op3"]
        
        for op in operations:
            metrics.record_timing(op, 0.1)
        
        # When
        metrics.clear_metrics("op2")
        
        # Then
        assert "op1" in metrics.get_all_operations()
        assert "op2" not in metrics.get_all_operations()
        assert "op3" in metrics.get_all_operations()
        
    def test_clear_metrics_all_operations(self):
        """Test that clear_metrics clears all metrics when no operation is specified."""
        # Given
        metrics = PerformanceMetrics()
        operations = ["op1", "op2", "op3"]
        
        for op in operations:
            metrics.record_timing(op, 0.1)
        
        # When
        metrics.clear_metrics()
        
        # Then
        assert metrics.get_all_operations() == []


class TestExchangeMetrics:
    """Tests for the ExchangeMetrics class."""
    
    def test_record_api_call(self):
        """Test that API call recording works correctly."""
        # Given
        metrics = ExchangeMetrics()
        endpoint = "get_ticker"
        duration = 0.1
        
        # When
        metrics.record_api_call(endpoint, duration)
        
        # Then
        operation = f"api_call:{endpoint}"
        stats = metrics.get_statistics(operation)
        assert stats["count"] == 1
        assert stats["mean"] == duration
        
    def test_record_order_placement(self):
        """Test that order placement recording works correctly."""
        # Given
        metrics = ExchangeMetrics()
        order_type = "market"
        duration = 0.2
        
        # When
        metrics.record_order_placement(order_type, duration)
        
        # Then
        operation = f"order_placement:{order_type}"
        stats = metrics.get_statistics(operation)
        assert stats["count"] == 1
        assert stats["mean"] == duration


class TestStrategyMetrics:
    """Tests for the StrategyMetrics class."""
    
    def test_record_signal_generation(self):
        """Test that signal generation recording works correctly."""
        # Given
        metrics = StrategyMetrics()
        strategy_name = "sma_crossover"
        duration = 0.3
        
        # When
        metrics.record_signal_generation(strategy_name, duration)
        
        # Then
        operation = f"signal_generation:{strategy_name}"
        stats = metrics.get_statistics(operation)
        assert stats["count"] == 1
        assert stats["mean"] == duration
        
    def test_record_backtest(self):
        """Test that backtest recording works correctly."""
        # Given
        metrics = StrategyMetrics()
        strategy_name = "rsi_strategy"
        duration = 0.4
        
        # When
        metrics.record_backtest(strategy_name, duration)
        
        # Then
        operation = f"backtest:{strategy_name}"
        stats = metrics.get_statistics(operation)
        assert stats["count"] == 1
        assert stats["mean"] == duration


class TestTimeFunction:
    """Tests for the time_function decorator."""
    
    def test_time_function_default_operation(self):
        """Test that the time_function decorator records timings with default operation name."""
        # Given
        metrics = PerformanceMetrics()
        
        @time_function(metrics)
        def test_func():
            time.sleep(0.01)
            
        # When
        test_func()
        
        # Then
        stats = metrics.get_statistics("test_func")
        assert stats["count"] == 1
        
    def test_time_function_custom_operation(self):
        """Test that the time_function decorator records timings with custom operation name."""
        # Given
        metrics = PerformanceMetrics()
        operation = "custom_operation"
        
        @time_function(metrics, operation)
        def test_func():
            time.sleep(0.01)
            
        # When
        test_func()
        
        # Then
        stats = metrics.get_statistics(operation)
        assert stats["count"] == 1
        
    def test_time_function_preserves_return_value(self):
        """Test that the time_function decorator preserves the return value of the decorated function."""
        # Given
        metrics = PerformanceMetrics()
        expected_return = "test_return"
        
        @time_function(metrics)
        def test_func():
            return expected_return
            
        # When
        actual_return = test_func()
        
        # Then
        assert actual_return == expected_return
        
    def test_time_function_preserves_exceptions(self):
        """Test that the time_function decorator preserves exceptions raised by the decorated function."""
        # Given
        metrics = PerformanceMetrics()
        
        @time_function(metrics)
        def test_func():
            raise ValueError("Test exception")
            
        # When/Then
        with pytest.raises(ValueError, match="Test exception"):
            test_func()
            
        # Verify timing was still recorded
        stats = metrics.get_statistics("test_func")
        assert stats["count"] == 1 