# Abidance Trading Bot Knowledge Base

## Project Structure

The Abidance Trading Bot is organized into the following core components:

- **abidance**: Main package containing all trading bot functionality
  - **trading**: Core trading functionality, engine, and order management
  - **exchange**: Exchange adapters and API integration
  - **strategy**: Trading strategies and technical indicators
    - **indicators**: Object-oriented technical indicators with a consistent interface
      - **base.py**: Base Indicator abstract class defining the common interface
      - **momentum.py**: Momentum indicators like RSI and MACD
    - **composition.py**: Strategy composition framework for combining multiple strategies
      - **CompositeStrategy**: Base class for composite strategies with weighted signal combination
      - **VotingStrategy**: Strategy that uses majority voting to combine signals
  - **optimization**: Strategy parameter optimization and performance metrics
    - **optimizer.py**: StrategyOptimizer class for parameter grid search
    - **metrics.py**: Performance metric calculations (Sharpe, Sortino, etc.)
  - **evaluation**: Strategy performance evaluation and reporting
    - **metrics.py**: PerformanceMetrics dataclass and StrategyEvaluator for calculating performance metrics
    - **reporting.py**: PerformanceReport class for generating and saving performance reports with visualizations
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
  - **monitoring**: Performance monitoring and metrics collection
  - **logging**: Advanced logging framework with structured logging
  - **tracing**: Distributed tracing system for tracking operations
  - **health**: Health checking system for monitoring system components
  - **database**: Database access and management
    - **repository**: Repository pattern implementation for data access
      - **base_repository.py**: Base repository with common CRUD operations and transaction support
      - **trade_repository.py**: Trade-specific repository with specialized queries
      - **strategy_repository.py**: Strategy-specific repository with specialized queries
  - **testing**: Testing infrastructure and utilities
    - **data_management.py**: HistoricalDataManager for storing and retrieving OHLCV data
    - **data_loaders.py**: Data loaders for fetching data from exchanges and loading from CSV files
    - **mock_exchange.py**: Mock exchange implementation for deterministic testing
    - **mock_data.py**: Utilities for generating synthetic market data
    - **pylon_storage.py**: Storage utilities for testing
    - **binance_data_fetcher.py**: Binance data fetching utilities for testing
    - **properties.py**: Property-based testing utilities for strategies
    - **generators.py**: Data generators for property-based testing

## Module Structure

- **Consistent Exports**: Each module has a well-defined `__all__` list that explicitly declares its public API
- **Docstrings**: Every module has a comprehensive docstring explaining its purpose
- **Import Organization**: Imports are organized in a consistent pattern across modules
- **Explicit Imports**: Modules explicitly import and re-export components from submodules
- **No Circular Imports**: The module structure is designed to avoid circular imports
- **Categorized Exports**: Exports in `__all__` are often categorized with comments for better readability

## Repository Pattern Implementation

The Abidance Trading Bot implements the Repository Pattern to provide a clean abstraction layer between the domain model and the data access layer. This pattern offers several benefits:

1. **Separation of Concerns**: Isolates data access logic from business logic
2. **Testability**: Makes it easier to mock data access for unit testing
3. **Maintainability**: Centralizes data access code, reducing duplication
4. **Flexibility**: Allows changing the underlying data storage without affecting business logic

The repository implementation consists of:

### BaseRepository

The `BaseRepository` class provides common CRUD operations for all entity types:

- **add**: Adds a new entity to the database
- **get_by_id**: Retrieves an entity by its ID
- **list**: Lists all entities of a specific type
- **delete**: Deletes an entity from the database
- **transaction**: Context manager for transaction handling

Example usage:
```python
with repository.transaction() as session:
    repository.add(entity, session=session)
    # If an exception occurs, the transaction will be rolled back
```

### TradeRepository

The `TradeRepository` extends the `BaseRepository` with trade-specific queries:

- **get_trades_by_symbol**: Retrieves trades for a specific symbol
- **get_trades_by_date_range**: Retrieves trades within a date range
- **get_trades_by_strategy**: Retrieves trades for a specific strategy
- **get_latest_trade_by_symbol**: Retrieves the most recent trade for a symbol

### StrategyRepository

The `StrategyRepository` extends the `BaseRepository` with strategy-specific queries:

