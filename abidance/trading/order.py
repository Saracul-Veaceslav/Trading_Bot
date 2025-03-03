"""
Order module for creating and managing trading orders.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class OrderType(Enum):
    """Enum representing different order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Enum representing order sides (buy or sell)."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """
    Represents a trading order.

    An order is an instruction to buy or sell a specific amount of an asset
    at a specific price or market conditions.
    """
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    created_at: datetime = None
    exchange_id: str = None
    exchange_order_id: Optional[str] = None
    status: str = "created"

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Convert the order to a dictionary for storage or transmission."""
        return {
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "stop_price": self.stop_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "exchange_id": self.exchange_id,
            "exchange_order_id": self.exchange_order_id,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """Create an Order instance from a dictionary."""
        # Convert string values back to enums
        if isinstance(data.get("side"), str):
            data["side"] = OrderSide(data["side"])
        if isinstance(data.get("order_type"), str):
            data["order_type"] = OrderType(data["order_type"])

        # Convert ISO format date back to datetime
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return cls(**data)