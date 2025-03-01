"""
Strategy-specific exceptions for the Trading Bot framework.

This module defines exceptions specific to the strategy module, providing more granular
error handling for strategy-related operations.
"""

from trading_bot.exceptions import StrategyError, SignalError, IndicatorError


class StrategyInitializationError(StrategyError):
    """Raised when a strategy cannot be properly initialized."""
    pass


class StrategyParameterError(StrategyError):
    """Raised when there are issues with strategy parameters."""
    pass


class MissingIndicatorError(IndicatorError):
    """Raised when a required indicator is missing in the data."""
    pass


class IndicatorCalculationError(IndicatorError):
    """Raised when an error occurs during indicator calculation."""
    pass


class InsufficientDataError(StrategyError):
    """Raised when there is not enough data to generate a signal or calculate indicators."""
    pass


class InvalidSignalError(SignalError):
    """Raised when the generated signal is invalid."""
    pass


class SignalGenerationError(SignalError):
    """Raised when an error occurs during signal generation."""
    pass


class BacktestingError(StrategyError):
    """Raised when there's an error during backtesting."""
    pass


class StrategyValidationError(StrategyError):
    """Raised when a strategy fails validation checks."""
    pass


class OptimizationError(StrategyError):
    """Raised when an error occurs during strategy optimization."""
    pass 