- **get_by_name**: Retrieves a strategy by its name
- **get_strategies_by_date_range**: Retrieves strategies within a date range
- **get_strategies_with_trades**: Retrieves strategies with their associated trades
- **get_strategies_by_parameter**: Retrieves strategies with a specific parameter value

### Transaction Handling

The repository implementation includes robust transaction handling:

- Transactions are managed using a context manager
- Automatic rollback on exceptions
- Session management is handled internally
- Support for explicit session passing for multi-repository operations

Example of transaction rollback:
```python
try:
    with repository.transaction() as session:
        repository.add(entity1, session=session)
        # If this raises an exception, the transaction will be rolled back
        repository.add(entity2, session=session)
except Exception:
    # The database state remains unchanged
    pass
```

### Date Range Filtering

The repositories provide date range filtering capabilities:

- Support for both naive and timezone-aware datetime objects
- Consistent handling of date ranges across repositories
- Efficient querying using database indexes

## Avoiding Cyclic Imports

Cyclic imports occur when two or more modules import each other, directly or indirectly, creating a dependency cycle. These can cause various issues including:

- Import errors
- Unexpected behavior
- Incomplete module initialization
- Reduced code maintainability

The Abidance Trading Bot uses several strategies to avoid cyclic imports:

1. **Proper Module Hierarchy**: Organizing modules in a hierarchical structure where higher-level modules import from lower-level modules, not vice versa.

2. **Import Organization**: Following a consistent import pattern:
   - Standard library imports first
   - Third-party library imports second
   - Local application imports last
   - Imports within each group are alphabetized

3. **Strategic Import Placement**: Moving imports inside functions or methods when they're only needed there, rather than at the module level.

4. **Forward References**: Using string literals for type hints when referring to types that would cause circular imports.

5. **Interface Segregation**: Breaking large interfaces into smaller, more focused ones to reduce dependencies.

6. **Dependency Inversion**: Using abstract base classes or protocols to define interfaces that both modules can depend on, rather than having them depend directly on each other.

7. **Refactoring Modules**: When cyclic dependencies are detected, refactoring the code to move shared functionality to a common module that both can import.

Example of fixing a cyclic import in the strategy indicators module:

```python
# Before (problematic):
# In __init__.py
from .base import Indicator
from .momentum import RSI, MACD

# In momentum.py
from .base import Indicator

# Solution:
# In __init__.py
# Standard library imports
import sys
from typing import Tuple, Dict, Any

# Third-party imports
import pandas as pd
import numpy as np

# Local imports
from .base import Indicator
from .momentum import RSI, MACD
```

This approach ensures that imports are organized properly and prevents cyclic dependencies by establishing a clear hierarchy of imports.

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

## Strategy Implementation Pattern

The Abidance Trading Bot uses a specific pattern for strategy implementation:

1. Each strategy has a corresponding configuration class (e.g., `SMAConfig` for `SMAStrategy`)
2. The strategy constructor expects a configuration object of the appropriate type
3. The configuration object contains all parameters needed by the strategy, including:
   - `

## Strategy Evaluation Framework

The Abidance Trading Bot includes a comprehensive strategy evaluation framework that helps assess the performance of trading strategies and generate detailed reports:

### Key Components

- **PerformanceMetrics**: A dataclass that serves as a container for strategy performance metrics:
  - `total_return`: The total return of the strategy
  - `sharpe_ratio`: Risk-adjusted return measure
  - `max_drawdown`: Maximum peak-to-trough decline
  - `win_rate`: Percentage of profitable trades
  - `profit_factor`: Ratio of gross profits to gross losses
  - `avg_trade`: Average profit/loss per trade
  - `num_trades`: Total number of trades

- **StrategyEvaluator**: The main class responsible for calculating performance metrics:
  - Calculates various performance metrics from trade history
  - Handles edge cases like empty trade history or all winning/losing trades
  - Provides methods for calculating Sharpe ratio and maximum drawdown

- **PerformanceReport**: Generates and saves performance reports:
  - Creates JSON reports with performance metrics and equity curve data
  - Plots equity curves with drawdown visualization
  - Handles serialization of complex objects for storage

### Usage Example

```python
from abidance.evaluation import StrategyEvaluator, PerformanceReport
import pandas as pd

