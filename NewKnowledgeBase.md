# Abidance Trading Bot Knowledge Base

## Project Structure

The Abidance Trading Bot is organized into the following core components:

- **abidance**: Main package containing all trading bot functionality
  - **trading**: Core trading functionality, engine, and order management
  - **exchange**: Exchange adapters and API integration
  - **strategy**: Trading strategies and technical indicators
  - **config**: Configuration loading and management
  - **type_defs**: Type definitions and custom types
  - **typing**: Alternative type definitions (to be consolidated with type_defs)
  - **exceptions**: Custom exception hierarchy
  - **utils**: Utility functions and common helpers
  - **data**: Data management and storage
  - **risk**: Risk management and position sizing
  - **web**: Web interface components
  - **core**: Core domain models and fundamental types
  - **api**: API interfaces and implementations
  - **ml**: Machine learning models and utilities

## Module Structure

- **Consistent Exports**: Each module has a well-defined `__all__` list that explicitly declares its public API
- **Docstrings**: Every module has a comprehensive docstring explaining its purpose
- **Import Organization**: Imports are organized in a consistent pattern across modules
- **Explicit Imports**: Modules explicitly import and re-export components from submodules
- **No Circular Imports**: The module structure is designed to avoid circular imports
- **Categorized Exports**: Exports in `__all__` are often categorized with comments for better readability

## Dependency Injection

- **ServiceRegistry**: A simple dependency injection container for managing service instances
  - Supports registering services by type or name
  - Supports factory functions for creating service instances
  - Supports singleton and transient service lifetimes
  - Provides a clear API for registering and retrieving services
  - Facilitates loose coupling between components
  - Enables easier testing through service substitution
  - Centralizes service creation and configuration
- **Global Registry Instance**: A global instance of the ServiceRegistry is available
  - Accessible via `from abidance.core import registry`
  - Provides a centralized service registry for the entire application
  - Simplifies service access without passing the registry around
  - Follows the singleton pattern for global access
  - Enables components to register and retrieve services from anywhere in the application
  - Can be cleared for testing purposes to ensure test isolation

## Service Registry Implementation

The Service Registry is implemented in the `abidance.core.container` module and provides a simple dependency injection container for the application. Key aspects of the implementation include:

- **Type-Based Registration**: Services can be registered by their type (class or protocol) or by a string name
- **Factory Functions**: Support for lazy instantiation through factory functions
- **Singleton Management**: Automatic caching of singleton instances for efficient reuse
- **Transient Services**: Support for creating new instances on each request
- **Clear API**: Simple methods for registering, checking, and retrieving services
- **Type Safety**: Comprehensive type annotations for better IDE support and static analysis
- **Global Instance**: A global registry instance is available for application-wide service access
- **Testing Support**: The registry can be cleared for test isolation

Example usage:
```python
from abidance.core import registry, ServiceRegistry

# Register a service instance
registry.register(Logger, logger_instance)

# Register a service with a name
registry.register("config", config_instance)

# Register a factory function for lazy instantiation
registry.register_factory(Database, create_database, singleton=True)

# Check if a service is registered
if registry.has(Logger):
    # Get a service
    logger = registry.get(Logger)
    logger.info("Service retrieved from registry")

# Get a named service
config = registry.get("config")

# Clear the registry (useful for testing)
registry.clear()

# Create a local registry for specific components
local_registry = ServiceRegistry()
local_registry.register(Cache, cache_instance)
```

The Service Registry facilitates dependency injection throughout the application, making component dependencies explicit and easier to manage. This reduces tight coupling between components and improves testability by allowing dependencies to be easily substituted during testing.

## Application Bootstrap

- **ApplicationBootstrap**: A framework for bootstrapping the application
  - Provides a structured approach to application initialization
  - Manages component registration and creation
  - Handles configuration loading from YAML files
  - Integrates with the ServiceRegistry for dependency injection
  - Supports component factories for creating components with configuration
  - Provides a consistent initialization process for all components
  - Centralizes error handling during application startup
  - Facilitates testing by allowing component substitution

## Event System Architecture

The Abidance Trading Bot implements a comprehensive event system that enables loose coupling between components and facilitates communication across the application. The event system consists of two main parts:

1. **EventSystem (events.py)**: The core event system that handles event registration, emission, and propagation. It provides the following features:
   - Event registration with optional filtering
   - Event emission with metadata
   - Event propagation to parent event types
   - Error handling for event handlers

