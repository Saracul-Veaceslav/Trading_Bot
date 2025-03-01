#!/usr/bin/env python3
"""
Main entry point for the Trading Bot application.
"""

import argparse
import logging
import sys
import time
from typing import Dict, Any

# Import from the new structure
from trading_bot.config.settings import SETTINGS
from trading_bot.data.manager import DataManager
from trading_bot.exchanges.base import BinanceTestnet
from trading_bot.core.strategy_executor import StrategyExecutor
from trading_bot.strategies.registry import get_strategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/trading.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("trading_bot")

def parse_args() -> Dict[str, Any]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Trading Bot')
    
    parser.add_argument('--symbol', type=str, default=SETTINGS.get('trading', {}).get('symbol', 'BTC/USDT'),
                        help='Trading symbol (default: BTC/USDT)')
    
    parser.add_argument('--timeframe', type=str, default=SETTINGS.get('trading', {}).get('timeframe', '1h'),
                        help='Timeframe for analysis (default: 1h)')
    
    parser.add_argument('--strategy', type=str, default=SETTINGS.get('trading', {}).get('strategy', 'SMAcrossover'),
                        help='Trading strategy to use (default: SMAcrossover)')
    
    parser.add_argument('--backtest', action='store_true',
                        help='Run in backtest mode')
    
    return vars(parser.parse_args())


def main():
    """Main function to run the trading bot."""
    args = parse_args()
    
    symbol = args['symbol']
    timeframe = args['timeframe']
    strategy_name = args['strategy']
    backtest_mode = args['backtest']
    
    logger.info(f"Starting Trading Bot with {strategy_name} strategy on {symbol} ({timeframe})")
    
    # Initialize components
    exchange = BinanceTestnet()
    data_manager = DataManager(exchange)
    strategy = get_strategy(strategy_name)
    
    if not strategy:
        logger.error(f"Strategy '{strategy_name}' not found")
        return 1
    
    executor = StrategyExecutor(exchange, data_manager, strategy)
    
    if backtest_mode:
        logger.info("Running in backtest mode")
        executor.run_backtest(symbol, timeframe)
    else:
        logger.info("Running in live trading mode")
        try:
            while True:
                executor.execute_strategy(symbol, timeframe)
                logger.info(f"Waiting for next execution cycle ({SETTINGS.get('trading', {}).get('execution_interval', 60)} seconds)")
                time.sleep(SETTINGS.get('trading', {}).get('execution_interval', 60))
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.exception(f"Error in trading loop: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 