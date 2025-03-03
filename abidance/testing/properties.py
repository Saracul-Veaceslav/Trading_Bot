"""
Property-based testing utilities for trading strategies.

This module provides utilities for property-based testing of trading strategies,
including property validators and test helpers.
"""
from typing import Any, Dict, List, Optional, Type, Callable
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st

from abidance.core.domain import SignalType
from abidance.strategy import Strategy, StrategyConfig
from .generators import generate_ohlcv_data


def validate_ohlcv_data(data: pd.DataFrame) -> bool:
    """
    Validate that OHLCV data satisfies basic properties.

    Args:
        data: DataFrame with OHLCV data

    Returns:
        True if data is valid, False otherwise
    """
    # Check that the DataFrame has the expected columns
    if not all(col in data.columns for col in ['timestamp', 'open', 'high', 'low', 'close', 'volume']):
        return False

    # Check that the data is sorted by timestamp
    if not data['timestamp'].is_monotonic_increasing:
        return False

    # Check that high is always >= low
    if not (data['high'] >= data['low']).all():
        return False

    # Check that high is always >= open and close
    if not (data['high'] >= data['open']).all() or not (data['high'] >= data['close']).all():
        return False

    # Check that low is always <= open and close
    if not (data['low'] <= data['open']).all() or not (data['low'] <= data['close']).all():
        return False

    # Check that all prices are positive
    if not ((data['open'] > 0) & (data['high'] > 0) & (data['low'] > 0) &
            (data['close'] > 0) & (data['volume'] > 0)).all():
        return False

    return True


def test_strategy_signal_invariants(
    strategy_class: Type[Strategy],
    config_class: Type[StrategyConfig],
    config_params: Dict[str, Any]
) -> Callable:
    """
    Create a test function that verifies a strategy's signal invariants.

    Args:
        strategy_class: The strategy class to test
        config_class: The configuration class for the strategy
        config_params: Parameters for the strategy configuration

    Returns:
        A test function that can be used with hypothesis
    """
    @given(data=generate_ohlcv_data())
    def test_function(data: pd.DataFrame) -> None:
        """Test that strategy signals satisfy basic invariants."""
        # Create strategy with the given parameters
        config = config_class(
            name="Test Strategy",
            symbols=["BTC/USDT"],
            **config_params
        )
        strategy = strategy_class(config)

        # Calculate signal
        signal = strategy.calculate_signal(data)

        # Check that the signal is valid
        assert signal in [1, 0, -1]  # 1=BUY, 0=HOLD, -1=SELL

    return test_function


def test_strategy_consistency(
    strategy_class: Type[Strategy],
    config_class: Type[StrategyConfig],
    config_params: Dict[str, Any]
) -> Callable:
    """
    Create a test function that verifies a strategy's consistency.

    Args:
        strategy_class: The strategy class to test
        config_class: The configuration class for the strategy
        config_params: Parameters for the strategy configuration

    Returns:
        A test function that can be used with hypothesis
    """
    @given(data=generate_ohlcv_data())
    def test_function(data: pd.DataFrame) -> None:
        """Test that strategy signals are consistent when run multiple times."""
        # Create strategy with the given parameters
        config = config_class(
            name="Test Strategy",
            symbols=["BTC/USDT"],
            **config_params
        )
        strategy = strategy_class(config)

        # Calculate signal multiple times
        signal1 = strategy.calculate_signal(data)
        signal2 = strategy.calculate_signal(data)
        signal3 = strategy.calculate_signal(data)

        # Check that all signals are the same
        assert signal1 == signal2 == signal3

    return test_function


def test_strategy_edge_cases(
    strategy_class: Type[Strategy],
    config_class: Type[StrategyConfig],
    config_params: Dict[str, Any]
) -> Callable:
    """
    Create a test function that verifies a strategy's behavior with edge cases.

    Args:
        strategy_class: The strategy class to test
        config_class: The configuration class for the strategy
        config_params: Parameters for the strategy configuration

    Returns:
        A test function that can be used with hypothesis
    """
    @given(data=generate_ohlcv_data())
    def test_function(data: pd.DataFrame) -> None:
        """Test that strategy handles edge cases gracefully."""
        import pytest

        # Create strategy with the given parameters
        config = config_class(
            name="Test Strategy",
            symbols=["BTC/USDT"],
            **config_params
        )
        strategy = strategy_class(config)

        # Test with NaN values in the middle
        data_with_nan = data.copy()
        if len(data_with_nan) > 50:
            data_with_nan.loc[45:47, 'close'] = np.nan

            # The strategy should handle NaN values without crashing
            try:
                signal = strategy.calculate_signal(data_with_nan)
                # We don't assert the value, just that it doesn't crash
            except Exception as e:
                pytest.fail(f"Strategy failed with NaN values: {e}")

        # Test with zero volume
        data_zero_volume = data.copy()
        if len(data_zero_volume) > 50:
            data_zero_volume.loc[45:47, 'volume'] = 0

            # The strategy should handle zero volume without crashing
            try:
                signal = strategy.calculate_signal(data_zero_volume)
                # We don't assert the value, just that it doesn't crash
            except Exception as e:
                pytest.fail(f"Strategy failed with zero volume: {e}")

    return test_function


def create_trending_market(data: pd.DataFrame, trend_factor: float = 0.01) -> pd.DataFrame:
    """
    Create a trending market from the given data.

    Args:
        data: Base OHLCV data
        trend_factor: Factor to apply for the trend (positive for uptrend, negative for downtrend)

    Returns:
        Modified DataFrame with a trend
    """
    trending_data = data.copy()

    # Ensure we have enough data
    if len(trending_data) < 100:
        return trending_data

    # Create a trend
    for i in range(50, len(trending_data)):
        trending_data.loc[i, 'close'] = trending_data.loc[i-1, 'close'] * (1 + trend_factor)
        trending_data.loc[i, 'high'] = max(trending_data.loc[i, 'close'] * 1.005, trending_data.loc[i, 'high'])
        trending_data.loc[i, 'low'] = min(trending_data.loc[i, 'close'] * 0.995, trending_data.loc[i, 'low'])
        trending_data.loc[i, 'open'] = trending_data.loc[i-1, 'close']

    return trending_data


def create_sideways_market(data: pd.DataFrame, volatility: float = 0.005) -> pd.DataFrame:
    """
    Create a sideways market from the given data.

    Args:
        data: Base OHLCV data
        volatility: Volatility factor for the sideways market

    Returns:
        Modified DataFrame with a sideways market
    """
    sideways_data = data.copy()

    # Ensure we have enough data
    if len(sideways_data) < 100:
        return sideways_data

    # Create a sideways market
    base_price = sideways_data.loc[50, 'close']
    for i in range(51, len(sideways_data)):
        # Random walk with mean reversion
        change = np.random.normal(0, volatility)
        if sideways_data.loc[i-1, 'close'] > base_price * 1.02:
            change -= 0.002  # Mean reversion
        elif sideways_data.loc[i-1, 'close'] < base_price * 0.98:
            change += 0.002  # Mean reversion

        sideways_data.loc[i, 'close'] = sideways_data.loc[i-1, 'close'] * (1 + change)
        sideways_data.loc[i, 'high'] = max(sideways_data.loc[i, 'close'] * 1.005, sideways_data.loc[i, 'high'])
        sideways_data.loc[i, 'low'] = min(sideways_data.loc[i, 'close'] * 0.995, sideways_data.loc[i, 'low'])
        sideways_data.loc[i, 'open'] = sideways_data.loc[i-1, 'close']

    return sideways_data