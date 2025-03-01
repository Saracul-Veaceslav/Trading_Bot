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

from trading_bot.strategies.sma_crossover import SMAcrossover


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
    
    # Check we got the expected hold signal (0)
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


def test_initialization_boundary_min_window():
    """
    Feature: Strategy Initialization with Minimum Values (BVA)
    
    Scenario: Strategy initializes with minimum valid window values
        Given a short window of 1 and a valid long window
        When a new SMAcrossover strategy is created
        Then it should initialize successfully with these parameters
    """
    # Test with minimum valid short window
    strategy = SMAcrossover(short_window=1, long_window=5)
    
    # Verify parameters
    assert strategy.short_window == 1
    assert strategy.long_window == 5
    assert strategy.min_required_candles == 6


def test_initialization_boundary_adjacent_windows():
    """
    Feature: Strategy Initialization with Adjacent Window Values (BVA)
    
    Scenario: Strategy initialization with adjacent window values (almost invalid)
        Given a short window of N and a long window of N+1
        When a new SMAcrossover strategy is created
        Then it should initialize successfully with these parameters
    """
    # Test with adjacent window values (nearest valid values to an invalid combination)
    strategy = SMAcrossover(short_window=5, long_window=6)
    
    # Verify parameters
    assert strategy.short_window == 5
    assert strategy.long_window == 6
    assert strategy.min_required_candles == 7


def test_initialization_boundary_large_windows():
    """
    Feature: Strategy Initialization with Large Window Values (BVA)
    
    Scenario: Strategy initializes with extremely large window values
        Given very large short and long windows
        When a new SMAcrossover strategy is created
        Then it should initialize successfully with these parameters
    """
    # Test with very large window values
    strategy = SMAcrossover(short_window=100, long_window=500)
    
    # Verify parameters
    assert strategy.short_window == 100
    assert strategy.long_window == 500
    assert strategy.min_required_candles == 501


def test_calculate_indicators_with_minimum_data(strategy):
    """
    Feature: SMA Calculation with Minimum Required Data (BVA)
    
    Scenario: Calculate indicators with exactly the minimum required data
        Given a DataFrame with exactly min_required_candles data points
        When calculate_indicators is called
        Then it should calculate the SMAs properly
    """
    # Create data with exactly min_required_candles (long_window + 1) data points
    min_candles = strategy.min_required_candles
    dates = [datetime.now() - timedelta(minutes=i) for i in range(min_candles)]
    close_prices = [100 + i for i in range(min_candles)]
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 2 for p in close_prices],
        'low': [p - 2 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * min_candles
    })
    
    # Calculate indicators
    result_df = strategy.calculate_indicators(df)
    
    # Check that required columns were added
    assert 'short_sma' in result_df.columns
    assert 'long_sma' in result_df.columns
    
    # Verify the last row has valid SMAs (not NaN)
    assert not pd.isna(result_df['short_sma'].iloc[-1])
    assert not pd.isna(result_df['long_sma'].iloc[-1])


def test_calculate_indicators_with_insufficient_data(strategy):
    """
    Feature: SMA Calculation with Insufficient Data (BVA)
    
    Scenario: Calculate indicators with insufficient data
        Given a DataFrame with fewer than min_required_candles data points
        When calculate_indicators is called
        Then it should return the DataFrame without adding SMA columns
    """
    # Create data with fewer than min_required_candles data points
    min_candles = strategy.min_required_candles
    insufficient_candles = min_candles - 1
    dates = [datetime.now() - timedelta(minutes=i) for i in range(insufficient_candles)]
    close_prices = [100 + i for i in range(insufficient_candles)]
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 2 for p in close_prices],
        'low': [p - 2 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * insufficient_candles
    })
    
    # Calculate indicators
    result_df = strategy.calculate_indicators(df)
    
    # Check that the SMA columns were not added due to insufficient data
    assert 'short_sma' not in result_df.columns
    assert 'long_sma' not in result_df.columns
    
    # Verify the original columns are still there
    assert 'timestamp' in result_df.columns
    assert 'close' in result_df.columns
    
    # Verify the dataframe shape is unchanged
    assert len(result_df) == insufficient_candles


