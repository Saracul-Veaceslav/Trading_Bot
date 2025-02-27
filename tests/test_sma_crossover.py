"""Tests for SMA Crossover Strategy"""

import unittest
import logging
from unittest.mock import MagicMock
import pandas as pd
from datetime import datetime, timedelta

from bot.strategies.sma_crossover import SMAcrossover
from bot.config.settings import STRATEGY_PARAMS


class TestSMAcrossover(unittest.TestCase):
    """Tests for the SMA Crossover strategy."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock loggers and create strategy
        self.trading_logger = MagicMock(spec=logging.Logger)
        self.error_logger = MagicMock(spec=logging.Logger)
        self.strategy = SMAcrossover(self.trading_logger, self.error_logger)
        
        # Backup and modify params for testing
        self.original_params = STRATEGY_PARAMS['sma_crossover'].copy()
        STRATEGY_PARAMS['sma_crossover'] = {'SMA_SHORT': 3, 'SMA_LONG': 5}
        self.strategy.params = STRATEGY_PARAMS['sma_crossover']
    
    def tearDown(self):
        """Clean up after tests."""
        STRATEGY_PARAMS['sma_crossover'] = self.original_params
    
    def test_calculate_signal_not_enough_data(self):
        """
        Feature: SMA Crossover Strategy Signal
        
        Scenario: Not enough data for calculation
            Given a DataFrame with less data points than required for long SMA
            When calculate_signal is called
            Then it should return 0 (HOLD signal)
            And log a warning message
        """
        # Create test data
        dates = [datetime.now() - timedelta(minutes=i) for i in range(3)]
        df = pd.DataFrame({
            'timestamp': dates,
            'open': [100, 101, 102],
            'high': [103, 104, 105],
            'low': [98, 99, 100],
            'close': [101, 102, 103],
            'volume': [1000, 1100, 1200]
        })
        
        # Test
        signal = self.strategy.calculate_signal(df)
        self.assertEqual(signal, 0)
        self.trading_logger.warning.assert_called_once()
    
    def test_calculate_signal_buy(self):
        """
        Feature: SMA Crossover Strategy Signal
        
        Scenario: Generate BUY signal
            Given a DataFrame with price data
            And the short SMA crosses above the long SMA in the most recent candles
            When calculate_signal is called
            Then it should return 1 (BUY signal)
            And log an info message about the buy signal
        """
        # Create data with short SMA crossing above long SMA
        dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
        close_prices = [100, 101, 103, 102, 99, 98, 97, 95, 94, 93]
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices,
            'high': [p + 2 for p in close_prices],
            'low': [p - 2 for p in close_prices],
            'close': close_prices,
            'volume': [1000] * 10
        })
        
        # Test
        signal = self.strategy.calculate_signal(df)
        self.assertEqual(signal, 1)
        self.trading_logger.info.assert_called_once()
    
    def test_calculate_signal_sell(self):
        """
        Feature: SMA Crossover Strategy Signal
        
        Scenario: Generate SELL signal
            Given a DataFrame with price data
            And the short SMA crosses below the long SMA in the most recent candles
            When calculate_signal is called
            Then it should return -1 (SELL signal)
            And log an info message about the sell signal
        """
        # Create data with short SMA crossing below long SMA
        dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
        close_prices = [90, 91, 89, 92, 95, 98, 101, 103, 102, 101]
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices,
            'high': [p + 2 for p in close_prices],
            'low': [p - 2 for p in close_prices],
            'close': close_prices,
            'volume': [1000] * 10
        })
        
        # Test
        signal = self.strategy.calculate_signal(df)
        self.assertEqual(signal, -1)
        self.trading_logger.info.assert_called_once()
    
    def test_calculate_signal_hold(self):
        """
        Feature: SMA Crossover Strategy Signal
        
        Scenario: Generate HOLD signal
            Given a DataFrame with price data
            And there is no SMA crossover in the most recent candles
            When calculate_signal is called
            Then it should return 0 (HOLD signal)
            And not log any signal info messages
        """
        # Create data with no crossover
        dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
        close_prices = [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]  # Steadily increasing
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices,
            'high': [p + 2 for p in close_prices],
            'low': [p - 2 for p in close_prices],
            'close': close_prices,
            'volume': [1000] * 10
        })
        
        self.trading_logger.info.reset_mock()
        
        # Test
        signal = self.strategy.calculate_signal(df)
        self.assertEqual(signal, 0)
        self.trading_logger.info.assert_not_called()
    
    def test_calculate_signals_for_dataframe(self):
        """
        Feature: SMA Crossover Dataframe Analysis
        
        Scenario: Calculate signals for an entire DataFrame
            Given a DataFrame with price data
            When calculate_signals_for_dataframe is called
            Then it should return a DataFrame with SMA columns and signal values
            And signal values should be 1, -1, or 0 based on SMA crossovers
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
        
        # Test
        result_df = self.strategy.calculate_signals_for_dataframe(df)
        
        self.assertIn('sma_short', result_df.columns)
        self.assertIn('sma_long', result_df.columns)
        self.assertIn('signal', result_df.columns)
        
        # Check signals
        self.assertTrue((result_df['signal'] == 1).any())
        self.assertTrue((result_df['signal'] == -1).any())
    
    def test_error_handling(self):
        """
        Feature: Error Handling
        
        Scenario: Handle calculation errors
            Given a DataFrame with invalid data
            When calculate_signal is called and an exception occurs
            Then it should catch the exception
            And log an error message
            And return 0 (HOLD signal)
        """
        # Create invalid data
        df = pd.DataFrame({
            'timestamp': [datetime.now()],
            'open': [100],
            'high': [103],
            'low': [98],
            'close': ['invalid'],  # String instead of number
            'volume': [1000]
        })
        
        # Test
        signal = self.strategy.calculate_signal(df)
        self.assertEqual(signal, 0)
        self.error_logger.exception.assert_called_once()


if __name__ == '__main__':
    unittest.main() 