"""
Benchmarking utilities for trading strategies.

This module provides tools for benchmarking trading strategies agains
standard datasets and comparing performance across different strategies.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Type, Any, Optional
import json


import pandas as pd
# Import matplotlib conditionally to avoid dependency for users who don't need plotting
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from abidance.strategy.base import Strategy
from abidance.evaluation.metrics import StrategyEvaluator
from abidance.testing.performance import PerformanceTester


class StrategyBenchmark:
    """Benchmark for comparing multiple trading strategies."""

    def __init__(self, data: pd.DataFrame,
                 evaluator: Optional[StrategyEvaluator] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize the strategy benchmark.

        Args:
            data: Market data as a pandas DataFrame
            evaluator: Optional strategy evaluator for performance metrics
            output_dir: Directory to save benchmark results
        """
        self.data = data
        self.evaluator = evaluator or StrategyEvaluator()
        self.output_dir = Path(output_dir) if output_dir else Path("benchmark_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: Dict[str, Dict[str, Any]] = {}

    def add_strategy(self, strategy_class: Type[Strategy],
                   name: Optional[str] = None,
                   **strategy_params) -> None:
        """
        Add a strategy to the benchmark.

        Args:
            strategy_class: The strategy class to benchmark
            name: Optional name for the strategy (defaults to class name)
            **strategy_params: Parameters to pass to the strategy constructor
        """
        strategy_name = name or strategy_class.__name__
        tester = PerformanceTester(strategy_class, self.data, self.evaluator)

        # Measure performance metrics
        execution_time = tester.measure_execution_time(num_runs=10, **strategy_params)
        memory_usage = tester.measure_memory_usage(**strategy_params)
        parallel_exec = tester.benchmark_parallel_execution(num_strategies=5, **strategy_params)

        # Store results
        self.results[strategy_name] = {
            "execution_time": execution_time,
            "memory_usage": memory_usage,
            "parallel_execution": parallel_exec,
            "parameters": strategy_params,
            "timestamp": datetime.now().isoformat()
        }

    def run_all(self, strategies: List[Dict[str, Any]]) -> None:
        """
        Run benchmark for multiple strategies.

        Args:
            strategies: List of dictionaries with keys:
                - 'class': Strategy class
                - 'name': Optional name
                - 'params': Strategy parameters
        """
        for strategy_info in strategies:
            strategy_class = strategy_info["class"]
            name = strategy_info.get("name")
            params = strategy_info.get("params", {})

            self.add_strategy(strategy_class, name, **params)

    def save_results(self, filename: Optional[str] = None) -> str:
        """
        Save benchmark results to a JSON file.

        Args:
            filename: Optional filename (defaults to timestamp)

        Returns:
            Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"

        file_path = self.output_dir / filename

        # Convert results to serializable forma
        serializable_results = {}
        for strategy_name, result in self.results.items():
            serializable_results[strategy_name] = {
                key: (value if isinstance(value, (dict, str, int, float, bool))
                     else str(value))
                for key, value in result.items()
            }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2)

        return str(file_path)

    def compare_strategies(self) -> pd.DataFrame:
        """
        Compare strategies based on key performance metrics.

        Returns:
            DataFrame with comparison results
        """
        comparison_data = []

        for strategy_name, result in self.results.items():
            comparison_data.append({
                "strategy": strategy_name,
                "mean_execution_time": result["execution_time"]["mean"],
                "memory_usage_mb": result["memory_usage"]["delta_mb"],
                "parallel_speedup": (
                    result["execution_time"]["mean"] * 5 /
                    result["parallel_execution"]["total_time"]
                )
            })

        return pd.DataFrame(comparison_data)

    def plot_comparison(self, metric: str = "mean_execution_time",
                      save_path: Optional[str] = None) -> None:
        """
        Plot comparison of strategies for a specific metric.

        Args:
            metric: Metric to compare ('mean_execution_time', 'memory_usage_mb', 'parallel_speedup')
            save_path: Optional path to save the plo
        """
        if plt is None:
            print("Matplotlib is required for plotting. Install with: pip install matplotlib")
            return

        comparison_df = self.compare_strategies()

        plt.figure(figsize=(10, 6))
        comparison_df.plot(
            kind='bar',
            x='strategy',
            y=metric,
            legend=False
        )

        plt.title(f"Strategy Comparison: {metric}")
        plt.ylabel(metric)
        plt.xlabel("Strategy")
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
