"""
Exchange-specific exceptions for the Trading Bot framework.

This module contains exceptions specific to exchange operations,
including API connections, order execution, and market data retrieval.
"""

from trading_bot.exceptions import ExchangeError


class ExchangeConnectionError(ExchangeError):
    """Raised when there is an error connecting to an exchange."""
    pass


class ExchangeAPIError(ExchangeError):
    """Raised when there is an error in the exchange API response."""
    pass


class ExchangeAuthenticationError(ExchangeError):
    """Raised when authentication with an exchange fails."""
    pass


class ExchangeRateLimitError(ExchangeError):
    """Raised when the exchange rate limit is exceeded."""
    pass


class OrderError(ExchangeError):
    """Base class for order-related errors."""
    pass


class OrderPlacementError(OrderError):
    """Raised when there is an error placing an order."""
    pass


class OrderCancellationError(OrderError):
    """Raised when there is an error cancelling an order."""
    pass


class OrderModificationError(OrderError):
    """Raised when there is an error modifying an order."""
    pass


class InsufficientFundsError(OrderError):
    """Raised when there are insufficient funds to place an order."""
    pass


class WebSocketError(ExchangeError):
    """Raised when there is an error with the exchange websocket connection."""
    pass 