"""
Trading Bot Configuration Settings

This module contains all configurable parameters for the trading bot.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Main settings dictionary
SETTINGS = {
    # Exchange settings
    'API_KEY': os.getenv('BINANCE_API_KEY', ''),
    'API_SECRET': os.getenv('BINANCE_API_SECRET', ''),
    'TESTNET': True,  # Paper trading only
    
    # Trading settings
    'TRADING_PAIR': 'BTC/USDT',  # Default trading pair
    'TIMEFRAME': '5m',           # Default timeframe (5 minutes)
    'UPDATE_INTERVAL': 60,       # Seconds between updates
    'ERROR_SLEEP_TIME': 30,      # Seconds to wait after error
    'MAX_RETRIES': 3,            # Maximum retries for API calls
    
    # Position management
    'POSITION_SIZE': 0.001,      # BTC amount
    
    # Risk management
    'STOP_LOSS_PERCENT': 0.02,   # 2% stop loss
    'TAKE_PROFIT_PERCENT': 0.04, # 4% take profit
    
    # Strategy settings
    'STRATEGY': 'sma_crossover', # Default strategy
    
    # File paths
    'HISTORICAL_DATA_PATH': 'data/historical_data.csv',
    'HISTORICAL_TRADES_PATH': 'data/historical_trades.csv',
}

# Strategy-specific parameters
# These will be used by the strategy module
STRATEGY_PARAMS = {
    # SMA Crossover strategy parameters
    'sma_crossover': {
        'SMA_SHORT': 10,         # Short moving average period
        'SMA_LONG': 50,          # Long moving average period
    },
    
    # RSI strategy parameters
    'rsi': {
        'RSI_PERIOD': 14,        # RSI calculation period
        'RSI_OVERBOUGHT': 70,    # RSI overbought threshold
        'RSI_OVERSOLD': 30,      # RSI oversold threshold
    },
    
    # MACD strategy parameters
    'macd': {
        'MACD_FAST': 12,         # MACD fast EMA period
        'MACD_SLOW': 26,         # MACD slow EMA period
        'MACD_SIGNAL': 9,        # MACD signal period
    }
} 