2. **EventHandlerRegistry (event_handlers.py)**: A higher-level abstraction that provides additional functionality for managing event handlers:
   - Centralized registry for event handlers
   - Event subscriptions for easy unsubscription
   - Event handler groups for managing related handlers
   - Decorator-based event handler registration

This two-tier approach allows for flexible event handling while maintaining a clean separation of concerns. The lower-level EventSystem provides the core functionality, while the higher-level EventHandlerRegistry provides convenience features for application code.

### Usage Examples

#### Basic Event Handling

```python
from abidance.core.events import EventSystem

# Create an event system
event_system = EventSystem()

# Register a handler
def handle_trade(event):
    print(f"Trade received: {event.data}")

event_system.register_handler("trade", handle_trade)

# Emit an event
event_system.emit("trade", {"symbol": "BTC/USD", "price": 50000})
```

#### Using the Event Handler Registry

```python
from abidance.core.events import EventSystem
from abidance.core.event_handlers import EventHandlerRegistry, event_handler

# Create an event system and registry
event_system = EventSystem()
registry = EventHandlerRegistry(event_system)

# Register a handler using the decorator
@event_handler("trade", registry)
def handle_trade(event):
    print(f"Trade received: {event.data}")

# Emit an event
event_system.emit("trade", {"symbol": "BTC/USD", "price": 50000})
```

#### Using Event Handler Groups

```python
from abidance.core.events import EventSystem
from abidance.core.event_handlers import EventHandlerRegistry, EventHandlerGroup

# Create an event system and registry
event_system = EventSystem()
registry = EventHandlerRegistry(event_system)

# Create a handler group
group = EventHandlerGroup(registry)

# Subscribe to events
group.subscribe("trade", lambda event: print(f"Trade: {event.data}"))
group.subscribe("order", lambda event: print(f"Order: {event.data}"))

# Later, unsubscribe from all events
group.unsubscribe_all()
```

## Validation Framework

The Abidance Trading Bot implements a comprehensive validation framework that provides a consistent way to validate data across the application. The validation framework consists of two main parts:

1. **Core Validation Framework (validation.py)**: The foundation of the validation system that defines the basic validation structures:
   - `ValidationError`: A dataclass representing a validation error with field, message, and code
   - `Validator`: An abstract base class that all validators must implement
   - `ValidationContext`: A class that manages multiple validators for different fields

2. **Common Validators (validators.py)**: A collection of common validators that can be used throughout the application:
   - `RequiredValidator`: Ensures a value is not None or empty
   - `TypeValidator`: Ensures a value is of a specific type
   - `RangeValidator`: Ensures a numeric value is within a specified range
   - `LengthValidator`: Ensures a value's length is within a specified range
   - `PatternValidator`: Ensures a string value matches a regular expression pattern
   - `EmailValidator`: Ensures a string value is a valid email address
   - `CustomValidator`: Uses a custom validation function for complex validation logic

This two-tier approach allows for flexible validation while maintaining a clean separation of concerns. The lower-level validation framework provides the core functionality, while the higher-level validators provide common validation logic.

### Usage Examples

#### Basic Validation

```python
from abidance.core.validation import ValidationError, Validator
from abidance.core.validators import RequiredValidator

# Create a validator
validator = RequiredValidator()

# Validate a value
errors = validator.validate(None)
if errors:
    for error in errors:
        print(f"Validation error: {error}")
```

#### Using the ValidationContext

```python
from abidance.core.validation import ValidationContext
from abidance.core.validators import RequiredValidator, TypeValidator, RangeValidator

# Create a validation context
context = ValidationContext()

# Add validators for different fields
context.add_validator("name", RequiredValidator())
context.add_validator("name", TypeValidator(str))
context.add_validator("age", TypeValidator(int))
context.add_validator("age", RangeValidator(min_value=18, max_value=120))

# Validate data
data = {"name": "John Doe", "age": 30}
if context.is_valid(data):
    print("Data is valid")
else:
    errors = context.validate(data)
    for error in errors:
        print(f"Field '{error.field}': {error.message} (code: {error.code})")
```

#### Creating a Custom Validator

