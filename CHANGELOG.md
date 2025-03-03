# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added
- Core domain model extraction
- Type definitions module
- Web monitoring capabilities
- Risk management module
- Machine learning integration
- Comprehensive exception hierarchy
- Event-driven architecture
- Dependency injection container
- Global service registry instance
- Application bootstrap framework
- Strategy factory pattern
- Exchange adapter pattern
- Technical indicator utilities
- Data management utilities
- Configuration validation
- Circuit breaker pattern
- Retry mechanism with exponential backoff
- Error boundary context manager
- Error context enrichment
- Plugin architecture
- Comprehensive test suite
- Documentation for all modules
- Environment class for environment variable management
- Enhanced .env.example file with comprehensive configuration options
- Event handler registry for centralized event handler management
- Event subscription and handler grouping capabilities
- Event handler decorator for simplified event registration
- Validation framework with common validators (Required, Type, Range, Length, Pattern, Email, Custom)
- Metrics collection system with specialized collectors (Performance, Trading, System)
- Time-based metric filtering and aggregation capabilities
- Thread-safe metrics recording and retrieval
- Function execution timing decorator
- Metrics Collection System with specialized collectors for performance, trading, and system metrics
- Fixed infinite loop issue in SystemMetricsCollector by adding single_run parameter
- Fixed TradingMetricsCollector.get_trading_summary method to correctly handle both specific symbol and all symbols cases
- Fixed fee calculation in trading summary to correctly sum all fees
- Enabled data recording functionality to store market data, trades, and strategy states
- Implemented file-based storage for OHLCV data, trades, and strategy states
- Advanced logging framework with structured JSON logging
- Custom log formatters with color support
- Asynchronous log handlers for improved performance
- Context-aware logging with request ID tracking
- Documentation about expected PytestCollectionWarnings related to @runtime_checkable Protocol classes
- Performance monitoring module with thread-safe metrics collection
- Specialized metric collectors for exchange and strategy operations
- Context manager for timing operations
- Function decorator for timing function execution
- Distributed tracing system for tracking operations across components
- Span-based tracing with parent-child relationship support
- Trace context management with timing information
- Metadata enrichment for trace spans
- Health checking system for monitoring system components and services
- Health status reporting with healthy, degraded, and unhealthy states
- Common health checks for memory, CPU, disk space, API endpoints, and database connectivity
- Async health check execution with error handling

### Changed
- Refactored codebase to follow Clean Architecture principles
- Improved error handling with contextual information
- Enhanced logging with structured data
- Standardized module structure and exports
- Simplified configuration management
- Improved type annotations
- Improved naming conventions
- Enhanced test coverage
- Improved documentation
- Optimized performance-critical code paths
- Improved error messages
- Updated main application to use DataManager with file storage for data persistence
- Updated pandas operations in strategy code to prevent downcasting warnings

### Fixed
- Module shadowing issues
- Parameter naming inconsistencies
- Concurrency issues
- Performance bottlenecks
- Deprecated warnings
- Import conflicts
- Duplicate class names
- Environment variable loading issues
- Type conversion issues
- Backward compatibility issues
- Inconsistencies in error handling
- Inconsistencies in logging
- Inconsistencies in type annotations
- Inconsistencies in documentation
- Fixed strategy initialization in abidance_main.py to properly create strategy config objects
- Fixed test_no_module_shadowing to exclude 'logging' from shadowing checks due to intentional abidance.logging module
- Fixed pandas FutureWarning related to silent downcasting in strategy code

## 0.2.0

### Added
- Backtesting module
- Performance metrics
- Strategy optimization
- Portfolio management
- Multi-timeframe analysis
- Advanced technical indicators
- Market sentiment analysis
- Risk management rules
- Position sizing algorithms
- Reporting and visualization
- Telegram notifications
- Email alerts
- Web dashboard
- REST API
- WebSocket support
- Database integration
- Logging enhancements
- Configuration management
- Documentation

### Changed
- Improved strategy framework
- Enhanced exchange integration
- Optimized data handling
- Refactored core components
- Updated dependencies

### Fixed
- Memory leaks in data processing
- Race conditions in order execution
- Error handling in API calls
- Configuration loading issues
- Timezone handling bugs
- Performance issues in backtesting
- Strategy signal calculation errors

## 0.1.0

### Added
- Initial release
- Basic trading functionality
- Support for Binance exchange
- SMA crossover strategy
- RSI strategy
- Data collection and storage
- Simple backtesting
- Configuration system
- Logging system
- Command-line interface 