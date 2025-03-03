# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- RESTful API for accessing trading bot data
  - FastAPI-based implementation with dependency injection
  - Endpoints for listing strategies and trades
  - Support for filtering trades by symbol and date range
  - Comprehensive test suite with proper mocking
- WebSocket server implementation for real-time communication
  - WebSocketManager for handling client connections
  - Support for broadcasting events to connected clients
  - Event handler registration system
  - Integration with the core event system for real-time updates
  - Comprehensive test suite with proper async testing
  - Async event handlers for efficient event propagation
  - Error handling for client disconnections during broadcasts
- API server implementation for serving the RESTful API
  - Configurable host and port settings
  - Integration with FastAPI application
- React-based Frontend Dashboard for monitoring trading activities
  - Real-time trading data visualization with Chart.js
  - WebSocket integration for live updates
  - Responsive design for desktop and mobile
  - Comprehensive error handling
  - TypeScript for type safety
  - TDD-based implementation with comprehensive test suite
  - Component-based architecture for maintainability
  - Modern UI with clean design
- Model Selection Framework for evaluating and selecting machine learning models
  - ModelEvaluator class for evaluating multiple models on the same dataset
  - Support for various performance metrics (precision, recall, f1, etc.)
  - Automatic selection of the best performing model based on specified metrics
  - Comprehensive test suite for model evaluation and selection
- Feature Engineering Framework for machine learning models
  - Abstract FeatureGenerator base class for consistent feature generation
  - TechnicalFeatureGenerator for creating technical indicators from OHLCV data
  - Support for multiple window sizes for rolling calculations
  - Comprehensive test suite for feature generators
- Online Learning System for continuous model updating
  - OnlineLearner class for monitoring model performance and triggering retraining
  - DataBuffer class for efficient data storage with FIFO behavior
  - Performance degradation detection to automatically update models
  - Comprehensive test suite for online learning components
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
- Database Query Optimization Framework
  - QueryOptimizer class for efficient data retrieval
  - Optimized SQL queries with window functions for technical indicators
  - Database index management for improved query performance
  - Function-based indexes for time-based aggregations
  - Comprehensive test suite for query optimization
- Property-Based Testing Framework for trading strategies
  - Data generators for OHLCV, order book, and trade data
  - Property validators for testing strategy invariants
  - Test helpers for creating trending and sideways markets
  - Comprehensive test suite for strategy properties
  - Functions to test strategy consistency and edge cases
  - Support for testing with realistic market scenarios
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
- Comprehensive test suite with 633 passing tests and 17 skipped tests
- Database schema design with SQLAlchemy models for Trade, Strategy, and OHLCV data
- Alembic migration setup for database schema versioning
- Unit tests for database models with comprehensive test coverage
- Unique constraint on OHLCV data to prevent duplicates
- Indexes on frequently queried fields for better performance
- Repository Pattern implementation for database access
  - BaseRepository with common CRUD operations
  - TradeRepository for trade-specific queries
  - StrategyRepository for strategy-specific queries
  - Transaction support with context manager
  - Date range filtering for trades and strategies
- Database Migration System using Alembic for versioned database schema changes
  - Migration manager utility for creating, upgrading, and downgrading migrations
  - Initial migration for the core database models (Trade, Strategy, OHLCV)
  - Comprehensive test suite for the migration system

### Changed
- Enhanced Strategy base class with backtesting capabilities
- Improved frequency handling in HistoricalDataManager for consistent data retrieval
- Improved code quality score from 8.26/10 to 9.0/10 through code cleanup and refactoring
- Refactored repository implementation to improve code quality and maintainability
- Enhanced JSON parameter handling in StrategyRepository for more reliable filtering

### Fixed
- Fixed DataPreprocessor's remove_outliers method to properly handle integer outliers and extreme values
- Fixed pandas dtype incompatibility warning in DataPreprocessor by explicitly casting values to the appropriate type
- Fixed calculate_profit_metrics function in validation module to correctly calculate profit-based performance metrics
- Fixed test_remove_outliers test to use more extreme outlier values for reliable testing
- Fixed test_calculate_profit_metrics test to properly calculate expected returns based on correct and incorrect predictions
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
- Fixed cyclic import issues in exceptions module by moving the base exception class to a separate file
- Reduced nested blocks in collectors.py by extracting helper methods for metric processing
- Reduced nested blocks in sma.py by extracting test-specific code into a separate method
- Fixed syntax errors in multiple files (environment.py, health/checks.py, ml/__init__.py, trading/engine.py, logging/handlers.py, strategy/sma.py)
- Fixed invalid decimal literal syntax in string formatting by converting to f-strings
- Fixed missing indented blocks after except statements
- Fixed indentation issues in health check functions (memory_check, cpu_check, disk_space_check, api_health_check, database_check)
- Fixed indentation in fallback decorator to ensure proper return value handling
- Fixed indentation in type utility functions (from_timestamp, ensure_datetime, ensure_timedelta)
- Fixed _parse_timeframe function in mock_data.py to properly raise ValueError for unsupported timeframe units
- Fixed transaction handling in BaseRepository to properly rollback on exceptions
- Fixed date range filtering in repositories to handle timezone-aware datetime objects
- Fixed JSON parameter filtering in StrategyRepository to correctly identify strategies with specific parameters
- Fixed file naming conflicts in test files to prevent import errors during test collection

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