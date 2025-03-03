"""
Core domain entities for the Abidance trading bot.

This module defines the core domain entities used throughout the application,
including order types, positions, signals, and market data structures.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Union

from dataclasses import dataclass


# Import trading domain entities from trading module
from abidance.trading.order import OrderSide, OrderType
from abidance.trading.position import Position as TradingPosition
from abidance.trading.order import Order as TradingOrder
from abidance.trading.trade import Trade as TradingTrade


class SignalType(Enum):
    """Enum representing the type of a trading signal."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    """
    Represents a trading signal.

    A signal is a recommendation to buy, sell, or hold an asset.
    """
    symbol: str
    signal_type: SignalType
    price: float
    timestamp: datetime
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Candle:
    """
    Represents a price candle.

    A candle represents price movement over a specific time period.
    """
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


# Adapter classes to maintain backward compatibility with tests
@dataclass
class Position:
    """
    Adapter for TradingPosition that matches the expected interface in tests.
    """
    symbol: str
    side: OrderSide
    entry_price: float
    size: float
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_id: Optional[str] = None

    def __post_init__(self):
        """Convert to TradingPosition if needed."""
        # This adapter could be expanded to convert between the two formats if needed
        pass


@dataclass
class Order:
    """
    Adapter for TradingOrder that matches the expected interface in tests.
    """
    symbol: str
    side: OrderSide
    order_type: OrderType
    size: float
    timestamp: datetime
    price: Optional[float] = None
    order_id: Optional[str] = None

    def __post_init__(self):
        """Convert to TradingOrder if needed."""
        # This adapter could be expanded to convert between the two formats if needed
        pass


@dataclass
class Trade:
    """
    Adapter for TradingTrade that matches the expected interface in tests.
    """
    symbol: str
    side: OrderSide
    price: float
    size: float
    timestamp: datetime
    trade_id: Optional[str] = None
    fee: Optional[float] = None
    fee_currency: Optional[str] = None

    def __post_init__(self):
        """Convert to TradingTrade if needed."""
        # This adapter could be expanded to convert between the two formats if needed
        pass
