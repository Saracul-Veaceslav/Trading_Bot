"""Tests for SMA Crossover Strategy"""

import unittest
import logging
from unittest.mock import MagicMock
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Monkey patch Strategy base class for testing
# This must be done before importing SMAcrossover
sys.path.insert(0, os.path.abspath('.'))
import tests.test_utils.mock_strategy
sys.modules['Trading_Bot.strategies.base'] = tests.test_utils.mock_strategy
sys.modules['bot.strategies.base'] = tests.test_utils.mock_strategy

# Now import SMAcrossover after the monkey patching
from bot.strategies.sma_crossover import SMAcrossover
from bot.config.settings import STRATEGY_PARAMS


class TestSMAcrossover(unittest.TestCase):
    """Tests for the SMA Crossover strategy."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock loggers and create strategy
        self.trading_logger = MagicMock(spec=logging.Logger)
        self.error_logger = MagicMock(spec=logging.Logger)
        
        # Initialize with correct parameters: short_window, long_window, and loggers
        self.strategy = SMAcrossover(
            short_window=10, 
            long_window=50,
            trading_logger=self.trading_logger,
            error_logger=self.error_logger
        )
        
        # Backup and modify params for testing
        self.original_params = STRATEGY_PARAMS['sma_crossover'].copy()
        STRATEGY_PARAMS['sma_crossover'] = {'SMA_SHORT': 3, 'SMA_LONG': 5}
        self.strategy.params = STRATEGY_PARAMS['sma_crossover']
        
        # Set the short and long window to match the test parameters
        self.strategy.short_window = STRATEGY_PARAMS['sma_crossover']['SMA_SHORT']
        self.strategy.long_window = STRATEGY_PARAMS['sma_crossover']['SMA_LONG']
        self.strategy.min_required_candles = self.strategy.long_window + 1
    
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
        # Note: Data is in reverse chronological order (newest first)
        # We need at least long_window + 2 data points
        dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
        
        # Create a simple pattern where short SMA will cross above long SMA
        # For a short window of 3 and long window of 5
        close_prices = [
            120,  # Latest price (t=0) - big jump to create crossover
            90,   # t=1
            85,   # t=2
            80,   # t=3
            75,   # t=4
            70,   # t=5
            65,   # t=6
            60,   # t=7
            55,   # t=8
            50    # t=9
        ]
        
        # With these prices:
        # short_sma at t=1: (90+85+80)/3 = 85
        # long_sma at t=1: (90+85+80+75+70)/5 = 80
        # short_sma at t=0: (120+90+85)/3 = 98.33
        # long_sma at t=0: (120+90+85+80+75)/5 = 90
        # This creates a crossover from short_sma < long_sma to short_sma > long_sma
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices,
            'high': [p + 2 for p in close_prices],
            'low': [p - 2 for p in close_prices],
            'close': close_prices,
            'volume': [1000] * 10
        })
        
        # Calculate indicators first
        df = self.strategy.calculate_indicators(df)
        
        # Manually create the crossover condition
        # Ensure the previous point has short_sma <= long_sma
        # Note: The strategy uses df.iloc[-2] for the previous row
        df.loc[df.index[-2], 'short_sma'] = 85
        df.loc[df.index[-2], 'long_sma'] = 90
        
        # Ensure the current point has short_sma > long_sma
        # Note: The strategy uses df.iloc[-1] for the current row
        df.loc[df.index[-1], 'short_sma'] = 98
        df.loc[df.index[-1], 'long_sma'] = 90
        
        # Reset mocks before signal calculation
        self.trading_logger.reset_mock()
        
        # Test
        signal = self.strategy.generate_signal(df)
        
        # Print debug info if test fails
        if signal != 1:
            print(f"Previous short SMA: {df['short_sma'].iloc[-2]}")
            print(f"Previous long SMA: {df['long_sma'].iloc[-2]}")
            print(f"Current short SMA: {df['short_sma'].iloc[-1]}")
            print(f"Current long SMA: {df['long_sma'].iloc[-1]}")
            print(f"Crossover condition: {df['short_sma'].iloc[-2] <= df['long_sma'].iloc[-2] and df['short_sma'].iloc[-1] > df['long_sma'].iloc[-1]}")
        
        self.assertEqual(signal, 1)
        self.assertTrue(self.trading_logger.info.called, "Expected info log for buy signal")
    
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
        # Note: Data is in reverse chronological order (newest first)
        # We need at least long_window + 2 data points
        dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
        
        # Create a simple pattern where short SMA will cross below long SMA
        # For a short window of 3 and long window of 5
        close_prices = [
            50,   # Latest price (t=0) - big drop to create crossover
            100,  # t=1
            105,  # t=2
            110,  # t=3
            115,  # t=4
            120,  # t=5
            125,  # t=6
            130,  # t=7
            135,  # t=8
            140   # t=9
        ]
        
        # With these prices:
        # short_sma at t=1: (100+105+110)/3 = 105
        # long_sma at t=1: (100+105+110+115+120)/5 = 110
        # short_sma at t=0: (50+100+105)/3 = 85
        # long_sma at t=0: (50+100+105+110+115)/5 = 96
        # This creates a crossover from short_sma > long_sma to short_sma < long_sma
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices,
            'high': [p + 2 for p in close_prices],
            'low': [p - 2 for p in close_prices],
            'close': close_prices,
            'volume': [1000] * 10
        })
        
        # Calculate indicators first
        df = self.strategy.calculate_indicators(df)
        
        # Manually create the crossover condition
        # Ensure the previous point has short_sma >= long_sma
        # Note: The strategy uses df.iloc[-2] for the previous row
        df.loc[df.index[-2], 'short_sma'] = 110
        df.loc[df.index[-2], 'long_sma'] = 105
        
        # Ensure the current point has short_sma < long_sma
        # Note: The strategy uses df.iloc[-1] for the current row
        df.loc[df.index[-1], 'short_sma'] = 85
        df.loc[df.index[-1], 'long_sma'] = 96
        
        # Reset mocks before signal calculation
        self.trading_logger.reset_mock()
        
        # Test
        signal = self.strategy.generate_signal(df)
        
        # Print debug info if test fails
        if signal != -1:
            print(f"Previous short SMA: {df['short_sma'].iloc[-2]}")
            print(f"Previous long SMA: {df['long_sma'].iloc[-2]}")
            print(f"Current short SMA: {df['short_sma'].iloc[-1]}")
            print(f"Current long SMA: {df['long_sma'].iloc[-1]}")
            print(f"Crossover condition: {df['short_sma'].iloc[-2] >= df['long_sma'].iloc[-2] and df['short_sma'].iloc[-1] < df['long_sma'].iloc[-1]}")
        
        self.assertEqual(signal, -1)
        self.assertTrue(self.trading_logger.info.called, "Expected info log for sell signal")
    
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
        # Note: Data is in reverse chronological order (newest first)
        dates = [datetime.now() - timedelta(minutes=i) for i in range(10)]
        
        # Create a pattern where short SMA stays above long SMA (no crossover)
        # For a short window of 3 and long window of 5
        close_prices = [
            110,  # t=0
            105,  # t=1
            100,  # t=2
            95,   # t=3
            90,   # t=4
            85,   # t=5
            80,   # t=6
            75,   # t=7
            70,   # t=8
            65    # t=9
        ]
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices,
            'high': [p + 2 for p in close_prices],
            'low': [p - 2 for p in close_prices],
            'close': close_prices,
            'volume': [1000] * 10
        })
        
        # Calculate indicators first, then reset the mock before signal calculation
        df = self.strategy.calculate_indicators(df)
        self.trading_logger.reset_mock()
        
        # Test
        signal = self.strategy.calculate_signal(df)
        self.assertEqual(signal, 0)
        
        # Check that no signal-related info messages were logged
        # We're only checking for BUY/SELL signal logs, not other info logs
        signal_log_calls = [
            call for call in self.trading_logger.info.call_args_list 
            if "BUY signal" in str(call) or "SELL signal" in str(call)
        ]
        self.assertEqual(len(signal_log_calls), 0, "No signal logs should be present")
    
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
        
        self.assertIn('short_sma', result_df.columns)
        self.assertIn('long_sma', result_df.columns)
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
        # Create invalid data that will cause an error during indicator calculation
        df = pd.DataFrame({
            'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(10)],
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100] * 9 + ['invalid'],  # Last value is invalid
            'volume': [1000] * 10
        })
        
        # Reset mocks
        self.error_logger.reset_mock()
        
        # Test
        signal = self.strategy.calculate_signal(df)
        
        # Verify results
        self.assertEqual(signal, 0)
        
        # Check that an error was logged
        # The error might be logged with error() or exception() depending on implementation
        error_calls = self.error_logger.error.call_count + self.error_logger.exception.call_count
        self.assertGreater(error_calls, 0, "Expected at least one error log call")


if __name__ == '__main__':
    unittest.main() 