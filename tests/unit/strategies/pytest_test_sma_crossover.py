"""
Tests for the SMA Crossover strategy.

These tests ensure that the SMA Crossover strategy correctly generates trading signals
based on the crossing of short and long moving averages.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

from trading_bot.strategies.sma_crossover import SMAcrossover

@pytest.fixture
def mock_loggers():
    """Create mock loggers for testing."""
    trading_logger = MagicMock()
    error_logger = MagicMock()
    return trading_logger, error_logger

@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing."""
    # Create a DataFrame with 100 rows of sample data
    np.random.seed(42)  # For reproducibility
    
    dates = pd.date_range(start='2023-01-01', periods=100, freq='h')
    
    # Generate random price data with some trend
    close_prices = np.random.normal(100, 10, 100)
    # Add some trend to make crossovers more likely
    for i in range(1, 100):
        if i > 50:
            close_prices[i] = close_prices[i-1] * (1 + np.random.normal(-0.01, 0.02))
        else:
            close_prices[i] = close_prices[i-1] * (1 + np.random.normal(0.01, 0.02))
    
    # Create OHLCV data
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices * (1 + np.random.normal(0, 0.01, 100)),
        'high': close_prices * (1 + np.random.normal(0.01, 0.01, 100)),
        'low': close_prices * (1 + np.random.normal(-0.01, 0.01, 100)),
        'close': close_prices,
        'volume': np.random.normal(1000, 200, 100).astype(int)
    })
    
    return df

@pytest.fixture
def sma_strategy(mock_loggers):
    """Create an SMA crossover strategy instance for testing."""
    trading_logger, error_logger = mock_loggers
    
    # Create strategy with mock loggers
    strategy = SMAcrossover(
        short_window=10,
        long_window=20,
        trading_logger=trading_logger,
        error_logger=error_logger
    )
    
    return strategy

def test_calculate_indicators(sma_strategy, sample_data):
    """Test that indicators are calculated correctly."""
    result = sma_strategy.calculate_indicators(sample_data)
    
    # Check that the result contains the expected columns
    assert 'short_sma' in result.columns
    assert 'long_sma' in result.columns
    assert 'sma_diff' in result.columns
    
    # Check that the SMAs are calculated correctly
    # For the first short_period-1 rows, short_sma should be NaN
    assert result['short_sma'].iloc[:9].isna().all()
    
    # For the first long_period-1 rows, long_sma should be NaN
    assert result['long_sma'].iloc[:19].isna().all()
    
    # After that, values should be calculated (starting from index 20)
    assert not result['short_sma'].iloc[10:].isna().any()
    # Check from index 20 onwards to avoid NaN values
    assert not result['long_sma'].iloc[20:].isna().any()

def test_calculate_signal_buy(sma_strategy, sample_data):
    """Test that buy signals are generated correctly."""
    # Create a DataFrame with indicators already calculated
    df = sample_data.copy()
    df = sma_strategy.calculate_indicators(df)
    
    # Create a buy signal scenario by modifying the last two rows
    # Previous row: short SMA below long SMA
    df.iloc[-2, df.columns.get_loc('short_sma')] = 95
    df.iloc[-2, df.columns.get_loc('long_sma')] = 100
    
    # Current row: short SMA above long SMA (crossover)
    df.iloc[-1, df.columns.get_loc('short_sma')] = 105
    df.iloc[-1, df.columns.get_loc('long_sma')] = 100
    
    signal = sma_strategy.calculate_signal(df)
    
    # Check that a buy signal is generated at the crossover
    assert signal == 1

def test_calculate_signal_sell(sma_strategy, sample_data):
    """Test that sell signals are generated correctly."""
    # Create a DataFrame with indicators already calculated
    df = sample_data.copy()
    df = sma_strategy.calculate_indicators(df)
    
    # Create a sell signal scenario by modifying the last two rows
    # Previous row: short SMA above long SMA
    df.iloc[-2, df.columns.get_loc('short_sma')] = 105
    df.iloc[-2, df.columns.get_loc('long_sma')] = 100
    
    # Current row: short SMA below long SMA (crossover)
    df.iloc[-1, df.columns.get_loc('short_sma')] = 95
    df.iloc[-1, df.columns.get_loc('long_sma')] = 100
    
    signal = sma_strategy.calculate_signal(df)
    
    # Check that a sell signal is generated at the crossover
    assert signal == -1

def test_calculate_signal_hold(sma_strategy, sample_data):
    """Test that hold signals are generated correctly when no crossover occurs."""
    # Create a DataFrame with indicators already calculated
    df = sample_data.copy()
    df = sma_strategy.calculate_indicators(df)
    
    # Create a hold signal scenario by modifying the last two rows
    # Both rows have short SMA above long SMA (no crossover)
    df.iloc[-2, df.columns.get_loc('short_sma')] = 105
    df.iloc[-2, df.columns.get_loc('long_sma')] = 100
    
    df.iloc[-1, df.columns.get_loc('short_sma')] = 110
    df.iloc[-1, df.columns.get_loc('long_sma')] = 100
    
    signal = sma_strategy.calculate_signal(df)
    
    # Check that a hold signal is generated (no crossover)
    assert signal == 0

def test_calculate_signal_not_enough_data(sma_strategy):
    """Test behavior when there's not enough data for calculation."""
    # Create a small DataFrame with insufficient data
    small_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=5, freq='h'),
        'open': [100] * 5,
        'high': [105] * 5,
        'low': [95] * 5,
        'close': [102] * 5,
        'volume': [1000] * 5
    })
    
    # Calculate indicators
    data_with_indicators = sma_strategy.calculate_indicators(small_data)
    
    # Calculate signal
    signal = sma_strategy.calculate_signal(data_with_indicators)
    
    # Check that a hold signal is generated due to insufficient data
    assert signal == 0

def test_error_handling(sma_strategy, mock_loggers):
    """Test error handling in the strategy."""
    trading_logger, error_logger = mock_loggers
    
    # Create a DataFrame that will cause an error
    df = pd.DataFrame({
        'wrong_column': [1, 2, 3]
    })
    
    # Reset the mock to ensure we're only counting calls from this test
    error_logger.error.reset_mock()
    trading_logger.warning.reset_mock()
    
    # Calculate signal (should handle the error)
    signal = sma_strategy.calculate_signal(df)
    
    # Verify hold signal (0) due to error
    assert signal == 0
    
    # The error might be logged in the log_warning method rather than log_error
    # Check if either warning or error was called
    assert trading_logger.warning.call_count > 0 or error_logger.error.call_count > 0 