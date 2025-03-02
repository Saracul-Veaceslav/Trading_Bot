# Abidance Trading Bot: User Guide

This guide provides simple, step-by-step instructions for using the Abidance Trading Bot.

## Table of Contents
- [Setting Up](#setting-up)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Monitoring the Bot](#monitoring-the-bot)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Setting Up

### Prerequisites
- Python 3.8 or higher
- Internet connection
- Binance account (for live trading) or Binance Testnet account (for paper trading)

### Installation

1. **Set up your environment**:
   ```
   # Create and activate a virtual environment
   python -m venv .venv
   
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

## Configuration

### Basic Setup

1. **Edit your configuration file**:
   - Open `config.yaml` in any text editor
   - Add your API credentials in the `exchange` section
   - Customize trading pairs and strategies as needed

2. **Getting Binance Testnet API Keys (for paper trading)**:
   - Visit [Binance Futures Testnet](https://testnet.binancefuture.com/) or [Binance Spot Testnet](https://testnet.binance.vision/)
   - Create an account or sign in with GitHub
   - Generate API keys (look for "API Key" tab or "Generate HMAC_SHA256 Key" button)
   - Copy the API key and secret to your `config.yaml` file

### Configuration Examples

#### Trading XRP/USDT with SMA Crossover Strategy
```yaml
symbols:
  - symbol: XRP/USDT
    timeframe: 15m
    strategy: sma_crossover
    quantity: 100
```

#### Using RSI Strategy
```yaml
symbols:
  - symbol: BTC/USDT
    timeframe: 1h
    strategy: rsi_strategy
    quantity: 0.001
```

## Running the Bot

### Basic Run
```
python abidance_main.py
```

### Run with Specific Parameters
```
# Override symbol, timeframe, and strategy
python abidance_main.py --symbol BTC/USDT --timeframe 1h --strategy rsi_strategy

# Run for a limited time (e.g., 5 minutes)
python abidance_main.py --timeout 300

# Run in backtest mode
python abidance_main.py --backtest
```

## Monitoring the Bot

### Checking if the Bot is Running
```
# Check for running bot process
ps aux | grep abidance_main.py | grep -v grep
```

### Viewing Logs

#### Real-time Log Monitoring
```
# Watch main log file in real-time
tail -f logs/trading.log

# View strategy-specific logs
tail -f logs/trading_bot_strategies_sma_crossover.log

# View risk management logs
tail -f logs/trading_bot_risk_position_sizer.log
```

#### Checking Recent Activity
```
# View last 50 log entries
tail -n 50 logs/trading.log
```

### Understanding Log Messages
- `INFO - Fetching latest data for XRP/USDT`: Bot is retrieving market data
- `INFO - Executing sma_crossover strategy`: Bot is running the trading strategy
- `INFO - Iteration X`: Shows which cycle the bot is on
- `INFO - Applying risk management settings`: Risk parameters being applied

### Database Location and Structure
- Market data is stored in the `data/` directory
- Trading results are stored in the `results/` directory
- Database files are SQLite (.db files) and can be opened with any SQLite browser

## Troubleshooting

### Common Issues

#### Bot Won't Start
1. Check for Python errors in the terminal output
2. Verify your API keys in `config.yaml`
3. Make sure all dependencies are installed correctly

#### No Trades Being Executed
1. Check logs for any error messages
2. Verify that your strategy parameters are properly configured
3. Ensure your account has sufficient balance (for paper or live trading)

#### Connection Errors
1. Check your internet connection
2. Verify that Binance/Exchange is accessible
3. Check for rate limit issues in the logs

### Error Messages Guide

| Error Message | What It Means | How to Fix |
|---------------|--------------|------------|
| "Authentication error" | API keys are invalid | Update API keys in config.yaml |
| "Insufficient balance" | Not enough funds to execute trade | Add funds or reduce trade size |
| "Symbol not found" | Trading pair is incorrect | Update symbol in config or parameters |
| "Rate limit exceeded" | Too many requests to exchange | Wait and try again later |

## FAQ

### General Questions

**Q: How do I change the trading strategy?**  
A: Edit the `strategy` field in `config.yaml` or use the `--strategy` command line option.

**Q: Can I run multiple strategies at once?**  
A: Yes, define multiple symbols with different strategies in `config.yaml`.

**Q: Is my real money at risk?**  
A: Only if you set `trading.mode` to `live` and use real API keys. Use `paper` mode and testnet for practice.

**Q: Where can I find trading results?**  
A: Check the `results/` directory for performance reports and trade history.

### Trading Questions

**Q: What does the SMA Crossover strategy do?**  
A: It buys when the short-term moving average crosses above the long-term moving average, and sells when it crosses below.

**Q: How do I set up stop losses?**  
A: Configure the `risk.default_stop_loss_pct` parameter in `config.yaml`.

**Q: How can I limit how much money the bot uses?**  
A: Set the `trading.max_open_trades` and `symbols.max_allocation` parameters.

## Advanced Usage

### Custom Strategies
To implement a custom strategy, create a new file in the `abidance/strategy/` directory following the existing examples.

### Backtesting
Backtesting allows you to test strategies against historical data:
```
python abidance_main.py --backtest
```

The results will be saved in the `results/` directory.

---

This guide will be updated as new features are added to the Abidance Trading Bot.

Last Updated: March 2, 2025 