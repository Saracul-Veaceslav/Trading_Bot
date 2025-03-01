"""
Module for executing trading strategies.
"""
import logging
import time
import importlib
from datetime import datetime
from trading_bot.config.settings import SETTINGS, STRATEGY_PARAMS

class StrategyExecutor:
    """
    Handles the execution of trading strategies and order management.
    """
    
    def __init__(self, exchange, data_manager, strategy_name=None, strategy=None, symbol="BTCUSDT", interval="1h", 
                 quantity=None, test_mode=True, trading_logger=None, error_logger=None):
        """
        Initialize the Strategy Executor.
        
        Args:
            exchange: Exchange client for placing orders
            data_manager: DataManager instance for retrieving market data
            strategy_name (str): Name of the strategy to load
            strategy: Strategy instance (if provided directly)
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            interval (str): Timeframe for the strategy (e.g., '1h', '4h')
            quantity (float): Trading quantity
            test_mode (bool): If True, only simulate trades without actual execution
            trading_logger: Logger for trade-specific logging
            error_logger: Logger for error logging
        """
        self.exchange = exchange
        self.data_manager = data_manager
        
        # Convert potentially mocked parameters to strings where needed
        try:
            self.symbol = str(symbol) if symbol else "BTCUSDT"
            self.interval = str(interval) if interval else "1h"
        except (TypeError, ValueError):
            # Fall back to defaults for mocked objects
            self.symbol = "BTCUSDT"
            self.interval = "1h"
            
        self.quantity = quantity if quantity is not None else SETTINGS.get('quantity', 0.001)
        self.test_mode = test_mode
        self.strategy_name = strategy_name
        
        # Set up loggers
        self.logger = trading_logger if trading_logger else logging.getLogger(__name__)
        self.error_logger = error_logger if error_logger else self.logger
        
        # Set up strategy
        if strategy:
            self.strategy = strategy
            # Set loggers if strategy supports it
            if hasattr(self.strategy, 'set_loggers'):
                self.strategy.set_loggers(self.logger, self.error_logger)
        elif strategy_name:
            self.strategy = self._load_strategy(strategy_name)
        else:
            self.strategy = None
            
        self.current_position = None  # 'long', 'short', or None
        self.active = False
        
        # Risk management parameters
        self.stop_loss_percent = SETTINGS.get('STOP_LOSS_PERCENT', 0.02)
        self.take_profit_percent = SETTINGS.get('TAKE_PROFIT_PERCENT', 0.03)
        self.entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None
    
    def _load_strategy(self, strategy_name):
        """
        Dynamically load a strategy by name.
        
        Args:
            strategy_name (str): Name of the strategy module
            
        Returns:
            object: Strategy instance
        """
        try:
            # Try to import the strategy module
            strategy_module = importlib.import_module(f"Trading_Bot.strategies.{strategy_name}")
            
            # Get the strategy class name (assuming it's the same as the module name with capitalized first letter)
            class_name = ''.join(word.capitalize() for word in strategy_name.split('_'))
            
            # Get the strategy class
            strategy_class = getattr(strategy_module, class_name)
            
            # Get strategy parameters from settings
            params = STRATEGY_PARAMS.get(strategy_name, {})
            
            # Create an instance of the strategy
            strategy = strategy_class(**params)
            
            # Set loggers if strategy supports it
            if hasattr(strategy, 'set_loggers'):
                strategy.set_loggers(self.logger, self.error_logger)
            
            return strategy
            
        except (ImportError, AttributeError) as e:
            self.error_logger.error(f"Failed to load strategy {strategy_name}: {e}")
            return None
        except Exception as e:
            self.error_logger.error(f"Unexpected error loading strategy {strategy_name}: {e}")
            return None
    
    def start(self):
        """
        Start the strategy execution.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.active:
            self.logger.warning("Strategy executor is already running")
            return False
            
        self.logger.info(f"Starting strategy executor for {self.symbol} on {self.interval} timeframe")
        self.active = True
        return True
    
    def stop(self):
        """
        Stop the strategy execution.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if not self.active:
            self.logger.warning("Strategy executor is not running")
            return False
            
        self.logger.info("Stopping strategy executor")
        self.active = False
        return True
    
    def execute_once(self):
        """
        Execute the strategy once.
        
        Returns:
            dict: Result of the execution
        """
        try:
            # Get latest data
            df = self.data_manager.get_historical_data(
                symbol=self.symbol,
                interval=self.interval
            )
            
            if df is None or df.empty:
                self.logger.warning("No data available for strategy execution")
                return {"success": False, "error": "No data available"}
            
            # Prepare data for the strategy
            prepared_data = self.data_manager.prepare_data_for_strategy(df)
            
            # Check if we need to use generate_signal or calculate_signal based on what's available
            if hasattr(self.strategy, 'calculate_signal'):
                signal = self.strategy.calculate_signal(prepared_data)
            else:
                signal = self.strategy.generate_signal(prepared_data)
            
            # Ensure signal is an integer
            signal_value = signal
            if isinstance(signal, str):
                if signal == "buy":
                    signal_value = 1
                elif signal == "sell":
                    signal_value = -1
                else:  # "hold"
                    signal_value = 0
            
            result = {
                "timestamp": datetime.now(),
                "symbol": self.symbol,
                "interval": self.interval,
                "signal": signal_value,
                "success": True
            }
            
            # Execute trades based on signals if not in test mode
            if not self.test_mode and signal_value != 0:
                order_result = self._execute_trade(signal_value)
                result["order"] = order_result
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"Error executing strategy: {e}")
            return {"success": False, "error": str(e)}
    
    def run(self, iterations=None, sleep_time=None):
        """
        Run the strategy continuously.
        
        Args:
            iterations (int): Number of iterations to run (None for indefinite)
            sleep_time (int): Time to sleep between iterations in seconds
            
        Returns:
            list: List of execution results
        """
        if not self.active:
            self.start()
        
        results = []
        iteration = 0
        
        try:
            while self.active:
                if iterations is not None and iteration >= iterations:
                    break
                
                result = self.execute_once()
                results.append(result)
                iteration += 1
                
                self.logger.info(f"Iteration {iteration} completed with signal: {result.get('signal', 'N/A')}")
                
                # Check for stop loss or take profit
                if self.current_position is not None:
                    risk_check = self._check_risk_management()
                    if risk_check['action'] in ['stop_loss', 'take_profit']:
                        self.logger.info(f"{risk_check['action']} triggered at {risk_check['price']}")
                
                if sleep_time:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            self.logger.info("Strategy execution interrupted by user")
        except Exception as e:
            self.error_logger.error(f"Error in run loop: {e}")
        
        self.stop()
        return results
        
    def _check_risk_management(self):
        """
        Check if stop loss or take profit has been triggered.
        
        Returns:
            dict: Action details
        """
        if self.current_position is None or self.entry_price is None:
            return {'action': None}
            
        try:
            current_price = self.exchange.get_current_price(self.symbol)
            
            if not current_price:
                return {'action': None}
                
            # Check stop loss
            if self.current_position == 'long' and current_price <= self.stop_loss_price:
                # Execute stop loss for long position
                if not self.test_mode:
                    self._close_position('sell')
                self.current_position = None
                self.entry_price = None
                return {'action': 'stop_loss', 'price': current_price}
                
            elif self.current_position == 'short' and current_price >= self.stop_loss_price:
                # Execute stop loss for short position
                if not self.test_mode:
                    self._close_position('buy')
                self.current_position = None
                self.entry_price = None
                return {'action': 'stop_loss', 'price': current_price}
                
            # Check take profit
            if self.current_position == 'long' and current_price >= self.take_profit_price:
                # Execute take profit for long position
                if not self.test_mode:
                    self._close_position('sell')
                self.current_position = None
                self.entry_price = None
                return {'action': 'take_profit', 'price': current_price}
                
            elif self.current_position == 'short' and current_price <= self.take_profit_price:
                # Execute take profit for short position
                if not self.test_mode:
                    self._close_position('buy')
                self.current_position = None
                self.entry_price = None
                return {'action': 'take_profit', 'price': current_price}
                
            return {'action': None}
            
        except Exception as e:
            self.error_logger.error(f"Error checking risk management: {e}")
            return {'action': None}
    
    def _execute_trade(self, signal):
        """
        Execute a trade based on the signal.
        
        Args:
            signal (int): Trading signal (1 for buy, -1 for sell, 0 for hold)
            
        Returns:
            dict: Order result
        """
        try:
            # Convert integer signal to string if needed
            signal_str = signal
            if isinstance(signal, int):
                if signal == 1:
                    signal_str = "buy"
                elif signal == -1:
                    signal_str = "sell"
                else:
                    signal_str = "hold"
                    
            if signal_str == "buy" and self.current_position != "long":
                # Close any existing short position first
                if self.current_position == "short":
                    self._close_position('buy')
                
                # Open long position
                current_price = self.exchange.get_current_price(self.symbol)
                if current_price:
                    order = self.exchange.create_market_order(
                        symbol=self.symbol,
                        side='buy',
                        amount=self.quantity
                    )
                    
                    if order:
                        self.current_position = "long"
                        self.entry_price = current_price
                        self.stop_loss_price = current_price * (1 - self.stop_loss_percent)
                        self.take_profit_price = current_price * (1 + self.take_profit_percent)
                        
                        # Log the trade
                        self.logger.info(f"Opened LONG position at {current_price} (SL: {self.stop_loss_price}, TP: {self.take_profit_price})")
                        
                        # Store the trade
                        trade_data = {
                            "timestamp": datetime.now().isoformat(),
                            "symbol": self.symbol,
                            "type": "entry",
                            "side": "buy",
                            "price": current_price,
                            "amount": self.quantity,
                            "stop_loss": self.stop_loss_price,
                            "take_profit": self.take_profit_price
                        }
                        self.data_manager.store_trade(trade_data)
                        
                    return order
                return {"status": "failed", "reason": "Could not get current price"}
                
            elif signal_str == "sell" and self.current_position != "short":
                # Close any existing long position first
                if self.current_position == "long":
                    self._close_position('sell')
                
                # Open short position
                current_price = self.exchange.get_current_price(self.symbol)
                if current_price:
                    order = self.exchange.create_market_order(
                        symbol=self.symbol,
                        side='sell',
                        amount=self.quantity
                    )
                    
                    if order:
                        self.current_position = "short"
                        self.entry_price = current_price
                        self.stop_loss_price = current_price * (1 + self.stop_loss_percent)
                        self.take_profit_price = current_price * (1 - self.take_profit_percent)
                        
                        # Log the trade
                        self.logger.info(f"Opened SHORT position at {current_price} (SL: {self.stop_loss_price}, TP: {self.take_profit_price})")
                        
                        # Store the trade
                        trade_data = {
                            "timestamp": datetime.now().isoformat(),
                            "symbol": self.symbol,
                            "type": "entry",
                            "side": "sell",
                            "price": current_price,
                            "amount": self.quantity,
                            "stop_loss": self.stop_loss_price,
                            "take_profit": self.take_profit_price
                        }
                        self.data_manager.store_trade(trade_data)
                        
                    return order
                return {"status": "failed", "reason": "Could not get current price"}
                
            return {"status": "no_action", "reason": "Signal does not warrant a trade"}
            
        except Exception as e:
            self.error_logger.error(f"Error executing trade: {e}")
            return {"status": "failed", "reason": str(e)}
        
    def _close_position(self, side):
        """
        Close an existing position.
        
        Args:
            side (str): Order side ('buy' or 'sell')
            
        Returns:
            dict: Order result
        """
        try:
            current_price = self.exchange.get_current_price(self.symbol)
            
            order = self.exchange.create_market_order(
                symbol=self.symbol,
                side=side,
                amount=self.quantity
            )
            
            if order:
                # Log the exit
                self.logger.info(f"Closed {'LONG' if side == 'sell' else 'SHORT'} position at {current_price}")
                
                # Store the exit
                if self.entry_price is not None:
                    pnl = 0
                    if side == 'sell':  # Closing a long position
                        pnl = (current_price - self.entry_price) / self.entry_price
                    else:  # Closing a short position
                        pnl = (self.entry_price - current_price) / self.entry_price
                        
                    trade_id = f"{self.symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    exit_data = {
                        "id": trade_id,
                        "timestamp": datetime.now().isoformat(),
                        "symbol": self.symbol,
                        "type": "exit",
                        "side": side,
                        "price": current_price,
                        "amount": self.quantity,
                        "pnl": pnl,
                        "pnl_percent": pnl * 100
                    }
                    self.data_manager.store_trade(exit_data)
            
            return order
            
        except Exception as e:
            self.error_logger.error(f"Error closing position: {e}")
            return None
