"""
Mock data generation utilities for testing.

This module provides utilities for generating synthetic market data
that can be used for testing trading strategies with the MockExchange.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


def generate_random_ohlcv(
    symbol: str,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    num_periods: int = 100,
    timeframe: str = '1h',
    base_price: float = 100.0,
    volatility: float = 0.02,
    trend: float = 0.0,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate random OHLCV data for testing.

    Args:
        symbol: The market symbol
        start_date: Starting date for the data
        end_date: Ending date for the data (if None, calculated from num_periods)
        num_periods: Number of periods to generate
        timeframe: Timeframe interval (e.g., '1m', '1h', '1d')
        base_price: Starting price
        volatility: Price volatility factor
        trend: Price trend factor (positive for uptrend, negative for downtrend)
        seed: Random seed for reproducibility

    Returns:
        DataFrame with OHLCV data
    """
    if seed is not None:
        np.random.seed(seed)

    # Calculate time delta based on timeframe
    delta = _parse_timeframe(timeframe)

    # Generate timestamps
    if end_date is None:
        timestamps = [start_date + i * delta for i in range(num_periods)]
    else:
        total_seconds = (end_date - start_date).total_seconds()
        period_seconds = delta.total_seconds()
        num_periods = min(num_periods, int(total_seconds / period_seconds) + 1)
        timestamps = [start_date + i * delta for i in range(num_periods)]

    # Generate price data
    closes = []
    opens = []
    highs = []
    lows = []
    volumes = []

    current_price = base_price

    for i in range(num_periods):
        # Add trend component
        current_price *= (1 + trend)

        # Add random component
        daily_volatility = np.random.normal(0, volatility)
        current_price *= (1 + daily_volatility)

        # Generate OHLC based on close price
        daily_range = current_price * volatility * 2  # Typical daily range

        open_price = current_price * (1 + np.random.normal(0, volatility / 2))
        high_price = max(open_price, current_price) + abs(np.random.normal(0, daily_range / 4))
        low_price = min(open_price, current_price) - abs(np.random.normal(0, daily_range / 4))

        # Ensure high is highest and low is lowest
        high_price = max(high_price, open_price, current_price)
        low_price = min(low_price, open_price, current_price)

        # Generate volume (higher on larger price moves)
        volume = np.random.gamma(2.0, 1.0) * 1000 * (1 + abs(daily_volatility) * 10)

        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(current_price)
        volumes.append(volume)

    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })

    return df