# Create a DataFrame of trades
trades = pd.DataFrame({
    'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
    'profit_pct': [0.02, -0.01, 0.03]
})

# Calculate performance metrics
evaluator = StrategyEvaluator()
metrics = evaluator.calculate_metrics(trades)

print(f"Total Return: {metrics.total_return:.2%}")
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
print(f"Max Drawdown: {metrics.max_drawdown:.2%}")
print(f"Win Rate: {metrics.win_rate:.2%}")

# Generate and save a performance report
report_generator = PerformanceReport(output_dir="reports/")
report_data = report_generator.generate_report(
    trades=trades,
    strategy_name="My Strategy",
    parameters={"param1": 10, "param2": 20}
)

# Save the report
report_path = report_generator.save_report(report_data)
print(f"Report saved to: {report_path}")

# Plot equity curve
report_generator.plot_equity_curve(report_data)
```

### Benefits

- **Standardized Evaluation**: Consistent metrics for comparing different strategies
- **Comprehensive Analysis**: Multiple metrics provide a holistic view of strategy performance
- **Visual Representation**: Equity curve plots help visualize strategy performance over time
- **Persistent Storage**: Reports can be saved for future reference and comparison
- **Flexible Integration**: The framework can be used with any strategy that produces trade history

This evaluation framework provides a robust foundation for assessing trading strategy performance and making data-driven decisions about strategy selection and parameter tuning.

## Testing Infrastructure

### Historical Data Management

The Abidance Trading Bot implements a robust Historical Data Management system that provides efficient storage and retrieval of OHLCV (Open, High, Low, Close, Volume) data for backtesting and strategy development. This system consists of two main components:

1. **HistoricalDataManager (testing/data_management.py)**: The core class responsible for managing historical price data:
   - **Parquet Storage**: Uses the Apache Parquet file format for efficient columnar storage and fast data retrieval
   - **Symbol Handling**: Properly manages trading pair symbols with special characters (e.g., BTC/USDT)
   - **Date Filtering**: Supports loading data within specific date ranges
   - **Frequency Support**: Handles different timeframes (1m, 5m, 15m, 1h, 4h, 1d, etc.)
   - **Directory Management**: Automatically creates necessary data directories
   - **Data Validation**: Ensures data integrity before storage
   - **Efficient Appending**: Intelligently appends new data to existing datasets
   - **Consistent Data Format**: Maintains a standardized DataFrame structure for all data

2. **Data Loaders (testing/data_loaders.py)**: Classes for fetching and loading historical data:
   - **ExchangeDataLoader**: Fetches historical data from cryptocurrency exchanges
     - Supports all exchanges available in the CCXT library
     - Handles rate limiting and retry logic
     - Supports fetching specific timeframes
     - Automatically saves fetched data to the data manager
     - Implements a load-or-fetch pattern to minimize API calls
     - Handles date range specifications
   - **CSVDataLoader**: Loads historical data from CSV files
     - Supports custom date formats
     - Validates required OHLCV columns
     - Automatically saves loaded data to the data manager
     - Handles various CSV formats and structures

### Key Learnings

- **Parquet vs. CSV**: Parquet provides significantly faster read/write operations and smaller file sizes compared to CSV, especially for large datasets
- **Symbol Normalization**: Trading pair symbols need to be normalized for filesystem storage (e.g., BTC/USDT → BTC_USDT)
- **Frequency Handling**: Consistent handling of timeframe frequencies is crucial for proper data retrieval and analysis
- **Data Integrity**: Validating timestamp uniqueness and sorting is essential for accurate backtesting
- **Efficient Appending**: Properly appending new data to existing datasets requires careful handling of duplicates and sorting
- **Directory Structure**: Organizing data by exchange, symbol, and frequency creates a clean and navigable data structure
- **Date Filtering**: Implementing efficient date filtering improves performance for backtesting specific time periods
- **Load-or-Fetch Pattern**: Minimizing API calls by first checking for local data significantly improves performance and reduces API rate limiting issues
- **Error Handling**: Robust error handling for network issues, API limitations, and file operations is essential for reliable data management

### Usage Examples

#### Basic Data Management

```python
from abidance.testing.data_management import HistoricalDataManager

# Create a data manager
data_manager = HistoricalDataManager(base_path="./data")

# Load OHLCV data
df = data_manager.load_ohlcv("binance", "BTC/USDT", "1h")

