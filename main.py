#!/usr/bin/env python
"""Trading Bot: Entry point for the Binance Testnet trading application."""

import argparse
import logging
import sys
import time
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bot.exchange import BinanceTestnet
from bot.strategy_executor import StrategyExecutor
from bot.data_manager import DataManager
from bot.config.settings import SETTINGS


def setup_logging():
    """Configure and return trading and error loggers."""
    Path("logs").mkdir(exist_ok=True)
    
    # Trading logger
    trading_logger = logging.getLogger('trading')
    trading_logger.setLevel(logging.INFO)
    
    # Error logger
    error_logger = logging.getLogger('errors')
    error_logger.setLevel(logging.ERROR)
    
    # Handlers
    file_fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setFormatter(file_fmt)
    
    # Trading log
    t_handler = logging.FileHandler('logs/trading.log')
    t_handler.setFormatter(file_fmt)
    trading_logger.addHandler(t_handler)
    trading_logger.addHandler(console)
    
    # Error log
    e_handler = logging.FileHandler('logs/errors.log')
    e_handler.setFormatter(file_fmt)
    error_logger.addHandler(e_handler)
    error_logger.addHandler(console)
    
    return trading_logger, error_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Trading Bot for Binance Testnet')
    parser.add_argument('--symbol', type=str, default=SETTINGS['TRADING_PAIR'],
                        help=f'Trading pair (default: {SETTINGS["TRADING_PAIR"]})')
    parser.add_argument('--interval', type=str, default=SETTINGS['TIMEFRAME'],
                        help=f'Candle timeframe (default: {SETTINGS["TIMEFRAME"]})')
    parser.add_argument('--strategy', type=str, default=SETTINGS['STRATEGY'],
                        help=f'Trading strategy (default: {SETTINGS["STRATEGY"]})')
    
    return parser.parse_args()


def main():
    """Run the trading bot."""
    args = parse_arguments()
    trading_logger, error_logger = setup_logging()
    
    trading_logger.info(f"Starting trading bot with {args.symbol} on {args.interval} timeframe")
    
    try:
        # Initialize components
        exchange = BinanceTestnet(trading_logger, error_logger)
        data_manager = DataManager(trading_logger, error_logger)
        executor = StrategyExecutor(
            exchange=exchange,
            data_manager=data_manager,
            trading_logger=trading_logger,
            error_logger=error_logger,
            symbol=args.symbol,
            timeframe=args.interval,
            strategy_name=args.strategy
        )
        
        # Create data directory
        Path("data").mkdir(exist_ok=True)
        
        # Bot main loop
        trading_logger.info("Bot initialized successfully. Starting main loop...")
        
        while True:
            try:
                executor.execute_iteration()
                time.sleep(SETTINGS['UPDATE_INTERVAL'])
            except KeyboardInterrupt:
                trading_logger.info("Bot stopped by user")
                break
            except Exception as e:
                error_logger.exception(f"Error in main loop: {str(e)}")
                time.sleep(SETTINGS['ERROR_SLEEP_TIME'])
    
    except Exception as e:
        error_logger.exception(f"Critical initialization error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 