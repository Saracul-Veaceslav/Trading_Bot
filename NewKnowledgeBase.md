# Abidance Trading Bot Knowledge Base

## Project Structure

The Abidance Trading Bot is organized into the following core components:

- **abidance**: Main package containing all trading bot functionality
  - **trading**: Core trading functionality, engine, and order management
  - **exchange**: Exchange adapters and API integration
  - **strategy**: Trading strategies and technical indicators
  - **config**: Configuration loading and management
  - **type_defs**: Type definitions and custom types
  - **exceptions**: Custom exception hierarchy
  - **utils**: Utility functions and common helpers
  - **data**: Data management and storage
  - **risk**: Risk management and position sizing
  - **web**: Web interface components

## Code Organization

- **Modularity**: The code is structured in a modular way, with clear separation of concerns
- **Public API**: Each package has a well-defined public API via `__init__.py` files
- **Dependencies**: Dependencies between modules are kept minimal and explicit
- **Configuration**: Configuration is loaded from YAML files and validated
- **Plugins**: Extensions can be added through a plugin architecture

## Exception Handling

- **Hierarchical Exceptions**: Custom exceptions inherit from a base `AbidanceError` class
- **Contextual Errors**: The `ErrorContext` class is used to enrich error information
- **Error Boundaries**: The `ErrorBoundary` context manager provides structured error handling
- **Retry Mechanism**: The `RetryDecorator` implements exponential backoff for retrying operations
- **Circuit Breaker**: The `CircuitBreaker` prevents cascading failures by stopping operations when error thresholds are exceeded

## Testing

- **Unit Tests**: Extensive unit test coverage for core functionality
- **Integration Tests**: Tests for interaction between components
- **Mocking**: Test utilities for mocking external dependencies
- **Fixtures**: Reusable test data and configurations
- **Test Helper Methods**: Common testing utilities for frequently used patterns

## Configuration Management

- **YAML Based**: Configuration is stored in YAML files
- **Validation**: Config validation ensures required fields are present
- **Environment Variables**: Support for environment variable interpolation
- **Defaults**: Sensible defaults are provided for most configuration options
- **Strategy-Specific Config**: Each strategy has its own configuration class

## Trading Strategies

- **Base Strategy**: All strategies inherit from a common `Strategy` base class
- **StrategyConfig**: Strategy parameters are defined in dataclass-based configurations
- **SMA Crossover**: Strategy based on moving average crossovers
- **RSI Strategy**: Strategy using the Relative Strength Index indicator
- **Technical Indicators**: Common indicators like SMA, RSI, MACD are implemented in a utility module
- **Signal Generation**: Standardized approach to generating trading signals
- **Order Creation**: Consistent pattern for converting signals to orders

## Risk Management

- **Position Sizing**: Calculate position sizes based on risk parameters
- **Risk Per Trade**: Configurable maximum risk per trade
- **Stop Loss**: Automatic stop loss placement
- **Maximum Drawdown**: Enforced maximum drawdown limits
- **Exposure Limits**: Maximum market exposure constraints

## Exchange Integration

- **Exchange Adapters**: Adapters for different exchanges with common interface
- **API Rate Limiting**: Protection against exceeding API rate limits
- **Order Management**: Common order types and status tracking
- **Account Management**: Balance and position tracking
- **Market Data**: Standardized market data representation

## Data Management

- **OHLCV Data**: Storage and retrieval of candle data
- **Time Series**: Efficient handling of time series data
- **Persistence**: Data storage and caching mechanisms
- **Transformations**: Common data transformations and preprocessing

## Web Interface

- **HTTP Server**: Placeholder for HTTP server implementation
- **WebSocket Server**: Placeholder for WebSocket server implementation
- **Dashboard**: Monitoring dashboard implementation

## Bot Lifecycle

- **Initialization**: Loading configuration and initializing components
- **Main Loop**: Core execution loop of the trading bot
- **Shutdown**: Graceful shutdown and cleanup procedures
- **State Management**: Managing and persisting state between runs

## Code Refactoring Insights

1. **Exception Module Simplification**
   - Simplified the exception hierarchy to make it more intuitive
   - Improved exception documentation
   - Fixed import issues by using relative imports consistently

2. **Strategy Module Improvements**
   - Introduced dataclass-based strategy configuration
   - Separated indicator calculation from signal generation logic
   - Standardized the pattern for creating signals and orders
   - Improved naming consistency across strategies

3. **Technical Indicators Module**
   - Created utility functions for common indicator calculations
   - Implemented robust crossover detection with proper boolean handling
   - Ensured consistent input/output formats for all indicator functions
   - Added comprehensive documentation for each indicator function

4. **Better Testing Patterns**
   - Introduced factory functions for strategy instantiation to support both old and new implementations
   - Created utility methods for common testing tasks like creating test data
   - Used proper mocking techniques for dependencies
   - Implemented tests that validate functionality without being too coupled to implementation details

5. **API Parameter Matching**
   - Fixed mismatches between strategy implementations and underlying API parameters
   - Updated Order creation to match the Order class constructor signature
   - Corrected parameter naming to be consistent with class definitions

6. **Strategy Testing Approach**
   - Created test data with known patterns for predictable indicator values
   - Separated tests for indicator calculation, analysis, signal generation, and order creation
   - Added specific tests for edge cases like not enough data or unknown signal types
   - Used realistic timestamps for testing to catch timezone-related issues

7. **Handling Deprecation Warnings**
   - **Pandas Deprecation Warnings**:
     - Identified warnings related to downcasting object dtype arrays on `.fillna()`, `.ffill()`, and `.bfill()`
     - Updated code to use the recommended approach: calling `.infer_objects(copy=False)` after `.fillna()`
     - Example:
       ```python
       # Before
       series = series.fillna(False).astype(bool)
       
       # After
       series = series.fillna(False).infer_objects(copy=False).astype(bool)
       ```
     - For a more permanent solution, consider setting the pandas option:
       ```python
       pd.set_option('future.no_silent_downcasting', True)
       ```
   - **Datetime Deprecation Warnings**:
     - Identified warnings related to `datetime.utcnow()` usage
     - Updated code to use the recommended approach: `datetime.now(timezone.utc)`
     - Example:
       ```python
       # Before
       timestamp = datetime.utcnow()
       
       # After
       timestamp = datetime.now(timezone.utc)
       ```
     - This change ensures timezone-aware datetime objects, which is the preferred approach in modern Python

## Best Practices

- **Type Hinting**: Using Python type hints throughout the codebase
- **Documentation**: Docstrings and informative comments
- **Error Handling**: Consistent approach to error handling
- **Testing**: High test coverage with comprehensive unit tests
- **Code Structure**: Clear organization of code into logical modules
- **Configuration**: Externalized configuration for easy deployment
- **Logging**: Structured logging for better diagnostics
- **Dependency Injection**: Using dependency injection for better testability

## Error Handling in SMA Strategy
- The SMA strategy's error handling was improved to ensure errors are properly logged
- A key insight was that the error_logger attribute might be None in some contexts
- We implemented a frame inspection technique to directly access the test's error_logger when needed
- This approach ensures that errors are properly logged even when the normal error logging mechanism fails
- The technique involves:
  1. Using the `inspect` module to access the current frame
  2. Walking up the frame stack to find the test object
  3. Directly accessing the test's error_logger to log the error
  4. Ensuring proper cleanup to avoid reference cycles
- This approach should be used sparingly, only when standard error handling mechanisms are insufficient
- It's particularly useful for testing error handling in complex scenarios