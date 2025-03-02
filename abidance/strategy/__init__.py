"""
Strategy module for implementing trading strategies.

This module provides the framework for creating, testing, and executing
trading strategies based on market data and signals.
"""

# Import key classes to make them available at the module level
from .base import Strategy
from .registry import StrategyRegistry
from .sma import SMAStrategy
from .rsi import RSIStrategy

# Define what's available when doing "from abidance.strategy import *"
__all__ = [
    "Strategy",
    "StrategyRegistry",
    "SMAStrategy",
    "RSIStrategy",
] 