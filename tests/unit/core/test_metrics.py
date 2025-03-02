"""
Tests for the metrics collection system.
"""

import pytest
import time
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor
import random

from abidance.core.metrics import MetricsCollector, AggregationType
from abidance.core.collectors import (
    PerformanceMetricsCollector,
    TradingMetricsCollector,
    SystemMetricsCollector
)


class TestMetricsCollector:
    """Tests for the MetricsCollector class."""
    
    def test_record_and_get_metric(self):
        """Test recording and retrieving a metric."""
        collector = MetricsCollector()
        
        # Record a metric
        collector.record("test_metric", 42)
        
        # Get the metric
        metrics = collector.get_metric("test_metric")
        
        # Check that we have one entry
        assert len(metrics) == 1
        
        # Check the value
        assert list(metrics.values())[0] == 42
    
    def test_record_with_timestamp(self):
        """Test recording a metric with a specific timestamp."""
        collector = MetricsCollector()
        timestamp = datetime.now() - timedelta(hours=1)
        
        # Record a metric with a timestamp
        collector.record_with_timestamp("test_metric", 42, timestamp)
        
        # Get the metric
        metrics = collector.get_metric("test_metric")
        
        # Check that we have one entry
        assert len(metrics) == 1
        
        # Check the timestamp and value
        assert list(metrics.keys())[0] == timestamp
        assert list(metrics.values())[0] == 42
    
    def test_get_metric_with_time_filtering(self):
        """Test retrieving metrics with time-based filtering."""
        collector = MetricsCollector()
        
        # Record metrics with different timestamps
        now = datetime.now()
        collector.record_with_timestamp("test_metric", 1, now - timedelta(hours=3))
        collector.record_with_timestamp("test_metric", 2, now - timedelta(hours=2))
        collector.record_with_timestamp("test_metric", 3, now - timedelta(hours=1))
        
        # Get metrics with since filter
        metrics = collector.get_metric("test_metric", since=now - timedelta(hours=2.5))
        assert len(metrics) == 2
        assert sorted(list(metrics.values())) == [2, 3]
        
        # Get metrics with until filter
        metrics = collector.get_metric("test_metric", until=now - timedelta(hours=1.5))
        assert len(metrics) == 2
        assert sorted(list(metrics.values())) == [1, 2]
        
        # Get metrics with both since and until filters
        metrics = collector.get_metric("test_metric", 
                                      since=now - timedelta(hours=2.5),
                                      until=now - timedelta(hours=0.5))
        assert len(metrics) == 2
        assert sorted(list(metrics.values())) == [2, 3]
    
    def test_get_metrics_list(self):
        """Test retrieving multiple metrics at once."""
        collector = MetricsCollector()
        
        # Record different metrics
        collector.record("metric1", 1)
        collector.record("metric2", 2)
        collector.record("metric3", 3)
        
        # Get multiple metrics
        metrics = collector.get_metrics_list(["metric1", "metric2"])
        
        # Check that we have entries for both metrics
        assert "metric1" in metrics
        assert "metric2" in metrics
        assert len(metrics["metric1"]) == 1
        assert len(metrics["metric2"]) == 1
        
        # Check the values
        assert list(metrics["metric1"].values())[0] == 1
        assert list(metrics["metric2"].values())[0] == 2
    
    def test_get_latest(self):
        """Test retrieving the latest metric value."""
        collector = MetricsCollector()
        
        # Record metrics with different timestamps
        now = datetime.now()
        collector.record_with_timestamp("test_metric", 1, now - timedelta(hours=3))
        collector.record_with_timestamp("test_metric", 2, now - timedelta(hours=2))
        collector.record_with_timestamp("test_metric", 3, now - timedelta(hours=1))
        
        # Get the latest value
        latest = collector.get_latest("test_metric")
        assert latest == 3
        
        # Test with a non-existent metric
        latest = collector.get_latest("non_existent")
        assert latest is None
    
    def test_aggregate(self):
        """Test aggregating metric values."""
        collector = MetricsCollector()
        
        # Record metrics with different timestamps
        now = datetime.now()
        collector.record_with_timestamp("test_metric", 1, now - timedelta(hours=3))
        collector.record_with_timestamp("test_metric", 2, now - timedelta(hours=2))
        collector.record_with_timestamp("test_metric", 3, now - timedelta(hours=1))
        
        # Test different aggregation types
        assert collector.aggregate("test_metric", AggregationType.SUM) == 6
        assert collector.aggregate("test_metric", AggregationType.AVG) == 2
        assert collector.aggregate("test_metric", AggregationType.MIN) == 1
        assert collector.aggregate("test_metric", AggregationType.MAX) == 3
        assert collector.aggregate("test_metric", AggregationType.COUNT) == 3
        assert collector.aggregate("test_metric", AggregationType.LAST) == 3
        assert collector.aggregate("test_metric", AggregationType.FIRST) == 1
        
        # Test with time filtering
        assert collector.aggregate("test_metric", AggregationType.SUM, 
                                  since=now - timedelta(hours=2.5)) == 5
        
        # Test with a non-existent metric
        assert collector.aggregate("non_existent", AggregationType.SUM) is None
    
    def test_clear(self):
        """Test clearing metrics data."""
        collector = MetricsCollector()
        
        # Record different metrics
        collector.record("metric1", 1)
        collector.record("metric2", 2)
        
        # Clear a specific metric
        collector.clear("metric1")
        
        # Check that only metric1 was cleared
        assert len(collector.get_metric("metric1")) == 0
        assert len(collector.get_metric("metric2")) == 1
        
        # Record metric1 again
        collector.record("metric1", 3)
        
        # Clear all metrics
        collector.clear()
        
        # Check that all metrics were cleared
        assert len(collector.get_metric("metric1")) == 0
        assert len(collector.get_metric("metric2")) == 0
    
    def test_concurrent_access(self):
        """Test concurrent access to the metrics collector."""
        collector = MetricsCollector()
        num_threads = 5
        iterations_per_thread = 20
        
        def record_metrics(thread_id):
            for i in range(iterations_per_thread):
                collector.record(f"thread_{thread_id}", i)
                # Add a small sleep to reduce race conditions
                time.sleep(0.001)
        
        # Start multiple threads to record metrics concurrently
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=record_metrics, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all metrics were recorded correctly
        for i in range(num_threads):
            metrics = collector.get_metric(f"thread_{i}")
            assert len(metrics) == iterations_per_thread
            assert sorted(list(metrics.values())) == list(range(iterations_per_thread))


