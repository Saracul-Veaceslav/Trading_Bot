"""
Exchange module for interfacing with cryptocurrency exchanges.

This module provides standardized interfaces for connecting to and 
interacting with various cryptocurrency exchanges.
"""

# Import key classes to make them available at the module level
from .base import Exchange as ExchangeBase
from .manager import ExchangeManager
from .binance import BinanceExchange
from .protocols import Exchange, ExchangeFactory

# Define what's available when doing "from abidance.exchange import *"
__all__ = [
    "Exchange",  # Protocol
    "ExchangeBase",  # Abstract base class
    "ExchangeFactory",  # Protocol
    "ExchangeManager",
    "BinanceExchange",
] 