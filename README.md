# Trading Bot for Binance Testnet

A paper trading bot that implements popular TradingView strategies on Binance Testnet.

## Features

- Paper trading with no real funds at risk
- Popular TradingView strategies implementation
- Stop-Loss and Take-Profit risk management
- Data storage for analysis and backtesting
- Modular and extensible architecture

## Installation

1. Clone the repository and navigate to it:
   ```
   git clone https://github.com/yourusername/Trading_Bot.git
   cd Trading_Bot
   ```

2. Set up Python environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Get Binance Testnet API credentials from [Binance Testnet](https://testnet.binance.vision/)

4. Create `.env` file with your credentials:
   ```
   cp .env.example .env
   # Edit .env file with your API key and secret
   ```

## Usage

```bash
# Run with default settings (BTC/USDT, 5m timeframe, SMA crossover)
python main.py

# Run with custom settings
python main.py --symbol ETH/USDT --interval 15m --strategy rsi
```

## Available Strategies

- **SMA Crossover**: Buy when short SMA crosses above long SMA, sell when it crosses below
- **RSI**: Buy when RSI crosses above oversold level, sell when it crosses below overbought level
- **MACD**: Buy on MACD line crossing above signal line, sell on crossing below

Strategy parameters can be configured in `config/settings.py`.

## Testing

```bash
# Run all tests
python -m unittest discover tests

# Run specific test
python -m unittest tests.test_sma_crossover
```

## Project Structure

```
├── main.py                     # Entry point
├── bot/                        # Core modules
│   ├── exchange.py             # Binance connectivity
│   ├── data_manager.py         # Data storage
│   ├── strategy_executor.py    # Strategy execution
│   ├── strategies/             # Trading strategies
│   └── config/                 # Settings
├── data/                       # CSV data storage
├── logs/                       # Log files
└── tests/                      # Unit tests
```

## Disclaimer

This bot is for educational purposes only. Paper trading does not involve real funds. Past performance of trading strategies is not indicative of future results. 