# Load data for a specific date range
import datetime
start_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2023, 1, 31)
df = data_manager.load_ohlcv("binance", "BTC/USDT", "1h", start_date=start_date, end_date=end_date)

# Store new OHLCV data
data_manager.store_ohlcv(df, "binance", "BTC/USDT", "1h")
```

#### Using the Exchange Data Loader

```python
from abidance.testing.data_loaders import ExchangeDataLoader
from abidance.testing.data_management import HistoricalDataManager

# Create a data manager
data_manager = HistoricalDataManager(base_path="./data")

# Create an exchange data loader
loader = ExchangeDataLoader(data_manager, exchange_id="binance")

# Fetch OHLCV data
df = loader.fetch_ohlcv("BTC/USDT", "1h", limit=1000)

# Load or fetch data (will load from disk if available, otherwise fetch from exchange)
df = loader.load_or_fetch_ohlcv("BTC/USDT", "1h", limit=1000)

# Fetch data for a specific date range
import datetime
start_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2023, 1, 31)
df = loader.fetch_ohlcv("BTC/USDT", "1h", since=start_date, until=end_date)
```

#### Using the CSV Data Loader

```python
from abidance.testing.data_loaders import CSVDataLoader
from abidance.testing.data_management import HistoricalDataManager

# Create a data manager
data_manager = HistoricalDataManager(base_path="./data")

# Create a CSV data loader
loader = CSVDataLoader(data_manager, exchange_id="binance")

# Load data from a CSV file
df = loader.load_csv("path/to/btc_usdt_1h.csv", "BTC/USDT", "1h")

# Load data with a custom date format
df = loader.load_csv("path/to/btc_usdt_1h.csv", "BTC/USDT", "1h", date_format="%Y-%m-%d %H:%M:%S")

# Load data and save to the data manager
df = loader.load_csv("path/to/btc_usdt_1h.csv", "BTC/USDT", "1h", save=True)
```

This Historical Data Management system provides a solid foundation for backtesting and strategy development by ensuring consistent access to historical market data. The combination of efficient storage with Parquet, flexible loading options, and robust data validation makes it a powerful tool for algorithmic trading development.

## Property-Based Testing Framework

The Abidance Trading Bot includes a comprehensive property-based testing framework that helps ensure trading strategies behave correctly under various market conditions. This framework is particularly valuable for discovering edge cases and validating strategy invariants.

### Key Components

- **Data Generators**: Functions that generate realistic test data
  - `generate_ohlcv_data`: Creates random OHLCV data with realistic price movements
  - `generate_strategy_parameters`: Creates random parameters for strategies
  - `generate_market_data`: Creates market data for multiple symbols
  - `generate_order_book_data`: Creates order book data with bids and asks
  - `generate_trade_data`: Creates trade data with timestamps, prices, and sides

- **Property Validators**: Functions that validate properties of data and strategies
  - `validate_ohlcv_data`: Ensures OHLCV data satisfies basic properties
  - `test_strategy_signal_invariants`: Tests that strategy signals are valid
  - `test_strategy_consistency`: Tests that strategies produce consistent results
  - `test_strategy_edge_cases`: Tests strategy behavior with edge cases

- **Market Scenario Generators**: Functions that create specific market conditions
  - `create_trending_market`: Creates a trending market (up or down)
  - `create_sideways_market`: Creates a sideways market with mean reversion

### Usage Example

```python
from abidance.testing.properties import test_strategy_signal_invariants
from abidance.strategy import SMAStrategy, SMAConfig

# Create a test function for the SMA strategy
test_sma_signals = test_strategy_signal_invariants(
    strategy_class=SMAStrategy,
    config_class=SMAConfig,
    config_params={
        'fast_period': 10,
        'slow_period': 30,
        'volume_factor': 1.5
    }
)

