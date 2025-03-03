"""
Trading module for executing orders and managing positions.

This module handles the core trading operations, including order creation,
trade execution, and position management.
"""

# Import key classes to make them available at the module level
from .order import Order, OrderSide, OrderType

from .trade import Trade
from .position import Position
from .engine import TradingEngine

# Define what's available when doing "from abidance.trading import *"
__all__ = [
    "Order",
    "OrderSide",
    "OrderType",
    "Trade",
    "Position",
    "TradingEngine",
]
