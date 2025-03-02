"""
Test for RSI Strategy

This module contains tests for the RSI strategy implementation.
"""
import unittest
from unittest.mock import patch, MagicMock
import logging
import pandas as pd
import numpy as np

try:
    from abidance.strategy.rsi import RSIStrategy, RSIConfig
    HAS_NEW_IMPLEMENTATION = True
except ImportError:
    # Fall back to old implementation
    from abidance.strategy.rsi import RSIStrategy
    HAS_NEW_IMPLEMENTATION = False


def get_strategy_instance(params=None):
    """Factory function to create an RSI strategy instance."""
    if HAS_NEW_IMPLEMENTATION:
        # Create config with required parameters
        config = RSIConfig(
            name="RSI Test Strategy",
            symbols=["BTC/USD"],
        )
        # Add any additional parameters
        if params:
            for key, value in params.items():
                setattr(config, key, value)
        return RSIStrategy(config)
    else:
        strategy = RSIStrategy()
        if params:
            for key, value in params.items():
                setattr(strategy.params, key, value)
        return strategy


class TestRSIStrategy(unittest.TestCase):
    """Test case for the RSI strategy."""

    def setUp(self):
        """Set up the test environment."""
        # Mock logger
        self.logger_patcher = patch('abidance.strategy.base.logging.getLogger')
        self.mock_logger = self.logger_patcher.start()
        self.mock_logger.return_value = MagicMock()

        # Create a strategy instance with test parameters
        self.params = {
            'rsi_period': 5,
            'oversold_threshold': 30,
            'overbought_threshold': 70,
        }
        self.strategy = get_strategy_instance(self.params)
        
        # Set up test data
        self.create_test_data()

    def tearDown(self):
        """Clean up after the test."""
        self.logger_patcher.stop()

    def create_test_data(self):
        """Create test market data."""
        # Create sample price data with known RSI pattern
        prices = [100.0, 102.0, 104.0, 103.0, 101.0, 99.0, 97.0, 96.0, 99.0, 103.0, 107.0, 105.0]
        
        # Create a DataFrame with OHLCV data
        self.test_data = pd.DataFrame({
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [1000] * len(prices)
        })
        
        # Set the index to be datetime for realism
        self.test_data.index = pd.date_range(start='2023-01-01', periods=len(prices), freq='1d')

    def test_calculate_indicators(self):
        """Test the calculation of RSI indicators."""
        result = self.strategy.calculate_indicators(self.test_data)
        
        # Check that the RSI column was added
        self.assertIn('rsi', result.columns)
        
        # Check that the crossover columns were added
        self.assertIn('oversold_crossover', result.columns)
        self.assertIn('overbought_crossover', result.columns)
        
        # Check the is_oversold and is_overbought columns
        self.assertIn('is_oversold', result.columns)
        self.assertIn('is_overbought', result.columns)

    def test_analyze_not_enough_data(self):
        """Test that analyze handles the case of insufficient data."""
        # Create data with too few rows
        short_data = self.test_data.iloc[:3]
        
        # Analyze should return an error
        result = self.strategy.analyze('BTC/USD', short_data)
        self.assertIn('error', result)
        self.assertEqual('Not enough data', result['error'])

    def test_analyze_with_enough_data(self):
        """Test that analyze produces expected results with sufficient data."""
        # Analyze the test data
        result = self.strategy.analyze('BTC/USD', self.test_data)
        
        # Check that analysis results are as expected
        self.assertEqual('BTC/USD', result['symbol'])
        self.assertIn('rsi', result)
        self.assertIn('prev_rsi', result)
        self.assertIn('is_oversold', result)
        self.assertIn('is_overbought', result)
        self.assertIn('oversold_crossover', result)
        self.assertIn('overbought_crossover', result)
        self.assertIn('data', result)

    def test_create_signal(self):
        """Test the create_signal method."""
        # Mock an analysis result
        analysis = {
            'symbol': 'BTC/USD',
            'timestamp': pd.Timestamp('2023-01-01'),
            'close': 100.0,
            'rsi': 25.0,
        }
        
        # Test creating a buy signal
        buy_signal = self.strategy.create_signal('BTC/USD', analysis, 'buy')
        self.assertEqual('buy', buy_signal['type'])
        self.assertIn('reason', buy_signal)
        self.assertEqual(100.0, buy_signal['price'])
        
        # Test creating a sell signal
        sell_signal = self.strategy.create_signal('BTC/USD', analysis, 'sell')
        self.assertEqual('sell', sell_signal['type'])
        self.assertIn('reason', sell_signal)
        self.assertEqual(100.0, sell_signal['price'])

    def test_generate_signals_oversold_crossover(self):
        """Test signal generation on oversold crossover."""
        # Mock an analysis result with oversold crossover
        analysis = {
            'symbol': 'BTC/USD',
            'timestamp': pd.Timestamp('2023-01-01'),
            'close': 100.0,
            'rsi': 31.0,
            'prev_rsi': 29.0,
            'is_oversold': False,
            'is_overbought': False,
            'oversold_crossover': True,
            'overbought_crossover': False,
        }
        
        # Generate signals
        signals = self.strategy.generate_signals('BTC/USD', analysis)
        
        # Should have one buy signal
        self.assertEqual(1, len(signals))
        self.assertEqual('buy', signals[0]['type'])

    def test_generate_signals_overbought_crossover(self):
        """Test signal generation on overbought crossover."""
        # Mock an analysis result with overbought crossover
        analysis = {
            'symbol': 'BTC/USD',
            'timestamp': pd.Timestamp('2023-01-01'),
            'close': 100.0,
            'rsi': 69.0,
            'prev_rsi': 71.0,
            'is_oversold': False,
            'is_overbought': False,
            'oversold_crossover': False,
            'overbought_crossover': True,
        }
        
        # Generate signals
        signals = self.strategy.generate_signals('BTC/USD', analysis)
        
        # Should have one sell signal
        self.assertEqual(1, len(signals))
        self.assertEqual('sell', signals[0]['type'])

    def test_generate_signals_no_crossover(self):
        """Test signal generation with no crossover."""
        # Mock an analysis result with no crossover
        analysis = {
            'symbol': 'BTC/USD',
            'timestamp': pd.Timestamp('2023-01-01'),
            'close': 100.0,
            'rsi': 50.0,
            'prev_rsi': 48.0,
            'is_oversold': False,
            'is_overbought': False,
            'oversold_crossover': False,
            'overbought_crossover': False,
        }
        
        # Generate signals
        signals = self.strategy.generate_signals('BTC/USD', analysis)
        
        # Should have no signals
        self.assertEqual(0, len(signals))

    def test_create_order_buy(self):
        """Test order creation for buy signals."""
        # Create a buy signal
        signal = {
            'symbol': 'BTC/USD',
            'timestamp': pd.Timestamp('2023-01-01'),
            'type': 'buy',
            'price': 100.0,
            'reason': 'RSI crossed above oversold level',
        }
        
        # Create an order
        order = self.strategy.create_order(signal)
        
        # Check order properties
        self.assertEqual('BTC/USD', order.symbol)
        self.assertEqual('buy', order.side.value.lower())
        self.assertEqual('market', order.order_type.value.lower())
        self.assertEqual(100.0, order.price)

    def test_create_order_sell(self):
        """Test order creation for sell signals."""
        # Create a sell signal
        signal = {
            'symbol': 'BTC/USD',
            'timestamp': pd.Timestamp('2023-01-01'),
            'type': 'sell',
            'price': 100.0,
            'reason': 'RSI crossed below overbought level',
        }
        
        # Create an order
        order = self.strategy.create_order(signal)
        
        # Check order properties
        self.assertEqual('BTC/USD', order.symbol)
        self.assertEqual('sell', order.side.value.lower())
        self.assertEqual('market', order.order_type.value.lower())
        self.assertEqual(100.0, order.price)

    def test_create_order_unknown_type(self):
        """Test order creation with an unknown signal type."""
        # Create a signal with an unknown type
        signal = {
            'symbol': 'BTC/USD',
            'timestamp': pd.Timestamp('2023-01-01'),
            'type': 'unknown',
            'price': 100.0,
            'reason': 'Unknown reason',
        }
        
        # Create an order
        order = self.strategy.create_order(signal)
        
        # Should not create an order for unknown signal type
        self.assertIsNone(order)


if __name__ == '__main__':
    unittest.main() 