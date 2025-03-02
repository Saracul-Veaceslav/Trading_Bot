# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Core domain model extraction with clear entity definitions (OrderSide, OrderType, SignalType, Position, Order, Signal, Candle, Trade)
- Type definitions module with common type aliases and custom types
- Web monitoring capabilities with Streamlit dashboard
- User guides and documentation
- Risk management module
- Machine learning integration for strategy enhancement
- Backtesting framework
- REST API support
- WebSocket support
- Notification system
- Multi-exchange support
- Portfolio management capabilities

### Changed
- Refactored codebase to follow Clean Architecture principles
- Improved error handling with context-aware exceptions
- Enhanced logging system
- Optimized data processing
- Modularized strategy implementation
- Standardized configuration management
- Improved type annotations
- Reorganized package structure

### Fixed
- Module shadowing in imports
- Improved error handling in SMA strategy
- Fixed parameter naming in RSI strategy (changed 'type' to 'order_type')
- Removed unnecessary 'params' parameter in RSI strategy
- Fixed threshold crossover detection
- Enhanced test coverage
- Resolved concurrency issues
- Fixed configuration validation
- Improved error messages
- Addressed performance bottlenecks
- Fixed memory leaks
- Updated datetime.utcnow() usage to datetime.now(timezone.utc) to address deprecation warnings
- Updated pandas fillna operations to use infer_objects(copy=False) to address deprecation warnings

## [0.2.0] - 2023-06-15

### Added
- Multiple strategy support
- Position sizing module
- Risk management rules
- Improved backtesting capabilities
- Data visualization tools
- Performance metrics
- Strategy optimization tools

### Changed
- Enhanced error handling
- Improved logging
- Optimized data processing
- Better configuration management

### Fixed
- Fixed bugs in order execution
- Improved error recovery
- Enhanced exception handling
- Fixed data synchronization issues

## [0.1.0] - 2023-03-01

### Added
- Initial release
- Basic trading bot framework
- Simple Moving Average (SMA) strategy
- Relative Strength Index (RSI) strategy
- Binance exchange integration
- Data management system
- Configuration system
- Logging system 