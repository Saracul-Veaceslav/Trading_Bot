"""
Technical indicators for trading strategies.

This module contains functions for calculating common technical indicators
that can be used across different trading strategies.
"""
from typing import Optional, Tuple, Dict, Any

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
    # Use recommended approach from warning message to avoid downcasting warning
    prev_above = prev_above.fillna(False).infer_objects(copy=False)
    prev_above = prev_above.astype(bool)
    
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


def analyze_price_action(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze price action patterns for the latest candle.
    
    Args:
        data: OHLCV data as a pandas DataFrame
        
    Returns:
        Dictionary with price action analysis
    """
    if len(data) < 2:
        return {"error": "Not enough data for price action analysis"}
    
    latest = data.iloc[-1]
    previous = data.iloc[-2]
    
    # Calculate candle body and shadows
    body_size = abs(latest['close'] - latest['open'])
    upper_shadow = latest['high'] - max(latest['open'], latest['close'])
    lower_shadow = min(latest['open'], latest['close']) - latest['low']
    
    # Bullish/bearish candle
    is_bullish = latest['close'] > latest['open']
    
    # Doji (open and close are almost the same)
    is_doji = body_size / (latest['high'] - latest['low']) < 0.1 if (latest['high'] - latest['low']) > 0 else False
    
    # Engulfing pattern
    is_bullish_engulfing = (
        is_bullish and 
        not previous['close'] > previous['open'] and
        latest['open'] < previous['close'] and
        latest['close'] > previous['open']
    )
    
    is_bearish_engulfing = (
        not is_bullish and
        previous['close'] > previous['open'] and
        latest['open'] > previous['close'] and
        latest['close'] < previous['open']
    )
    
    return {
        "is_bullish": is_bullish,
        "is_doji": is_doji,
        "is_bullish_engulfing": is_bullish_engulfing,
        "is_bearish_engulfing": is_bearish_engulfing,
        "body_size": body_size,
        "upper_shadow": upper_shadow,
        "lower_shadow": lower_shadow,
    } 