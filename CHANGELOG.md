# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Created a new modular structure for the Trading Bot
- Implemented core bot infrastructure with command-line interface
- Added configuration management with support for different data sources
- Developed exchange abstraction layer with Binance integration
- Created data management system for historical and real-time data
- Implemented risk management module with position sizing and stop loss functionality
- Added strategy registry for dynamic loading of trading strategies
- Set up framework for machine learning integration
- Created utility functions for backtesting and optimization
- Added pytest-based test framework for SMA Crossover strategy and configuration module
- Implemented comprehensive backtesting functionality in the SMA Crossover strategy

### Changed
- Refactored project to follow clean architecture principles
- Reorganized codebase into domain-specific modules
- Enhanced logging system for better debugging and monitoring
- Updated dependency management
- Implemented enhanced error handling throughout the application
- Migrated from unittest to pytest for better test organization and fixtures
- Fixed import issues in tests to work with the new project structure

### Fixed
- Fixed issues with data handling and pandas warnings
- Added graceful handling of missing dependencies
- Improved error communication during initialization
- Fixed compatibility issues between tests and implementation (signal return types, column names)
- Resolved abstract method implementation issues in strategy classes

## [0.1.0] - 2023-09-15

### Added
- Initial release of the Trading Bot
- Basic SMA crossover strategy implementation
- Connectivity to Binance exchange
- Simple backtesting capabilities
- Basic command-line interface
- Unit tests with pytest 