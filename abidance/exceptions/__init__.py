"""
Exceptions module for the Abidance trading bot.

This module contains all the custom exceptions used throughout the application.
"""

class AbidanceError(Exception):
    """Base exception for all Abidance-related errors."""
    pass


class ConfigError(AbidanceError):
    """Exception raised for configuration errors."""
    pass


# Alias for ConfigError to match the expected export name in tests
ConfigurationError = ConfigError


class ExchangeError(AbidanceError):
    """Exception raised for exchange-related errors."""
    pass


class StrategyError(AbidanceError):
    """Exception raised for strategy-related errors."""
    pass


class DataError(AbidanceError):
    """Exception raised for data-related errors."""
    pass


class TradeError(AbidanceError):
    """Exception raised for trade-related errors."""
    pass


class OrderError(AbidanceError):
    """Exception raised for order-related errors."""
    pass


class PositionError(AbidanceError):
    """Exception raised for position-related errors."""
    pass


class ValidationError(AbidanceError):
    """Exception raised for validation errors."""
    pass


class APIError(AbidanceError):
    """Exception raised for API-related errors."""
    pass


class MLError(AbidanceError):
    """Exception raised for machine learning-related errors."""
    pass


class BacktestError(AbidanceError):
    """Exception raised for backtesting-related errors."""
    pass


class NotImplementedFeatureError(AbidanceError):
    """Exception raised when a feature is not implemented."""
    pass


class AuthenticationError(ExchangeError):
    """Exception raised for authentication errors."""
    pass


class RateLimitError(ExchangeError):
    """Exception raised when rate limits are exceeded."""
    pass


class InsufficientFundsError(ExchangeError):
    """Exception raised when there are insufficient funds for an operation."""
    pass


class MarketClosedError(ExchangeError):
    """Exception raised when trying to trade on a closed market."""
    pass


class InvalidOrderError(OrderError):
    """Exception raised when an order is invalid."""
    pass


class OrderNotFoundError(OrderError):
    """Exception raised when an order is not found."""
    pass


class InvalidSymbolError(ValidationError):
    """Exception raised when a symbol is invalid."""
    pass


class InvalidTimeframeError(ValidationError):
    """Exception raised when a timeframe is invalid."""
    pass


class InvalidParameterError(ValidationError):
    """Exception raised when a parameter is invalid."""
    pass


class InsufficientDataError(DataError):
    """Exception raised when there is insufficient data for an operation."""
    pass


class DataFetchError(DataError):
    """Exception raised when data cannot be fetched."""
    pass


class RepositoryError(DataError):
    """Exception raised for repository-related errors."""
    pass


class DatabaseError(RepositoryError):
    """Exception raised for database-related errors."""
    pass


class FileStorageError(RepositoryError):
    """Exception raised for file storage-related errors."""
    pass


class CircuitOpenError(AbidanceError):
    """Exception raised when a circuit breaker is open and no fallback is provided."""
    pass


# Import error context utilities
from .error_context import ErrorContext, error_boundary, retry
from .fallback import fallback, CircuitBreaker


# Define what should be available for import from this module
__all__ = [
    'AbidanceError',
    'ConfigError',
    'ConfigurationError',
    'ExchangeError',
    'StrategyError',
    'DataError',
    'TradeError',
    'OrderError',
    'PositionError',
    'ValidationError',
    'APIError',
    'MLError',
    'BacktestError',
    'NotImplementedFeatureError',
    'AuthenticationError',
    'RateLimitError',
    'InsufficientFundsError',
    'MarketClosedError',
    'InvalidOrderError',
    'OrderNotFoundError',
    'InvalidSymbolError',
    'InvalidTimeframeError',
    'InvalidParameterError',
    'InsufficientDataError',
    'DataFetchError',
    'RepositoryError',
    'DatabaseError',
    'FileStorageError',
    'CircuitOpenError',
    # Error context utilities
    'ErrorContext',
    'error_boundary',
    'retry',
    'fallback',
    'CircuitBreaker',
] 