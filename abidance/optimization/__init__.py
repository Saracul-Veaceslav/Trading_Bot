"""
Strategy optimization framework for the Abidance trading bot.

This package provides tools for optimizing trading strategy parameters
through backtesting and performance evaluation.
"""

from .optimizer import StrategyOptimizer, OptimizationResult
from .metrics import calculate_sharpe_ratio, calculate_sortino_ratio, calculate_max_drawdown

__all__ = [
    'StrategyOptimizer',
    'OptimizationResult',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'calculate_max_drawdown',
]