class TestPerformanceMetricsCollector:
    """Tests for the PerformanceMetricsCollector class."""
    
    def test_timer(self):
        """Test the timer functionality."""
        collector = PerformanceMetricsCollector()
        
        # Start a timer
        collector.start_timer("test_timer")
        
        # Sleep for a short time
        time.sleep(0.1)
        
        # Stop the timer
        elapsed = collector.stop_timer("test_timer")
        
        # Check that the elapsed time is reasonable
        assert 0.05 < elapsed < 0.2
        
        # Check that the timer was recorded as a metric
        metrics = collector.get_metric("timer.test_timer")
        assert len(metrics) == 1
        assert 0.05 < list(metrics.values())[0] < 0.2
        
        # Test stopping a non-existent timer
        with pytest.raises(KeyError):
            collector.stop_timer("non_existent")
    
    def test_time_function_decorator(self):
        """Test the time_function decorator."""
        collector = PerformanceMetricsCollector()
        
        @collector.time_function()
        def test_function():
            time.sleep(0.1)
            return 42
        
        # Call the decorated function
        result = test_function()
        
        # Check that the function returned the correct result
        assert result == 42
        
        # Check that the timer was recorded as a metric
        metrics = collector.get_metric("timer.test_function")
        assert len(metrics) == 1
        assert 0.05 < list(metrics.values())[0] < 0.2
        
        # Test with a custom timer name
        @collector.time_function("custom_timer")
        def another_function():
            time.sleep(0.1)
            return 84
        
        # Call the decorated function
        result = another_function()
        
        # Check that the function returned the correct result
        assert result == 84
        
        # Check that the timer was recorded with the custom name
        metrics = collector.get_metric("timer.custom_timer")
        assert len(metrics) == 1
        assert 0.05 < list(metrics.values())[0] < 0.2


