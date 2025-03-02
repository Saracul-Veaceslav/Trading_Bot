"""
Technical indicators for trading strategies.

This module contains functions for calculating common technical indicators
that can be used across different trading strategies.
"""
from typing import Optional, Tuple

import pandas as pd
import numpy as np


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
    # Calculate price changes
    delta = data[column].diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


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
    # Calculate fast and slow EMAs
    fast_ema = calculate_ema(data, fast_period, column)
    slow_ema = calculate_ema(data, slow_period, column)
    
    # Calculate MACD line
    macd_line = fast_ema - slow_ema
    
    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def detect_crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Detect crossovers between two series.
    
    Args:
        series1: First series
        series2: Second series
        
    Returns:
        Series with values:
         1: series1 crosses above series2
        -1: series1 crosses below series2
         0: No crossover
    """
    # Current relationship
    above = series1 > series2
    
    # Previous relationship
    prev_above = above.shift(1)
    
    # Detect crossovers
    crossover = pd.Series(0, index=series1.index)
    crossover.loc[(~prev_above) & above] = 1    # Bullish crossover
    crossover.loc[prev_above & (~above)] = -1   # Bearish crossover
    
    return crossover 