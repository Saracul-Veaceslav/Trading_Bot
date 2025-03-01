# Trading Bot

A flexible cryptocurrency trading bot framework for implementing and testing various trading strategies.

## Overview

This Trading Bot is designed to automate cryptocurrency trading using various technical analysis strategies. It supports multiple exchanges, timeframes, and trading pairs, with a focus on modularity and extensibility.

Key features include:
- Multiple built-in trading strategies (SMA Crossover, RSI with Bollinger Bands)
- Support for multiple exchanges
- Comprehensive risk management
- Data collection and storage
- Backtesting capabilities
- Customizable configuration

## 🚨 Important Notice: Package Structure Changes

**As of version 0.2.0, we've refactored the package structure for better maintainability and standardization.**

The package has been renamed from mixed-case `Trading_Bot` to lowercase `trading_bot` following Python conventions.
For migration instructions, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Trading_Bot.git
   cd Trading_Bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Create a configuration file:
   ```bash
   cp config.yaml.example config.yaml
   ```

5. Edit the configuration file with your exchange API keys and strategy parameters.

## Configuration

The bot is configured using a YAML file located at `config.yaml`. This file contains:

- Exchange API credentials
- Strategy parameters
- Risk management settings
- Logging configuration

Example configuration:

```yaml
exchanges:
  binance:
    api_key: "your_api_key"
    api_secret: "your_api_secret"
    test_mode: true

strategies:
  sma_crossover:
    short_window: 10
    long_window: 30
    
risk_management:
  max_position_size: 0.1  # 10% of available balance
  stop_loss_pct: 0.02     # 2% stop loss
  take_profit_pct: 0.05   # 5% take profit
```

## Usage

### Running the Bot

To start the bot with the default configuration:

```bash
trading-bot
```

Or directly with Python:

```bash
python -m trading_bot
```

With specific parameters:

```bash
trading-bot --strategy sma_crossover --symbol BTC/USDT --interval 1h
```

### Command Line Arguments

- `--strategy`: Trading strategy to use (default: sma_crossover)
- `--symbol`: Trading pair (default: BTC/USDT)
- `--interval`: Timeframe (default: 1h)
- `--exchange`: Exchange to use (default: binance)
- `--config`: Path to configuration file (default: config.yaml)
- `--test`: Run in test mode without executing real trades (default: True)

## Available Strategies

### SMA Crossover
A simple moving average crossover strategy that generates buy signals when the short-term moving average crosses above the long-term moving average, and sell signals when it crosses below.

Parameters:
- `short_window`: Period for the short-term moving average
- `long_window`: Period for the long-term moving average

### RSI with Bollinger Bands
A strategy that uses the Relative Strength Index (RSI) in combination with Bollinger Bands to identify overbought and oversold conditions.

Parameters:
- `rsi_period`: Period for RSI calculation
- `rsi_overbought`: RSI level considered overbought
- `rsi_oversold`: RSI level considered oversold
- `bb_period`: Period for Bollinger Bands calculation
- `bb_std_dev`: Standard deviation multiplier for Bollinger Bands

## Testing

The project includes a comprehensive test suite. To run the tests:

```bash
python run_tests.py
```

For more specific test runs:

```bash
# Run only unit tests
python run_tests.py --unit

# Run tests for a specific module
python run_tests.py --module strategies

# Run a specific test file
python run_tests.py --file test_sma_crossover.py

# Run tests with coverage report
python run_tests.py --coverage
```

See the [Tests README](tests/README.md) for more details on testing.

## Project Structure

```
trading_bot/             # Main package (new standardized structure)
├── core/                # Core functionality
│   ├── __init__.py
│   ├── strategy_executor.py
│   └── main.py
├── data/                # Data management
│   ├── __init__.py
│   ├── exceptions.py
│   └── manager.py
├── exchanges/           # Exchange integrations
│   ├── __init__.py
│   ├── exceptions.py
│   ├── base.py
│   └── binance.py
├── strategies/          # Trading strategies
│   ├── __init__.py
│   ├── base.py
│   ├── sma_crossover.py
│   └── rsi_bollinger.py
├── risk/                # Risk management
│   ├── __init__.py
│   └── position_sizer.py
├── config/              # Configuration
│   ├── __init__.py
│   ├── exceptions.py
│   └── settings.py
├── utils/               # Utility functions
│   ├── __init__.py
│   └── logger.py
├── __init__.py
└── exceptions.py
```

## Development

### Code Style

We use the following tools to ensure code quality:
- Black for code formatting
- isort for import sorting
- mypy for type checking
- flake8 for linting

You can run these tools using the pre-configured settings in `pyproject.toml`:

```bash
# Format code
black .

# Sort imports
isort .

# Type check
mypy .

# Lint
flake8 .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. 