def test_generate_signal_with_nan_values():
    """
    Feature: Signal Generation with NaN Values (BVA)
    
    Scenario: Generate signal when some indicator values are NaN
        Given a DataFrame with NaN values in indicator columns
        When generate_signal is called
        Then it should handle the NaN values gracefully and return a safe signal (0)
    """
    # Create a strategy with custom parameters
    strategy = SMAcrossover(short_window=3, long_window=5)
    
    # Create data with 10 candles
    dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
    close_prices = [100 + i for i in range(10)]
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 2 for p in close_prices],
        'low': [p - 2 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 10
    })
    
    # Calculate indicators
    df = strategy.calculate_indicators(df)
    
    # Deliberately introduce NaN values in the last row
    df.loc[df.index[-1], 'short_sma'] = np.nan
    
    # Call generate_signal
    signal = strategy.generate_signal(df)
    
    # Check we got the expected safe signal (0) when dealing with NaN values
    assert signal == 0


def test_generate_signal_with_extreme_price_movement():
    """
    Feature: Signal Generation with Extreme Price Movement (EP)
    
    Scenario: Generate signal when there's an extreme price movement
        Given a DataFrame with a very large price jump
        When generate_signal is called
        Then it should correctly identify the resulting crossover signal
    """
    # Create a strategy with custom parameters
    strategy = SMAcrossover(short_window=3, long_window=5)
    
    # Create data with 10 candles
    dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
    close_prices = [100] * 10  # Flat prices initially
    
    # Create an extreme price movement at the end
    close_prices[-2] = 100  # Before the jump
    close_prices[-1] = 200  # Extreme jump
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 10 for p in close_prices],
        'low': [p - 10 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 10
    })
    
    # Calculate indicators
    df = strategy.calculate_indicators(df)
    
    # Call generate_signal
    signal = strategy.generate_signal(df)
    
    # Check we got the expected buy signal (1) due to the rapid short SMA increase
    assert signal == 1


def test_generate_signal_with_flat_market(strategy):
    """
    Feature: Signal Generation in Flat Market (EP)
    
    Scenario: Generate signal in a completely flat market
        Given a DataFrame with identical prices throughout
        When generate_signal is called
        Then it should return a hold signal (0)
    """
    # Create data with flat prices (completely sideways market)
    dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
    close_prices = [100] * 10  # All prices are identical
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 1 for p in close_prices],
        'low': [p - 1 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 10
    })
    
    # Calculate indicators
    df = strategy.calculate_indicators(df)
    
    # Call generate_signal
    signal = strategy.generate_signal(df)
    
    # In a flat market, short SMA equals long SMA, so there's no crossover
    assert signal == 0


def test_generate_signal_with_price_oscillation():
    """
    Feature: Signal Generation with Price Oscillation (EP)
    
    Scenario: Generate signals with oscillating prices
        Given a DataFrame with prices that oscillate up and down
        When calculate_signals_for_dataframe is called
        Then it should identify multiple buy and sell signals
    """
    # Create a strategy
    strategy = SMAcrossover(short_window=2, long_window=4)
    
    # Create oscillating price data to generate multiple crossovers
    dates = [datetime.now() - timedelta(minutes=i) for i in range(20)]
    
    # Create a series of prices that oscillate to force multiple crossovers
    close_prices = []
    for i in range(20):
        if i % 4 == 0 or i % 4 == 1:
            close_prices.append(100 + i)  # Rising prices
        else:
            close_prices.append(140 - i)  # Falling prices
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices,
        'high': [p + 5 for p in close_prices],
        'low': [p - 5 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 20
    })
    
    # Calculate signals
    result_df = strategy.calculate_signals_for_dataframe(df)
    
    # Check that there are multiple buy and sell signals
    buy_signals = (result_df['signal'] == 1).sum()
    sell_signals = (result_df['signal'] == -1).sum()
    
    # With this pattern, we should have multiple signals
    assert buy_signals > 1
    assert sell_signals > 1


