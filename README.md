# Trading Bot

A Python-based trading bot for paper trading on Binance using popular TradingView strategies.

## Features

- **Paper Trading**: Test strategies without risking real funds
- **Multiple Strategies**: Includes SMA Crossover and popular TradingView strategies (RSI, MACD, Bollinger Bands)
- **Data Collection**: Gathers and stores historical market data for analysis
- **Risk Management**: Implements stop-loss and take-profit mechanisms
- **Backtest Support**: Test strategies on historical data
- **Modular Design**: Easy to add new strategies or exchange connectors

## Installation

### Prerequisites

- Python 3.8 or higher
- Binance API keys (for live trading)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Trading_Bot.git
cd Trading_Bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Binance API keys:
```
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

## Usage

### Basic Command

```bash
python -m Trading_Bot.main --symbol BTCUSDT --interval 1h --strategy sma_crossover --test-mode
```

### Command Line Arguments

- `--symbol`: Trading pair symbol (e.g., BTCUSDT, ETHUSDT)
- `--interval`: Timeframe (e.g., 1m, 5m, 1h, 4h, 1d)
- `--strategy`: Strategy to use (sma_crossover, rsi_strategy, macd_strategy, bollinger_bands_strategy)
- `--quantity`: Trading quantity
- `--test-mode`: Run in test mode (no real orders)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Path to log file
- `--iterations`: Number of iterations to run (None for indefinite)
- `--sleep-time`: Time to sleep between iterations in seconds

### Examples

**SMA Crossover Strategy**
```bash
python -m Trading_Bot.main --symbol ETHUSDT --interval 4h --strategy sma_crossover --test-mode
```

**RSI Strategy**
```bash
python -m Trading_Bot.main --symbol BTCUSDT --interval 1h --strategy rsi_strategy --test-mode
```

**MACD Strategy**
```bash
python -m Trading_Bot.main --symbol ETHUSDT --interval 1d --strategy macd_strategy --test-mode
```

**Bollinger Bands Strategy**
```bash
python -m Trading_Bot.main --symbol BTCUSDT --interval 15m --strategy bollinger_bands_strategy --test-mode
```

## Project Structure

```
Trading_Bot/
├── __init__.py
├── main.py                  # Main entry point
├── backtest.py              # Backtesting functionality
├── data_manager.py          # Handles data storage and retrieval
├── exchange.py              # Exchange connector (Binance)
├── strategy_executor.py     # Executes trading strategies
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration settings
├── strategies/
│   ├── __init__.py
│   ├── sma_crossover.py     # SMA Crossover strategy
│   └── tradingview_adapter.py # Adapter for TradingView strategies
├── logs/                    # Log files
└── data/                    # Data storage
    ├── historical/          # Historical OHLCV data
    └── trades/              # Trade records
```

## Trading Strategies

### SMA Crossover

The SMA Crossover strategy generates trading signals based on the crossing of two Simple Moving Averages:
- Buy signal: Short SMA crosses above Long SMA
- Sell signal: Short SMA crosses below Long SMA

### RSI Strategy

The RSI (Relative Strength Index) strategy generates signals based on overbought/oversold conditions:
- Buy signal: RSI crosses below the oversold level
- Sell signal: RSI crosses above the overbought level

### MACD Strategy

The MACD (Moving Average Convergence Divergence) strategy generates signals based on MACD line and signal line:
- Buy signal: MACD line crosses above signal line
- Sell signal: MACD line crosses below signal line

### Bollinger Bands Strategy

The Bollinger Bands strategy generates signals based on price touching or crossing the bands:
- Buy signal: Price touches or crosses below the lower band
- Sell signal: Price touches or crosses above the upper band

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

Or use the included test runner:

```bash
python simple_test_runner.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. 