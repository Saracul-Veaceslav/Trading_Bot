"""
Risk management-specific exceptions for the Trading Bot framework.

This module defines exceptions specific to the risk management module, providing more granular
error handling for risk-related operations.
"""

from trading_bot.exceptions import RiskManagementError, PositionSizingError, StopLossError


class RiskParameterError(RiskManagementError):
    """Raised when there's an issue with risk management parameters."""
    pass


class MaxDrawdownExceededError(RiskManagementError):
    """Raised when the maximum drawdown limit is exceeded."""
    pass


class InvalidPositionSizeError(PositionSizingError):
    """Raised when a position size is invalid (too small or too large)."""
    pass


class PositionLimitExceededError(PositionSizingError):
    """Raised when position limits are exceeded."""
    pass


class StopLossCalculationError(StopLossError):
    """Raised when there's an error calculating stop loss levels."""
    pass


class TakeProfitError(RiskManagementError):
    """Raised when there's an issue with take profit management."""
    pass


class ExposureExceededError(RiskManagementError):
    """Raised when the maximum exposure limit is exceeded."""
    pass


class RiskRewardRatioError(RiskManagementError):
    """Raised when the risk/reward ratio doesn't meet the required threshold."""
    pass


class KellyCriterionError(PositionSizingError):
    """Raised when there's an error calculating position size using Kelly Criterion."""
    pass


class RiskManagementValidationError(RiskManagementError):
    """Raised when risk management configuration fails validation."""
    pass 