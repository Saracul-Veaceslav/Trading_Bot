"""
Exceptions module for the Abidance trading bot.

Defines a hierarchical exception system for the application.
All exceptions inherit from AbidanceError.
"""

# Base exceptions
class AbidanceError(Exception):
    """Base exception for all Abidance-related errors."""

# Domain exceptions
class ConfigError(AbidanceError): """Configuration errors."""
ConfigurationError = ConfigError  # Alias for backward compatibility

class ExchangeError(AbidanceError): """Exchange-related errors."""
class StrategyError(AbidanceError): """Strategy-related errors."""
class DataError(AbidanceError): """Data-related errors."""
class TradeError(AbidanceError): """Trade-related errors."""
class OrderError(AbidanceError): """Order-related errors."""
class PositionError(AbidanceError): """Position-related errors."""
class ValidationError(AbidanceError): """Validation errors."""
class APIError(AbidanceError): """API-related errors."""
class MLError(AbidanceError): """Machine learning errors."""
class BacktestError(AbidanceError): """Backtesting errors."""
class NotImplementedFeatureError(AbidanceError): """Not implemented features."""

# Specialized exceptions
class AuthenticationError(ExchangeError): """Authentication errors."""
class RateLimitError(ExchangeError): """Rate limit exceeded errors."""
class InsufficientFundsError(ExchangeError): """Insufficient funds errors."""
class MarketClosedError(ExchangeError): """Market closed errors."""
class InvalidOrderError(OrderError): """Invalid order errors."""
class OrderPlacementError(OrderError): """Order placement errors."""
class OrderCancellationError(OrderError): """Order cancellation errors."""
class OrderNotFoundError(OrderError): """Order not found errors."""

class DataSourceError(DataError): """Data source errors."""
class DataFormatError(DataError): """Data format errors."""
class DataProcessingError(DataError): """Data processing errors."""

class StrategyValidationError(StrategyError): """Strategy validation errors."""
class StrategyExecutionError(StrategyError): """Strategy execution errors."""

class PositionOpenError(PositionError): """Position opening errors."""
class PositionCloseError(PositionError): """Position closing errors."""
class PositionUpdateError(PositionError): """Position update errors."""

class ConfigParsingError(ConfigError): """Configuration parsing errors."""
class ConfigValidationError(ConfigError): """Configuration validation errors."""
class ConfigFileNotFoundError(ConfigError): """Configuration file not found."""

class ModelTrainError(MLError): """Model training errors."""
class ModelPredictionError(MLError): """Model prediction errors."""
class ModelLoadError(MLError): """Model loading errors."""
class ModelSaveError(MLError): """Model saving errors."""

class ConnectionError(ExchangeError): """Connection errors."""
class TimeoutError(ExchangeError): """Timeout errors."""

# Circuit breaker specific exceptions
class CircuitOpenError(AbidanceError): """Circuit breaker is open."""

# Import the ErrorContext and error handling utilities
from .error_context import ErrorContext, error_boundary, retry
from .fallback import fallback, CircuitBreaker

# Export all error types and utilities
__all__ = [
    'AbidanceError',
    'ConfigError', 'ConfigurationError',
    'ExchangeError', 'StrategyError', 'DataError',
    'TradeError', 'OrderError', 'PositionError',
    'ValidationError', 'APIError', 'MLError',
    'BacktestError', 'NotImplementedFeatureError',
    'AuthenticationError', 'RateLimitError',
    'InsufficientFundsError', 'MarketClosedError',
    'InvalidOrderError', 'OrderPlacementError',
    'OrderCancellationError', 'OrderNotFoundError',
    'DataSourceError', 'DataFormatError', 'DataProcessingError',
    'StrategyValidationError', 'StrategyExecutionError',
    'PositionOpenError', 'PositionCloseError', 'PositionUpdateError',
    'ConfigParsingError', 'ConfigValidationError', 'ConfigFileNotFoundError',
    'ModelTrainError', 'ModelPredictionError', 'ModelLoadError', 'ModelSaveError',
    'ConnectionError', 'TimeoutError',
    'CircuitOpenError',
    'ErrorContext', 'error_boundary', 'retry',
    'fallback', 'CircuitBreaker'
]