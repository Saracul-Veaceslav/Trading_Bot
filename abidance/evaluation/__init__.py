"""
Evaluation module for trading strategy performance analysis.

This module provides tools for calculating performance metrics and generating reports
for trading strategies.
"""

from abidance.evaluation.metrics import PerformanceMetrics, StrategyEvaluator
from abidance.evaluation.reporting import PerformanceReport

__all__ = [
    'PerformanceMetrics',
    'StrategyEvaluator',
    'PerformanceReport',
]