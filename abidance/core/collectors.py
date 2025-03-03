"""
Specialized metric collectors for the Abidance trading bot.

This module provides specialized metric collectors for different aspects
of the application, such as performance, trading, and system metrics.
"""

from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
import time
import threading
import psutil
import os
from functools import wraps

from .metrics import MetricsCollector, AggregationType


class PerformanceMetricsCollector(MetricsCollector):
    """
    Collector for performance-related metrics.

    This collector specializes in tracking execution time, memory usage,
    and other performance-related metrics.
    """

    def __init__(self):
        """Initialize the performance metrics collector."""
        super().__init__()
        self._timers: Dict[str, float] = {}

    def start_timer(self, timer_name: str) -> None:
        """
        Start a timer for measuring execution time.

        Args:
            timer_name: The name of the timer
        """
        self._timers[timer_name] = time.time()

    def stop_timer(self, timer_name: str) -> float:
        """
        Stop a timer and record the elapsed time.

        Args:
            timer_name: The name of the timer

        Returns:
            The elapsed time in seconds

        Raises:
            KeyError: If the timer was not started
        """
        if timer_name not in self._timers:
            raise KeyError(f"Timer '{timer_name}' was not started")

        elapsed = time.time() - self._timers[timer_name]
        self.record(f"timer.{timer_name}", elapsed)
        del self._timers[timer_name]
        return elapsed

    def record_memory_usage(self, label: str = "memory") -> float:
        """
        Record the current memory usage of the process.

        Args:
            label: Label to use for the metric

        Returns:
            The memory usage in bytes
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_usage = memory_info.rss  # Resident Set Size in bytes
        self.record(f"{label}.rss", memory_usage)
        return memory_usage

    def record_cpu_usage(self, label: str = "cpu") -> float:
        """
        Record the current CPU usage of the process.

        Args:
            label: Label to use for the metric

        Returns:
            The CPU usage as a percentage
        """
        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent(interval=0.1)
        self.record(f"{label}.percent", cpu_percent)
        return cpu_percent

    def time_function(self, func_name: Optional[str] = None):
        """
        Decorator to time a function's execution.

        Args:
            func_name: Optional name for the timer. If not provided,
                      the function's name will be used.

        Returns:
            A decorator function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                timer_name = func_name or func.__name__
                self.start_timer(timer_name)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    self.stop_timer(timer_name)
            return wrapper
        return decorator