def test_backtest_with_various_market_conditions():
    """
    Feature: Backtesting in Various Market Conditions (EP)
    
    Scenario: Backtest strategy performance in different market conditions
        Given data representing different market conditions (uptrend, downtrend, sideways)
        When the backtest method is called
        Then it should correctly calculate performance metrics for each condition
    """
    # Create a strategy
    strategy = SMAcrossover(short_window=3, long_window=7)
    
    # Create a test for 3 market conditions: uptrend, downtrend, and sideways
    
    # 1. Uptrend market condition
    dates_up = [datetime.now() - timedelta(minutes=i) for i in range(30)]
    close_prices_up = [100 + i for i in range(30)]  # Steadily increasing
    
    df_up = pd.DataFrame({
        'timestamp': dates_up,
        'open': close_prices_up,
        'high': [p + 2 for p in close_prices_up],
        'low': [p - 2 for p in close_prices_up],
        'close': close_prices_up,
        'volume': [1000] * 30
    })
    
    # 2. Downtrend market condition
    dates_down = [datetime.now() - timedelta(minutes=i) for i in range(30)]
    close_prices_down = [129 - i for i in range(30)]  # Steadily decreasing
    
    df_down = pd.DataFrame({
        'timestamp': dates_down,
        'open': close_prices_down,
        'high': [p + 2 for p in close_prices_down],
        'low': [p - 2 for p in close_prices_down],
        'close': close_prices_down,
        'volume': [1000] * 30
    })
    
    # 3. Sideways market condition
    dates_side = [datetime.now() - timedelta(minutes=i) for i in range(30)]
    close_prices_side = [100 + (i % 6) for i in range(30)]  # Oscillating in a range
    
    df_side = pd.DataFrame({
        'timestamp': dates_side,
        'open': close_prices_side,
        'high': [p + 2 for p in close_prices_side],
        'low': [p - 2 for p in close_prices_side],
        'close': close_prices_side,
        'volume': [1000] * 30
    })
    
    # Run backtests
    results_up = strategy.backtest(df_up)
    results_down = strategy.backtest(df_down)
    results_side = strategy.backtest(df_side)
    
    # Verify we get reasonable performance metrics for each market condition
    assert isinstance(results_up['total_return'], float)
    assert isinstance(results_down['total_return'], float)
    assert isinstance(results_side['total_return'], float)
    
    # In an uptrend, the strategy should ideally have some positive return
    # In a downtrend, the strategy might avoid some losses
    # In a sideways market, the return might be closer to zero or slightly negative due to overtrading
    
    # Check that the backtest returns all expected metrics
    expected_keys = ['total_return', 'max_drawdown', 'buy_signals', 'sell_signals', 
                     'final_balance', 'portfolio']
    
    for key in expected_keys:
        assert key in results_up
        assert key in results_down
        assert key in results_side


def test_set_parameters_with_invalid_values():
    """
    Feature: Parameter Validation (BVA)
    
    Scenario: Attempt to set invalid parameters
        Given a strategy instance
        When set_parameters is called with invalid values
        Then it should return False and not update the parameters
    """
    # Create a strategy with valid parameters
    strategy = SMAcrossover(short_window=10, long_window=20)
    
    # Try to set invalid parameters (short_window >= long_window)
    result = strategy.set_parameters({'short_window': 25, 'long_window': 20})
    
    # Verify that set_parameters returned False and parameters weren't changed
    assert result is False
    assert strategy.short_window == 10  # Original value preserved
    assert strategy.long_window == 20  # Original value preserved 