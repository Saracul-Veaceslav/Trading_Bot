"""
Tests for the SMA Crossover strategy.

These tests ensure that the SMA Crossover strategy correctly generates trading signals
based on the crossing of short and long moving averages.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

from Trading_Bot.strategies.sma_crossover import SMAcrossover

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
    strategy = SMAcrossover(10, 50, trading_logger=mock_trading_logger, error_logger=mock_error_logger)
    strategy.set_loggers(trading_logger, error_logger)
    return strategy

@pytest.fixture
def sample_data():
    """Create sample price data for testing."""
    # Create a DataFrame with 20 rows of price data
    dates = pd.date_range(start='2023-01-01', periods=20)
    prices = np.array([100, 101, 102, 103, 104, 105, 104, 103, 102, 101,
                       100, 99, 98, 97, 96, 95, 96, 97, 98, 99])
    
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
    assert 'sma_short' in result_df.columns
    assert 'sma_long' in result_df.columns
    
    # SMA values should be NaN for the first N-1 rows
    assert np.isnan(result_df['sma_short'].iloc[3])
    assert not np.isnan(result_df['sma_short'].iloc[4])  # 5th row should have a value
    
    assert np.isnan(result_df['sma_long'].iloc[8])
    assert not np.isnan(result_df['sma_long'].iloc[9])  # 10th row should have a value
    
    # Verify some SMA values
    expected_short_sma = np.mean(sample_data['close'].iloc[0:5])
    assert result_df['sma_short'].iloc[4] == pytest.approx(expected_short_sma)

def test_calculate_signal_buy(sma_strategy, sample_data):
    """
    Feature: SMA Crossover Strategy Signal
    
    Test buy signal generation when short SMA crosses above long SMA.
    """
    # Modify the DataFrame to create a buy signal
    # Short SMA crosses above long SMA between rows 15 and 16
    df = sample_data.copy()
    df.loc[df.index[11:16], 'close'] = [90, 85, 80, 75, 70]  # Create a downtrend
    df.loc[df.index[16:], 'close'] = [85, 90, 95, 100]       # Create a sharp uptrend
    
    # Calculate signal
    signal = sma_strategy.calculate_signal(df)
    
    # Verify buy signal (1)
    assert signal == 1

def test_calculate_signal_sell(sma_strategy, sample_data):
    """
    Feature: SMA Crossover Strategy Signal
    
    Test sell signal generation when short SMA crosses below long SMA.
    """
    # Modify the DataFrame to create a sell signal
    # Short SMA crosses below long SMA between rows 15 and 16
    df = sample_data.copy()
    df.loc[df.index[11:16], 'close'] = [110, 115, 120, 125, 130]  # Create an uptrend
    df.loc[df.index[16:], 'close'] = [115, 110, 105, 100]         # Create a sharp downtrend
    
    # Calculate signal
    signal = sma_strategy.calculate_signal(df)
    
    # Verify sell signal (-1)
    assert signal == -1

def test_calculate_signal_hold(sma_strategy, sample_data):
    """
    Feature: SMA Crossover Strategy Signal
    
    Test hold signal generation when no crossover occurs.
    """
    # Modify the DataFrame to create a situation with no crossover
    # Short SMA stays above long SMA
    df = sample_data.copy()
    df.loc[df.index[11:16], 'close'] = [90, 85, 80, 75, 70]  # Create a downtrend
    df.loc[df.index[16:], 'close'] = [65, 60, 55, 50]        # Continue the downtrend
    
    # Calculate signal
    signal = sma_strategy.calculate_signal(df)
    
    # Verify hold signal (0)
    assert signal == 0

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
    _, error_logger = mock_loggers
    
    # Create a DataFrame that will cause an error
    df = pd.DataFrame({
        'wrong_column': [1, 2, 3]
    })
    
    # Calculate signal (should handle the error)
    signal = sma_strategy.calculate_signal(df)
    
    # Verify hold signal (0) due to error
    assert signal == 0
    error_logger.error.assert_called_once() 