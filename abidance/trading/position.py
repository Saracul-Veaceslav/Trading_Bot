"""
Position module for tracking open positions.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from .trade import Trade


@dataclass
class Position:
    """
    Represents a trading position.

    A position is created when a trade is executed and tracks the current
    state of a holding, including entry and exit information, P&L, etc.
    """
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    position_id: str = None
    strategy_id: Optional[str] = None
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    trades: List[Trade] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Optional[dict] = None

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.position_id is None:
            self.position_id = str(uuid4())
        if self.trades is None:
            self.trades = []
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_open(self) -> bool:
        """Check if the position is still open."""
        return self.exit_price is None

    @property
    def current_value(self, current_price: Optional[float] = None) -> float:
        """Calculate the current value of the position."""
        price = current_price if current_price is not None else self.exit_price or self.entry_price
        return price * self.quantity

    @property
    def cost_basis(self) -> float:
        """Calculate the cost basis of the position."""
        return self.entry_price * self.quantity

    @property
    def unrealized_pnl(self, current_price: Optional[float] = None) -> float:
        """Calculate the unrealized P&L for the position."""
        if not self.is_open:
            return 0
        return self.current_value(current_price) - self.cost_basis

    @property
    def realized_pnl(self) -> float:
        """Calculate the realized P&L for the position."""
        if self.is_open:
            return 0
        return (self.exit_price - self.entry_price) * self.quantity

    def add_trade(self, trade: Trade) -> None:
        """Add a trade to the position."""
        self.trades.append(trade)

    def close(self, exit_price: float, exit_time: datetime) -> None:
        """Close the position with the given exit price and time."""
        self.exit_price = exit_price
        self.exit_time = exit_time

    def to_dict(self) -> dict:
        """Convert the position to a dictionary for storage or transmission."""
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat() if self.entry_time else None,
            "position_id": self.position_id,
            "strategy_id": self.strategy_id,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "trades": [trade.to_dict() for trade in self.trades] if self.trades else [],
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Create a Position instance from a dictionary."""
        # Handle nested trade objects
        trades_data = data.pop("trades", [])

        # Convert ISO format dates back to datetime
        if isinstance(data.get("entry_time"), str):
            data["entry_time"] = datetime.fromisoformat(data["entry_time"])
        if isinstance(data.get("exit_time"), str):
            data["exit_time"] = datetime.fromisoformat(data["exit_time"])

        position = cls(**data)

        # Add trades to the position
        if trades_data:
            position.trades = [Trade.from_dict(trade_data) for trade_data in trades_data]

        return position