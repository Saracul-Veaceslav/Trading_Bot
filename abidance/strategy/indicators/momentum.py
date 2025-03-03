"""
Momentum indicators for trading strategies.

This module contains implementations of momentum-based technical indicators
such as RSI and MACD that can be used across different trading strategies.
"""
# Third-party imports
import numpy as np
import pandas as pd


# Local imports
from .base import Indicator


class RSI(Indicator):
    """Relative Strength Index indicator."""

    def __init__(self, period: int = 14, column: str = 'close'):
        """
        Initialize RSI indicator.

        Args:
            period: RSI calculation period
            column: Column name to use for calculation
        """
        self.period = period
        self.column = column

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate RSI values.

        Args:
            data: OHLCV data as a pandas DataFrame

        Returns:
            Series with RSI values

        Raises:
            ValueError: If the specified column is not found in the data
        """
        if self.column not in data.columns:
            raise ValueError(f"Column '{self.column}' not found in data")

        # Calculate price changes
        delta = data[self.column].diff()

        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)

        # Calculate average gain and loss
        avg_gain = gain.ewm(com=self.period-1, adjust=False).mean()
        avg_loss = loss.ewm(com=self.period-1, adjust=False).mean()

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @property
    def name(self) -> str:
        """Get the name of the indicator."""
        return f"RSI({self.period})"


class MACD(Indicator):
    """Moving Average Convergence Divergence indicator."""

    def __init__(self, fast_period: int = 12, slow_period: int = 26,
                signal_period: int = 9, column: str = 'close'):
        """
        Initialize MACD indicator.

        Args:
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal EMA period
            column: Column name to use for calculation
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.column = column

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD indicator.

        Args:
            data: OHLCV data as a pandas DataFrame

        Returns:
            DataFrame with MACD, signal line, and histogram values

        Raises:
            ValueError: If the specified column is not found in the data
        """
        if self.column not in data.columns:
            raise ValueError(f"Column '{self.column}' not found in data")

        # Calculate EMAs
        fast_ema = data[self.column].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = data[self.column].ewm(span=self.slow_period, adjust=False).mean()

        # Calculate MACD line
        macd_line = fast_ema - slow_ema

        # Calculate signal line
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        # Calculate histogram
        histogram = macd_line - signal_line

        # Create result DataFrame
        result = pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }, index=data.index)

        # Set initial values to NaN based on the longest period
        # This ensures proper handling of warmup periods
        max_period = max(self.fast_period, self.slow_period)
        result.iloc[:max_period-1] = np.nan

        return result

    @property
    def name(self) -> str:
        """Get the name of the indicator."""
        return f"MACD({self.fast_period},{self.slow_period},{self.signal_period})"
