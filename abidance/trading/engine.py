"""
Trading engine module for executing orders and managing positions.
"""
import logging
from typing import Dict, List, Optional, Tuple, Union

from ..exceptions import ExchangeError
from .order import Order, OrderSide, OrderType
from .position import Position
from .trade import Trade


class TradingEngine:
    """
    Trading engine responsible for executing orders and tracking positions.

    This class serves as the central component for trade execution, coordinating
    between strategies, exchanges, and data management.
    """

    def __init__(self, exchange_manager=None, data_manager=None):
        """
        Initialize the trading engine.

        Args:
            exchange_manager: Manager for exchange interactions
            data_manager: Manager for data storage and retrieval
        """
        self.exchange_manager = exchange_manager
        self.data_manager = data_manager
        self.open_orders: Dict[str, Order] = {}
        self.open_positions: Dict[str, Position] = {}
        self.logger = logging.getLogger(__name__)

    def create_order(self, symbol: str, side: Union[OrderSide, str], order_type: Union[OrderType, str],
                     quantity: float, price: Optional[float] = None, stop_price: Optional[float] = None,
                     exchange_id: Optional[str] = None) -> Order:
        """
        Create a new order.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            side: Buy or sell
            order_type: Type of order (market, limit, etc.)
            quantity: Amount to buy or sell
            price: Limit price (required for limit orders)
            stop_price: Stop price (required for stop orders)
            exchange_id: Specific exchange to use, or None for default

        Returns:
            The created Order object
        """
        # Convert string types to enums if needed
        if isinstance(side, str):
            side = OrderSide(side)
        if isinstance(order_type, str):
            order_type = OrderType(order_type)

        # Create the order
        order = Order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            exchange_id=exchange_id
        )

        self.logger.info(f"Created order: {order}")
        return order

    def execute_order(self, order: Order) -> Tuple[bool, Optional[Trade]]:
        """
        Execute an order on the exchange.

        Args:
            order: The order to execute

        Returns:
            Tuple of (success, trade)
        """
        if not self.exchange_manager:
            self.logger.error("Cannot execute order: No exchange manager available")
            return False, None

        try:
            # Use the exchange manager to place the order
            exchange = self.exchange_manager.get_exchange(order.exchange_id)
            result = exchange.place_order(order)

            if result.get("success"):
                # Create and store the trade
                trade = Trade(
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    price=result.get("price"),
                    timestamp=result.get("timestamp"),
                    order_id=order.exchange_order_id,
                    exchange_id=order.exchange_id,
                    exchange_trade_id=result.get("trade_id"),
                    fee=result.get("fee"),
                    fee_currency=result.get("fee_currency")
                )

                # Store the trade in the data manager if available
                if self.data_manager:
                    self.data_manager.store_trade(trade)

                self.logger.info(f"Executed order successfully: {order.exchange_order_id}")
                return True, trade
            else:
                self.logger.error(f"Failed to execute order: {result.get('error')}")
                return False, None

        except ExchangeError as e:
            self.logger.error(f"Exchange error executing order: {e}")
            return False, None
        except Exception as e:
            self.logger.error(f"Unexpected error executing order: {e}")
            return False, None

    def get_open_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """
        Get all open positions, optionally filtered by symbol.

        Args:
            symbol: Trading pair to filter by, or None for all

        Returns:
            List of open Position objects
        """
        if symbol:
            return [p for p in self.open_positions.values() if p.symbol == symbol and p.is_open]
        return [p for p in self.open_positions.values() if p.is_open]

    def get_position(self, position_id: str) -> Optional[Position]:
        """
        Get a specific position by ID.

        Args:
            position_id: The ID of the position to retrieve

        Returns:
            The Position object if found, otherwise None
        """
        return self.open_positions.get(position_id)

    def close_position(self, position_id: str, price: float) -> bool:
        """
        Close an open position.

        Args:
            position_id: The ID of the position to close
            price: The exit price

        Returns:
            True if successful, False otherwise
        """
        position = self.open_positions.get(position_id)
        if not position or not position.is_open:
            self.logger.warning(f"Cannot close position {position_id}: not found or already closed")
            return False

        # Create an order to close the position
        side = OrderSide.SELL if position.quantity > 0 else OrderSide.BUY
        close_order = self.create_order(
            symbol=position.symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=abs(position.quantity),
            exchange_id=position.trades[0].exchange_id if position.trades else None
        )

        # Execute the order
        success, trade = self.execute_order(close_order)
        if success and trade:
            # Update the position
            position.close(trade.price, trade.timestamp)
            position.add_trade(trade)

            # Update data storage
            if self.data_manager:
                self.data_manager.update_position(position)

            self.logger.info(f"Closed position {position_id} at price {trade.price}")
            return True
        else:
            self.logger.error(f"Failed to close position {position_id}")
            return False