```python
from abidance.core.validation import Validator, ValidationError
from typing import List, Any

class CustomPasswordValidator(Validator):
    def validate(self, value: Any) -> List[ValidationError]:
        errors = []
        if not isinstance(value, str):
            errors.append(ValidationError("password", "Password must be a string", "TYPE_ERROR"))
            return errors
            
        if len(value) < 8:
            errors.append(ValidationError("password", "Password must be at least 8 characters", "MIN_LENGTH"))
            
        if not any(c.isupper() for c in value):
            errors.append(ValidationError("password", "Password must contain at least one uppercase letter", "UPPERCASE_REQUIRED"))
            
        if not any(c.isdigit() for c in value):
            errors.append(ValidationError("password", "Password must contain at least one digit", "DIGIT_REQUIRED"))
            
        return errors
```

## Metrics Collection System

The Abidance Trading Bot implements a comprehensive metrics collection system that enables tracking and analyzing various aspects of the application's performance and behavior. The metrics system consists of two main parts:

1. **Core Metrics Framework (metrics.py)**: The foundation of the metrics system that defines the basic metrics structures:
   - `MetricsCollector`: A base class for collecting and retrieving metrics with timestamps
   - `AggregationType`: An enumeration of supported aggregation types (SUM, AVG, MIN, MAX, COUNT, LAST, FIRST)

2. **Specialized Metrics Collectors (collectors.py)**: A collection of specialized collectors for different types of metrics:
   - `PerformanceMetricsCollector`: Tracks execution time, memory usage, and CPU usage
   - `TradingMetricsCollector`: Tracks trading activities, orders, trades, portfolio values, and positions
   - `SystemMetricsCollector`: Tracks system-level metrics like CPU, memory, disk, and network usage

This two-tier approach allows for flexible metrics collection while maintaining a clean separation of concerns. The lower-level metrics framework provides the core functionality, while the higher-level collectors provide specialized metrics collection logic.

### Key Features

- **Time-Based Metrics**: All metrics are recorded with timestamps, allowing for time-based filtering and analysis
- **Thread Safety**: The metrics collection system is thread-safe, allowing for concurrent access from multiple threads
- **Aggregation**: Metrics can be aggregated using various aggregation types (sum, average, min, max, count, etc.)
- **Filtering**: Metrics can be filtered by time range (since, until) for targeted analysis
- **Performance Timing**: The `PerformanceMetricsCollector` provides a decorator for timing function execution
- **Trading Metrics**: The `TradingMetricsCollector` provides methods for tracking orders, trades, and portfolio values
- **System Monitoring**: The `SystemMetricsCollector` provides methods for tracking system resource usage

### Usage Examples

#### Basic Metrics Collection

```python
from abidance.core.metrics import MetricsCollector

# Create a metrics collector
collector = MetricsCollector()

# Record a metric
collector.record("api_requests", 1)

# Record a metric with a specific timestamp
from datetime import datetime
collector.record_with_timestamp("api_latency", 150, datetime.now())

# Get metrics
metrics = collector.get_metric("api_requests")
print(f"API requests: {metrics}")

# Get the latest metric value
latest = collector.get_latest("api_latency")
print(f"Latest API latency: {latest} ms")
```

#### Using Aggregation

```python
from abidance.core.metrics import MetricsCollector, AggregationType

# Create a metrics collector
collector = MetricsCollector()

# Record multiple metrics
collector.record("response_time", 100)
collector.record("response_time", 150)
collector.record("response_time", 120)

# Aggregate metrics
avg_response_time = collector.aggregate("response_time", AggregationType.AVG)
max_response_time = collector.aggregate("response_time", AggregationType.MAX)
min_response_time = collector.aggregate("response_time", AggregationType.MIN)

print(f"Average response time: {avg_response_time} ms")
print(f"Maximum response time: {max_response_time} ms")
print(f"Minimum response time: {min_response_time} ms")
```

#### Performance Timing

```python
from abidance.core.collectors import PerformanceMetricsCollector

# Create a performance metrics collector
collector = PerformanceMetricsCollector()

# Use the timer manually
collector.start_timer("database_query")
# ... perform database query ...
elapsed = collector.stop_timer("database_query")
print(f"Database query took {elapsed:.2f} seconds")

# Use the decorator for timing functions
@collector.time_function()
def process_data(data):
    # ... process data ...
    return result

# Call the function - timing will be recorded automatically
result = process_data(data)

# Get the timing metrics
timing_metrics = collector.get_metric("timer.process_data")
print(f"Process data timing: {timing_metrics}")
```

#### Trading Metrics

