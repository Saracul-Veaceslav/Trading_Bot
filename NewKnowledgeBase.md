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
  - **ml**: Machine learning components for prediction and analysis
    - **features**: Feature engineering framework for generating features from raw data
      - **base.py**: Abstract FeatureGenerator base class defining the common interface
      - **technical.py**: TechnicalFeatureGenerator for creating technical indicators from OHLCV data
    - **pipeline**: ML pipeline components for data processing and model training
      - **preprocessing.py**: DataPreprocessor class for data cleaning and preparation
      - **validation.py**: TimeSeriesValidator for time series cross-validation and metrics calculation
      - **trainer.py**: ModelTrainer for training and optimizing ML models
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
  - **database**: Database models, repositories, and query optimization
    - **models.py**: SQLAlchemy ORM models for trades, strategies, and OHLCV data
    - **repository**: Repository pattern implementation for data access
    - **queries.py**: Optimized query implementations for efficient data retrieval
    - **indexes.py**: Database index management for improved query performance

## Module Structure

- **Consistent Exports**: Each module has a well-defined `__all__` list that explicitly declares its public API
- **Docstrings**: Every module has a comprehensive docstring explaining its purpose
- **Import Organization**: Imports are organized in a consistent pattern across modules
- **Explicit Imports**: Modules explicitly import and re-export components from submodules
- **No Circular Imports**: The module structure is designed to avoid circular imports
- **Categorized Exports**: Exports in `__all__` are often categorized with comments for better readability

## ML Pipeline Implementation

The Abidance Trading Bot implements a comprehensive machine learning pipeline for data preprocessing, model training, and validation. This pipeline is designed to handle time series data specifically for trading applications.

### DataPreprocessor

The `DataPreprocessor` class in `abidance.ml.pipeline.preprocessing` provides data cleaning and preparation functionality:

- **handle_missing_values**: Fills missing values using various strategies (mean, median, forward fill, etc.)
- **remove_outliers**: Detects and handles outliers using z-score or IQR methods
  - Supports different thresholds for outlier detection
  - Handles both moderate and extreme outliers differently
  - Properly manages different data types (float, int) during outlier replacement
- **normalize_data**: Normalizes data using various methods (min-max, z-score, robust scaling)
- **process_pipeline**: Applies a sequence of preprocessing steps in a defined order

Key implementation details:
```python
def remove_outliers(self, data, column, method='z_score', threshold=3.0):
    """
    Detect and handle outliers in the specified column.
    
    For z-score method:
    - Moderate outliers (3 < |z| < 4): replaced with threshold * std from mean
    - Extreme outliers (|z| >= 4): removed from the dataset
    
    For IQR method:
    - Outliers outside Q1 - 1.5*IQR and Q3 + 1.5*IQR are handled
    """
    result = data.copy()
    
    if method == 'z_score':
        mean = data[column].mean()
        std = data[column].std()
        
        # Calculate z-scores
        z_scores = (data[column] - mean) / std
        
        # Identify moderate and extreme outliers
        moderate_outliers = (z_scores.abs() > threshold) & (z_scores.abs() <= threshold + 1)
        extreme_outliers = z_scores.abs() > threshold + 1
        
        # Handle moderate outliers - replace with threshold * std from mean
        result.loc[moderate_outliers & (data[column] < mean), column] = mean - threshold * std
        result.loc[moderate_outliers & (data[column] > mean), column] = mean + threshold * std
        
        # Handle extreme outliers - remove them
        result = result[~extreme_outliers]
    
    elif method == 'iqr':
        q1 = data[column].quantile(0.25)
        q3 = data[column].quantile(0.75)
        iqr = q3 - q1
        
        # Define bounds
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Replace outliers with bounds
        result.loc[data[column] < lower_bound, column] = lower_bound
        result.loc[data[column] > upper_bound, column] = upper_bound
    
    return result
```

### TimeSeriesValidator

The `TimeSeriesValidator` class in `abidance.ml.pipeline.validation` provides time series cross-validation and metrics calculation:

- **split_indices**: Generates train/test split indices for time series data
- **expanding_window**: Implements expanding window cross-validation for time series
- **sliding_window**: Implements sliding window cross-validation for time series
- **cross_validate**: Performs cross-validation with a given model and data

