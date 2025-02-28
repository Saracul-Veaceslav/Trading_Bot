"""
Configuration settings for the trading bot.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
HISTORICAL_DATA_DIR = os.path.join(DATA_DIR, 'historical')
TRADES_DATA_DIR = os.path.join(DATA_DIR, 'trades')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HISTORICAL_DATA_DIR, exist_ok=True)
os.makedirs(TRADES_DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Exchange settings
SETTINGS = {
    "api_key": os.getenv("BINANCE_API_KEY", ""),
    "api_secret": os.getenv("BINANCE_API_SECRET", ""),
    "symbol": "BTCUSDT",
    "interval": "1h",
    "limit": 500,
    "quantity": 0.001,  # Default trade quantity
    "test_mode": True,  # Default to test mode (no real orders)
    "log_level": "INFO",
    "log_file": os.path.join(LOGS_DIR, "trading_bot.log"),
    "data_dir": DATA_DIR,
    "HISTORICAL_DATA_PATH": HISTORICAL_DATA_DIR,
    "TRADES_DATA_PATH": TRADES_DATA_DIR,
    "HISTORICAL_TRADES_PATH": TRADES_DATA_DIR,
    "STOP_LOSS_PERCENT": 0.02,
    "TAKE_PROFIT_PERCENT": 0.03
}

# Strategy parameters
STRATEGY_PARAMS = {
    "sma_crossover": {
        "short_window": 20,
        "long_window": 50,
        "name": "SMA Crossover"
    },
    # Add more strategies here as needed
}

# TradingView strategy parameters
TRADINGVIEW_STRATEGIES = {
    "rsi_strategy": {
        "name": "RSI Strategy",
        "parameters": {
            "rsi_period": 14,
            "overbought": 70,
            "oversold": 30
        }
    },
    "macd_strategy": {
        "name": "MACD Strategy",
        "parameters": {
            "fast_length": 12,
            "slow_length": 26,
            "signal_length": 9
        }
    },
    "bollinger_bands_strategy": {
        "name": "Bollinger Bands Strategy",
        "parameters": {
            "length": 20,
            "std_dev": 2
        }
    }
}

# Paper trading settings
PAPER_TRADING = {
    "initial_balance": 10000,  # Initial balance in USD
    "fee_rate": 0.001,  # 0.1% fee per trade
    "slippage": 0.0005  # 0.05% slippage
}
