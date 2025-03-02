# Abidance Crypto Trading Bot

A comprehensive cryptocurrency trading bot framework with support for multiple exchanges, strategies, and risk management techniques.

## Features

- **Multi-Exchange Support**: Integration with cryptocurrency exchanges (primarily Binance)
- **Trading Strategy Framework**: Support for implementing and executing various trading strategies
  - Pre-built strategies include SMA Crossover and RSI Bollinger Bands
  - Modular design for adding custom strategies
- **Risk Management System**: 
  - Multiple position sizing algorithms (Fixed Risk, Volatility-based, Kelly Criterion)
  - Stop-loss and take-profit functionality
- **Data Management**: 
  - Historical and real-time OHLCV data handling
  - Storage and retrieval via both file-based and database systems
- **Backtesting Capabilities**: Ability to test strategies against historical market data
- **Error Handling Framework**: Comprehensive error management with retries, fallbacks, and circuit breakers

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/abidance.git
   cd abidance
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example configuration file:
   ```
   cp config.yaml.example config.yaml
   ```

2. Edit the configuration file to set up your trading preferences:
   - API credentials for your exchange
   - Trading pairs and timeframes
   - Strategy parameters
   - Risk management settings

### Getting Binance Testnet API Keys

For paper trading, you'll need Binance Testnet API keys:

1. For Futures Testnet:
   - Visit https://testnet.binancefuture.com/
   - Look for the "API Key" tab in the panel below the main chart

2. For Spot Testnet:
   - Visit https://testnet.binance.vision/
   - Sign in with GitHub
   - Click "Generate HMAC_SHA256 Key"

## Usage

### Running the Bot

To run the bot with default settings from the config file:
```
python abidance_main.py
```

### Command Line Options

- `--config CONFIG`: Path to configuration file (default: config.yaml)
- `--symbol SYMBOL`: Trading symbol (overrides config.yaml)
- `--timeframe TIMEFRAME`: Timeframe for analysis (overrides config.yaml)
- `--strategy STRATEGY`: Trading strategy to use (overrides config.yaml)
- `--backtest`: Run in backtest mode
- `--timeout TIMEOUT`: Timeout in seconds (0 for no timeout, default: 0)

### Examples

Run with a specific symbol and timeframe:
```
python abidance_main.py --symbol BTC/USDT --timeframe 1h
```

Run in backtest mode:
```
python abidance_main.py --backtest
```

Run with a specific strategy:
```
python abidance_main.py --strategy rsi_strategy
```

## Available Strategies

1. **SMA Crossover Strategy**
   - Uses two Simple Moving Averages to generate buy/sell signals
   - Buy when short SMA crosses above long SMA
   - Sell when short SMA crosses below long SMA

2. **RSI Strategy**
   - Uses Relative Strength Index to identify overbought/oversold conditions
   - Buy when RSI crosses below oversold threshold and then back above
   - Sell when RSI crosses above overbought threshold and then back below

## Development

### Project Structure

- `abidance/`: Main package
  - `core/`: Core functionality
  - `data/`: Data management
  - `exchange/`: Exchange integrations
  - `strategy/`: Trading strategies
  - `trading/`: Trading engine and order management
  - `type_defs/`: Type definitions
  - `exceptions/`: Custom exceptions
  - `utils/`: Utility functions

### Adding a New Strategy

1. Create a new file in the `abidance/strategy/` directory
2. Implement the `Strategy` interface
3. Register your strategy in the `StrategyRegistry`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred from using this software.

## 🚨 Important Notice: Package Structure Changes

**As of version 0.2.0, we've refactored the package structure for better maintainability and standardization.**

The package has been renamed from mixed-case `Trading_Bot` to lowercase `trading_bot` following Python conventions.
For migration instructions, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

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

 