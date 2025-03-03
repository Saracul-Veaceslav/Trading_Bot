"""
Performance testing framework for trading strategies.

This module provides tools for measuring and benchmarking the performance
of trading strategies, including execution time, memory usage, and parallel
execution capabilities.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Type
import os
import time


import numpy as np
import pandas as pd
import psutil  # Import psutil at the top level

from abidance.strategy.base import Strategy, StrategyConfig
from abidance.evaluation.metrics import StrategyEvaluator


class PerformanceTester:
    """Framework for testing strategy performance."""

    def __init__(self, strategy_class: Type[Strategy],
                 data: pd.DataFrame,
                 evaluator: Optional[StrategyEvaluator] = None):
        """
        Initialize the performance tester.

        Args:
            strategy_class: The strategy class to tes
            data: Market data as a pandas DataFrame
            evaluator: Optional strategy evaluator for performance metrics
        """
        self.strategy_class = strategy_class
        self.data = data
        self.evaluator = evaluator or StrategyEvaluator()

    def measure_execution_time(self, num_runs: int = 100,
                             **strategy_params) -> Dict[str, float]:
        """
        Measure strategy execution time statistics.

        Args:
            num_runs: Number of times to run the strategy
            **strategy_params: Parameters to pass to the strategy constructor

        Returns:
            Dictionary with execution time statistics (mean, median, std, min, max)
        """
        strategy = self._create_strategy(**strategy_params)
        execution_times = []

        for _ in range(num_runs):
            start_time = time.perf_counter()
            strategy.calculate_signal(self.data)
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)

        return {
            'mean': np.mean(execution_times),
            'median': np.median(execution_times),
            'std': np.std(execution_times),
            'min': np.min(execution_times),
            'max': np.max(execution_times)
        }

    def measure_memory_usage(self, **strategy_params) -> Dict[str, float]:
        """
        Measure strategy memory usage.

        Args:
            **strategy_params: Parameters to pass to the strategy constructor

        Returns:
            Dictionary with memory usage statistics (initial_mb, final_mb, delta_mb)
        """
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        strategy = self._create_strategy(**strategy_params)
        strategy.calculate_signal(self.data)

        final_memory = process.memory_info().rss

        return {
            'initial_mb': initial_memory / (1024 * 1024),
            'final_mb': final_memory / (1024 * 1024),
            'delta_mb': (final_memory - initial_memory) / (1024 * 1024)
        }

    def benchmark_parallel_execution(self, num_strategies: int = 10,
                                  **strategy_params) -> Dict[str, float]:
        """
        Benchmark parallel strategy execution.

        Args:
            num_strategies: Number of strategy instances to run in parallel
            **strategy_params: Parameters to pass to the strategy constructor

        Returns:
            Dictionary with parallel execution statistics (total_time, avg_time_per_strategy)
        """
        strategies = [
            self._create_strategy(**strategy_params)
            for _ in range(num_strategies)
        ]

        start_time = time.perf_counter()
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(strategy.calculate_signal, self.data)
                for strategy in strategies
            ]
            # We need to consume the results to ensure all futures complete
            _ = [future.result() for future in futures]
        end_time = time.perf_counter()

        return {
            'total_time': end_time - start_time,
            'avg_time_per_strategy': (end_time - start_time) / num_strategies
        }

    def _create_strategy(self, **strategy_params) -> Strategy:
        """
        Create a strategy instance with the given parameters.

        Args:
            **strategy_params: Parameters to pass to the strategy constructor

        Returns:
            Strategy instance
        """
        # Create a default config if none is provided in strategy_params
        if 'config' not in strategy_params:
            config = StrategyConfig(
                name=f"perf_test_{self.strategy_class.__name__}",
                symbols=["BTC/USDT"],  # Default symbol
                timeframe="1h",        # Default timeframe
                parameters=strategy_params.get('parameters', {})
            )
            strategy_params['config'] = config

        return self.strategy_class(**strategy_params)
