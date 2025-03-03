"""
Base exchange module defining the abstract Exchange interface.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..trading.order import Order


class Exchange(ABC):
    """
    Abstract base class for exchange implementations.

    All exchange implementations must inherit from this class and implement
    its abstract methods to provide a consistent interface.
    """

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 testnet: bool = False, **kwargs):
        """
        Initialize the exchange.

        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            testnet: Whether to use testnet/sandbox environment
            **kwargs: Additional exchange-specific parameters
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.exchange_id = self.__class__.__name__

    @abstractmethod
    def get_markets(self) -> List[Dict[str, Any]]:
        """
        Get all available markets/symbols on the exchange.

        Returns:
            List of market dictionaries with symbol information
        """
        pass

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get current ticker data for a symbol.

        Args:
            symbol: The market symbol (e.g., 'BTC/USDT')

        Returns:
            Dictionary with ticker data
        """
        pass

    @abstractmethod
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

    @abstractmethod
    def get_balance(self) -> Dict[str, Dict[str, float]]:
        """
        Get account balances.

        Returns:
            Dictionary of asset balances
        """
        pass

    @abstractmethod
    def place_order(self, order: Order) -> Dict[str, Any]:
        """
        Place an order on the exchange.

        Args:
            order: Order object with trade parameters

        Returns:
            Dictionary with order result information
        """
        pass

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open orders.

        Args:
            symbol: Filter by market symbol, or None for all

        Returns:
            List of open order dictionaries
        """
        pass

    def __str__(self) -> str:
        """String representation of the exchange."""
        return f"{self.exchange_id}({'testnet' if self.testnet else 'live'})"