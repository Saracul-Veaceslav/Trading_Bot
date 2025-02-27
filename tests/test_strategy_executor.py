"""
Tests for Strategy Executor Module

This module contains tests for the StrategyExecutor class responsible for
orchestrating the trading workflow.
"""

import unittest
import logging
import importlib
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime, timedelta

from bot.strategy_executor import StrategyExecutor
from bot.config.settings import SETTINGS


class TestStrategyExecutor(unittest.TestCase):
    """Tests for the StrategyExecutor class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock loggers
        self.trading_logger = MagicMock(spec=logging.Logger)
        self.error_logger = MagicMock(spec=logging.Logger)
        
        # Create mock exchange, data manager, and strategy
        self.mock_exchange = MagicMock()
        self.mock_data_manager = MagicMock()
        self.mock_strategy = MagicMock()
        
        # Patch the _load_strategy method to return our mock strategy
        with patch.object(StrategyExecutor, '_load_strategy', return_value=self.mock_strategy):
            # Create StrategyExecutor instance
            self.executor = StrategyExecutor(
                exchange=self.mock_exchange,
                data_manager=self.mock_data_manager,
                trading_logger=self.trading_logger,
                error_logger=self.error_logger,
                symbol='BTC/USDT',
                timeframe='5m',
                strategy_name='sma_crossover'
            )
    
    def test_load_strategy(self):
        """
        Feature: Strategy Loading
        
        Scenario: Load a strategy module dynamically
            Given a strategy name
            When _load_strategy is called
            Then it should import the module and instantiate the strategy class
            And return the strategy instance
        """
        # Restore the original _load_strategy method for this test
        self.executor._load_strategy = StrategyExecutor._load_strategy.__get__(self.executor, StrategyExecutor)
        
        # Create mock module, class, and instance
        mock_module = MagicMock()
        mock_strategy_class = MagicMock()
        mock_module.SMAcrossover = mock_strategy_class
        
        # Patch importlib.import_module to return our mock module
        with patch('importlib.import_module', return_value=mock_module):
            # Call _load_strategy
            result = self.executor._load_strategy('sma_crossover')
            
            # Check that import_module was called correctly
            importlib.import_module.assert_called_once_with('bot.strategies.sma_crossover')
            
            # Check that strategy class was instantiated correctly
            mock_strategy_class.assert_called_once_with(self.trading_logger, self.error_logger)
            
            # Check result is the instance returned by mock_strategy_class
            self.assertEqual(result, mock_strategy_class.return_value)
    
    def test_execute_iteration_buy_signal(self):
        """
        Feature: Trading Iteration Execution
        
        Scenario: Execute a trading iteration with a buy signal
            Given a mock exchange, data manager, and strategy
            And the strategy returns a buy signal
            And no open position
            When execute_iteration is called
            Then it should fetch data, store it, calculate signal, and execute a buy trade
            And log appropriate messages
        """
        # Create mock OHLCV data
        now = datetime.now()
        ohlcv_df = pd.DataFrame({
            'timestamp': [now - timedelta(minutes=i) for i in range(5)],
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # Configure mocks
        self.mock_exchange.fetch_ohlcv.return_value = ohlcv_df
        self.mock_strategy.calculate_signal.return_value = 1  # Buy signal
        self.mock_exchange.open_position = None  # No open position
        self.mock_exchange.get_current_price.return_value = 50000.0
        self.mock_exchange.create_market_order.return_value = {'id': '123456'}
        
        # Call execute_iteration
        self.executor.execute_iteration()
        
        # Check that methods were called correctly
        self.mock_exchange.fetch_ohlcv.assert_called_once_with('BTC/USDT', '5m')
        self.mock_data_manager.store_ohlcv_data.assert_called_once()
        self.mock_strategy.calculate_signal.assert_called_once_with(ohlcv_df)
        
        # Check that buy order was placed
        self.mock_exchange.create_market_order.assert_called_once_with(
            symbol='BTC/USDT',
            side='buy',
            amount=SETTINGS['POSITION_SIZE']
        )
        
        # Check that trade was stored
        self.mock_data_manager.store_trade.assert_called_once()
        
        # Check logging
        self.assertEqual(self.trading_logger.info.call_count, 2)  # Start and end logs
    
    def test_execute_iteration_sell_signal(self):
        """
        Feature: Trading Iteration Execution
        
        Scenario: Execute a trading iteration with a sell signal
            Given a mock exchange, data manager, and strategy
            And the strategy returns a sell signal
            And an open position
            When execute_iteration is called
            Then it should fetch data, store it, calculate signal, and execute a sell trade
            And update the trade exit information
            And log appropriate messages
        """
        # Create mock OHLCV data
        now = datetime.now()
        ohlcv_df = pd.DataFrame({
            'timestamp': [now - timedelta(minutes=i) for i in range(5)],
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # Configure mocks
        self.mock_exchange.fetch_ohlcv.return_value = ohlcv_df
        self.mock_strategy.calculate_signal.return_value = -1  # Sell signal
        
        # Set up an open position
        self.mock_exchange.open_position = {
            'symbol': 'BTC/USDT',
            'entry_price': 50000.0,
            'amount': 0.001,
            'side': 'long',
            'entry_time': datetime.now(),
            'order_id': '123456',
        }
        
        self.mock_exchange.get_current_price.return_value = 51000.0  # 2% profit
        self.mock_exchange.create_market_order.return_value = {'id': '789012'}
        
        # Call execute_iteration
        self.executor.execute_iteration()
        
        # Check that methods were called correctly
        self.mock_exchange.fetch_ohlcv.assert_called_once_with('BTC/USDT', '5m')
        self.mock_data_manager.store_ohlcv_data.assert_called_once()
        self.mock_strategy.calculate_signal.assert_called_once_with(ohlcv_df)
        
        # Check that sell order was placed
        self.mock_exchange.create_market_order.assert_called_once_with(
            symbol='BTC/USDT',
            side='sell',
            amount=0.001
        )
        
        # Check that trade exit was updated
        self.mock_data_manager.update_trade_exit.assert_called_once_with('123456', {
            'exit_price': 51000.0,
            'pnl': 1.0,  # (51000 - 50000) * 0.001
            'stop_loss_triggered': False,
            'take_profit_triggered': False
        })
        
        # Check logging
        self.assertEqual(self.trading_logger.info.call_count, 2)  # Start and end logs
    
    def test_execute_iteration_hold_signal(self):
        """
        Feature: Trading Iteration Execution
        
        Scenario: Execute a trading iteration with a hold signal
            Given a mock exchange, data manager, and strategy
            And the strategy returns a hold signal
            When execute_iteration is called
            Then it should fetch data, store it, calculate signal, but not execute any trades
            And log appropriate messages
        """
        # Create mock OHLCV data
        now = datetime.now()
        ohlcv_df = pd.DataFrame({
            'timestamp': [now - timedelta(minutes=i) for i in range(5)],
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # Configure mocks
        self.mock_exchange.fetch_ohlcv.return_value = ohlcv_df
        self.mock_strategy.calculate_signal.return_value = 0  # Hold signal
        
        # Call execute_iteration
        self.executor.execute_iteration()
        
        # Check that methods were called correctly
        self.mock_exchange.fetch_ohlcv.assert_called_once_with('BTC/USDT', '5m')
        self.mock_data_manager.store_ohlcv_data.assert_called_once()
        self.mock_strategy.calculate_signal.assert_called_once_with(ohlcv_df)
        
        # Check that no orders were placed
        self.mock_exchange.create_market_order.assert_not_called()
        
        # Check logging
        self.assertEqual(self.trading_logger.info.call_count, 2)  # Start and end logs
    
    def test_check_risk_management_stop_loss(self):
        """
        Feature: Risk Management
        
        Scenario: Stop loss is triggered
            Given a mock exchange with an open position
            And the current price is below the stop-loss threshold
            When _check_risk_management is called
            Then it should execute a sell order
            And update the trade with stop_loss_triggered=True
            And log appropriate messages
        """
        # Set up an open position
        self.mock_exchange.open_position = {
            'symbol': 'BTC/USDT',
            'entry_price': 50000.0,
            'amount': 0.001,
            'side': 'long',
            'entry_time': datetime.now(),
            'order_id': '123456',
        }
        
        # Mock check_stop_loss_take_profit to return 'stop_loss'
        self.mock_exchange.check_stop_loss_take_profit.return_value = 'stop_loss'
        self.mock_exchange.get_current_price.return_value = 49000.0  # 2% loss
        self.mock_exchange.create_market_order.return_value = {'id': '789012'}
        
        # Call _check_risk_management
        self.executor._check_risk_management()
        
        # Check that methods were called correctly
        self.mock_exchange.check_stop_loss_take_profit.assert_called_once_with('BTC/USDT')
        
        # Check that sell order was placed
        self.mock_exchange.create_market_order.assert_called_once_with(
            symbol='BTC/USDT',
            side='sell',
            amount=0.001
        )
        
        # Check that trade exit was updated with stop_loss_triggered=True
        call_args = self.mock_data_manager.update_trade_exit.call_args[0]
        self.assertEqual(call_args[0], '123456')
        self.assertTrue(call_args[1]['stop_loss_triggered'])
        self.assertFalse(call_args[1]['take_profit_triggered'])
        
        # Check logging
        self.assertIn("STOP_LOSS", self.trading_logger.info.call_args[0][0])
    
    def test_check_risk_management_take_profit(self):
        """
        Feature: Risk Management
        
        Scenario: Take profit is triggered
            Given a mock exchange with an open position
            And the current price is above the take-profit threshold
            When _check_risk_management is called
            Then it should execute a sell order
            And update the trade with take_profit_triggered=True
            And log appropriate messages
        """
        # Set up an open position
        self.mock_exchange.open_position = {
            'symbol': 'BTC/USDT',
            'entry_price': 50000.0,
            'amount': 0.001,
            'side': 'long',
            'entry_time': datetime.now(),
            'order_id': '123456',
        }
        
        # Mock check_stop_loss_take_profit to return 'take_profit'
        self.mock_exchange.check_stop_loss_take_profit.return_value = 'take_profit'
        self.mock_exchange.get_current_price.return_value = 52000.0  # 4% gain
        self.mock_exchange.create_market_order.return_value = {'id': '789012'}
        
        # Call _check_risk_management
        self.executor._check_risk_management()
        
        # Check that methods were called correctly
        self.mock_exchange.check_stop_loss_take_profit.assert_called_once_with('BTC/USDT')
        
        # Check that sell order was placed
        self.mock_exchange.create_market_order.assert_called_once_with(
            symbol='BTC/USDT',
            side='sell',
            amount=0.001
        )
        
        # Check that trade exit was updated with take_profit_triggered=True
        call_args = self.mock_data_manager.update_trade_exit.call_args[0]
        self.assertEqual(call_args[0], '123456')
        self.assertFalse(call_args[1]['stop_loss_triggered'])
        self.assertTrue(call_args[1]['take_profit_triggered'])
        
        # Check logging
        self.assertIn("TAKE_PROFIT", self.trading_logger.info.call_args[0][0])
    
    def test_check_risk_management_no_trigger(self):
        """
        Feature: Risk Management
        
        Scenario: No risk management trigger
            Given a mock exchange with an open position
            And the current price is within acceptable range
            When _check_risk_management is called
            Then it should not execute any orders
            And not update any trade information
            And not log any related messages
        """
        # Set up an open position
        self.mock_exchange.open_position = {
            'symbol': 'BTC/USDT',
            'entry_price': 50000.0,
            'amount': 0.001,
            'side': 'long',
            'entry_time': datetime.now(),
            'order_id': '123456',
        }
        
        # Mock check_stop_loss_take_profit to return None (no trigger)
        self.mock_exchange.check_stop_loss_take_profit.return_value = None
        
        # Call _check_risk_management
        self.executor._check_risk_management()
        
        # Check that methods were called correctly
        self.mock_exchange.check_stop_loss_take_profit.assert_called_once_with('BTC/USDT')
        
        # Check that no orders were placed
        self.mock_exchange.create_market_order.assert_not_called()
        
        # Check that no trade exits were updated
        self.mock_data_manager.update_trade_exit.assert_not_called()
        
        # Check no related logging
        self.trading_logger.info.assert_not_called()


if __name__ == '__main__':
    unittest.main() 