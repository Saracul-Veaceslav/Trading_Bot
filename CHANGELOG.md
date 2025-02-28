# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-02-28

### Added
- TradingView strategy adapter for popular strategies (RSI, MACD, Bollinger Bands)
- Improved command-line interface with more options
- Better error handling and logging
- Support for test mode (paper trading)
- Detailed README with usage examples
- Script for converting unittest tests to pytest format
- Made TA-Lib optional with fallback implementations for strategies
- Added instructions for making run_tests.sh executable
- Sample pytest test file for SMA crossover strategy
- Warning log for insufficient data points in SMA crossover strategy

### Fixed
- Method signatures in DataManager to match test expectations
- Parameter handling in SMAcrossover strategy for mock objects
- Path and directory structure issues
- Error handling in all components
- Logger integration across components
- TA-Lib dependency issues by providing fallback implementations
- Script permissions with clear instructions
- Warning log for insufficient data in SMA crossover strategy
- Pandas warnings in pytest tests by using .loc instead of chained assignment

### Changed
- Refactored BinanceTestnet class for better mock handling
- Updated StrategyExecutor to support error_logger parameter
- Improved main script with better signal handling
- Enhanced settings with correct path configuration
- Made TA-Lib an optional dependency with clear installation instructions

## [0.1.0] - 2023-07-10

### Added
- Initial project structure and architecture
- Binance Testnet integration using ccxt
- SMA Crossover strategy implementation
- Data storage for OHLCV data and trades
- Stop-Loss and Take-Profit risk management
- Comprehensive logging system
- Unit tests with Gherkin-style docstrings
- Command-line interface for bot configuration

## [Unreleased]

### Added
- Implementation of the `DataManager`, `BinanceTestnet`, `StrategyExecutor`, and `SMAcrossover` classes
- Proper project structure with symbolic links to resolve import issues
- Package initialization files (`__init__.py`) added to relevant directories
- Test runner scripts for better debugging of test failures
- Simple test script to check imports are working correctly

### Fixed
- Method names in classes were corrected to match expected names in tests
- Missing methods were added to the `BinanceTestnet` and `SMAcrossover` classes
- The `_load_strategy` method was added to the `StrategyExecutor` class
- The `settings.py` file was updated with required configuration values
- Matplotlib was made an optional dependency to avoid build issues
- Updated `DataManager` class to accept logger parameters as expected by tests
- Fixed the test runner to properly handle Python 3.13 compatibility issues
- Updated `BinanceTestnet` class to handle mock objects in tests
- Added handling for mock objects in `StrategyExecutor` class
- Enhanced `SMAcrossover` class with additional methods needed by tests 