class TestTradingMetricsCollector:
    """Tests for the TradingMetricsCollector class."""
    
    def test_record_order(self):
        """Test recording an order."""
        collector = TradingMetricsCollector()
        
        # Record an order
        collector.record_order(
            order_id="123",
            symbol="BTC/USD",
            side="buy",
            order_type="market",
            quantity=1.0,
            price=50000.0
        )
        
        # Check that the order was recorded
        metrics = collector.get_metric("order.BTC/USD.buy")
        assert len(metrics) == 1
        
        order_data = list(metrics.values())[0]
        assert order_data["order_id"] == "123"
        assert order_data["symbol"] == "BTC/USD"
        assert order_data["side"] == "buy"
        assert order_data["type"] == "market"
        assert order_data["quantity"] == 1.0
        assert order_data["price"] == 50000.0
        
        # Check that the order count metrics were recorded
        assert collector.get_latest("order_count.BTC/USD.buy") == 1
        assert collector.get_latest("order_volume.BTC/USD.buy") == 1.0
        assert collector.get_latest("order_value.BTC/USD.buy") == 50000.0
    
    def test_record_trade(self):
        """Test recording a trade."""
        collector = TradingMetricsCollector()
        
        # Record a trade
        collector.record_trade(
            trade_id="456",
            symbol="BTC/USD",
            side="sell",
            quantity=0.5,
            price=51000.0,
            fee=25.5
        )
        
        # Check that the trade was recorded
        metrics = collector.get_metric("trade.BTC/USD.sell")
        assert len(metrics) == 1
        
        trade_data = list(metrics.values())[0]
        assert trade_data["trade_id"] == "456"
        assert trade_data["symbol"] == "BTC/USD"
        assert trade_data["side"] == "sell"
        assert trade_data["quantity"] == 0.5
        assert trade_data["price"] == 51000.0
        assert trade_data["fee"] == 25.5
        
        # Check that the trade count metrics were recorded
        assert collector.get_latest("trade_count.BTC/USD.sell") == 1
        assert collector.get_latest("trade_volume.BTC/USD.sell") == 0.5
        assert collector.get_latest("trade_value.BTC/USD.sell") == 25500.0
        assert collector.get_latest("trade_fee.BTC/USD") == 25.5
    
    def test_record_portfolio_value(self):
        """Test recording portfolio value."""
        collector = TradingMetricsCollector()
        
        # Record portfolio value
        collector.record_portfolio_value(100000.0)
        
        # Check that the portfolio value was recorded
        assert collector.get_latest("portfolio.value") == 100000.0
    
    def test_record_position(self):
        """Test recording a position."""
        collector = TradingMetricsCollector()
        
        # Record a position
        collector.record_position(
            symbol="BTC/USD",
            quantity=2.0,
            entry_price=48000.0,
            current_price=50000.0
        )
        
        # Check that the position was recorded
        metrics = collector.get_metric("position.BTC/USD")
        assert len(metrics) == 1
        
        position_data = list(metrics.values())[0]
        assert position_data["symbol"] == "BTC/USD"
        assert position_data["quantity"] == 2.0
        assert position_data["entry_price"] == 48000.0
        assert position_data["current_price"] == 50000.0
        assert position_data["position_value"] == 100000.0
        assert position_data["unrealized_pnl"] == 4000.0
        assert position_data["unrealized_pnl_percent"] == 4.166666666666666
    
    def test_get_trading_summary(self):
        """Test getting a trading summary."""
        collector = TradingMetricsCollector()
        
        # Record some trading activity
        collector.record_order("1", "BTC/USD", "buy", "market", 1.0, 50000.0)
        collector.record_order("2", "BTC/USD", "sell", "market", 0.5, 51000.0)
        collector.record_order("3", "ETH/USD", "buy", "market", 10.0, 3000.0)
        
        collector.record_trade("1", "BTC/USD", "buy", 1.0, 50000.0, 50.0)
        collector.record_trade("2", "BTC/USD", "sell", 0.5, 51000.0, 25.5)
        collector.record_trade("3", "ETH/USD", "buy", 10.0, 3000.0, 30.0)
        
        # Get a summary for a specific symbol
        summary = collector.get_trading_summary("BTC/USD")
        
        # Check the summary values
        assert summary["order_count_buy"] == 1
        assert summary["order_count_sell"] == 1
        assert summary["order_count"] == 2
        assert summary["order_volume_buy"] == 1.0
        assert summary["order_volume_sell"] == 0.5
        assert summary["order_volume"] == 1.5
        assert summary["order_value_buy"] == 50000.0
        assert summary["order_value_sell"] == 25500.0
        assert summary["order_value"] == 75500.0
        assert summary["trade_count_buy"] == 1
        assert summary["trade_count_sell"] == 1
        assert summary["trade_count"] == 2
        assert summary["trade_volume_buy"] == 1.0
        assert summary["trade_volume_sell"] == 0.5
        assert summary["trade_volume"] == 1.5
        assert summary["trade_value_buy"] == 50000.0
        assert summary["trade_value_sell"] == 25500.0
        assert summary["trade_value"] == 75500.0
        assert summary["fee"] == 75.5
        
        # Get a summary for all symbols
        summary = collector.get_trading_summary()
        
        # Check the summary values
        assert summary["order_count"] == 3
        assert summary["trade_count"] == 3
        assert summary["trade_value"] == 105500.0


