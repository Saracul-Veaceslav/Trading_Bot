# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Mock Exchange Framework for deterministic testing of trading strategies
  - MockExchange class implementing the Exchange protocol
  - Mock data generation utilities for creating synthetic OHLCV data
  - Support for different market patterns and trends
  - Comprehensive test suite for the mock exchange
- Data analysis script (analyze_data.py) for visualizing and analyzing historical data with technical indicators
- Command-line script (fetch_historical_data.py) for fetching historical data from Binance
- Strategy Composition Framework with CompositeStrategy and VotingStrategy classes
- Strategy Optimization Framework with grid search capabilities
- Performance metrics calculation (Sharpe ratio, Sortino ratio, max drawdown, win rate, profit factor)
- Property-Based Testing Framework for trading strategies
  - Data generators for OHLCV, order book, and trade data
  - Property validators for testing strategy invariants
  - Test helpers for creating trending and sideways markets
  - Comprehensive test suite for strategy properties
- Parallel optimization execution for improved performance
- Backtest method in Strategy base class for strategy evaluation
- Comprehensive test suite for optimization module
- Strategy Evaluation Framework with PerformanceMetrics and StrategyEvaluator classes
- Performance reporting with equity curve visualization and metrics calculation
- JSON report generation for strategy performance analysis
- Historical Data Management with HistoricalDataManager for efficient storage and retrieval of OHLCV data
  - Parquet file format for optimized storage and fast data retrieval
  - Date range filtering for targeted data access
  - Automatic directory management for organized data storage
  - Symbol normalization for consistent data handling
- Data loaders for fetching data from exchanges and loading from CSV files
  - ExchangeDataLoader with support for all CCXT exchanges
  - CSVDataLoader with flexible date format handling
  - Load-or-fetch pattern to minimize API calls
  - Automatic data saving to the data manager
- Binance Historical Data Fetcher for efficient data retrieval from Binance exchange
  - Support for multiple symbols and timeframes
  - Pagination for large date ranges
  - Rate limiting with exponential backoff
  - Parallel fetching for improved performance
- Pylon Storage system for optimized time series data storage
  - Apache Arrow and Parquet-based storage for efficient columnar data access
  - Partitioning for faster data retrieval
  - Compression for reduced storage size
  - Schema enforcement for data consistency
  - Memory-mapped files for faster reads
- Pylint code quality check for the entire project with results saved to pylint_report.txt

### Changed
- Enhanced Strategy base class with backtesting capabilities
- Improved frequency handling in HistoricalDataManager for consistent data retrieval

### Fixed
- Symbol handling in HistoricalDataManager to properly handle special characters
- Fixed parallel fetching in BinanceDataFetcher to correctly handle multiple symbols
- Fixed PylonStorage's load_dataframe method to properly preserve DatetimeIndex frequency
- Fixed PylonStorage's append_dataframe method to correctly handle duplicate timestamps
- Fixed PylonStorage's store_dataframe method to support custom partitioning columns
- Fixed test_performance method in PylonStorage tests to use non-deprecated frequency format ('h' instead of 'H')
- Fixed code quality issues in performance testing framework (trailing whitespace, missing newlines, import organization)
- Fixed cyclic import issue in strategy indicators module by reorganizing imports
- Fixed unnecessary ellipsis constants in protocol methods
- Fixed missing final newlines in multiple files
- Fixed unused imports in various modules

### Removed

## [0.1.0] - 2023-03-01

### Added
- Initial project structure
- Basic trading bot functionality
- Configuration system
- Logging system
- Data fetching and processing
- Strategy interface
- Simple moving average crossover strategy
- RSI strategy
- Backtesting module
- Paper trading mode
- Live trading mode
- Risk management
- Position sizing
- Order management
- Exchange integration
- Performance metrics
- Web interface
- API endpoints
- Documentation

### Changed
- Improved error handling
- Enhanced logging
- Optimized data processing
- Refined strategy interface

### Fixed
- Performance issues in backtesting
- Data synchronization bugs
- Error handling in exchange communication
- Configuration validation

### Removed
- Deprecated strategies
- Legacy code
- Unused dependencies
- Simple backtesting 