"""
Technical indicators package for trading strategies.

This package contains implementations of various technical indicators
that can be used across different trading strategies.
"""

from .base import Indicator
from .momentum import RSI, MACD

# Re-export functions from the original indicators.py for backward compatibility
import sys
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

# Function implementations for backward compatibility
def calculate_sma(data: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
    """
    Calculate Simple Moving Average.
    
    Args:
        data: OHLCV data as a pandas DataFrame
        period: SMA period
        column: Column name to use for calculation
        
    Returns:
        Series with SMA values
    """
    return data[column].rolling(window=period).mean()


def calculate_ema(data: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
    """
    Calculate Exponential Moving Average.
    
    Args:
        data: OHLCV data as a pandas DataFrame
        period: EMA period
        column: Column name to use for calculation
        
    Returns:
        Series with EMA values
    """
    return data[column].ewm(span=period, adjust=False).mean()


def calculate_rsi(data: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        data: OHLCV data as a pandas DataFrame
        period: RSI period
        column: Column name to use for calculation
        
    Returns:
        Series with RSI values
    """
    rsi_indicator = RSI(period=period, column=column)
    return rsi_indicator.calculate(data)


def calculate_macd(
    data: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    column: str = 'close'
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Moving Average Convergence Divergence (MACD).
    
    Args:
        data: OHLCV data as a pandas DataFrame
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal EMA period
        column: Column name to use for calculation
        
    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    macd_indicator = MACD(
        fast_period=fast_period,
        slow_period=slow_period,
        signal_period=signal_period,
        column=column
    )
    result = macd_indicator.calculate(data)
    return result['macd'], result['signal'], result['histogram']


def calculate_bollinger_bands(
    data: pd.DataFrame, 
    period: int = 20, 
    deviations: float = 2.0,
    column: str = 'close'
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands.
    
    Args:
        data: OHLCV data as a pandas DataFrame
        period: Period for the moving average
        deviations: Number of standard deviations for the bands
        column: Column name to use for calculation
        
    Returns:
        Tuple of (middle_band, upper_band, lower_band)
    """
    middle_band = calculate_sma(data, period, column)
    std_dev = data[column].rolling(window=period).std()
    
    upper_band = middle_band + (std_dev * deviations)
    lower_band = middle_band - (std_dev * deviations)
    
    return middle_band, upper_band, lower_band


def detect_crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Detect when series1 crosses above or below series2.
    
    Returns a Series with values:
         1: series1 crosses above series2 (bullish)
        -1: series1 crosses below series2 (bearish)
         0: No crossover
    """
    # Current relationship
    above = series1 > series2
    
    # Previous relationship
    prev_above = above.shift(1)
    
    # Ensure boolean type to avoid issues with unary ~ operator
    above = above.astype(bool)
    # Use infer_objects before astype to avoid downcasting warnings
    prev_above = prev_above.fillna(False).infer_objects(copy=False).astype(bool)
    
    # Detect crossovers
    crossover = pd.Series(0, index=series1.index)
    crossover.loc[(~prev_above) & above] = 1    # Bullish crossover
    crossover.loc[prev_above & (~above)] = -1   # Bearish crossover
    
    return crossover


def detect_threshold_crossover(series: pd.Series, threshold: float) -> pd.Series:
    """
    Detect when a series crosses above or below a threshold value.
    
    Args:
        series: The data series
        threshold: The threshold value
        
    Returns:
        Series with values:
         1: series crosses above threshold
        -1: series crosses below threshold
         0: No crossover
    """
    # Current relationship
    above = series > threshold
    
    # Previous relationship
    prev_above = above.shift(1)
    
    # Detect crossovers
    crossover = pd.Series(0, index=series.index)
    crossover.loc[(~prev_above) & above] = 1    # Crosses above threshold
    crossover.loc[prev_above & (~above)] = -1   # Crosses below threshold
    
    return crossover


def analyze_volume(data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    """
    Analyze volume data using SMA to detect unusual volume activity.
    
    Args:
        data: OHLCV data as a pandas DataFrame
        period: Period for volume SMA calculation
        
    Returns:
        DataFrame with added volume analysis columns
    """
    # Calculate volume SMA
    data = data.copy()
    data['volume_sma'] = calculate_sma(data, period, 'volume')
    
    # Calculate volume ratio (current volume / average volume)
    data['volume_ratio'] = data['volume'] / data['volume_sma']
    
    # Detect abnormal volume (> 1.5x average)
    data['abnormal_volume'] = data['volume_ratio'] > 1.5
    
    return data


__all__ = [
    # Indicator classes
    'Indicator',
    'RSI',
    'MACD',
    
    # Backward compatibility functions
    'calculate_sma',
    'calculate_ema',
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'detect_crossover',
    'detect_threshold_crossover',
    'analyze_volume',
] 