"""
Base exceptions for the Trading Bot framework.

This module defines the base exception classes used throughout the trading bot,
providing a consistent error handling approach.
"""

class TradingBotException(Exception):
    """Base exception for all Trading Bot errors."""
    pass


class ConfigurationError(TradingBotException):
    """Raised when there is an error in the configuration."""
    pass


class ExchangeError(TradingBotException):
    """Base exception for all exchange-related errors."""
    pass


class ExchangeConnectionError(ExchangeError):
    """Raised when there is an error connecting to an exchange."""
    pass


class ExchangeAPIError(ExchangeError):
    """Raised when there is an error in the exchange API response."""
    pass


class OrderError(ExchangeError):
    """Raised when there is an error placing, modifying, or canceling an order."""
    pass


class DataError(TradingBotException):
    """Base exception for all data-related errors."""
    pass


class DataNotFoundError(DataError):
    """Raised when requested data cannot be found."""
    pass


class DataValidationError(DataError):
    """Raised when data fails validation checks."""
    pass


class StrategyError(TradingBotException):
    """Base exception for all strategy-related errors."""
    pass


class SignalError(StrategyError):
    """Raised when there is an error generating a trading signal."""
    pass


class IndicatorError(StrategyError):
    """Raised when there is an error calculating a technical indicator."""
    pass


class RiskManagementError(TradingBotException):
    """Base exception for all risk management-related errors."""
    pass


class PositionSizingError(RiskManagementError):
    """Raised when there is an error calculating position size."""
    pass


class StopLossError(RiskManagementError):
    """Raised when there is an error setting or managing stop losses."""
    pass 