```python
from abidance.core.collectors import TradingMetricsCollector

# Create a trading metrics collector
collector = TradingMetricsCollector()

# Record an order
collector.record_order(
    order_id="123",
    symbol="BTC/USD",
    side="buy",
    order_type="market",
    quantity=1.0,
    price=50000.0
)

# Record a trade
collector.record_trade(
    trade_id="456",
    symbol="BTC/USD",
    side="buy",
    quantity=1.0,
    price=50000.0,
    fee=25.0
)

# Record portfolio value
collector.record_portfolio_value(100000.0)

# Record a position
collector.record_position(
    symbol="BTC/USD",
    quantity=1.0,
    entry_price=50000.0,
    current_price=52000.0
)

# Get a trading summary
summary = collector.get_trading_summary("BTC/USD")
print(f"Trading summary: {summary}")
```

#### System Metrics

```python
from abidance.core.collectors import SystemMetricsCollector

# Create a system metrics collector
collector = SystemMetricsCollector()

# Start collecting system metrics in the background
collector.start_collection(interval=5.0)  # Collect every 5 seconds

# ... application runs ...

# Stop collection
collector.stop_collection()

# Get CPU metrics
cpu_metrics = collector.get_metric("system.cpu.percent")
print(f"CPU usage: {cpu_metrics}")

# Get memory metrics
memory_metrics = collector.get_metric("system.memory.percent")
print(f"Memory usage: {memory_metrics}")
```

## Environment Management

- **Environment**: A class for managing environment variables
  - Provides methods for loading environment variables from .env files
  - Supports type conversion for boolean, integer, float, list, dictionary, and path values
  - Handles required environment variables with clear error messages
  - Supports default values for missing environment variables
  - Provides a consistent API for accessing environment variables
  - Centralizes environment variable access and validation
  - Facilitates testing by allowing environment variable mocking
  - Supports filtering environment variables by prefix
  - Uses Path.exists() instead of os.path.exists() for better testability
  - Raises ConfigurationError with descriptive messages when environment files don't exist
  - Implements comprehensive type conversion with error handling
  - Provides get_all() method to retrieve all environment variables with a specific prefix
  - Integrates with the Configuration class for a complete configuration management system
  - Supports both .env file loading and direct environment variable access
  - Includes comprehensive test coverage with mocking of environment variables and file operations
  - Follows a consistent error handling pattern across all methods
  - Provides clear documentation for all methods and parameters
  - Implements a clean separation between loading and accessing environment variables

## Domain Model

- **Core Entities**: The system is built around well-defined domain entities:
  - **OrderSide**: Enum for buy/sell order sides
  - **OrderType**: Enum for market/limit/stop-loss/take-profit order types
  - **SignalType**: Enum for buy/sell/hold trading signals
  - **Position**: Represents an open trading position
  - **Order**: Represents a trading order
  - **Signal**: Represents a trading signal
  - **Candle**: Represents price movement over a time period
  - **Trade**: Represents a completed trade

## Type System

- **Type Aliases**: Common types are defined as aliases for better code readability:
  - **Timestamp**: Union of int and float for Unix timestamps
  - **Price**: Union of float and Decimal for price values
  - **Volume**: Union of float and Decimal for volume values
  - **Symbol**: String type for trading pair symbols
  - **TimeseriesData**: Pandas DataFrame for time series data
  - **Parameters**: Dictionary for generic parameters
  - **Config**: Dictionary for configuration values

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
- **Module Structure Tests**: Tests to verify consistent module structure and exports

## Configuration Management

- **YAML Based**: Configuration is stored in YAML files
- **Validation**: Config validation ensures required fields are present
- **Environment Variables**: Support for environment variable interpolation
- **Defaults**: Sensible defaults are provided for most configuration options
- **Strategy-Specific Config**: Each strategy has its own configuration class
- **Environment Management**: Dedicated Environment class for handling environment variables with type conversion

## Configuration and Environment Integration

- **Layered Configuration**: The system supports a layered configuration approach
  - Base configuration from YAML files
  - Environment variable overrides with the `ABIDANCE_` prefix
  - Command-line argument overrides (planned)
  - Runtime configuration changes
- **Backward Compatibility**: The Configuration class maintains backward compatibility with existing code
  - Supports both direct environment variable names and prefixed names
  - Maps common configuration keys to their environment variable equivalents
  - Preserves existing behavior while enabling new features
- **Type Conversion**: Both Configuration and Environment classes handle type conversion
  - Environment class provides specialized methods for different types
  - Configuration class handles nested dictionaries and complex structures
  - Both use consistent error handling patterns
