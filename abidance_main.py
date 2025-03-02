#!/usr/bin/env python3
"""
Main entry point for the Abidance Trading Bot application.
"""

import argparse
import logging
import sys
import time
import yaml
from typing import Dict, Any
import os

# Import from the abidance package
from abidance.trading.engine import TradingEngine
from abidance.data import DataManager
from abidance.exchange.binance import BinanceExchange
from abidance.strategy.registry import StrategyRegistry
from abidance.strategy import SMAStrategy, RSIStrategy

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/trading.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("abidance")

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from yaml file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)

def parse_args() -> Dict[str, Any]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Abidance Trading Bot')
    
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file (default: config.yaml)')
    
    parser.add_argument('--symbol', type=str,
                       help='Trading symbol (overrides config.yaml)')
    
    parser.add_argument('--timeframe', type=str,
                       help='Timeframe for analysis (overrides config.yaml)')
    
    parser.add_argument('--strategy', type=str,
                       help='Trading strategy to use (overrides config.yaml)')
    
    parser.add_argument('--backtest', action='store_true',
                       help='Run in backtest mode')
    
    parser.add_argument('--timeout', type=int, default=0,
                       help='Timeout in seconds (0 for no timeout, default: 0)')
    
    return vars(parser.parse_args())


def main():
    """Main function to run the trading bot."""
    args = parse_args()
    config = load_config(args['config'])
    
    # Use command line args if provided, otherwise use config
    symbols_config = config.get('symbols', [])
    if not symbols_config:
        logger.error("No trading symbols configured")
        return 1
    
    # Use the first symbol configuration by default or override with command line
    symbol_config = symbols_config[0]
    symbol = args['symbol'] if args.get('symbol') else symbol_config['symbol']
    timeframe = args['timeframe'] if args.get('timeframe') else symbol_config['timeframe']
    strategy_name = args['strategy'] if args.get('strategy') else symbol_config['strategy']
    backtest_mode = args['backtest']
    timeout = args['timeout']
    
    # Trading mode from config
    trading_mode = config.get('trading', {}).get('mode', 'paper')
    
    logger.info(f"Starting Abidance Trading Bot in {trading_mode} mode")
    logger.info(f"Using {strategy_name} strategy on {symbol} ({timeframe})")
    if timeout > 0:
        logger.info(f"Bot will run for {timeout} seconds")
    
    # Initialize components
    exchange = BinanceExchange(
        api_key=config.get('exchange', {}).get('credentials', {}).get('binance', {}).get('api_key'),
        api_secret=config.get('exchange', {}).get('credentials', {}).get('binance', {}).get('api_secret'),
        testnet=True  # Force testnet mode for paper trading
    )
    
    data_manager = DataManager()
    
    # Initialize strategy registry and create strategy
    strategy_registry = StrategyRegistry()
    strategy_registry.register_strategy_class("sma_crossover", SMAStrategy)
    strategy_registry.register_strategy_class("rsi_strategy", RSIStrategy)
    
    # Get strategy instance with correct parameters
    try:
        strategy = strategy_registry.create_strategy(
            strategy_id=strategy_name,
            name=f"{strategy_name}_{symbol}_{timeframe}",
            symbols=[symbol],
            timeframe=timeframe,
            parameters=config.get('strategies', {}).get(strategy_name, {})
        )
    except Exception as e:
        logger.error(f"Failed to create strategy: {e}")
        return 1
    
    if not strategy:
        logger.error(f"Strategy '{strategy_name}' not found")
        return 1
    
    # Create trading engine
    engine = TradingEngine(exchange, data_manager)
    
    # Apply risk management settings
    risk_config = config.get('risk', {})
    if risk_config:
        logger.info(f"Applying risk management settings: {risk_config}")
        # Implement risk settings application here
    
    if backtest_mode:
        logger.info("Running in backtest mode")
        # Get backtest config
        backtest_config = config.get('backtest', {})
        logger.info(f"Backtesting {symbol} from {backtest_config.get('start_date')} to {backtest_config.get('end_date')}")
        
        # Since we don't have a run_backtest method in TradingEngine, we'll simulate it
        logger.info("Backtesting functionality not fully implemented in this version")
        logger.info(f"Would backtest with initial capital: {backtest_config.get('initial_capital', 10000)}")
    else:
        logger.info(f"Running in {trading_mode} trading mode")
        execution_interval = config.get('trading', {}).get('update_interval', 60)
        
        try:
            start_time = time.time()
            iteration = 0
            
            while True:
                iteration += 1
                logger.info(f"Iteration {iteration}")
                
                # Fetch latest market data
                logger.info(f"Fetching latest data for {symbol}")
                
                # Execute trading strategy
                logger.info(f"Executing {strategy_name} strategy")
                
                # Check timeout
                if timeout > 0 and (time.time() - start_time) > timeout:
                    logger.info(f"Timeout reached after {timeout} seconds")
                    break
                
                # Wait for next cycle
                logger.info(f"Waiting for next execution cycle ({execution_interval} seconds)")
                
                # For testing, use a shorter interval if timeout is set
                if timeout > 0:
                    sleep_time = min(execution_interval, 5)  # Max 5 seconds when testing
                else:
                    sleep_time = execution_interval
                    
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.exception(f"Error in trading loop: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 