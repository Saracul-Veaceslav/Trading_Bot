# Adaptive Crypto Trading Bot

An advanced, adaptive cryptocurrency trading bot with machine learning capabilities, comprehensive backtesting, and flexible strategy implementation.

## Features

- **Multi-Exchange Support**: Trade on Binance and other exchanges (via CCXT)
- **Multiple Trading Strategies**: From classic technical indicators to machine learning models
- **Risk Management**: Advanced position sizing, stop-loss and take-profit management
- **Real-time and Paper Trading**: Test strategies in a risk-free environment
- **Comprehensive Backtesting**: Test strategies against historical data
- **Strategy Optimization**: Find optimal parameters for any strategy
- **Data Collection & Storage**: Efficiently store and manage market data
- **Machine Learning Integration**: Enhance strategies with predictive models
- **Web API & Dashboard**: Monitor and control your bot through a web interface
- **Modular Architecture**: Easily extend with new exchanges, strategies, or features
- **Detailed Reporting**: Track performance with detailed metrics and visualizations

## Architecture

The trading bot follows a clean architecture pattern with domain-driven design:

```
trading_bot/
├── api/                 # Web API endpoints
├── backtesting/         # Backtesting engine
├── core/                # Core functionality and bot logic
├── data/                # Data management
│   ├── models/          # Database models
│   └── repositories/    # Data access layer
├── exchanges/           # Exchange adapters
├── ml/                  # Machine learning models
│   └── models/          # Trained model storage
├── risk/                # Risk management
├── strategies/          # Trading strategies
│   ├── indicators/      # Technical indicators
│   └── patterns/        # Chart patterns
└── utils/               # Utility functions
```

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip (Python package manager)
- Optional: TA-Lib (for technical analysis)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/adaptive-crypto-trading-bot.git
   cd adaptive-crypto-trading-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On Unix or MacOS
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Install TA-Lib:
   - Windows: `pip install https://download.lfd.uci.edu/pythonlibs/archived/TA_Lib-0.4.24-cp310-cp310-win_amd64.whl`
   - macOS: `brew install ta-lib && pip install ta-lib`
   - Linux: Install via package manager (e.g., `apt-get install ta-lib`) then `pip install ta-lib`

### Configuration

1. Create a configuration file:
   ```bash
   cp config.yaml.example config.yaml
   ```

2. Edit the configuration file with your exchange API keys and preferred settings.

### Running

#### Command-line Interface

Run the bot with the CLI:

```bash
python -m trading_bot --mode=paper --config=config.yaml --exchange=binance --symbols=BTC/USDT,ETH/USDT --strategy=sma_crossover
```

Available modes:
- `live`: Live trading with real funds
- `paper`: Paper trading (simulated with real market data)
- `backtest`: Backtesting against historical data
- `optimize`: Optimize strategy parameters
- `web`: Start the web dashboard and API

#### Web Dashboard

Start the web dashboard:

```bash
python -m trading_bot --mode=web --port=8080
```

Then open your browser and navigate to `http://localhost:8080`.

## Trading Strategies

### Built-in Strategies

- **SMA Crossover**: Simple Moving Average crossover strategy
- **RSI**: Relative Strength Index strategy
- **MACD**: Moving Average Convergence Divergence strategy
- **Bollinger Bands**: Bollinger Bands strategy
- **ML Prediction**: Machine learning-based prediction strategy

### Creating Custom Strategies

Create a new strategy by inheriting from the base Strategy class:

```python
from trading_bot.strategies.base import Strategy

class MyCustomStrategy(Strategy):
    def __init__(self, **kwargs):
        super().__init__(name="MyCustomStrategy", **kwargs)
        # Initialize strategy-specific parameters
        
    def calculate_indicators(self, df):
        # Calculate indicators on the DataFrame
        return df
        
    def generate_signal(self, df):
        # Generate buy/sell signals
        return signal
```

## Backtesting

Backtest a strategy against historical data:

```bash
python -m trading_bot --mode=backtest --strategy=sma_crossover --symbols=BTC/USDT --start=2022-01-01 --end=2022-12-31 --timeframe=1h --initial-capital=10000
```

The backtesting results will be saved to the `results/` directory.

## Optimization

Optimize strategy parameters:

```bash
python -m trading_bot --mode=optimize --strategy=sma_crossover --symbols=BTC/USDT --start=2022-01-01 --end=2022-12-31 --timeframe=1h
```

The optimization results will be saved to the `results/` directory.

## API Reference

### REST API

The bot provides a REST API for monitoring and control when running in web mode:

- `GET /api/status`: Get the bot status
- `GET /api/strategies`: List available strategies
- `GET /api/symbols`: List available trading symbols
- `GET /api/positions`: List open positions
- `POST /api/start`: Start the bot
- `POST /api/stop`: Stop the bot
- `POST /api/trade`: Create a manual trade

### Webhook API

You can trigger trades via webhooks:

```bash
curl -X POST http://localhost:8080/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"strategy":"sma_crossover", "symbol":"BTC/USDT", "action":"buy", "price":50000, "amount":0.1}'
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

## Acknowledgements

- [CCXT](https://github.com/ccxt/ccxt) for exchange connectivity
- [pandas](https://pandas.pydata.org/) for data manipulation
- [scikit-learn](https://scikit-learn.org/) for machine learning capabilities
- [TA-Lib](https://ta-lib.org/) for technical analysis indicators 