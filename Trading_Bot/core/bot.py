"""
Trading Bot Core Implementation

This module contains the main TradingBot class, which serves as the central
component of the application, orchestrating all the bot's functionality.
"""
import logging
import signal
import sys
import time
from typing import Dict, List, Optional, Any, Union
from argparse import Namespace
from datetime import datetime

logger = logging.getLogger('trading_bot.core')

class TradingBot:
    """
    Main Trading Bot class that coordinates all components and trading activities.
    
    This class is responsible for:
    - Initializing all components (exchange, strategies, risk management, etc.)
    - Managing the trading lifecycle
    - Coordinating data flow between components
    - Handling signals and shutdown
    """
    
    def __init__(self, args: Union[Namespace, Dict[str, Any]]):
        """
        Initialize the Trading Bot with the provided configuration.
        
        Args:
            args: Command line arguments or configuration dictionary
        """
        self.args = args
        self.running = False
        self.initialized = False
        
        # Default values
        self.config = {}
        self.exchange = None
        self.strategies = []
        self.strategy_executor = None
        self.data_manager = None
        self.decision_engine = None
        self.risk_manager = None
        self.web_server = None
        
        # Initialize components
        self._setup_signal_handlers()
    
    def initialize(self):
        """Initialize all bot components."""
        if self.initialized:
            return
        
        try:
            logger.info("Initializing Trading Bot components...")
            
            # Load configuration
            self._load_configuration()
            
            # Initialize data manager
            self._init_data_manager()
            
            # Initialize exchange
            self._init_exchange()
            
            # Initialize strategies
            self._init_strategies()
            
            # Initialize risk manager
            self._init_risk_manager()
            
            # Initialize strategy executor
            self._init_strategy_executor()
            
            # Initialize decision engine (for adaptive selection)
            self._init_decision_engine()
            
            self.initialized = True
            logger.info("Trading Bot initialization complete")
            
        except Exception as e:
            logger.exception(f"Error initializing Trading Bot: {e}")
            raise
    
    def _load_configuration(self):
        """Load configuration from file or command line arguments."""
        try:
            from trading_bot.core.config import load_config
            
            if hasattr(self.args, 'config') and self.args.config:
                # Load from config file
                self.config = load_config(self.args.config)
            else:
                # Create config from command line args
                self.config = {k: v for k, v in vars(self.args).items() if v is not None}
            
            logger.info(f"Configuration loaded successfully with {len(self.config)} parameters")
            
        except Exception as e:
            logger.exception(f"Error loading configuration: {e}")
            raise
    
    def _init_data_manager(self):
        """Initialize the data manager component."""
        try:
            from trading_bot.data.manager import DataManager
            
            self.data_manager = DataManager(config=self.config)
            logger.info("Data manager initialized")
            
        except Exception as e:
            logger.exception(f"Error initializing data manager: {e}")
            raise
    
    def _init_exchange(self):
        """Initialize the exchange interface."""
        try:
            from trading_bot.exchanges.factory import create_exchange
            
            exchange_id = self.config.get('exchange', 'binance')
            is_paper = hasattr(self.args, 'paper') and self.args.paper
            
            self.exchange = create_exchange(
                exchange_id=exchange_id,
                paper_trading=is_paper,
                config=self.config
            )
            
            logger.info(f"Exchange {'paper' if is_paper else 'live'} initialized: {exchange_id}")
            
        except Exception as e:
            logger.exception(f"Error initializing exchange: {e}")
            raise
    
    def _init_strategies(self):
        """Initialize trading strategies."""
        try:
            from trading_bot.strategies.registry import create_strategy
            
            strategy_names = self.config.get('strategies', ['sma_crossover'])
            if isinstance(strategy_names, str):
                strategy_names = [strategy_names]
            
            for strategy_name in strategy_names:
                strategy_config = self.config.get(f'strategy_{strategy_name}', {})
                strategy = create_strategy(strategy_name, strategy_config)
                self.strategies.append(strategy)
                logger.info(f"Strategy initialized: {strategy_name}")
            
            if not self.strategies:
                logger.warning("No strategies specified, using default SMA Crossover")
                from trading_bot.strategies.sma_crossover import SMAcrossover
                self.strategies.append(SMAcrossover())
                
        except Exception as e:
            logger.exception(f"Error initializing strategies: {e}")
            raise
    
    def _init_risk_manager(self):
        """Initialize risk management component."""
        try:
            from trading_bot.risk.manager import RiskManager
            
            self.risk_manager = RiskManager(
                config=self.config
            )
            
            logger.info("Risk manager initialized")
            
        except Exception as e:
            logger.exception(f"Error initializing risk manager: {e}")
            raise
    
    def _init_strategy_executor(self):
        """Initialize strategy executor component."""
        try:
            from trading_bot.core.executor import StrategyExecutor
            
            self.strategy_executor = StrategyExecutor(
                exchange=self.exchange,
                data_manager=self.data_manager,
                risk_manager=self.risk_manager,
                config=self.config
            )
            
            # Register strategies with the executor
            for strategy in self.strategies:
                self.strategy_executor.register_strategy(strategy)
                
            logger.info("Strategy executor initialized")
            
        except Exception as e:
            logger.exception(f"Error initializing strategy executor: {e}")
            raise
    
    def _init_decision_engine(self):
        """Initialize decision engine for adaptive strategy selection."""
        try:
            from trading_bot.ml.decision_engine import DecisionEngine
            
            # Only initialize if multiple strategies are used
            if len(self.strategies) > 1:
                self.decision_engine = DecisionEngine(
                    strategies=self.strategies,
                    data_manager=self.data_manager,
                    config=self.config
                )
                logger.info("Decision engine initialized for adaptive strategy selection")
                
        except Exception as e:
            logger.error(f"Error initializing decision engine: {e}")
            # Not critical, can continue without decision engine
            pass
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, sig, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {sig}, shutting down...")
        self.running = False
    
    def run_backtest(self):
        """Run the bot in backtesting mode."""
        try:
            from trading_bot.backtesting.engine import BacktestEngine
            
            self.initialize()
            
            # Parse date range for backtesting
            from_date = self.config.get('from_date')
            to_date = self.config.get('to_date', datetime.now().strftime('%Y-%m-%d'))
            initial_capital = float(self.config.get('initial_capital', 10000.0))
            
            # Create and run backtesting engine
            backtest_engine = BacktestEngine(
                strategies=self.strategies,
                data_manager=self.data_manager,
                exchange=self.exchange,
                from_date=from_date,
                to_date=to_date,
                initial_capital=initial_capital,
                config=self.config
            )
            
            logger.info(f"Starting backtest from {from_date} to {to_date} with {initial_capital} initial capital")
            results = backtest_engine.run()
            
            # Display and store results
            self._process_backtest_results(results)
            
        except Exception as e:
            logger.exception(f"Error during backtesting: {e}")
            raise
    
    def _process_backtest_results(self, results):
        """Process and display backtesting results."""
        try:
            from trading_bot.backtesting.analyzer import BacktestAnalyzer
            
            analyzer = BacktestAnalyzer(results)
            summary = analyzer.get_summary()
            
            print("\n=== Backtest Results ===")
            print(f"Total Return: {summary['total_return']:.2%}")
            print(f"Annualized Return: {summary['annualized_return']:.2%}")
            print(f"Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
            print(f"Max Drawdown: {summary['max_drawdown']:.2%}")
            print(f"Win Rate: {summary['win_rate']:.2%}")
            print(f"Profit Factor: {summary['profit_factor']:.2f}")
            print(f"Total Trades: {summary['total_trades']}")
            
            # Store results if data manager is available
            if self.data_manager:
                self.data_manager.store_backtest_results(results)
                
            # Generate plots if requested
            if hasattr(self.args, 'plot') and self.args.plot:
                analyzer.plot_equity_curve()
                analyzer.plot_drawdown_curve()
                analyzer.plot_monthly_returns()
                
        except Exception as e:
            logger.exception(f"Error processing backtest results: {e}")
    
    def run_optimization(self):
        """Run strategy parameter optimization."""
        try:
            from trading_bot.ml.optimizer import StrategyOptimizer
            
            self.initialize()
            
            # Create and run optimizer
            optimizer = StrategyOptimizer(
                strategies=self.strategies,
                data_manager=self.data_manager,
                config=self.config
            )
            
            logger.info("Starting strategy optimization")
            results = optimizer.run()
            
            # Display and store optimization results
            self._process_optimization_results(results)
            
        except Exception as e:
            logger.exception(f"Error during optimization: {e}")
            raise
    
    def _process_optimization_results(self, results):
        """Process and display optimization results."""
        print("\n=== Optimization Results ===")
        for strategy_name, params in results.items():
            print(f"\nBest parameters for {strategy_name}:")
            for param_name, param_value in params.items():
                print(f"  {param_name}: {param_value}")
                
        # Store optimized parameters if data manager is available
        if self.data_manager:
            self.data_manager.store_optimization_results(results)
    
    def run_paper_trading(self):
        """Run the bot in paper trading mode."""
        try:
            self.initialize()
            
            if not self.exchange:
                raise ValueError("Exchange not initialized")
                
            if not self.strategy_executor:
                raise ValueError("Strategy executor not initialized")
            
            self.running = True
            logger.info("Starting paper trading mode")
            
            self._trading_loop()
            
        except Exception as e:
            logger.exception(f"Error during paper trading: {e}")
            raise
    
    def run_live_trading(self):
        """Run the bot in live trading mode."""
        try:
            self.initialize()
            
            if not self.exchange:
                raise ValueError("Exchange not initialized")
                
            if not self.strategy_executor:
                raise ValueError("Strategy executor not initialized")
            
            # Check if exchange is in paper mode and warn if trying to run live
            if hasattr(self.exchange, 'paper_trading') and self.exchange.paper_trading:
                logger.warning("Exchange is in paper trading mode but live trading was requested")
                choice = input("Exchange is in paper trading mode. Continue anyway? [y/N]: ")
                if choice.lower() != 'y':
                    logger.info("Live trading aborted by user")
                    return
            
            self.running = True
            logger.info("Starting live trading mode")
            
            self._trading_loop()
            
        except Exception as e:
            logger.exception(f"Error during live trading: {e}")
            raise
    
    def _trading_loop(self):
        """Main trading loop for live and paper trading."""
        update_interval = int(self.config.get('update_interval', 60))  # Default 60 seconds
        
        try:
            while self.running:
                cycle_start = time.time()
                
                # Update market data
                self.strategy_executor.update_market_data()
                
                # Run trading cycle
                self.strategy_executor.execute_trading_cycle()
                
                # Calculate sleep time to maintain the update interval
                elapsed = time.time() - cycle_start
                sleep_time = max(0, update_interval - elapsed)
                
                if sleep_time > 0:
                    logger.debug(f"Sleeping for {sleep_time:.2f} seconds until next cycle")
                    # Use small sleep intervals to allow for faster response to shutdown signals
                    for _ in range(int(sleep_time)):
                        if not self.running:
                            break
                        time.sleep(1)
                    # Sleep any remaining fraction of a second
                    if self.running and sleep_time % 1 > 0:
                        time.sleep(sleep_time % 1)
                        
        except KeyboardInterrupt:
            logger.info("Trading bot manually stopped")
        except Exception as e:
            logger.exception(f"Error in trading loop: {e}")
        finally:
            self._shutdown()
    
    def _shutdown(self):
        """Perform clean shutdown of all components."""
        logger.info("Shutting down Trading Bot...")
        
        # Close all positions if configured to do so
        if self.config.get('close_positions_on_exit', False) and self.strategy_executor:
            try:
                logger.info("Closing all positions")
                self.strategy_executor.close_all_positions()
            except Exception as e:
                logger.error(f"Error closing positions: {e}")
        
        # Shutdown exchange connection
        if self.exchange:
            try:
                logger.info("Closing exchange connection")
                self.exchange.close()
            except Exception as e:
                logger.error(f"Error closing exchange connection: {e}")
        
        # Shutdown web server if running
        if self.web_server:
            try:
                logger.info("Shutting down web server")
                self.web_server.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down web server: {e}")
        
        # Save data and state
        if self.data_manager:
            try:
                logger.info("Saving data and state")
                self.data_manager.save_state()
            except Exception as e:
                logger.error(f"Error saving data: {e}")
        
        logger.info("Trading Bot shutdown complete")
    
    def run_web_interface(self):
        """Start the web interface for monitoring and control."""
        try:
            from trading_bot.api.server import create_server
            
            self.initialize()
            
            # Create and start web server
            port = int(self.config.get('web_port', 5000))
            self.web_server = create_server(
                trading_bot=self,
                port=port,
                config=self.config
            )
            
            logger.info(f"Starting web interface on port {port}")
            self.web_server.start()
            
            # Keep the main thread alive
            self.running = True
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            logger.exception(f"Error starting web interface: {e}")
            raise
        finally:
            self._shutdown() 