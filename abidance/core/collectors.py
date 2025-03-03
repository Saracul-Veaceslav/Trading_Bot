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
        Get a summary of trading activity.

        Args:
            symbol: Optional symbol to filter by
            since: Optional start time for filtering
            until: Optional end time for filtering

        Returns:
            Dictionary with trading summary metrics
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
            # For a specific symbol
            symbol_part = f".{symbol}"

            # Process order metrics
            buy_order_count = self.get_metric(f"order_count{symbol_part}.buy", since, until)
            if buy_order_count:
                summary["order_count_buy"] = sum(buy_order_count.values())

            sell_order_count = self.get_metric(f"order_count{symbol_part}.sell", since, until)
            if sell_order_count:
                summary["order_count_sell"] = sum(sell_order_count.values())

            summary["order_count"] = summary["order_count_buy"] + summary["order_count_sell"]

            buy_volume = self.get_metric(f"order_volume{symbol_part}.buy", since, until)
            if buy_volume:
                summary["order_volume_buy"] = sum(buy_volume.values())

            sell_volume = self.get_metric(f"order_volume{symbol_part}.sell", since, until)
            if sell_volume:
                summary["order_volume_sell"] = sum(sell_volume.values())

            summary["order_volume"] = summary["order_volume_buy"] + summary["order_volume_sell"]

            buy_value = self.get_metric(f"order_value{symbol_part}.buy", since, until)
            if buy_value:
                summary["order_value_buy"] = sum(buy_value.values())

            sell_value = self.get_metric(f"order_value{symbol_part}.sell", since, until)
            if sell_value:
                summary["order_value_sell"] = sum(sell_value.values())

            summary["order_value"] = summary["order_value_buy"] + summary["order_value_sell"]

            # Process trade metrics
            buy_trades = self.get_metric(f"trade_count{symbol_part}.buy", since, until)
            if buy_trades:
                summary["trade_count_buy"] = sum(buy_trades.values())

            sell_trades = self.get_metric(f"trade_count{symbol_part}.sell", since, until)
            if sell_trades:
                summary["trade_count_sell"] = sum(sell_trades.values())

            summary["trade_count"] = summary["trade_count_buy"] + summary["trade_count_sell"]

            buy_trade_volume = self.get_metric(f"trade_volume{symbol_part}.buy", since, until)
            if buy_trade_volume:
                summary["trade_volume_buy"] = sum(buy_trade_volume.values())

            sell_trade_volume = self.get_metric(f"trade_volume{symbol_part}.sell", since, until)
            if sell_trade_volume:
                summary["trade_volume_sell"] = sum(sell_trade_volume.values())

            summary["trade_volume"] = summary["trade_volume_buy"] + summary["trade_volume_sell"]

            buy_trade_value = self.get_metric(f"trade_value{symbol_part}.buy", since, until)
            if buy_trade_value:
                summary["trade_value_buy"] = sum(buy_trade_value.values())

            sell_trade_value = self.get_metric(f"trade_value{symbol_part}.sell", since, until)
            if sell_trade_value:
                summary["trade_value_sell"] = sum(sell_trade_value.values())

            summary["trade_value"] = summary["trade_value_buy"] + summary["trade_value_sell"]

            # Calculate total fee
            fee = self.get_metric(f"trade_fee{symbol_part}", since, until)
            if fee:
                summary["fee"] = sum(fee.values())
        else:
            # For all symbols, aggregate metrics across all symbols
            # Find all metrics that match our patterns
            for metric_name in list(self._metrics.keys()):
                # Process order metrics
                if metric_name.startswith("order_count."):
                    parts = metric_name.split(".")
                    if len(parts) >= 3 and parts[-1] in ["buy", "sell"]:
                        side = parts[-1]
                        values = self.get_metric(metric_name, since, until)
                        if values:
                            if side == "buy":
                                summary["order_count_buy"] += sum(values.values())
                            elif side == "sell":
                                summary["order_count_sell"] += sum(values.values())

                elif metric_name.startswith("order_volume."):
                    parts = metric_name.split(".")
                    if len(parts) >= 3 and parts[-1] in ["buy", "sell"]:
                        side = parts[-1]
                        values = self.get_metric(metric_name, since, until)
                        if values:
                            if side == "buy":
                                summary["order_volume_buy"] += sum(values.values())
                            elif side == "sell":
                                summary["order_volume_sell"] += sum(values.values())

                elif metric_name.startswith("order_value."):
                    parts = metric_name.split(".")
                    if len(parts) >= 3 and parts[-1] in ["buy", "sell"]:
                        side = parts[-1]
                        values = self.get_metric(metric_name, since, until)
                        if values:
                            if side == "buy":
                                summary["order_value_buy"] += sum(values.values())
                            elif side == "sell":
                                summary["order_value_sell"] += sum(values.values())

                # Process trade metrics
                elif metric_name.startswith("trade_count."):
                    parts = metric_name.split(".")
                    if len(parts) >= 3 and parts[-1] in ["buy", "sell"]:
                        side = parts[-1]
                        values = self.get_metric(metric_name, since, until)
                        if values:
                            if side == "buy":
                                summary["trade_count_buy"] += sum(values.values())
                            elif side == "sell":
                                summary["trade_count_sell"] += sum(values.values())

                elif metric_name.startswith("trade_volume."):
                    parts = metric_name.split(".")
                    if len(parts) >= 3 and parts[-1] in ["buy", "sell"]:
                        side = parts[-1]
                        values = self.get_metric(metric_name, since, until)
                        if values:
                            if side == "buy":
                                summary["trade_volume_buy"] += sum(values.values())
                            elif side == "sell":
                                summary["trade_volume_sell"] += sum(values.values())

                elif metric_name.startswith("trade_value."):
                    parts = metric_name.split(".")
                    if len(parts) >= 3 and parts[-1] in ["buy", "sell"]:
                        side = parts[-1]
                        values = self.get_metric(metric_name, since, until)
                        if values:
                            if side == "buy":
                                summary["trade_value_buy"] += sum(values.values())
                            elif side == "sell":
                                summary["trade_value_sell"] += sum(values.values())

                # Process fee metrics
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

        return summary


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