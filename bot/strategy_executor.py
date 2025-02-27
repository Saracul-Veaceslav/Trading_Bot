"""Module for executing trading strategies based on market data."""

import importlib
from datetime import datetime
from typing import Any

import pandas as pd

from bot.config.settings import SETTINGS


class StrategyExecutor:
    """Executes trading strategies and manages the trading workflow."""
    
    def __init__(self, exchange, data_manager, trading_logger, error_logger, 
                 symbol: str, timeframe: str, strategy_name: str):
        """Initialize the Strategy Executor."""
        self.exchange = exchange
        self.data_manager = data_manager
        self.trading_logger = trading_logger
        self.error_logger = error_logger
        self.symbol = symbol
        self.timeframe = timeframe
        self.strategy_name = strategy_name
        self.strategy = self._load_strategy(strategy_name)
    
    def _load_strategy(self, strategy_name: str) -> Any:
        """Dynamically load a strategy module."""
        try:
            # Import the strategy module
            module_path = f"bot.strategies.{strategy_name}"
            module = importlib.import_module(module_path)
            
            # Get strategy class (camelCase naming convention)
            class_name = ''.join(word.capitalize() for word in strategy_name.split('_'))
            strategy_class = getattr(module, class_name)
            
            # Create and return instance
            return strategy_class(self.trading_logger, self.error_logger)
            
        except (ImportError, AttributeError) as e:
            self.error_logger.exception(f"Failed to load strategy '{strategy_name}': {str(e)}")
            raise ImportError(f"Strategy '{strategy_name}' could not be loaded") from e
    
    def execute_iteration(self):
        """Execute a single iteration of the trading strategy."""
        self.trading_logger.info(f"Starting iteration for {self.symbol} ({self.timeframe})")
        
        try:
            # 1. Fetch and store market data
            ohlcv_df = self.exchange.fetch_ohlcv(self.symbol, self.timeframe)
            if ohlcv_df.empty:
                self.trading_logger.warning("No OHLCV data received, skipping iteration")
                return
            
            self.data_manager.store_ohlcv_data(ohlcv_df, self.symbol)
            
            # 2. Calculate trading signal
            signal = self.strategy.calculate_signal(ohlcv_df)
            
            # 3. Execute trades based on signal
            self._execute_trades(signal)
            
            # 4. Check stop-loss and take-profit
            self._check_risk_management()
            
            self.trading_logger.info(f"Iteration completed for {self.symbol}")
            
        except Exception as e:
            self.error_logger.exception(f"Error in strategy execution: {str(e)}")
    
    def _execute_trades(self, signal: int):
        """Execute trades based on the strategy signal."""
        has_position = self.exchange.open_position is not None
        
        # BUY signal
        if signal == 1 and not has_position:
            try:
                position_size = SETTINGS['POSITION_SIZE']
                
                # Place buy order
                order = self.exchange.create_market_order(
                    symbol=self.symbol,
                    side='buy',
                    amount=position_size
                )
                
                # Record trade
                entry_price = self.exchange.get_current_price(self.symbol)
                trade_data = {
                    'timestamp': datetime.now(),
                    'order_id': order['id'],
                    'symbol': self.symbol,
                    'side': 'buy',
                    'entry_price': entry_price,
                    'exit_price': None,
                    'quantity': position_size,
                    'pnl': None,
                    'stop_loss_triggered': False,
                    'take_profit_triggered': False
                }
                
                self.data_manager.store_trade(trade_data)
                
            except Exception as e:
                self.error_logger.exception(f"Error executing buy: {str(e)}")
        
        # SELL signal
        elif signal == -1 and has_position:
            try:
                # Get position details
                position = self.exchange.open_position
                position_size = position['amount']
                entry_price = position['entry_price']
                order_id = position['order_id']
                
                # Place sell order
                order = self.exchange.create_market_order(
                    symbol=self.symbol,
                    side='sell',
                    amount=position_size
                )
                
                # Update trade record
                exit_price = self.exchange.get_current_price(self.symbol)
                pnl = (exit_price - entry_price) * position_size
                
                exit_data = {
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'stop_loss_triggered': False,
                    'take_profit_triggered': False
                }
                
                self.data_manager.update_trade_exit(order_id, exit_data)
                
            except Exception as e:
                self.error_logger.exception(f"Error executing sell: {str(e)}")
    
    def _check_risk_management(self):
        """Check and execute stop-loss/take-profit if triggered."""
        if not self.exchange.open_position:
            return
            
        exit_reason = self.exchange.check_stop_loss_take_profit(self.symbol)
        
        if exit_reason:
            try:
                # Get position details
                position = self.exchange.open_position
                position_size = position['amount']
                entry_price = position['entry_price']
                order_id = position['order_id']
                
                # Execute sell order
                order = self.exchange.create_market_order(
                    symbol=self.symbol,
                    side='sell',
                    amount=position_size
                )
                
                # Update trade record
                exit_price = self.exchange.get_current_price(self.symbol)
                pnl = (exit_price - entry_price) * position_size
                
                exit_data = {
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'stop_loss_triggered': exit_reason == 'stop_loss',
                    'take_profit_triggered': exit_reason == 'take_profit'
                }
                
                self.data_manager.update_trade_exit(order_id, exit_data)
                
                self.trading_logger.info(
                    f"{exit_reason.upper()} triggered - Closed position with P&L: {pnl:.6f}"
                )
                
            except Exception as e:
                self.error_logger.exception(f"Error executing risk management: {str(e)}") 