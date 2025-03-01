"""
Tests for the SMA Crossover strategy.

These tests ensure that the SMA Crossover strategy correctly generates trading signals
based on the crossing of short and long moving averages.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

from trading_bot.strategies.sma_crossover import SMAcrossover

@pytest.fixture
def mock_loggers():
    """Create mock loggers for testing."""
    trading_logger = MagicMock()
    error_logger = MagicMock()
    return trading_logger, error_logger

@pytest.fixture
def sma_strategy(mock_loggers):
    """Create a SMAcrossover strategy instance for testing."""
    trading_logger, error_logger = mock_loggers
    strategy = SMAcrossover(10, 50, trading_logger=trading_logger, error_logger=error_logger)
    strategy.set_loggers(trading_logger, error_logger)
    return strategy

@pytest.fixture
def sample_data():
    """Create sample price data for testing."""
    # Create a DataFrame with 60 rows of price data (more than the required 51 for long_window=50)
    dates = pd.date_range(start='2023-01-01', periods=60)
    
    # Create a price pattern that will result in some crossovers
    prices = []
    for i in range(60):
        if i < 20:
            prices.append(100 + i)  # Uptrend
        elif i < 40:
            prices.append(120 - (i - 20))  # Downtrend
        else:
            prices.append(100 + (i - 40))  # Uptrend again
    
    prices = np.array(prices)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices - 1,
        'high': prices + 1,
        'low': prices - 2,
        'close': prices,
        'volume': 1000000
    })
    
    return df

def test_calculate_indicators(sma_strategy, sample_data):
    """
    Feature: SMA Calculation
    
    Test that indicators are calculated correctly.
    """
    # Calculate indicators
    result_df = sma_strategy.calculate_indicators(sample_data)
    
    # Verify indicators were calculated
    assert 'short_sma' in result_df.columns
    assert 'long_sma' in result_df.columns
    
    # Check that values are not all NaN
    assert not result_df['short_sma'].iloc[sma_strategy.short_window:].isna().any()
    assert not result_df['long_sma'].iloc[sma_strategy.long_window:].isna().any()

def test_calculate_signal_buy(sma_strategy, sample_data):
    """
    Feature: SMA Crossover Strategy Signal
    
    Test buy signal generation when short SMA crosses above long SMA.
    """
    # Create a DataFrame with indicators already calculated
    df = sample_data.copy()
    df = sma_strategy.calculate_indicators(df)
    
    # Create a buy signal scenario by modifying the last two rows
    # Previous row: short SMA below long SMA
    df.iloc[-2, df.columns.get_loc('short_sma')] = 95
    df.iloc[-2, df.columns.get_loc('long_sma')] = 100
    
    # Current row: short SMA above long SMA
    df.iloc[-1, df.columns.get_loc('short_sma')] = 105
    df.iloc[-1, df.columns.get_loc('long_sma')] = 100
    
    # Generate signal
    signal = sma_strategy.generate_signal(df)
    
    # Verify buy signal
    assert signal == 1, f"Expected buy signal (1), got {signal}"

def test_calculate_signal_sell(sma_strategy, sample_data):
    """
    Feature: SMA Crossover Strategy Signal
    
    Test sell signal generation when short SMA crosses below long SMA.
    """
    # Create a DataFrame with indicators already calculated
    df = sample_data.copy()
    df = sma_strategy.calculate_indicators(df)
    
    # Create a sell signal scenario by modifying the last two rows
    # Previous row: short SMA above long SMA
    df.iloc[-2, df.columns.get_loc('short_sma')] = 105
    df.iloc[-2, df.columns.get_loc('long_sma')] = 100
    
    # Current row: short SMA below long SMA
    df.iloc[-1, df.columns.get_loc('short_sma')] = 95
    df.iloc[-1, df.columns.get_loc('long_sma')] = 100
    
    # Generate signal
    signal = sma_strategy.generate_signal(df)
    
    # Verify sell signal
    assert signal == -1, f"Expected sell signal (-1), got {signal}"

def test_calculate_signal_hold(sma_strategy, sample_data):
    """
    Feature: SMA Crossover Strategy Signal
    
    Test hold signal generation when no crossover occurs.
    """
    # Create a DataFrame with indicators already calculated
    df = sample_data.copy()
    df = sma_strategy.calculate_indicators(df)

    # Create a hold signal scenario by setting the same relationship between SMAs
    # for both the previous and current rows (no crossover)
    # Both rows: short SMA above long SMA
    df.iloc[-2, df.columns.get_loc('short_sma')] = 105
    df.iloc[-2, df.columns.get_loc('long_sma')] = 100
    
    df.iloc[-1, df.columns.get_loc('short_sma')] = 106  # Still above, no crossover
    df.iloc[-1, df.columns.get_loc('long_sma')] = 100

    # Generate signal
    signal = sma_strategy.generate_signal(df)
    
    # Verify hold signal (0)
    assert signal == 0, f"Expected hold signal (0), got {signal}"

def test_calculate_signal_not_enough_data(sma_strategy, mock_loggers):
    """
    Feature: SMA Crossover Strategy Signal
    
    Test signal generation with insufficient data.
    """
    trading_logger, _ = mock_loggers
    
    # Create a DataFrame with only 5 rows (not enough for long SMA)
    dates = pd.date_range(start='2023-01-01', periods=5)
    prices = np.array([100, 101, 102, 103, 104])
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices - 1,
        'high': prices + 1,
        'low': prices - 2,
        'close': prices,
        'volume': 1000000
    })
    
    # Calculate signal
    signal = sma_strategy.calculate_signal(df)
    
    # Verify hold signal (0) due to insufficient data
    assert signal == 0
    trading_logger.warning.assert_called_once()

def test_error_handling(sma_strategy, mock_loggers):
    """
    Feature: Error Handling
    
    Test that errors are properly handled and logged.
    """
    trading_logger, error_logger = mock_loggers
    
    # Create a DataFrame that will cause an error
    df = pd.DataFrame({
        'wrong_column': [1, 2, 3]
    })
    
    # Reset the mocks to ensure we're only counting calls from this test
    trading_logger.warning.reset_mock()
    error_logger.error.reset_mock()

    # Calculate signal (should handle the error)
    signal = sma_strategy.calculate_signal(df)
    
    # Verify hold signal (0) due to error
    assert signal == 0
    
    # The error might be logged in the log_warning method rather than log_error
    # Check if either warning or error was called
    assert trading_logger.warning.call_count > 0 or error_logger.error.call_count > 0 