# Run the test
test_sma_signals()
```

### Benefits

- **Automated Edge Case Discovery**: The framework automatically generates diverse test cases, including edge cases that might be missed in manual testing.
- **Invariant Validation**: Ensures that key properties always hold true, regardless of input data.
- **Realistic Market Scenarios**: Tests strategies under different market conditions to ensure robust performance.
- **Consistency Checking**: Verifies that strategies produce consistent results when run multiple times on the same data.

This property-based testing approach complements traditional unit tests and helps build more reliable trading strategies by systematically exploring the input space and validating core properties.

## Pylon Storage System

The Pylon Storage system is a high-performance time series data storage solution built on Apache Arrow and Parquet. It provides efficient storage and retrieval of financial time series data with the following key features:

- **Columnar Storage**: Uses Apache Arrow and Parquet for efficient columnar data access, which is particularly well-suited for time series data analysis.
- **Partitioning**: Supports data partitioning (by default using year and month) to enable faster data retrieval by limiting the amount of data that needs to be scanned.
- **Custom Partitioning**: Allows custom partitioning columns to be specified for specialized data organization needs.
- **Compression**: Implements data compression to reduce storage requirements while maintaining fast access.
- **DatetimeIndex Preservation**: Carefully preserves the frequency of DatetimeIndex when loading data, which is critical for time series analysis.
- **Duplicate Handling**: Properly handles duplicate timestamps when appending data, ensuring data integrity.
- **Efficient Appending**: Provides optimized methods for appending new data to existing datasets.
- **Date Filtering**: Supports efficient filtering by date ranges during data retrieval.
- **Column Projection**: Allows loading only specific columns to reduce memory usage and improve performance.

The Pylon Storage system is implemented in `abidance/testing/pylon_storage.py` and provides three main methods:

1. **store_dataframe**: Stores a DataFrame with time series data, partitioning it by year and month (or custom columns).
2. **load_dataframe**: Loads a DataFrame with time series data, with support for date filtering and column projection.
3. **append_dataframe**: Appends new data to an existing dataset, handling overlapping timestamps correctly.

Important implementation details:
- When loading data, the system sets the appropriate frequency on the DatetimeIndex based on the timeframe parameter.
- When appending data, the system removes duplicate timestamps to ensure data integrity.
- The system uses PyArrow for efficient data manipulation and Parquet for storage.

## Binance Data Fetcher

The Binance Data Fetcher is a specialized component for retrieving historical OHLCV data from the Binance exchange. It provides efficient data retrieval with the following key features:

- **Multiple Symbol Support**: Can fetch data for multiple trading pairs in a single operation.
- **Multiple Timeframe Support**: Supports various timeframes (1m, 5m, 15m, 1h, etc.).
- **Pagination**: Handles large date ranges by automatically paginating requests.
- **Rate Limiting**: Implements exponential backoff for rate limit handling.
- **Parallel Fetching**: Uses asyncio and concurrent.futures to fetch data for multiple symbols in parallel.
- **Integration with Pylon**: Seamlessly stores fetched data in the Pylon Storage system.

The Binance Data Fetcher is implemented in `abidance/testing/binance_data_fetcher.py` and provides methods for fetching historical data with various options.

Important implementation details:
- The parallel fetching functionality uses a ThreadPoolExecutor to fetch data for multiple symbols concurrently.
- The fetcher properly handles the results from concurrent futures to ensure all symbols are processed correctly.
- Rate limiting is implemented with exponential backoff to avoid hitting Binance API limits.

## New Knowledge Base

This document contains key learnings and insights about the codebase that help improve productivity.

## Data Fetching and Storage

### Pylon Storage System
- Columnar storage using Apache Arrow and Parquet for efficient data access
- Support for data partitioning by year, month, or custom columns
- Data compression using Snappy for reduced storage size
- Efficient appending with duplicate handling
- Preservation of DatetimeIndex frequency when loading data
- Methods provided: `store_dataframe`, `load_dataframe`, and `append_dataframe`
- Partitioning improves query performance by allowing the system to skip irrelevant data

### Binance Data Fetcher
- Support for multiple symbols and timeframes
- Pagination for large date ranges with automatic handling
- Rate limiting with exponential backoff to avoid API restrictions
- Parallel fetching using asyncio and concurrent.futures
- Integration with the Pylon Storage system
- Methods for fetching single symbol/timeframe or multiple combinations
- Efficient handling of date ranges and data updates

### Command-line Data Fetching
- The `fetch_historical_data.py` script provides a convenient command-line interface for fetching data
- Supports fetching multiple symbols and timeframes in a single command
- Options for parallel fetching to improve performance
- Flexible date range specification (start/end dates or number of days)
- Automatic storage using the Pylon system
- Command examples:
  - Basic usage: `python fetch_historical_data.py`
  - Custom symbols: `python fetch_historical_data.py --symbols BTCUSDT ETHUSDT`
  - Custom timeframes: `python fetch_historical_data.py --timeframes 15m 1h 4h`
  - Date range: `python fetch_historical_data.py --start-date 2023-01-01 --end-date 2023-02-01`
  - Last N days: `python fetch_historical_data.py --days 60`
  - Parallel fetching: `python fetch_historical_data.py --parallel --max-workers 8`

### Data Analysis and Visualization
- The `analyze_data.py` script provides tools for analyzing and visualizing historical data
- Calculates common technical indicators (SMA, RSI, MACD, Bollinger Bands)
- Generates summary statistics (price change, returns, Sharpe ratio, etc.)
- Creates visualizations with price charts and indicators
- Saves analysis results to CSV and text files
- Command examples:
  - Basic usage: `python analyze_data.py`
  - Custom symbol: `python analyze_data.py --symbol ADAUSDT`
  - Custom timeframe: `python analyze_data.py --timeframe 4h`
  - Date range: `python analyze_data.py --start-date 2023-01-01 --end-date 2023-02-01`
  - Last N days: `python analyze_data.py --days 60`
  - Custom output directory: `python analyze_data.py --output-dir my_reports`

## Important Implementation Details

### Working with DatetimeIndex Frequency
- When loading data from storage, it's important to preserve the frequency of the DatetimeIndex
- The PylonStorage system maps timeframe strings (e.g., '1h', '15m') to pandas frequency strings
- This mapping ensures that loaded data has the correct frequency for resampling and other time-based operations

### Handling Duplicate Timestamps
- When appending data, duplicate timestamps can occur at the boundaries of data chunks
- The PylonStorage system handles this by using `drop_duplicates` with the 'timestamp' column
- This ensures that the resulting dataset has unique timestamps and consistent data

### Parallel Data Fetching
- The ThreadPoolExecutor is used for parallel fetching to improve performance
- Each symbol/timeframe combination is fetched in a separate thread
- The max_workers parameter controls the level of parallelism
- Results are collected as they complete using concurrent.futures.as_completed

### Data Partitioning
- Partitioning data by year and month improves query performance
- When querying a specific date range, only relevant partitions are read
- Custom partitioning is supported by providing a list of partition columns
- Partitioning is especially beneficial for large datasets spanning multiple years

### Technical Indicator Calculation
- Technical indicators are calculated using pandas rolling windows and other operations
- The RSI calculation uses the standard formula with gain/loss averaging
- MACD is calculated using exponential moving averages (EMAs)
- Bollinger Bands use a 20-period moving average with 2 standard deviation bands
- These indicators can be used for strategy development and backtesting

## Performance Testing Framework

The Abidance Trading Bot includes a comprehensive performance testing framework for evaluating and benchmarking trading strategies. This framework is implemented in the `abidance.testing.performance` and `abidance.testing.benchmarks` modules and provides tools for measuring execution time, memory usage, and parallel execution capabilities.

### Key Components

1. **PerformanceTester (performance.py)**: A class for testing the performance of individual trading strategies:
   - `measure_execution_time`: Measures strategy execution time statistics (mean, median, std, min, max)
   - `measure_memory_usage`: Measures strategy memory usage (initial, final, delta)
   - `benchmark_parallel_execution`: Benchmarks parallel strategy execution

2. **StrategyBenchmark (benchmarks.py)**: A class for benchmarking and comparing multiple trading strategies:
   - `add_strategy`: Adds a strategy to the benchmark
   - `run_all`: Runs benchmark for multiple strategies
   - `save_results`: Saves benchmark results to a JSON file
   - `compare_strategies`: Compares strategies based on key performance metrics
   - `plot_comparison`: Plots comparison of strategies for a specific metric

### Implementation Notes

- The performance testing framework uses conditional imports for optional dependencies like `psutil` (for memory usage) and `matplotlib` (for plotting)
- The framework is designed to be used with any strategy that implements the `Strategy` interface
- The benchmark results are saved in a structured JSON format for easy analysis
- The framework supports parallel execution testing to evaluate strategy performance in multi-threaded environments
- The `PerformanceTester` class creates strategy instances with default configurations if none are provided

### Usage Examples

#### Basic Performance Testing

```python
from abidance.testing.performance import PerformanceTester
from abidance.strategy.moving_average import MovingAverageCrossoverStrategy
import pandas as pd

