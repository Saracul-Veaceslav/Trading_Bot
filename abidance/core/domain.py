"""
Core domain entities for the Abidance trading bot.

This module defines the core domain entities used throughout the application,
including order types, positions, signals, and market data structures.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Union


class OrderSide(Enum):
    """Enum representing the side of an order (buy or sell)."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Enum representing the type of an order."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class SignalType(Enum):
    """Enum representing the type of a trading signal."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Position:
    """
    Represents a trading position.
    
    A position is an open holding of an asset.
    """
    symbol: str
    side: OrderSide
    entry_price: float
    size: float
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_id: Optional[str] = None


@dataclass
class Order:
    """
    Represents a trading order.
    
    An order is an instruction to buy or sell an asset.
    """
    symbol: str
    side: OrderSide
    order_type: OrderType
    size: float
    timestamp: datetime
    price: Optional[float] = None  # Optional for market orders
    order_id: Optional[str] = None


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


@dataclass
class Trade:
    """
    Represents a completed trade.
    
    A trade is a completed transaction to buy or sell an asset.
    """
    symbol: str
    side: OrderSide
    price: float
    size: float
    timestamp: datetime
    trade_id: Optional[str] = None
    fee: Optional[float] = None
    fee_currency: Optional[str] = None 