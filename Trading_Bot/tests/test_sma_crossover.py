"""
Tests for the SMA Crossover strategy.

These tests ensure that the SMA Crossover strategy correctly generates trading signals
based on the crossing of short and long moving averages.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from Trading_Bot.strategies.sma_crossover import SMAcrossover


@pytest.fixture
def strategy():
    """Create a strategy instance for testing."""
    return SMAcrossover(short_window=3, long_window=5)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame with OHLCV data for testing."""
    dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107],
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    })
    return df


def test_initialization():
    """
    Feature: Strategy Initialization
    
    Scenario: Strategy initializes with custom parameters
        Given a set of parameters for short and long windows
        When a new SMAcrossover strategy is created
        Then it should have the correct parameters set
        And minimum required candles should be set to long_window + 1
    """
    # Test with custom parameters
    strategy = SMAcrossover(short_window=10, long_window=30)
    
    # Verify parameters
    assert strategy.short_window == 10
    assert strategy.long_window == 30
    assert strategy.min_required_candles == 31
    assert strategy.name == "SMA Crossover"


def test_initialization_with_invalid_parameters():
    """
    Feature: Strategy Initialization With Validation
    
    Scenario: Strategy initialization fails with invalid parameters
        Given a set of invalid parameters where short_window >= long_window
        When attempting to create a new SMAcrossover strategy
        Then it should raise a ValueError
    """
    # Test with invalid parameters
    with pytest.raises(ValueError):
        SMAcrossover(short_window=20, long_window=10)
    
    # Test with equal parameters
    with pytest.raises(ValueError):
        SMAcrossover(short_window=10, long_window=10)


def test_calculate_indicators(strategy, sample_dataframe):
    """
    Feature: SMA Calculation
    
    Scenario: Calculate SMA indicators on a DataFrame
        Given a DataFrame with OHLCV data
        When calculate_indicators is called
        Then it should add short_sma, long_sma, and sma_diff columns
        And the values should be correctly calculated
    """
    # Calculate indicators
    result_df = strategy.calculate_indicators(sample_dataframe)
    
    # Check that required columns were added
    assert 'short_sma' in result_df.columns
    assert 'long_sma' in result_df.columns
    assert 'sma_diff' in result_df.columns
    
    # Check calculations for short SMA (window=3)
    # First 2 values should be NaN, then we should have calculated values
    assert pd.isna(result_df['short_sma'].iloc[0])
    assert pd.isna(result_df['short_sma'].iloc[1])
    assert not pd.isna(result_df['short_sma'].iloc[2])
    
    # Verify some calculations (manually calculated)
    # For index 2, SMA should be mean of close prices [101, 102, 103]
    assert result_df['short_sma'].iloc[2] == 102.0
    
    # For index 3, SMA should be mean of close prices [102, 103, 104]
    assert result_df['short_sma'].iloc[3] == 103.0


def test_generate_signal_buy(strategy):
    """
    Feature: SMA Crossover Buy Signal
    
    Scenario: Generate buy signal when short SMA crosses above long SMA
        Given a DataFrame with OHLCV data
        When short SMA crosses above long SMA
        And generate_signal is called
        Then it should return a buy signal (1)
    """
    # Create data with a buy signal (short SMA crossing above long SMA)
    dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
    close_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    
    # Modify the last two points to create a crossover
    close_prices[-2] = 95  # Make the short SMA dip below long SMA
    close_prices[-1] = 115  # Then make it rise above
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 2 for p in close_prices],
        'low': [p - 2 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 10
    })
    
    # First calculate indicators
    df = strategy.calculate_indicators(df)
    
    # Call generate_signal
    signal = strategy.generate_signal(df)
    
    # Check we got the expected buy signal
    assert signal == 1


def test_generate_signal_sell(strategy):
    """
    Feature: SMA Crossover Sell Signal
    
    Scenario: Generate sell signal when short SMA crosses below long SMA
        Given a DataFrame with OHLCV data
        When short SMA crosses below long SMA
        And generate_signal is called
        Then it should return a sell signal (-1)
    """
    # Create data with a sell signal (short SMA crossing below long SMA)
    dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
    close_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    
    # Modify the last two points to create a crossover
    close_prices[-2] = 115  # Make the short SMA above long SMA
    close_prices[-1] = 90   # Then make it fall below
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 2 for p in close_prices],
        'low': [p - 2 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 10
    })
    
    # First calculate indicators
    df = strategy.calculate_indicators(df)
    
    # Call generate_signal
    signal = strategy.generate_signal(df)
    
    # Check we got the expected sell signal
    assert signal == -1


def test_generate_signal_hold(strategy):
    """
    Feature: SMA Crossover Hold Signal
    
    Scenario: Generate hold signal when no crossover occurs
        Given a DataFrame with OHLCV data
        When no SMA crossover occurs
        And generate_signal is called
        Then it should return a hold signal (0)
    """
    # Create data with no crossover (steadily increasing prices)
    dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
    close_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 2 for p in close_prices],
        'low': [p - 2 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 10
    })
    
    # First calculate indicators
    df = strategy.calculate_indicators(df)
    
    # Call generate_signal
    signal = strategy.generate_signal(df)
    
    # Check we got the expected hold signal (None or 0)
    assert signal == 0


def test_calculate_signals_for_dataframe(strategy):
    """
    Feature: Calculate Signals for Entire DataFrame
    
    Scenario: Calculate signals for an entire DataFrame
        Given a DataFrame with OHLCV data containing crossovers
        When calculate_signals_for_dataframe is called
        Then it should return a DataFrame with signal column
        And signal values should indicate buy, sell, or hold correctly
    """
    # Create data with multiple crossovers
    dates = [datetime.now() - timedelta(minutes=i) for i in range(20)]
    close_prices = [
        100, 101, 102, 103, 104,  # Uptrend
        103, 102, 101, 100, 99,   # Downtrend
        98, 99, 100, 101, 102,    # Uptrend
        101, 100, 99, 98, 97      # Downtrend
    ]
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 2 for p in close_prices],
        'low': [p - 2 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 20
    })
    
    # Calculate signals
    result_df = strategy.calculate_signals_for_dataframe(df)
    
    # Check that signal column was added
    assert 'signal' in result_df.columns
    
    # There should be at least one buy and one sell signal
    assert (result_df['signal'] == 1).any()
    assert (result_df['signal'] == -1).any()


def test_not_enough_data(strategy):
    """
    Feature: Not Enough Data Handling
    
    Scenario: Handle case with insufficient data
        Given a DataFrame with fewer data points than required
        When calculate_indicators is called
        Then it should log a warning
        And return the DataFrame without calculations
    """
    # Create a DataFrame with not enough data
    dates = [datetime.now() - timedelta(minutes=i) for i in range(3)]
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [100, 101, 102],
        'high': [103, 104, 105],
        'low': [98, 99, 100],
        'close': [101, 102, 103],
        'volume': [1000, 1100, 1200]
    })
    
    # Spy on the logger
    strategy.logger = MagicMock()
    
    # Call calculate_indicators
    result_df = strategy.calculate_indicators(df)
    
    # Verify that a warning was logged
    strategy.logger.warning.assert_called_once()
    
    # Verify that no indicator columns were added
    assert 'short_sma' not in result_df.columns
    assert 'long_sma' not in result_df.columns 