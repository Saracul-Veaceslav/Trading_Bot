"""
Tests for Exchange Module

This module contains tests for the BinanceTestnet class responsible for
interacting with the Binance Testnet exchange.
"""

import unittest
import logging
from unittest.mock import MagicMock, patch, PropertyMock
import pandas as pd
from datetime import datetime, timedelta

from bot.exchange import BinanceTestnet
from bot.config.settings import SETTINGS


class TestBinanceTestnet(unittest.TestCase):
    """Tests for the BinanceTestnet class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock loggers
        self.trading_logger = MagicMock(spec=logging.Logger)
        self.error_logger = MagicMock(spec=logging.Logger)
        
        # Patch ccxt.binance
        self.ccxt_binance_patch = patch('ccxt.binance')
        self.mock_ccxt_binance = self.ccxt_binance_patch.start()
        
        # Mock exchange instance
        self.mock_exchange = MagicMock()
        self.mock_ccxt_binance.return_value = self.mock_exchange
        
        # Configure mock methods
        self.mock_exchange.fetch_status.return_value = {'status': 'ok'}
        
        # Create BinanceTestnet instance with mocked ccxt
        self.exchange = BinanceTestnet(self.trading_logger, self.error_logger)
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.ccxt_binance_patch.stop()
    
    def test_initialize_exchange(self):
        """
        Feature: Exchange Initialization
        
        Scenario: Initialize Binance Testnet exchange
            Given API credentials in settings
            When a BinanceTestnet instance is created
            Then it should initialize the ccxt exchange object with correct parameters
            And set sandbox mode to True
            And test the connection
            And log a success message
        """
        # Check that ccxt.binance was called with correct parameters
        self.mock_ccxt_binance.assert_called_once()
        
        # Check that sandbox mode was set
        self.mock_exchange.set_sandbox_mode.assert_called_once_with(True)
        
        # Check that connection was tested
        self.mock_exchange.fetch_status.assert_called_once()
        
        # Check logging
        self.trading_logger.info.assert_called_once_with("Successfully connected to Binance Testnet")
    
    def test_fetch_ohlcv_success(self):
        """
        Feature: OHLCV Data Fetching
        
        Scenario: Successfully fetch OHLCV data
            Given a mock exchange that returns valid OHLCV data
            When fetch_ohlcv is called
            Then it should return a DataFrame with the correct columns
            And convert timestamps to datetime
            And log a debug message
        """
        # Mock fetch_ohlcv response
        now = datetime.now()
        candles = [
            [now.timestamp() * 1000, 100, 105, 95, 101, 1000],
            [(now - timedelta(minutes=1)).timestamp() * 1000, 99, 104, 94, 100, 900],
            [(now - timedelta(minutes=2)).timestamp() * 1000, 98, 103, 93, 99, 800],
        ]
        self.mock_exchange.fetch_ohlcv.return_value = candles
        
        # Call fetch_ohlcv
        result = self.exchange.fetch_ohlcv('BTC/USDT', '1m', limit=3)
        
        # Check that exchange method was called correctly
        self.mock_exchange.fetch_ohlcv.assert_called_once_with('BTC/USDT', '1m', limit=3)
        
        # Check result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(col in result.columns for col in ['timestamp', 'open', 'high', 'low', 'close', 'volume']))
        
        # Check that timestamp was converted
        self.assertTrue(pd.api.types.is_datetime64_dtype(result['timestamp']))
        
        # Check logging
        self.trading_logger.debug.assert_called_once()
    
    def test_fetch_ohlcv_retry(self):
        """
        Feature: OHLCV Data Fetching with Retry
        
        Scenario: Retry fetching OHLCV data after temporary failure
            Given a mock exchange that fails on first attempt but succeeds on second
            When fetch_ohlcv is called
            Then it should retry the API call
            And eventually return the data
            And log error and retry messages
        """
        # Mock fetch_ohlcv to fail first, then succeed
        now = datetime.now()
        candles = [
            [now.timestamp() * 1000, 100, 105, 95, 101, 1000],
            [(now - timedelta(minutes=1)).timestamp() * 1000, 99, 104, 94, 100, 900],
        ]
        
        # Set up side effect to fail first, then succeed
        self.mock_exchange.fetch_ohlcv.side_effect = [
            Exception("API error"),
            candles
        ]
        
        # Mock time.sleep to avoid waiting
        with patch('time.sleep'):
            # Call fetch_ohlcv
            result = self.exchange.fetch_ohlcv('BTC/USDT', '1m')
            
            # Check that exchange method was called twice
            self.assertEqual(self.mock_exchange.fetch_ohlcv.call_count, 2)
            
            # Check result
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(len(result), 2)
            
            # Check logging
            self.error_logger.error.assert_called_once()
            self.trading_logger.info.assert_called_once()
    
    def test_create_market_order_buy(self):
        """
        Feature: Market Order Creation
        
        Scenario: Create a buy market order
            Given a mock exchange
            When create_market_order is called with 'buy' side
            Then it should create a market order on the exchange
            And update the open position tracking
            And log the trade
        """
        # Mock fetch_ticker response
        self.mock_exchange.fetch_ticker.return_value = {'last': 50000.0}
        
        # Mock create_market_order response
        self.mock_exchange.create_market_order.return_value = {
            'id': '123456',
            'symbol': 'BTC/USDT',
            'type': 'market',
            'side': 'buy',
            'amount': 0.001,
            'price': 50000.0
        }
        
        # Call create_market_order
        result = self.exchange.create_market_order('BTC/USDT', 'buy', 0.001)
        
        # Check that exchange methods were called correctly
        self.mock_exchange.fetch_ticker.assert_called_once_with('BTC/USDT')
        self.mock_exchange.create_market_order.assert_called_once_with('BTC/USDT', 'buy', 0.001)
        
        # Check that open position was updated
        self.assertIsNotNone(self.exchange.open_position)
        self.assertEqual(self.exchange.open_position['symbol'], 'BTC/USDT')
        self.assertEqual(self.exchange.open_position['amount'], 0.001)
        self.assertEqual(self.exchange.open_position['entry_price'], 50000.0)
        self.assertEqual(self.exchange.open_position['side'], 'long')
        
        # Check logging
        self.assertEqual(self.trading_logger.info.call_count, 2)  # One for order, one for position
    
    def test_create_market_order_sell(self):
        """
        Feature: Market Order Creation
        
        Scenario: Create a sell market order to close a position
            Given a mock exchange and an open position
            When create_market_order is called with 'sell' side
            Then it should create a market order on the exchange
            And calculate the PnL
            And clear the open position tracking
            And log the trade and PnL
        """
        # Set up an open position
        self.exchange.open_position = {
            'symbol': 'BTC/USDT',
            'entry_price': 50000.0,
            'amount': 0.001,
            'side': 'long',
            'entry_time': pd.Timestamp.now(),
            'order_id': '123456',
        }
        
        # Mock fetch_ticker response
        self.mock_exchange.fetch_ticker.return_value = {'last': 51000.0}  # 2% profit
        
        # Mock create_market_order response
        self.mock_exchange.create_market_order.return_value = {
            'id': '789012',
            'symbol': 'BTC/USDT',
            'type': 'market',
            'side': 'sell',
            'amount': 0.001,
            'price': 51000.0
        }
        
        # Call create_market_order
        result = self.exchange.create_market_order('BTC/USDT', 'sell', 0.001)
        
        # Check that exchange methods were called correctly
        self.mock_exchange.fetch_ticker.assert_called_once_with('BTC/USDT')
        self.mock_exchange.create_market_order.assert_called_once_with('BTC/USDT', 'sell', 0.001)
        
        # Check that open position was cleared
        self.assertIsNone(self.exchange.open_position)
        
        # Check logging
        self.assertIn("Closed position with P&L", self.trading_logger.info.call_args_list[1][0][0])
    
    def test_check_stop_loss_take_profit_stop_loss(self):
        """
        Feature: Stop Loss Check
        
        Scenario: Stop loss condition is met
            Given a mock exchange and an open long position
            And current price below stop loss threshold
            When check_stop_loss_take_profit is called
            Then it should return 'stop_loss'
            And log a message about the stop loss
        """
        # Set up an open position
        self.exchange.open_position = {
            'symbol': 'BTC/USDT',
            'entry_price': 50000.0,
            'amount': 0.001,
            'side': 'long',
            'entry_time': pd.Timestamp.now(),
            'order_id': '123456',
        }
        
        # Mock fetch_ticker response - price below stop loss (2% down)
        stop_price = 50000.0 * (1 - SETTINGS['STOP_LOSS_PERCENT'])
        self.mock_exchange.fetch_ticker.return_value = {'last': stop_price - 100}
        
        # Check stop loss / take profit
        result = self.exchange.check_stop_loss_take_profit('BTC/USDT')
        
        # Check result
        self.assertEqual(result, 'stop_loss')
        
        # Check logging
        self.trading_logger.info.assert_called_once_with(f"Stop loss triggered at {stop_price - 100}")
    
    def test_check_stop_loss_take_profit_take_profit(self):
        """
        Feature: Take Profit Check
        
        Scenario: Take profit condition is met
            Given a mock exchange and an open long position
            And current price above take profit threshold
            When check_stop_loss_take_profit is called
            Then it should return 'take_profit'
            And log a message about the take profit
        """
        # Set up an open position
        self.exchange.open_position = {
            'symbol': 'BTC/USDT',
            'entry_price': 50000.0,
            'amount': 0.001,
            'side': 'long',
            'entry_time': pd.Timestamp.now(),
            'order_id': '123456',
        }
        
        # Mock fetch_ticker response - price above take profit (4% up)
        take_profit_price = 50000.0 * (1 + SETTINGS['TAKE_PROFIT_PERCENT'])
        self.mock_exchange.fetch_ticker.return_value = {'last': take_profit_price + 100}
        
        # Check stop loss / take profit
        result = self.exchange.check_stop_loss_take_profit('BTC/USDT')
        
        # Check result
        self.assertEqual(result, 'take_profit')
        
        # Check logging
        self.trading_logger.info.assert_called_once_with(f"Take profit triggered at {take_profit_price + 100}")
    
    def test_check_stop_loss_take_profit_no_position(self):
        """
        Feature: Position Check
        
        Scenario: No open position
            Given a mock exchange with no open position
            When check_stop_loss_take_profit is called
            Then it should return None
            And not log any messages
        """
        # Ensure no open position
        self.exchange.open_position = None
        
        # Check stop loss / take profit
        result = self.exchange.check_stop_loss_take_profit('BTC/USDT')
        
        # Check result
        self.assertIsNone(result)
        
        # Check no logging
        self.trading_logger.info.assert_not_called()
        
    def test_get_current_price(self):
        """
        Feature: Current Price Retrieval
        
        Scenario: Get current price for a symbol
            Given a mock exchange with ticker data
            When get_current_price is called
            Then it should return the latest price
        """
        # Mock fetch_ticker response
        self.mock_exchange.fetch_ticker.return_value = {'last': 50000.0}
        
        # Get current price
        price = self.exchange.get_current_price('BTC/USDT')
        
        # Check result
        self.assertEqual(price, 50000.0)
        
        # Check exchange call
        self.mock_exchange.fetch_ticker.assert_called_once_with('BTC/USDT')


if __name__ == '__main__':
    unittest.main() 