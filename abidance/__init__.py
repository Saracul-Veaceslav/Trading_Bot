"""
Abidance - A comprehensive cryptocurrency trading bot framework.

This package provides tools and infrastructure for building, testing,
and running cryptocurrency trading strategies across multiple exchanges.
"""

__version__ = "0.1.0"

# Import key modules to make them available at the package level
from . import trading
from . import exchange
from . import strategy
from . import data
from . import ml
from . import api
from . import core
from . import utils
from . import exceptions
from . import type_defs

# Import commonly used classes for easier access
from .trading import Order, Trade, Position, TradingEngine
from .exchange import Exchange, ExchangeManager
from .strategy import Strategy, StrategyRegistry
from .data import DataManager

# Define what's available when doing "from abidance import *"
__all__ = [
    "trading",
    "exchange",
    "strategy",
    "data",
    "ml",
    "api",
    "core",
    "utils",
    "exceptions",
    "type_defs",
    "Order",
    "Trade",
    "Position",
    "TradingEngine",
    "Exchange",
    "ExchangeManager",
    "Strategy",
    "StrategyRegistry",
    "DataManager",
] 