"""
Exchange module for interfacing with cryptocurrency exchanges.

This module provides standardized interfaces for connecting to and 
interacting with various cryptocurrency exchanges.
"""

# Import key classes to make them available at the module level
from .base import Exchange
from .manager import ExchangeManager
from .binance import BinanceExchange

# Define what's available when doing "from abidance.exchange import *"
__all__ = [
    "Exchange",
    "ExchangeManager",
    "BinanceExchange",
] 