# Load test data
data = pd.read_csv("test_data.csv")

# Create a performance tester
tester = PerformanceTester(MovingAverageCrossoverStrategy, data)

# Measure execution time
execution_time = tester.measure_execution_time(num_runs=100, fast_period=10, slow_period=30)
print(f"Mean execution time: {execution_time['mean']:.6f} seconds")

# Measure memory usage
memory_usage = tester.measure_memory_usage(fast_period=10, slow_period=30)
print(f"Memory delta: {memory_usage['delta_mb']:.2f} MB")
```

#### Benchmarking Multiple Strategies

```python
from abidance.testing.benchmarks import StrategyBenchmark
from abidance.strategy.moving_average import MovingAverageCrossoverStrategy
from abidance.strategy.rsi import RSIStrategy
import pandas as pd

# Load test data
data = pd.read_csv("test_data.csv")

# Create a benchmark
benchmark = StrategyBenchmark(data, output_dir="benchmark_results")

# Add strategies to benchmark
benchmark.add_strategy(MovingAverageCrossoverStrategy, "MA_Cross_10_30", fast_period=10, slow_period=30)
benchmark.add_strategy(MovingAverageCrossoverStrategy, "MA_Cross_5_20", fast_period=5, slow_period=20)
benchmark.add_strategy(RSIStrategy, "RSI_14", period=14, overbought=70, oversold=30)

