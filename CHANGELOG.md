# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Strategy Composition Framework with CompositeStrategy and VotingStrategy classes
- Strategy Optimization Framework with grid search capabilities
- Performance metrics calculation (Sharpe ratio, Sortino ratio, max drawdown, win rate, profit factor)
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

### Changed
- Enhanced Strategy base class with backtesting capabilities
- Improved frequency handling in HistoricalDataManager for consistent data retrieval

### Fixed
- Symbol handling in HistoricalDataManager to properly handle special characters

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