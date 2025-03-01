"""
Test for RSI Bollinger Bands Strategy

This module contains tests for the RSI Bollinger Bands strategy.
"""
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Create a proper mock for the Strategy base class
class MockStrategy:
    """Mock Strategy base class for testing."""
    BUY = 1
    SELL = -1
    HOLD = 0
    
    def __init__(self, **kwargs):
        self.name = None
        self.metadata = {}
        self.logger = kwargs.get('trading_logger', MagicMock())
        self.error_logger = kwargs.get('error_logger', MagicMock())
    
    def log_info(self, message):
        self.logger.info(message)
    
    def log_warning(self, message):
        self.logger.warning(message)
    
    def log_error(self, message):
        self.error_logger.error(message)
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
    
    def get_metadata(self):
        return self.metadata
    
    def set_metadata(self, metadata):
        self.metadata = metadata

# Mock the Strategy base class before importing the RSIBollingerStrategy
with patch('bot.strategies.base.Strategy', MockStrategy):
    from bot.strategies.rsi_bollinger import RSIBollingerStrategy

class TestRSIBollingerStrategy(unittest.TestCase):
    """Test case for the RSI Bollinger Bands strategy."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create mock loggers
        self.mock_logger = MagicMock()
        self.mock_error_logger = MagicMock()
        
        # Create strategy instance with default parameters
        self.strategy = RSIBollingerStrategy(
            rsi_period=14,
            rsi_overbought=70.0,
            rsi_oversold=30.0,
            bb_period=20,
            bb_std_dev=2.0,
            signal_threshold=0.5,
            trading_logger=self.mock_logger,
            error_logger=self.mock_error_logger
        )
        
        # Create sample data
        self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample OHLCV data for testing."""
        # Create date range
        dates = [datetime.now() - timedelta(days=i) for i in range(100, 0, -1)]
        
        # Create price data with a trend and some volatility
        base_price = 100.0
        trend = np.linspace(0, 20, 100)  # Upward trend
        volatility = np.random.normal(0, 1, 100) * 2  # Random noise
        
        # Calculate OHLCV data
        close_prices = base_price + trend + volatility
        open_prices = close_prices - np.random.normal(0, 0.5, 100)
        high_prices = np.maximum(close_prices, open_prices) + np.random.normal(0, 0.5, 100)
        low_prices = np.minimum(close_prices, open_prices) - np.random.normal(0, 0.5, 100)
        volumes = np.random.normal(1000, 200, 100)
        
        # Create DataFrame
        self.sample_data = pd.DataFrame({
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        }, index=dates)
        
        # Create data with buy signal (low RSI, price below lower BB)
        self.buy_signal_data = self.sample_data.copy()
        # Modify the last few data points to create oversold condition
        for i in range(5):
            # Use proper pandas indexing to avoid warnings
            self.buy_signal_data.loc[self.buy_signal_data.index[-5+i], 'close'] = self.buy_signal_data.loc[self.buy_signal_data.index[-6], 'close'] * 0.98
        
        # Create data with sell signal (high RSI, price above upper BB)
        self.sell_signal_data = self.sample_data.copy()
        # Modify the last few data points to create overbought condition
        for i in range(5):
            # Use proper pandas indexing to avoid warnings
            self.sell_signal_data.loc[self.sell_signal_data.index[-5+i], 'close'] = self.sell_signal_data.loc[self.sell_signal_data.index[-6], 'close'] * 1.02
    
    def test_initialization(self):
        """Test strategy initialization."""
        # Check that parameters are set correctly
        self.assertEqual(self.strategy.rsi_period, 14)
        self.assertEqual(self.strategy.rsi_overbought, 70.0)
        self.assertEqual(self.strategy.rsi_oversold, 30.0)
        self.assertEqual(self.strategy.bb_period, 20)
        self.assertEqual(self.strategy.bb_std_dev, 2.0)
        self.assertEqual(self.strategy.signal_threshold, 0.5)
        
        # Check that name and metadata are set
        self.assertEqual(self.strategy.get_name(), "RSI_Bollinger")
        metadata = self.strategy.get_metadata()
        self.assertIn("description", metadata)
        self.assertIn("parameters", metadata)
        self.assertIn("version", metadata)
    
    def test_calculate_indicators(self):
        """Test indicator calculation."""
        # Calculate indicators
        result = self.strategy.calculate_indicators(self.sample_data)
        
        # Check that all indicators are calculated
        self.assertIn('rsi', result.columns)
        self.assertIn('bb_middle', result.columns)
        self.assertIn('bb_upper', result.columns)
        self.assertIn('bb_lower', result.columns)
        self.assertIn('bb_pct_b', result.columns)
        self.assertIn('rsi_signal', result.columns)
        self.assertIn('bb_signal', result.columns)
        self.assertIn('combined_signal', result.columns)
        
        # Check that RSI is between 0 and 100
        self.assertTrue((result['rsi'].dropna() >= 0).all())
        self.assertTrue((result['rsi'].dropna() <= 100).all())
        
        # Check that Bollinger Bands are calculated correctly
        self.assertTrue((result['bb_upper'].dropna() > result['bb_middle'].dropna()).all())
        self.assertTrue((result['bb_lower'].dropna() < result['bb_middle'].dropna()).all())
        
        # Check that signal values are between 0 and 1
        self.assertTrue((result['rsi_signal'].dropna() >= 0).all())
        self.assertTrue((result['rsi_signal'].dropna() <= 1).all())
        self.assertTrue((result['bb_signal'].dropna() >= 0).all())
        self.assertTrue((result['bb_signal'].dropna() <= 1).all())
        self.assertTrue((result['combined_signal'].dropna() >= 0).all())
        self.assertTrue((result['combined_signal'].dropna() <= 1).all())
    
    def test_generate_signal_buy(self):
        """Test buy signal generation."""
        # Calculate indicators for buy signal data
        data_with_indicators = self.strategy.calculate_indicators(self.buy_signal_data)
        
        # Manually modify the indicators to ensure a buy signal
        data_with_indicators.loc[data_with_indicators.index[-1], 'rsi'] = 25.0  # Below oversold
        data_with_indicators.loc[data_with_indicators.index[-1], 'close'] = 90.0
        data_with_indicators.loc[data_with_indicators.index[-1], 'bb_lower'] = 92.0  # Price below lower band
        data_with_indicators.loc[data_with_indicators.index[-1], 'combined_signal'] = 0.2  # Strong buy signal
        
        # Generate signal
        signal = self.strategy.generate_signal(data_with_indicators)
        
        # Check that a buy signal is generated
        self.assertEqual(signal, self.strategy.BUY)
    
    def test_generate_signal_sell(self):
        """Test sell signal generation."""
        # Calculate indicators for sell signal data
        data_with_indicators = self.strategy.calculate_indicators(self.sell_signal_data)
        
        # Manually modify the indicators to ensure a sell signal
        data_with_indicators.loc[data_with_indicators.index[-1], 'rsi'] = 75.0  # Above overbought
        data_with_indicators.loc[data_with_indicators.index[-1], 'close'] = 110.0
        data_with_indicators.loc[data_with_indicators.index[-1], 'bb_upper'] = 108.0  # Price above upper band
        data_with_indicators.loc[data_with_indicators.index[-1], 'combined_signal'] = 0.8  # Strong sell signal
        
        # Generate signal
        signal = self.strategy.generate_signal(data_with_indicators)
        
        # Check that a sell signal is generated
        self.assertEqual(signal, self.strategy.SELL)
    
    def test_generate_signal_hold(self):
        """Test hold signal generation."""
        # Calculate indicators for normal data
        data_with_indicators = self.strategy.calculate_indicators(self.sample_data)
        
        # Manually modify the indicators to ensure a hold signal
        data_with_indicators.loc[data_with_indicators.index[-1], 'rsi'] = 50.0  # Neutral RSI
        data_with_indicators.loc[data_with_indicators.index[-1], 'combined_signal'] = 0.5  # Neutral signal
        
        # Generate signal
        signal = self.strategy.generate_signal(data_with_indicators)
        
        # Check that a hold signal is generated
        self.assertEqual(signal, self.strategy.HOLD)
    
    def test_calculate_signal_strength(self):
        """Test signal strength calculation."""
        # Calculate indicators
        data_with_indicators = self.strategy.calculate_indicators(self.sample_data)
        
        # Test buy signal strength
        data_with_indicators.loc[data_with_indicators.index[-1], 'combined_signal'] = 0.0
        buy_strength = self.strategy.calculate_signal_strength(data_with_indicators)
        self.assertAlmostEqual(buy_strength, 1.0)
        
        # Test sell signal strength
        data_with_indicators.loc[data_with_indicators.index[-1], 'combined_signal'] = 1.0
        sell_strength = self.strategy.calculate_signal_strength(data_with_indicators)
        self.assertAlmostEqual(sell_strength, -1.0)
        
        # Test neutral signal strength
        data_with_indicators.loc[data_with_indicators.index[-1], 'combined_signal'] = 0.5
        neutral_strength = self.strategy.calculate_signal_strength(data_with_indicators)
        self.assertAlmostEqual(neutral_strength, 0.0)
    
    def test_get_parameters(self):
        """Test getting strategy parameters."""
        # Get parameters
        parameters = self.strategy.get_parameters()
        
        # Check that all parameters are included
        self.assertIn('rsi_period', parameters)
        self.assertIn('rsi_overbought', parameters)
        self.assertIn('rsi_oversold', parameters)
        self.assertIn('bb_period', parameters)
        self.assertIn('bb_std_dev', parameters)
        self.assertIn('signal_threshold', parameters)
        
        # Check parameter values
        self.assertEqual(parameters['rsi_period'], 14)
        self.assertEqual(parameters['rsi_overbought'], 70.0)
        self.assertEqual(parameters['rsi_oversold'], 30.0)
        self.assertEqual(parameters['bb_period'], 20)
        self.assertEqual(parameters['bb_std_dev'], 2.0)
        self.assertEqual(parameters['signal_threshold'], 0.5)
    
    def test_set_parameters(self):
        """Test setting strategy parameters."""
        # Set new parameters
        new_parameters = {
            'rsi_period': 10,
            'rsi_overbought': 75.0,
            'rsi_oversold': 25.0,
            'bb_period': 15,
            'bb_std_dev': 2.5,
            'signal_threshold': 0.6
        }
        
        self.strategy.set_parameters(new_parameters)
        
        # Check that parameters are updated
        self.assertEqual(self.strategy.rsi_period, 10)
        self.assertEqual(self.strategy.rsi_overbought, 75.0)
        self.assertEqual(self.strategy.rsi_oversold, 25.0)
        self.assertEqual(self.strategy.bb_period, 15)
        self.assertEqual(self.strategy.bb_std_dev, 2.5)
        self.assertEqual(self.strategy.signal_threshold, 0.6)
    
    def test_empty_data(self):
        """Test behavior with empty data."""
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        
        # Test calculate_indicators
        result = self.strategy.calculate_indicators(empty_df)
        self.assertTrue(result.empty)
        
        # Test generate_signal
        signal = self.strategy.generate_signal(empty_df)
        self.assertEqual(signal, self.strategy.HOLD)
        
        # Test calculate_signal_strength
        strength = self.strategy.calculate_signal_strength(empty_df)
        self.assertEqual(strength, 0.0)
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        # Create data with fewer rows than required
        short_df = self.sample_data.iloc[-10:].copy()
        
        # Test generate_signal
        signal = self.strategy.generate_signal(short_df)
        self.assertEqual(signal, self.strategy.HOLD)
    
    def test_error_handling(self):
        """Test error handling in methods."""
        # Create a DataFrame that will cause errors
        bad_df = pd.DataFrame({'wrong_column': [1, 2, 3]})
        
        # Test calculate_indicators with bad data
        result = self.strategy.calculate_indicators(bad_df)
        # Should return the original data without crashing
        self.assertEqual(len(result), len(bad_df))
        
        # Test generate_signal with bad data
        signal = self.strategy.generate_signal(bad_df)
        # Should return HOLD without crashing
        self.assertEqual(signal, self.strategy.HOLD)
        
        # Test calculate_signal_strength with bad data
        strength = self.strategy.calculate_signal_strength(bad_df)
        # Should return 0.0 without crashing
        self.assertEqual(strength, 0.0)

if __name__ == '__main__':
    unittest.main() 