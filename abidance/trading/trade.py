"""
Trade module for tracking executed trades.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from .order import OrderSide


@dataclass
class Trade:
    """
    Represents an executed trade.

    A trade is created when an order is executed (fully or partially).
    It tracks the details of the execution, including price, quantity, and fees.
    """
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    trade_id: str = None
    order_id: Optional[str] = None
    exchange_id: str = None
    exchange_trade_id: Optional[str] = None
    fee: Optional[float] = 0.0
    fee_currency: Optional[str] = None

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.trade_id is None:
            self.trade_id = str(uuid4())

    @property
    def value(self) -> float:
        """Calculate the value of the trade (price * quantity)."""
        return self.price * self.quantity

    @property
    def net_value(self) -> float:
        """Calculate the net value of the trade after fees."""
        return self.value - self.fee

    def to_dict(self) -> dict:
        """Convert the trade to a dictionary for storage or transmission."""
        return {
            "symbol": self.symbol,
            "side": self.side.value if hasattr(self.side, "value") else self.side,
            "quantity": self.quantity,
            "price": self.price,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "exchange_id": self.exchange_id,
            "exchange_trade_id": self.exchange_trade_id,
            "fee": self.fee,
            "fee_currency": self.fee_currency,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Trade':
        """Create a Trade instance from a dictionary."""
        # Convert string values back to enums
        if isinstance(data.get("side"), str):
            data["side"] = OrderSide(data["side"])

        # Convert ISO format date back to datetime
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        return cls(**data)