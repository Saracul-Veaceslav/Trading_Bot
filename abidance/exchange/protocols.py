"""
Exchange protocols module defining the interfaces for exchange implementations.

This module provides Protocol classes that define the interfaces that exchange
implementations must satisfy. Using Protocol classes (structural typing) enables
interface extraction without modifying existing implementations.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Protocol, runtime_checkable


from ..trading.order import Order


@runtime_checkable
class Exchange(Protocol):
    """
    Protocol defining the interface for cryptocurrency exchanges.

    This protocol defines the methods that all exchange implementations must provide.
    It enables static type checking and runtime verification of exchange implementations.
    """

    exchange_id: str
    testnet: bool
    api_key: Optional[str]
    api_secret: Optional[str]

    def get_markets(self) -> List[Dict[str, Any]]:
        """
        Get all available markets/symbols on the exchange.

        Returns:
            List of market dictionaries with symbol information
        """
        pass

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get current ticker data for a symbol.

        Args:
            symbol: The market symbol (e.g., 'BTC/USDT')

        Returns:
            Dictionary with ticker data
        """
        pass

    def get_ohlcv(self, symbol: str, timeframe: str = '1h',
                 since: Optional[Union[datetime, int]] = None,
                 limit: Optional[int] = None) -> List[List[float]]:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data.

        Args:
            symbol: The market symbol
            timeframe: Timeframe interval (e.g., '1m', '1h', '1d')
            since: Starting time
            limit: Maximum number of candles to retrieve

        Returns:
            List of OHLCV candles as lists [timestamp, open, high, low, close, volume]
        """
        pass

    def get_balance(self) -> Dict[str, Dict[str, float]]:
        """
        Get account balances.

        Returns:
            Dictionary of asset balances
        """
        pass

    def place_order(self, order: Order) -> Dict[str, Any]:
        """
        Place an order on the exchange.

        Args:
            order: Order object with trade parameters

        Returns:
            Dictionary with order result information
        """
        pass

    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an existing order.

        Args:
            order_id: ID of the order to cancel
            symbol: Market symbol (may be required by some exchanges)

        Returns:
            Dictionary with cancellation result
        """
        pass

    def get_order_status(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the status of an order.

        Args:
            order_id: ID of the order to check
            symbol: Market symbol (may be required by some exchanges)

        Returns:
            Dictionary with order status information
        """
        pass

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open orders.

        Args:
            symbol: Filter by market symbol, or None for all

        Returns:
            List of open order dictionaries
        """
        pass


@runtime_checkable
class ExchangeFactory(Protocol):
    """
    Protocol defining the interface for exchange factories.

    Exchange factories are responsible for creating exchange instances
    based on configuration parameters.
    """

    def create_exchange(self, config: Dict[str, Any]) -> Exchange:
        """
        Create an exchange instance from configuration.

        Args:
            config: Exchange configuration dictionary with parameters like:
                   - exchange_id: Identifier for the exchange
                   - api_key: API key for authentication
                   - api_secret: API secret for authentication
                   - testnet: Whether to use testnet/sandbox
                   - Additional exchange-specific parameters

        Returns:
            Exchange instance
        """
        pass
