"""
Strategy module for implementing trading strategies.

This module provides the framework for creating, testing, and executing
trading strategies based on market data and signals.
"""

# Import key classes to make them available at the module level
from .base import Strategy, StrategyConfig
from .registry import StrategyRegistry
from .sma import SMAStrategy, SMAConfig
from .rsi import RSIStrategy, RSIConfig
from .indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_macd,
    detect_crossover
)

# Define what's available when doing "from abidance.strategy import *"
__all__ = [
    # Base classes
    "Strategy",
    "StrategyConfig",
    
    # Registry
    "StrategyRegistry",
    
    # Strategy implementations
    "SMAStrategy",
    "SMAConfig",
    "RSIStrategy",
    "RSIConfig",
    
    # Indicators
    "calculate_sma",
    "calculate_ema",
    "calculate_rsi",
    "calculate_bollinger_bands",
    "calculate_macd",
    "detect_crossover",
] 