class TradingMetricsCollector(MetricsCollector):
    """
    Collector for trading-related metrics.

    This collector specializes in tracking trading activity, such as
    orders, trades, and portfolio performance.
    """

    def record_order(self, order_id: str, symbol: str, side: str,
                    order_type: str, quantity: float, price: float) -> None:
        """
        Record an order.

        Args:
            order_id: The ID of the order
            symbol: The trading symbol
            side: The order side (buy/sell)
            order_type: The order type (market/limit/etc.)
            quantity: The order quantity
            price: The order price
        """
        self.record(f"order.{symbol}.{side}", {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "price": price,
            "timestamp": datetime.now()
        })

        # Also record order count metrics
        self.record(f"order_count.{symbol}.{side}", 1)
        self.record(f"order_volume.{symbol}.{side}", quantity)
        self.record(f"order_value.{symbol}.{side}", quantity * price)

    def record_trade(self, trade_id: str, symbol: str, side: str,
                    quantity: float, price: float, fee: float) -> None:
        """
        Record a trade.

        Args:
            trade_id: The ID of the trade
            symbol: The trading symbol
            side: The trade side (buy/sell)
            quantity: The trade quantity
            price: The trade price
            fee: The trade fee
        """
        self.record(f"trade.{symbol}.{side}", {
            "trade_id": trade_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "fee": fee,
            "timestamp": datetime.now()
        })

        # Also record trade count metrics
        self.record(f"trade_count.{symbol}.{side}", 1)
        self.record(f"trade_volume.{symbol}.{side}", quantity)
        self.record(f"trade_value.{symbol}.{side}", quantity * price)
        self.record(f"trade_fee.{symbol}", fee)

    def record_portfolio_value(self, portfolio_value: float) -> None:
        """
        Record the current portfolio value.

        Args:
            portfolio_value: The total value of the portfolio
        """
        self.record("portfolio.value", portfolio_value)

    def record_position(self, symbol: str, quantity: float,
                       entry_price: float, current_price: float) -> None:
        """
        Record a position.

        Args:
            symbol: The trading symbol
            quantity: The position quantity
            entry_price: The average entry price
            current_price: The current market price
        """
        position_value = quantity * current_price
        unrealized_pnl = quantity * (current_price - entry_price)
        unrealized_pnl_percent = (unrealized_pnl / (quantity * entry_price)) * 100 if quantity * entry_price != 0 else 0

        self.record(f"position.{symbol}", {
            "symbol": symbol,
            "quantity": quantity,
            "entry_price": entry_price,
            "current_price": current_price,
            "position_value": position_value,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_percent": unrealized_pnl_percent,
            "timestamp": datetime.now()
        })

    def get_trading_summary(self, symbol: Optional[str] = None, since: Optional[datetime] = None, until: Optional[datetime] = None) -> Dict[str, float]:
        """
        Get a summary of trading metrics.

        Args:
            symbol: Optional symbol to filter by
            since: Optional start time for filtering
            until: Optional end time for filtering

        Returns:
            Dictionary with trading metrics summary
        """
        summary = {
            "order_count_buy": 0,
            "order_count_sell": 0,
            "order_count": 0,
            "order_volume_buy": 0.0,
            "order_volume_sell": 0.0,
            "order_volume": 0.0,
            "order_value_buy": 0.0,
            "order_value_sell": 0.0,
            "order_value": 0.0,
            "trade_count_buy": 0,
            "trade_count_sell": 0,
            "trade_count": 0,
            "trade_volume_buy": 0.0,
            "trade_volume_sell": 0.0,
            "trade_volume": 0.0,
            "trade_value_buy": 0.0,
            "trade_value_sell": 0.0,
            "trade_value": 0.0,
            "fee": 0.0
        }

        if symbol:
            self._process_symbol_metrics(summary, symbol, since, until)
        else:
            self._process_all_symbols_metrics(summary, since, until)

        return summary

    def _process_symbol_metrics(self, summary: Dict[str, float], symbol: str, since: Optional[datetime], until: Optional[datetime]) -> None:
        """
        Process metrics for a specific symbol.
        
        Args:
            summary: Dictionary to update with metrics
            symbol: Symbol to process metrics for
            since: Optional start time for filtering
            until: Optional end time for filtering
        """
        symbol_part = f".{symbol}"
        
        # Process order metrics
        self._update_metric_sum(summary, "order_count_buy", f"order_count{symbol_part}.buy", since, until)
        self._update_metric_sum(summary, "order_count_sell", f"order_count{symbol_part}.sell", since, until)
        summary["order_count"] = summary["order_count_buy"] + summary["order_count_sell"]
        
        self._update_metric_sum(summary, "order_volume_buy", f"order_volume{symbol_part}.buy", since, until)
        self._update_metric_sum(summary, "order_volume_sell", f"order_volume{symbol_part}.sell", since, until)
        summary["order_volume"] = summary["order_volume_buy"] + summary["order_volume_sell"]
        
        self._update_metric_sum(summary, "order_value_buy", f"order_value{symbol_part}.buy", since, until)
        self._update_metric_sum(summary, "order_value_sell", f"order_value{symbol_part}.sell", since, until)
        summary["order_value"] = summary["order_value_buy"] + summary["order_value_sell"]
        
        # Process trade metrics
        self._update_metric_sum(summary, "trade_count_buy", f"trade_count{symbol_part}.buy", since, until)
        self._update_metric_sum(summary, "trade_count_sell", f"trade_count{symbol_part}.sell", since, until)
        summary["trade_count"] = summary["trade_count_buy"] + summary["trade_count_sell"]
        
        self._update_metric_sum(summary, "trade_volume_buy", f"trade_volume{symbol_part}.buy", since, until)
        self._update_metric_sum(summary, "trade_volume_sell", f"trade_volume{symbol_part}.sell", since, until)
        summary["trade_volume"] = summary["trade_volume_buy"] + summary["trade_volume_sell"]
        
        self._update_metric_sum(summary, "trade_value_buy", f"trade_value{symbol_part}.buy", since, until)
        self._update_metric_sum(summary, "trade_value_sell", f"trade_value{symbol_part}.sell", since, until)
        summary["trade_value"] = summary["trade_value_buy"] + summary["trade_value_sell"]
        
        # Calculate total fee
        self._update_metric_sum(summary, "fee", f"trade_fee{symbol_part}", since, until)
    
    def _update_metric_sum(self, summary: Dict[str, float], summary_key: str, metric_name: str, 
                          since: Optional[datetime], until: Optional[datetime]) -> None:
        """
        Update a summary value with the sum of a metric's values.
        
        Args:
            summary: Dictionary to update
            summary_key: Key in the summary dictionary to update
            metric_name: Name of the metric to sum
            since: Optional start time for filtering
            until: Optional end time for filtering
        """
        values = self.get_metric(metric_name, since, until)
        if values:
            summary[summary_key] = sum(values.values())
    
    def _process_all_symbols_metrics(self, summary: Dict[str, float], since: Optional[datetime], until: Optional[datetime]) -> None:
        """
        Process metrics for all symbols.
        
        Args:
            summary: Dictionary to update with metrics
            since: Optional start time for filtering
            until: Optional end time for filtering
        """
        # Find all metrics that match our patterns
        for metric_name in list(self._metrics.keys()):
            parts = metric_name.split(".")
            
            # Process order metrics
            if metric_name.startswith("order_count.") and len(parts) >= 3:
                self._process_metric_by_side(summary, metric_name, parts, "order_count", since, until)
            elif metric_name.startswith("order_volume.") and len(parts) >= 3:
                self._process_metric_by_side(summary, metric_name, parts, "order_volume", since, until)
            elif metric_name.startswith("order_value.") and len(parts) >= 3:
                self._process_metric_by_side(summary, metric_name, parts, "order_value", since, until)
            
            # Process trade metrics
            elif metric_name.startswith("trade_count.") and len(parts) >= 3:
                self._process_metric_by_side(summary, metric_name, parts, "trade_count", since, until)
            elif metric_name.startswith("trade_volume.") and len(parts) >= 3:
                self._process_metric_by_side(summary, metric_name, parts, "trade_volume", since, until)
            elif metric_name.startswith("trade_value.") and len(parts) >= 3:
                self._process_metric_by_side(summary, metric_name, parts, "trade_value", since, until)
            elif metric_name.startswith("trade_fee."):
                values = self.get_metric(metric_name, since, until)
                if values:
                    summary["fee"] += sum(values.values())
        
        # Calculate totals
        summary["order_count"] = summary["order_count_buy"] + summary["order_count_sell"]
        summary["order_volume"] = summary["order_volume_buy"] + summary["order_volume_sell"]
        summary["order_value"] = summary["order_value_buy"] + summary["order_value_sell"]
        summary["trade_count"] = summary["trade_count_buy"] + summary["trade_count_sell"]
        summary["trade_volume"] = summary["trade_volume_buy"] + summary["trade_volume_sell"]
        summary["trade_value"] = summary["trade_value_buy"] + summary["trade_value_sell"]
    
    def _process_metric_by_side(self, summary: Dict[str, float], metric_name: str, parts: List[str], 
                               metric_type: str, since: Optional[datetime], until: Optional[datetime]) -> None:
        """
        Process a metric by its side (buy/sell).
        
        Args:
            summary: Dictionary to update
            metric_name: Name of the metric
            parts: Split parts of the metric name
            metric_type: Type of metric (order_count, trade_volume, etc.)
            since: Optional start time for filtering
            until: Optional end time for filtering
        """
        if parts[-1] in ["buy", "sell"]:
            side = parts[-1]
            values = self.get_metric(metric_name, since, until)
            if values:
                summary_key = f"{metric_type}_{side}"
                summary[summary_key] += sum(values.values())