# Skip the SystemMetricsCollector tests if psutil is not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
class TestSystemMetricsCollector:
    """Tests for the SystemMetricsCollector class."""
    
    def test_collect_system_metrics(self):
        """Test collecting system metrics."""
        collector = SystemMetricsCollector()
        
        # Collect metrics once using the single_run parameter
        collector.collect_system_metrics(interval=0.1, single_run=True)
        
        # Check that CPU metrics were recorded
        cpu_metrics = collector.get_metric("system.cpu.percent")
        assert len(cpu_metrics) >= 1
        
        # Check that memory metrics were recorded
        memory_metrics = collector.get_metric("system.memory.total")
        assert len(memory_metrics) >= 1
        
        # Check that disk metrics were recorded
        disk_metrics = collector.get_metric("system.disk.total")
        assert len(disk_metrics) >= 1
        
        # Check that network metrics were recorded
        network_metrics = collector.get_metric("system.network.bytes_sent")
        assert len(network_metrics) >= 1
    
    def test_start_stop_collection(self):
        """Test starting and stopping metric collection."""
        collector = SystemMetricsCollector()
        
        # Start collection with a short interval
        collector.start_collection(interval=0.1)
        
        # Wait for some metrics to be collected
        time.sleep(0.3)
        
        # Stop collection
        collector.stop_collection()
        
        # Check that metrics were collected
        cpu_metrics = collector.get_metric("system.cpu.percent")
        assert len(cpu_metrics) >= 1
        
        # Clear metrics
        collector.clear()
        
        # Check that metrics were cleared
        cpu_metrics = collector.get_metric("system.cpu.percent")
        assert len(cpu_metrics) == 0
        
        # Start collection again
        collector.start_collection(interval=0.1)
        
        # Wait for some metrics to be collected
        time.sleep(0.3)
        
        # Stop collection
        collector.stop_collection()
        
        # Check that new metrics were collected
        cpu_metrics = collector.get_metric("system.cpu.percent")
        assert len(cpu_metrics) >= 1 