# Compare strategies
comparison = benchmark.compare_strategies()
print(comparison)

# Plot comparison
benchmark.plot_comparison(metric="mean_execution_time", save_path="execution_time_comparison.png")

# Save results
result_path = benchmark.save_results()
print(f"Benchmark results saved to: {result_path}")
```

## Code Quality and Testing

## Common Issues and Solutions

- When using string formatting with decimal precision, use f-strings instead of the old-style formatting to avoid invalid decimal literal syntax errors. For example, use `f"Value: {number:.2f}"` instead of `"Value: %s:.2f" % number`.
- Pay attention to indentation in functions, especially after conditional statements and exception handling. Incorrect indentation can lead to unexpected behavior where functions return None instead of the expected value.
- Health check functions should always return a HealthStatus value, even in error cases. Ensure proper indentation of return statements to avoid returning None by mistake.
- When implementing functions that should raise exceptions for invalid inputs, ensure the raise statement is properly indented and not accidentally placed outside the function's scope.
- The fallback decorator in error handling requires proper indentation to ensure it returns the correct value from the decorated function or the fallback value when an exception occurs.
- Type utility functions like from_timestamp, ensure_datetime, and ensure_timedelta need proper indentation for their error handling to work correctly.

## Code Quality

The project maintains a high code quality standard with a Pylint score of 8.34/10. This score is achieved through:

- Consistent code style and formatting
- Comprehensive docstrings for all modules, classes, and functions
- Proper error handling and exception propagation
- Clear separation of concerns between components
- Explicit type annotations for improved static analysis
- Organized imports following a consistent pattern
- Minimal code duplication through proper abstraction
- Adherence to the SOLID principles of object-oriented design

The code quality is continuously monitored and improved through regular Pylint checks, with results saved to pylint_report.txt for tracking progress over time.

## Refactoring Deeply Nested Code

Deeply nested code can be difficult to read, maintain, and test. The Abidance Trading Bot uses several strategies to reduce code nesting and improve readability:

1. **Extract Method Refactoring**: Breaking down complex methods into smaller, more focused helper methods.
   - Improves readability by giving meaningful names to code blocks
   - Reduces nesting depth by moving nested logic to separate methods
   - Facilitates testing by isolating specific functionality
   - Makes the code more maintainable by separating concerns

2. **Early Returns**: Using early returns to handle edge cases and preconditions.
   - Reduces nesting by eliminating the need for else blocks
   - Makes the main logic path clearer by handling special cases first
   - Improves readability by reducing indentation levels

3. **Guard Clauses**: Using guard clauses to validate inputs and handle error conditions early.
   - Similar to early returns, but specifically for validation and error handling
   - Reduces nesting by handling invalid cases immediately
   - Makes the code more robust by ensuring preconditions are met

Example of refactoring deeply nested code in the `get_trading_summary` method:

```python
# Before refactoring (deeply nested):
def get_trading_summary(self, symbol=None):
    summary = {
        "order_count_buy": 0,
        "order_count_sell": 0,
        # ... more metrics ...
    }
    
    if symbol:
        # Process metrics for a specific symbol
        for metric in self.order_metrics:
            value = self.get_metric(f"order_{metric}_{symbol}")
            if value:
                if "buy" in metric:
                    summary[f"order_{metric}_buy"] += value
                elif "sell" in metric:
                    summary[f"order_{metric}_sell"] += value
                else:
                    summary[f"order_{metric}"] += value
        
        # Similar nested logic for trade metrics
        # ... more nested code ...
    else:
        # Process metrics for all symbols
        # ... similar nested logic ...
    
    return summary