The module also includes metrics calculation functions:
- **calculate_metrics**: Calculates classification metrics (accuracy, precision, recall, F1)
- **calculate_profit_metrics**: Calculates profit-based performance metrics (total return, win rate, profit factor)

Key implementation details for profit metrics:
```python
def calculate_profit_metrics(y_true, y_pred, returns):
    """
    Calculate profit-based performance metrics.
    
    Parameters:
    -----------
    y_true : array-like
        True binary labels.
    y_pred : array-like
        Predicted binary labels.
    returns : array-like
        Actual returns for each prediction period.
        
    Returns:
    --------
    dict
        Dictionary containing profit-based metrics:
        - total_return: Sum of returns where predictions were correct minus penalty for incorrect predictions
        - win_rate: Proportion of correct predictions
        - profit_factor: Ratio of gains to losses
    """
    metrics = {}
    
    # Convert inputs to numpy arrays
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    returns = np.array(returns)
    
    # Calculate correct predictions
    correct_predictions = y_true == y_pred
    
    # Calculate win rate
    metrics['win_rate'] = np.mean(correct_predictions)
    
    # Calculate total return
    # For correct predictions, we get the actual return
    # For incorrect predictions, we get the negative of the return (penalty)
    correct_returns = returns[correct_predictions].sum() if any(correct_predictions) else 0
    incorrect_penalty = returns[~correct_predictions].sum() if any(~correct_predictions) else 0
    metrics['total_return'] = correct_returns - incorrect_penalty
    
    # Calculate profit factor (ratio of gains to losses)
    gains = returns[returns > 0].sum() if any(returns > 0) else 0
    losses = abs(returns[returns < 0].sum()) if any(returns < 0) else 1  # Avoid division by zero
    metrics['profit_factor'] = gains / losses
    
    return metrics
```

### ModelTrainer

The `ModelTrainer` class in `abidance.ml.pipeline.trainer` provides model training and optimization functionality:

- **prepare_data**: Prepares data for training by splitting features and target
- **train_with_cross_validation**: Trains a model using time series cross-validation
- **predict**: Makes predictions using a trained model
- **optimize_parameters**: Optimizes model parameters using grid search
- **parallel_optimization**: Performs parameter optimization in parallel for improved performance

## Testing ML Components

Testing machine learning components requires special considerations:

1. **Test Data Preparation**: Creating appropriate test data that can verify both normal operation and edge cases
   - For outlier detection, include both moderate and extreme outliers
   - For profit metrics, include various combinations of correct/incorrect predictions and returns

2. **Deterministic Testing**: Ensuring tests are deterministic despite the stochastic nature of some ML algorithms
   - Use fixed random seeds
   - Create synthetic data with known properties
   - Test boundary conditions explicitly

3. **Tolerance in Assertions**: Using appropriate tolerances when comparing floating-point results
   - Use `np.isclose()` or `pytest.approx()` for floating-point comparisons
   - Define acceptable error margins based on the precision requirements

4. **Mocking Complex Dependencies**: Using mocks to isolate the component being tested
   - Mock model objects to return predetermined predictions
   - Mock data preprocessing steps when testing model training

5. **Testing Extreme Cases**: Ensuring the system handles extreme values correctly
   - Test with very large outliers
   - Test with edge cases like all-zero or all-one predictions

Example of a robust test for outlier removal:
```python
def test_remove_outliers(self):
    """Test that extreme outliers are properly removed from the dataset."""
    # Create sample data with a known outlier
    data = pd.DataFrame({
        'A': [1, 2, 3, 4, 5, 1000]  # 1000 is an extreme outlier
    })
    
    # Create a copy to verify the original is unchanged
    data_copy = data.copy()
    
    # Process the data
    preprocessor = DataPreprocessor()
    result = preprocessor.remove_outliers(data, 'A', method='z_score', threshold=3.0)
    
    # Verify the original data is unchanged
    pd.testing.assert_frame_equal(data, data_copy)
    
    # Verify the outlier was removed
    self.assertEqual(len(result), 5)  # One row should be removed
    self.assertNotIn(1000, result['A'].values)  # The outlier value should not be present
```

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
```