def generate_trending_ohlcv(
    symbol: str,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    num_periods: int = 100,
    timeframe: str = '1h',
    base_price: float = 100.0,
    volatility: float = 0.02,
    trend_changes: List[Tuple[int, float]] = None,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate OHLCV data with specific trend changes for testing.

    Args:
        symbol: The market symbol
        start_date: Starting date for the data
        end_date: Ending date for the data (if None, calculated from num_periods)
        num_periods: Number of periods to generate
        timeframe: Timeframe interval (e.g., '1m', '1h', '1d')
        base_price: Starting price
        volatility: Price volatility factor
        trend_changes: List of (period_index, new_trend) tuples
        seed: Random seed for reproducibility

    Returns:
        DataFrame with OHLCV data
    """
    if seed is not None:
        np.random.seed(seed)

    # Default trend changes if none provided
    if trend_changes is None:
        trend_changes = [
            (0, 0.001),      # Start with slight uptrend
            (int(num_periods * 0.3), -0.002),  # Switch to downtrend
            (int(num_periods * 0.6), 0.003),   # Switch to strong uptrend
            (int(num_periods * 0.8), 0.0),     # Switch to sideways
        ]

    # Calculate time delta based on timeframe
    delta = _parse_timeframe(timeframe)

    # Generate timestamps
    if end_date is None:
        timestamps = [start_date + i * delta for i in range(num_periods)]
    else:
        total_seconds = (end_date - start_date).total_seconds()
        period_seconds = delta.total_seconds()
        num_periods = min(num_periods, int(total_seconds / period_seconds) + 1)
        timestamps = [start_date + i * delta for i in range(num_periods)]

    # Generate price data
    closes = []
    opens = []
    highs = []
    lows = []
    volumes = []

    current_price = base_price
    current_trend = trend_changes[0][1]
    next_trend_idx = 1

    for i in range(num_periods):
        # Check if we need to change trend
        if next_trend_idx < len(trend_changes) and i >= trend_changes[next_trend_idx][0]:
            current_trend = trend_changes[next_trend_idx][1]
            next_trend_idx += 1

        # Add trend component
        current_price *= (1 + current_trend)

        # Add random component
        daily_volatility = np.random.normal(0, volatility)
        current_price *= (1 + daily_volatility)

        # Generate OHLC based on close price
        daily_range = current_price * volatility * 2  # Typical daily range

        open_price = current_price * (1 + np.random.normal(0, volatility / 2))
        high_price = max(open_price, current_price) + abs(np.random.normal(0, daily_range / 4))
        low_price = min(open_price, current_price) - abs(np.random.normal(0, daily_range / 4))

        # Ensure high is highest and low is lowest
        high_price = max(high_price, open_price, current_price)
        low_price = min(low_price, open_price, current_price)

        # Generate volume (higher on larger price moves and trend changes)
        trend_change_factor = 1.0
        if next_trend_idx < len(trend_changes) and i == trend_changes[next_trend_idx][0] - 1:
            trend_change_factor = 3.0  # Higher volume near trend changes

        volume = np.random.gamma(2.0, 1.0) * 1000 * (1 + abs(daily_volatility) * 10) * trend_change_factor

        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(current_price)
        volumes.append(volume)

    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })

    return df


def generate_pattern_ohlcv(
    symbol: str,
    pattern_type: str,
    start_date: datetime,
    num_periods: int = 100,
    timeframe: str = '1h',
    base_price: float = 100.0,
    volatility: float = 0.02,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate OHLCV data with specific chart patterns for testing.

    Args:
        symbol: The market symbol
        pattern_type: Type of pattern ('double_top', 'head_shoulders', etc.)
        start_date: Starting date for the data
        num_periods: Number of periods to generate
        timeframe: Timeframe interval (e.g., '1m', '1h', '1d')
        base_price: Starting price
        volatility: Price volatility factor
        seed: Random seed for reproducibility

    Returns:
        DataFrame with OHLCV data
    """
    if seed is not None:
        np.random.seed(seed)

    # Define trend changes based on pattern type
    if pattern_type == 'double_top':
        trend_changes = [
            (0, 0.003),                      # Initial uptrend
            (int(num_periods * 0.3), 0.0),   # First top
            (int(num_periods * 0.35), -0.002),  # Pullback
            (int(num_periods * 0.45), 0.003),   # Move to second top
            (int(num_periods * 0.6), 0.0),      # Second top
            (int(num_periods * 0.65), -0.004),  # Breakdown
        ]
    elif pattern_type == 'head_shoulders':
        trend_changes = [
            (0, 0.002),                      # Initial uptrend
            (int(num_periods * 0.2), 0.0),   # Left shoulder
            (int(num_periods * 0.25), -0.001),  # Pullback
            (int(num_periods * 0.35), 0.003),   # Move to head
            (int(num_periods * 0.5), 0.0),      # Head
            (int(num_periods * 0.55), -0.002),  # Pullback
            (int(num_periods * 0.65), 0.001),   # Move to right shoulder
            (int(num_periods * 0.75), 0.0),     # Right shoulder
            (int(num_periods * 0.8), -0.004),   # Breakdown
        ]
    elif pattern_type == 'cup_and_handle':
        trend_changes = [
            (0, 0.002),                      # Initial uptrend
            (int(num_periods * 0.1), -0.001),   # Start of cup
            (int(num_periods * 0.3), -0.0005),  # Bottom of cup
            (int(num_periods * 0.5), 0.001),    # Right side of cup
            (int(num_periods * 0.7), 0.0),      # Rim of cup
            (int(num_periods * 0.75), -0.001),  # Handle
            (int(num_periods * 0.85), 0.0),     # End of handle
            (int(num_periods * 0.9), 0.003),    # Breakout
        ]
    else:  # Default to random trend
        trend_changes = [
            (0, 0.001),
            (int(num_periods * 0.3), -0.001),
            (int(num_periods * 0.6), 0.002),
            (int(num_periods * 0.8), -0.001),
        ]

    return generate_trending_ohlcv(
        symbol=symbol,
        start_date=start_date,
        num_periods=num_periods,
        timeframe=timeframe,
        base_price=base_price,
        volatility=volatility,
        trend_changes=trend_changes,
        seed=seed
    )


def _parse_timeframe(timeframe: str) -> timedelta:
    """
    Parse timeframe string into timedelta.

    Args:
        timeframe: Timeframe string (e.g., '1m', '1h', '1d')

    Returns:
        Equivalent timedelta

    Raises:
        ValueError: If timeframe format is invalid
    """
    if not timeframe:
        raise ValueError("Timeframe cannot be empty")

    # Extract number and unit
    if timeframe[-1].isdigit():
        raise ValueError(f"Invalid timeframe format: {timeframe}")

    try:
        amount = int(timeframe[:-1])
    except ValueError:
        raise ValueError(f"Invalid timeframe format: {timeframe}")

    unit = timeframe[-1].lower()

    if unit == 'm':
        return timedelta(minutes=amount)
    elif unit == 'h':
        return timedelta(hours=amount)
    elif unit == 'd':
        return timedelta(days=amount)
    elif unit == 'w':
        return timedelta(weeks=amount)
    else:
        raise ValueError(f"Unsupported timeframe unit: {unit}")