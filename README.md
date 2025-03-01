# Trading Bot

A sophisticated algorithmic trading bot for cryptocurrency markets with support for multiple strategies, exchanges, and risk management techniques.

## Overview

This Trading Bot is designed to automate cryptocurrency trading using various technical analysis strategies. It supports multiple exchanges, timeframes, and trading pairs, with a focus on modularity and extensibility.

Key features include:
- Multiple built-in trading strategies (SMA Crossover, RSI with Bollinger Bands)
- Support for multiple exchanges
- Comprehensive risk management
- Data collection and storage
- Backtesting capabilities
- Customizable configuration

## Installation

### Prerequisites
- Python 3.8 or higher
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

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
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
python main.py
```

With specific parameters:

```bash
python main.py --strategy sma_crossover --symbol BTC/USDT --interval 1h
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

See the [Tests README](Tests/README.md) for more details on testing.

## Project Structure

```
Trading_Bot/
├── Trading_Bot/           # Main package
│   ├── core/              # Core functionality
│   ├── strategies/        # Trading strategies
│   ├── exchanges/         # Exchange integrations
│   ├── data/              # Data management
│   ├── risk/              # Risk management
│   └── utils/             # Utility functions
├── Tests/                 # Test suite
├── config/                # Configuration files
├── data/                  # Data storage
└── logs/                  # Log files
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