class SystemMetricsCollector(MetricsCollector):
    """
    Collector for system-related metrics.

    This collector specializes in tracking system metrics such as
    CPU usage, memory usage, disk I/O, and network activity.
    """

    def __init__(self):
        """Initialize the system metrics collector."""
        super().__init__()
        self._collection_thread = None
        self._stop_collection = threading.Event()

    def collect_system_metrics(self, interval: float = 60.0, single_run: bool = False) -> None:
        """
        Collect system metrics at regular intervals.

        Args:
            interval: The collection interval in seconds
            single_run: If True, collect metrics once and return (for testing)
        """
        while not self._stop_collection.is_set():
            # Collect CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.record("system.cpu.percent", cpu_percent)

            # Collect memory metrics
            memory = psutil.virtual_memory()
            self.record("system.memory.total", memory.total)
            self.record("system.memory.available", memory.available)
            self.record("system.memory.used", memory.used)
            self.record("system.memory.percent", memory.percent)

            # Collect disk metrics
            disk = psutil.disk_usage('/')
            self.record("system.disk.total", disk.total)
            self.record("system.disk.used", disk.used)
            self.record("system.disk.free", disk.free)
            self.record("system.disk.percent", disk.percent)

            # Collect network metrics
            net_io = psutil.net_io_counters()
            self.record("system.network.bytes_sent", net_io.bytes_sent)
            self.record("system.network.bytes_recv", net_io.bytes_recv)
            self.record("system.network.packets_sent", net_io.packets_sent)
            self.record("system.network.packets_recv", net_io.packets_recv)

            # If single_run is True, break after one collection
            if single_run:
                break

            # Wait for the next collection interval
            self._stop_collection.wait(interval)

    def start_collection(self, interval: float = 60.0) -> None:
        """
        Start collecting system metrics in a background thread.

        Args:
            interval: The collection interval in seconds
        """
        if self._collection_thread and self._collection_thread.is_alive():
            return

        self._stop_collection.clear()
        self._collection_thread = threading.Thread(
            target=self.collect_system_metrics,
            args=(interval,),
            daemon=True
        )
        self._collection_thread.start()

    def stop_collection(self) -> None:
        """Stop collecting system metrics."""
        if self._collection_thread and self._collection_thread.is_alive():
            self._stop_collection.set()
            self._collection_thread.join(timeout=1.0)
            self._collection_thread = None