- **Validation**: Configuration validation ensures required fields are present
  - Required keys are checked before the application starts
  - Type validation ensures values are of the expected type
  - Range validation ensures values are within acceptable bounds
- **Testing**: Comprehensive test coverage for both classes
  - Mocking of environment variables and file operations
  - Tests for edge cases and error conditions
  - Tests for type conversion and validation
  - Tests for backward compatibility

## Trading Strategies

- **Base Strategy**: All strategies inherit from a common `Strategy` base class
- **StrategyConfig**: Strategy parameters are defined in dataclass-based configurations
- **SMA Crossover**: Strategy based on moving average crossovers
- **RSI Strategy**: Strategy using the Relative Strength Index indicator
- **Technical Indicators**: Common indicators like SMA, RSI, MACD are implemented in a utility module
- **Signal Generation**: Standardized approach to generating trading signals
- **Order Creation**: Consistent pattern for converting signals to orders
- **Strategy Protocol**: Protocol defining the interface that all strategies must implement
- **StrategyFactory Protocol**: Protocol for creating strategy instances with consistent configuration

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
- **Exchange Protocol**: Protocol defining the interface that all exchange implementations must satisfy
- **ExchangeFactory Protocol**: Protocol for creating exchange instances with consistent configuration

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

8. **Resolving Import Conflicts and Module Shadowing**
   - **Module Shadowing Issues**:
     - Identified and resolved cases where module names shadowed Python standard library or third-party modules
     - Renamed modules to avoid conflicts with built-in modules
     - Used absolute imports to ensure correct module resolution
     - Implemented consistent import patterns across the codebase
   - **Duplicate Class Names**:
     - Identified and resolved cases where the same class name was used in multiple modules
     - Renamed classes to be more specific and avoid conflicts
     - Added tests to detect duplicate class names across modules
     - Implemented a test that verifies no module shadowing occurs
   - **Import Conflict Resolution**:
     - Created a test suite specifically for detecting import conflicts
     - Implemented tests for detecting module shadowing, duplicate class names, and wildcard imports
     - Added checks for direct internal imports that could cause circular dependencies
     - Established a consistent import pattern across the codebase
   - **Package Structure Improvements**:
     - Reorganized the package structure to avoid naming conflicts
     - Implemented tests to verify the package structure is correct
     - Added checks for duplicate modules in the package
     - Ensured all modules have proper `__init__.py` files with explicit exports

9. **Adapter Pattern for Module Compatibility**
   - **Problem**: Duplicate class names (`Order`, `Position`, `Trade`, `OrderSide`, `OrderType`) across `abidance.trading` and `abidance.core` modules
   - **Solution**: Implemented the adapter pattern to maintain backward compatibility while resolving duplicate class names
   - **Implementation**:
     - Kept detailed implementations in the `trading` module
     - Created adapter classes in the `core` module that delegate to the `trading` module implementations
     - Updated the `core/__init__.py` to import and re-export the adapter classes
     - Modified the import conflict test to allow specific duplicates for adapter classes
   - **Benefits**:
     - Preserved backward compatibility with existing code that imports from `abidance.core`
     - Eliminated duplicate implementations that could lead to inconsistencies
     - Established a clear ownership of domain models in the `trading` module
     - Maintained the existing test suite without requiring extensive rewrites

10. **Configuration Class Improvements**
    - **Problem**: The `Configuration` class had inconsistencies between implementation and tests, particularly with environment variable handling
    - **Solution**: Refactored the `Configuration` class to align with test expectations and improve functionality
    - **Implementation**:
      - Renamed internal `_config` attribute to `data` for better clarity and consistency with tests
      - Enhanced `load_from_env` method to properly handle environment variables with the `ABIDANCE_` prefix
      - Added JSON parsing for environment variables that contain list or dictionary values
      - Implemented type conversion for boolean, integer, and float values
      - Added backward compatibility for specific hardcoded environment variable mappings
      - Renamed `validate_required` to `validate_required_keys` while maintaining backward compatibility
    - **Benefits**:
      - Improved consistency between implementation and tests
      - Enhanced environment variable handling with proper type conversion
      - Maintained backward compatibility with existing code
      - Simplified configuration management with clearer attribute naming
      - Improved error handling for configuration validation

11. **Import Conflict Resolution**
    - **Problem**: Duplicate class names and module paths between different parts of the codebase
    - **Solution**: Centralized exception definitions and restructured imports to avoid conflicts
    - **Implementation**:
      - Moved `ConfigurationError` definition to the `