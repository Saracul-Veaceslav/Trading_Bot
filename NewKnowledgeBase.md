# New Knowledge Base

This file documents new insights and knowledge gained during the development of the Trading Bot.

## Architecture Insights

- Using a modular architecture with clear separation of concerns (exchange, data management, strategy execution) makes the codebase more maintainable and testable.
- Dynamic strategy loading allows for easy addition of new trading strategies without modifying the core execution logic.

## Technical Insights

- CCXT library provides a unified interface for multiple exchanges, making it easy to switch between Binance Testnet and other exchanges.
- Pandas DataFrame is highly efficient for OHLCV data manipulation and strategy calculations.
- Using exponential backoff for API retries helps handle temporary network issues gracefully.

## Testing Insights

- Gherkin-style docstrings make tests more readable and help document the expected behavior.
- Using temporary directories for test data ensures tests don't interfere with each other.
- Mocking external dependencies like the exchange API allows for faster and more reliable tests.

## Trading Strategy Insights

- SMA Crossover is a simple but effective strategy for trend following.
- Proper risk management (SL/TP) is crucial for protecting capital, even in paper trading.
- Storing historical data and trades enables future backtesting and strategy optimization. 