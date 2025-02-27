"""
Tests for Data Manager Module

This module contains tests for the DataManager class responsible for
storing and retrieving OHLCV data and trade information.
"""

import unittest
import logging
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime, timedelta

from bot.data_manager import DataManager
from bot.config.settings import SETTINGS


class TestDataManager(unittest.TestCase):
    """Tests for the Data Manager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create mock loggers
        self.trading_logger = MagicMock(spec=logging.Logger)
        self.error_logger = MagicMock(spec=logging.Logger)
        
        # Backup original settings
        self.original_historical_data_path = SETTINGS['HISTORICAL_DATA_PATH']
        self.original_historical_trades_path = SETTINGS['HISTORICAL_TRADES_PATH']
        
        # Set test file paths
        SETTINGS['HISTORICAL_DATA_PATH'] = os.path.join(self.test_dir, 'historical_data.csv')
        SETTINGS['HISTORICAL_TRADES_PATH'] = os.path.join(self.test_dir, 'historical_trades.csv')
        
        # Create data manager instance
        self.data_manager = DataManager(self.trading_logger, self.error_logger)
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original settings
        SETTINGS['HISTORICAL_DATA_PATH'] = self.original_historical_data_path
        SETTINGS['HISTORICAL_TRADES_PATH'] = self.original_historical_trades_path
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_initialize_files(self):
        """
        Feature: Data Files Initialization
        
        Scenario: Initialize data files on creation
            Given a new DataManager instance
            When it is initialized
            Then it should create the historical data and trades files if they don't exist
            And the files should have the correct headers
        """
        # Check that files were created
        self.assertTrue(os.path.exists(SETTINGS['HISTORICAL_DATA_PATH']))
        self.assertTrue(os.path.exists(SETTINGS['HISTORICAL_TRADES_PATH']))
        
        # Check file headers
        historical_data_df = pd.read_csv(SETTINGS['HISTORICAL_DATA_PATH'])
        historical_trades_df = pd.read_csv(SETTINGS['HISTORICAL_TRADES_PATH'])
        
        # Check historical data columns
        expected_data_columns = [
            'timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'strategy_signal'
        ]
        self.assertTrue(all(col in historical_data_df.columns for col in expected_data_columns))
        
        # Check trades columns
        expected_trades_columns = [
            'timestamp', 'order_id', 'symbol', 'side', 'entry_price', 'exit_price', 
            'quantity', 'pnl', 'stop_loss_triggered', 'take_profit_triggered'
        ]
        self.assertTrue(all(col in historical_trades_df.columns for col in expected_trades_columns))
    
    def test_store_ohlcv_data_new(self):
        """
        Feature: OHLCV Data Storage
        
        Scenario: Store new OHLCV data
            Given an empty historical data file
            When store_ohlcv_data is called with a DataFrame
            Then it should write the data to the file
            And log a message about storing the data
        """
        # Create test data
        dates = [datetime.now() - timedelta(minutes=i) for i in range(5)]
        df = pd.DataFrame({
            'timestamp': dates,
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # Store data
        self.data_manager.store_ohlcv_data(df, 'BTC/USDT')
        
        # Check that data was stored
        stored_df = pd.read_csv(SETTINGS['HISTORICAL_DATA_PATH'])
        self.assertEqual(len(stored_df), 5)
        self.assertEqual(stored_df['symbol'].iloc[0], 'BTC/USDT')
        
        # Check logging
        self.trading_logger.info.assert_called_once()
    
    def test_store_ohlcv_data_append(self):
        """
        Feature: OHLCV Data Storage
        
        Scenario: Append only new OHLCV data
            Given an existing historical data file with some data
            When store_ohlcv_data is called with a DataFrame containing some overlapping data
            Then it should only append the new data
            And avoid duplicates
            And log a message about storing the new data
        """
        # Create initial data
        dates1 = [datetime.now() - timedelta(minutes=i) for i in range(5)]
        df1 = pd.DataFrame({
            'timestamp': dates1,
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400],
            'symbol': ['BTC/USDT'] * 5
        })
        
        # Store initial data
        df1.to_csv(SETTINGS['HISTORICAL_DATA_PATH'], index=False)
        
        # Create new data with some overlap
        dates2 = [datetime.now() - timedelta(minutes=i) for i in range(3, 8)]  # Overlap at index 3,4
        df2 = pd.DataFrame({
            'timestamp': dates2,
            'open': [103, 104, 105, 106, 107],
            'high': [108, 109, 110, 111, 112],
            'low': [98, 99, 100, 101, 102],
            'close': [104, 105, 106, 107, 108],
            'volume': [1300, 1400, 1500, 1600, 1700]
        })
        
        # Reset mock to clear previous calls
        self.trading_logger.info.reset_mock()
        
        # Store new data
        self.data_manager.store_ohlcv_data(df2, 'BTC/USDT')
        
        # Check that data was appended without duplicates
        stored_df = pd.read_csv(SETTINGS['HISTORICAL_DATA_PATH'])
        
        # Should have 7 rows total (5 original + 2 new)
        self.assertEqual(len(stored_df), 7)
        
        # Check logging
        self.trading_logger.info.assert_called_once()
    
    def test_load_latest_ohlcv(self):
        """
        Feature: OHLCV Data Retrieval
        
        Scenario: Load latest OHLCV data
            Given a historical data file with multiple symbols
            When load_latest_ohlcv is called for a specific symbol and limit
            Then it should return the most recent data for that symbol
            And the number of rows should not exceed the limit
        """
        # Create test data with multiple symbols
        dates = [datetime.now() - timedelta(minutes=i) for i in range(20)]
        
        data = []
        for i in range(20):
            symbol = 'BTC/USDT' if i % 2 == 0 else 'ETH/USDT'
            data.append({
                'timestamp': dates[i],
                'symbol': symbol,
                'open': 100 + i,
                'high': 105 + i,
                'low': 95 + i,
                'close': 101 + i,
                'volume': 1000 + i * 100
            })
        
        df = pd.DataFrame(data)
        df.to_csv(SETTINGS['HISTORICAL_DATA_PATH'], index=False)
        
        # Load latest data
        result_df = self.data_manager.load_latest_ohlcv('BTC/USDT', limit=5)
        
        # Check results
        self.assertEqual(len(result_df), 5)  # Should respect limit
        self.assertTrue(all(row == 'BTC/USDT' for row in result_df['symbol']))  # Only BTC/USDT
        
        # Check sorting (should be ascending by timestamp)
        timestamps = pd.to_datetime(result_df['timestamp'])
        self.assertTrue(all(timestamps.iloc[i] < timestamps.iloc[i+1] for i in range(len(timestamps)-1)))
    
    def test_store_trade(self):
        """
        Feature: Trade Data Storage
        
        Scenario: Store trade information
            Given an empty trades file
            When store_trade is called with trade data
            Then it should append the trade data to the file
            And log a message about recording the trade
        """
        # Create test trade data
        trade_data = {
            'timestamp': datetime.now(),
            'order_id': '123456',
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'entry_price': 50000.0,
            'exit_price': None,
            'quantity': 0.001,
            'pnl': None,
            'stop_loss_triggered': False,
            'take_profit_triggered': False
        }
        
        # Store trade
        self.data_manager.store_trade(trade_data)
        
        # Check that trade was stored
        trades_df = pd.read_csv(SETTINGS['HISTORICAL_TRADES_PATH'])
        self.assertEqual(len(trades_df), 1)
        self.assertEqual(trades_df['order_id'].iloc[0], '123456')
        self.assertEqual(trades_df['symbol'].iloc[0], 'BTC/USDT')
        
        # Check logging
        self.trading_logger.info.assert_called_once()
    
    def test_update_trade_exit(self):
        """
        Feature: Trade Exit Update
        
        Scenario: Update trade with exit information
            Given a trades file with an open trade
            When update_trade_exit is called with exit data
            Then it should update the trade with exit information
            And log a message about updating the trade
        """
        # Create test trade data
        trade_data = {
            'timestamp': datetime.now(),
            'order_id': '123456',
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'entry_price': 50000.0,
            'exit_price': None,
            'quantity': 0.001,
            'pnl': None,
            'stop_loss_triggered': False,
            'take_profit_triggered': False
        }
        
        # Create initial trade file
        trades_df = pd.DataFrame([trade_data])
        trades_df.to_csv(SETTINGS['HISTORICAL_TRADES_PATH'], index=False)
        
        # Create exit data
        exit_data = {
            'exit_price': 51000.0,
            'pnl': 1.0,
            'stop_loss_triggered': False,
            'take_profit_triggered': True
        }
        
        # Update trade
        self.data_manager.update_trade_exit('123456', exit_data)
        
        # Check that trade was updated
        updated_df = pd.read_csv(SETTINGS['HISTORICAL_TRADES_PATH'])
        self.assertEqual(updated_df['exit_price'].iloc[0], 51000.0)
        self.assertEqual(updated_df['pnl'].iloc[0], 1.0)
        self.assertEqual(updated_df['take_profit_triggered'].iloc[0], True)
        
        # Check logging
        self.trading_logger.info.assert_called_once()
    
    def test_update_trade_exit_not_found(self):
        """
        Feature: Trade Exit Update Error Handling
        
        Scenario: Attempt to update a non-existent trade
            Given a trades file without the target trade
            When update_trade_exit is called with an unknown order ID
            Then it should log an error message
            And not modify the trades file
        """
        # Create test trade data
        trade_data = {
            'timestamp': datetime.now(),
            'order_id': '123456',
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'entry_price': 50000.0,
            'exit_price': None,
            'quantity': 0.001,
            'pnl': None,
            'stop_loss_triggered': False,
            'take_profit_triggered': False
        }
        
        # Create initial trade file
        trades_df = pd.DataFrame([trade_data])
        trades_df.to_csv(SETTINGS['HISTORICAL_TRADES_PATH'], index=False)
        
        # Create exit data
        exit_data = {
            'exit_price': 51000.0,
            'pnl': 1.0,
            'stop_loss_triggered': False,
            'take_profit_triggered': True
        }
        
        # Update non-existent trade
        self.data_manager.update_trade_exit('unknown_id', exit_data)
        
        # Check error logging
        self.error_logger.error.assert_called_once()
        
        # Check that file was not modified
        updated_df = pd.read_csv(SETTINGS['HISTORICAL_TRADES_PATH'])
        self.assertTrue(pd.isna(updated_df['exit_price'].iloc[0]))


if __name__ == '__main__':
    unittest.main() 