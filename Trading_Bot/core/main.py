"""
Main module for the Trading Bot.

This script initializes and runs the trading bot with user-specified configuration.
"""
import os
import argparse
import logging
import time
import signal
import sys
from datetime import datetime

# Early check for TA-Lib availability
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

from trading_bot.config.settings import SETTINGS, TRADINGVIEW_STRATEGIES
from trading_bot.data_manager import DataManager
from trading_bot.exchange import BinanceTestnet
from trading_bot.strategy_executor import StrategyExecutor

# Import get_strategy conditionally to avoid import errors
try:
    from trading_bot.strategies.tradingview_adapter import get_strategy
except ImportError as e:
    def get_strategy(strategy_name, parameters=None):
        logging.getLogger('error').error(f"Could not import strategy adapter: {e}")
        return None

# Set up logging
def setup_logging(log_level=None, log_file=None):
    """
    Set up logging configuration.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Path to log file
    """
    if log_level is None:
        log_level = SETTINGS.get('log_level', 'INFO')
    
    if log_file is None:
        log_file = SETTINGS.get('log_file', 'logs/trading_bot.log')
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Create trading and error loggers
    trading_logger = logging.getLogger('trading')
    error_logger = logging.getLogger('error')
    
    return trading_logger, error_logger

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Trading Bot')
    
    # Basic configuration
    parser.add_argument('--symbol', type=str, default=SETTINGS.get('symbol', 'BTCUSDT'),
                        help='Trading pair symbol (e.g., BTCUSDT)')
    parser.add_argument('--interval', type=str, default=SETTINGS.get('interval', '1h'),
                        help='Timeframe (e.g., 1h, 4h, 1d)')
    parser.add_argument('--quantity', type=float, default=SETTINGS.get('quantity', 0.001),
                        help='Trading quantity')
    
    # Strategy configuration
    parser.add_argument('--strategy', type=str, default='sma_crossover',
                        help='Strategy to use (e.g., sma_crossover, rsi_strategy, macd_strategy)')
    
    # Trading mode
    parser.add_argument('--test-mode', action='store_true', default=SETTINGS.get('test_mode', True),
                        help='Run in test mode (no real orders)')
    
    # Logging configuration
    parser.add_argument('--log-level', type=str, default=SETTINGS.get('log_level', 'INFO'),
                        help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--log-file', type=str, default=SETTINGS.get('log_file', 'logs/trading_bot.log'),
                        help='Path to log file')
    
    # Run configuration
    parser.add_argument('--iterations', type=int, default=None,
                        help='Number of iterations to run (None for indefinite)')
    parser.add_argument('--sleep-time', type=int, default=60,
                        help='Time to sleep between iterations in seconds')
    
    return parser.parse_args()

def initialize_components(args, trading_logger, error_logger):
    """
    Initialize bot components.
    
    Args:
        args (argparse.Namespace): Command line arguments
        trading_logger (logging.Logger): Logger for trading activity
        error_logger (logging.Logger): Logger for errors
        
    Returns:
        tuple: Initialized components (exchange, data_manager, strategy_executor)
    """
    # Initialize exchange
    trading_logger.info("Initializing exchange...")
    exchange = BinanceTestnet(
        api_key=SETTINGS.get('api_key', ''),
        api_secret=SETTINGS.get('api_secret', '')
    )
    
    # Initialize data manager
    trading_logger.info("Initializing data manager...")
    data_manager = DataManager(trading_logger, error_logger)
    
    # Get the strategy
    strategy = None
    if args.strategy in TRADINGVIEW_STRATEGIES:
        trading_logger.info(f"Using TradingView strategy: {args.strategy}")
        if not TALIB_AVAILABLE:
            trading_logger.warning(
                "TA-Lib is not installed. TradingView strategies will use fallback implementations. "
                "For better performance, install TA-Lib: brew install ta-lib && pip install TA-Lib"
            )
        strategy = get_strategy(args.strategy)
    else:
        trading_logger.info(f"Using strategy: {args.strategy}")
        strategy = None  # Will be loaded by StrategyExecutor
    
    # Initialize strategy executor
    trading_logger.info("Initializing strategy executor...")
    strategy_executor = StrategyExecutor(
        exchange=exchange,
        data_manager=data_manager,
        strategy_name=None if strategy else args.strategy,
        strategy=strategy,
        symbol=args.symbol,
        interval=args.interval,
        quantity=args.quantity,
        test_mode=args.test_mode,
        trading_logger=trading_logger,
        error_logger=error_logger
    )
    
    return exchange, data_manager, strategy_executor

def setup_signal_handlers(strategy_executor, trading_logger):
    """
    Set up signal handlers for graceful shutdown.
    
    Args:
        strategy_executor (StrategyExecutor): Strategy executor instance
        trading_logger (logging.Logger): Logger for trading activity
    """
    def signal_handler(sig, frame):
        trading_logger.info(f"Received signal {sig}, shutting down...")
        strategy_executor.stop()
        trading_logger.info("Trading bot stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """
    Main function to run the trading bot.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    trading_logger, error_logger = setup_logging(args.log_level, args.log_file)
    
    # Print system status
    trading_logger.info("=" * 50)
    trading_logger.info(f"Trading Bot - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    trading_logger.info(f"Python version: {sys.version}")
    trading_logger.info(f"TA-Lib available: {TALIB_AVAILABLE}")
    trading_logger.info(f"Symbol: {args.symbol}, Interval: {args.interval}, Strategy: {args.strategy}")
    trading_logger.info(f"Test Mode: {'Enabled' if args.test_mode else 'Disabled'}")
    trading_logger.info("=" * 50)
    
    # Initialize components
    try:
        exchange, data_manager, strategy_executor = initialize_components(args, trading_logger, error_logger)
    except ImportError as e:
        error_logger.error(f"Failed to initialize components due to missing module: {e}")
        trading_logger.error(
            "Cannot start the bot due to missing dependencies. "
            "Please check the error log and install the required packages."
        )
        sys.exit(1)
    except Exception as e:
        error_logger.exception(f"Failed to initialize components: {e}")
        trading_logger.error("Cannot start the bot due to initialization error.")
        sys.exit(1)
    
    # Set up signal handlers
    setup_signal_handlers(strategy_executor, trading_logger)
    
    # Run the bot
    try:
        trading_logger.info("Starting trading bot...")
        results = strategy_executor.run(
            iterations=args.iterations,
            sleep_time=args.sleep_time
        )
        trading_logger.info("Trading bot finished")
        
    except Exception as e:
        error_logger.exception(f"Error running trading bot: {e}")
        trading_logger.error("Trading bot stopped due to error")
        
    finally:
        # Print summary
        trading_logger.info("=" * 50)
        trading_logger.info(f"Trading Bot - Stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        trading_logger.info("=" * 50)

if __name__ == "__main__":
    main()