# After refactoring (reduced nesting):
def get_trading_summary(self, symbol=None):
    summary = {
        "order_count_buy": 0,
        "order_count_sell": 0,
        # ... more metrics ...
    }
    
    if symbol:
        self._process_symbol_metrics(summary, symbol)
    else:
        self._process_all_symbols_metrics(summary)
    
    return summary

def _process_symbol_metrics(self, summary, symbol):
    # Process order metrics
    for metric in self.order_metrics:
        value = self.get_metric(f"order_{metric}_{symbol}")
        if value:
            self._update_metric_sum(summary, metric, value)
    
    # Process trade metrics
    # ... similar code but cleaner ...

def _update_metric_sum(self, summary, metric, value):
    if "buy" in metric:
        summary[f"order_{metric}_buy"] += value
    elif "sell" in metric:
        summary[f"order_{metric}_sell"] += value
    else:
        summary[f"order_{metric}"] += value
```

This refactoring approach significantly improves code readability and maintainability by reducing nesting depth and giving meaningful names to code blocks.

## Resolving Cyclic Imports in the Exceptions Module

Cyclic imports in the exceptions module were resolved by applying the following approach:

1. **Identify the Cycle**: The cycle involved `abidance.exceptions`, `abidance.exceptions.fallback`, and `abidance.exceptions.error_context`.

2. **Extract Base Class**: The `

## Indentation and String Formatting Issues

During code quality improvements, several common issues were identified and fixed:

1. **F-string Formatting**: 
   - When using string formatting with decimal precision, use f-strings instead of the old-style formatting to avoid invalid decimal literal syntax errors. 
   - Example: Use `f"Value: {number:.2f}"` instead of `"Value: %s:.2f" % number`.
   - This issue was particularly common in logger statements in the health check module.

2. **Indentation in Functions**:
   - Pay attention to indentation in functions, especially after conditional statements and exception handling.
   - Incorrect indentation can lead to unexpected behavior where functions return None instead of the expected value.
   - Health check functions should always return a HealthStatus value, even in error cases. Ensure proper indentation of return statements to avoid returning None by mistake.

3. **Exception Handling**:
   - When implementing functions that should raise exceptions for invalid inputs, ensure the raise statement is properly indented and not accidentally placed outside the function's scope.
   - The fallback decorator in error handling requires proper indentation to ensure it returns the correct value from the decorated function or the fallback value when an exception occurs.

4. **Type Utility Functions**:
   - Type utility functions like from_timestamp, ensure_datetime, and ensure_timedelta need proper indentation for their error handling to work correctly.
   - These functions are critical for type conversion and validation throughout the codebase.

Fixing these issues resulted in all tests passing successfully, improving the reliability and correctness of the codebase.

## Database Design

- SQLAlchemy models can be used to create a clean and maintainable database schema for trading data
- Using SQLAlchemy's declarative_base from sqlalchemy.orm instead of sqlalchemy.ext.declarative avoids deprecation warnings in SQLAlchemy 2.0
- Unique constraints on OHLCV data (symbol + timestamp) prevent duplicate market data entries
- Creating indexes on frequently queried fields (symbol, timestamp) improves query performance
- Alembic provides a robust migration system for evolving the database schema over time
- Using in-memory SQLite databases for testing provides fast and isolated test environments
- The relationship between Strategy and Trade models allows for efficient querying of trades by strategy