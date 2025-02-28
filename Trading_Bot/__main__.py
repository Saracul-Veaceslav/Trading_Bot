#!/usr/bin/env python
"""
Trading Bot - Command Line Interface

This module serves as the main entry point for running the Trading Bot from the command line.
It provides a command-line interface with various options for configuring and running the bot.
"""
import argparse
import sys
import logging
from pathlib import Path

# Configure basic logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('trading_bot')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Crypto Trading Bot with adaptive learning capabilities')
    
    # Mode options
    mode_group = parser.add_argument_group('mode')
    mode_group.add_argument('--live', action='store_true', help='Run in live trading mode')
    mode_group.add_argument('--paper', action='store_true', help='Run in paper trading mode')
    mode_group.add_argument('--backtest', action='store_true', help='Run in backtesting mode')
    mode_group.add_argument('--optimize', action='store_true', help='Run strategy optimization')
    mode_group.add_argument('--web', action='store_true', help='Start the web interface')
    
    # Configuration options
    config_group = parser.add_argument_group('configuration')
    config_group.add_argument('--config', type=str, help='Path to configuration file')
    config_group.add_argument('--exchange', type=str, help='Exchange to use (e.g., binance, coinbase)')
    config_group.add_argument('--symbols', type=str, nargs='+', help='Trading symbols (e.g., BTC/USDT)')
    config_group.add_argument('--strategies', type=str, nargs='+', help='Strategies to use')
    
    # Backtest options
    backtest_group = parser.add_argument_group('backtest')
    backtest_group.add_argument('--from-date', type=str, help='Start date for backtesting (YYYY-MM-DD)')
    backtest_group.add_argument('--to-date', type=str, help='End date for backtesting (YYYY-MM-DD)')
    backtest_group.add_argument('--initial-capital', type=float, default=10000.0, help='Initial capital for backtesting')
    
    # Logging options
    logging_group = parser.add_argument_group('logging')
    logging_group.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            default='INFO', help='Logging level')
    logging_group.add_argument('--log-file', type=str, help='Path to log file')
    
    # Version
    parser.add_argument('--version', action='store_true', help='Show version information')
    
    return parser.parse_args()

def setup_logging(args):
    """Configure logging based on command line arguments."""
    log_level = getattr(logging, args.log_level)
    logger.setLevel(log_level)
    
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

def show_version():
    """Display version information."""
    from trading_bot import __version__
    print(f"Trading Bot v{__version__}")
    print("An adaptive crypto trading bot with machine learning capabilities")
    print("(c) 2025 Trading Bot Team")

def main():
    """Main entry point for the command-line interface."""
    args = parse_arguments()
    
    if args.version:
        show_version()
        return 0
    
    setup_logging(args)
    
    try:
        # Import actual bot implementation here to avoid circular imports
        from trading_bot.core.bot import TradingBot
        
        # Initialize and run the bot with the parsed arguments
        bot = TradingBot(args)
        
        if args.backtest:
            logger.info("Starting backtesting mode")
            bot.run_backtest()
        elif args.optimize:
            logger.info("Starting strategy optimization")
            bot.run_optimization()
        elif args.web:
            logger.info("Starting web interface")
            bot.run_web_interface()
        elif args.paper:
            logger.info("Starting paper trading mode")
            bot.run_paper_trading()
        elif args.live:
            logger.info("Starting live trading mode")
            bot.run_live_trading()
        else:
            logger.error("No mode specified. Use --live, --paper, --backtest, --optimize, or --web")
            return 1
            
        return 0
        
    except KeyboardInterrupt:
        logger.info("Trading Bot stopped by user")
        return 0
    except Exception as e:
        logger.exception(f"Error running Trading Bot: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 