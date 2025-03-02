# Abidance Crypto Trading Bot Implementation Plan

This document outlines the step-by-step implementation plan for the Abidance Crypto Trading Bot. We will follow a test-driven development (TDD) approach, where tests are created first before implementing any feature.

## Implementation Approach

For each step:
1. **Create tests first**: Write comprehensive tests that define the expected behavior
2. **Implement the feature**: Develop the feature until all tests pass
3. **Refactor**: Clean up the implementation while ensuring tests continue to pass
4. **Document**: Update documentation to reflect the implemented feature

## Implementation Timeline and Prioritization

The implementation is organized into four prioritized phases:

1. **Phase 1: Core Architecture Restructuring** (Weeks 1-3)
2. **Phase 2: Error Handling and Observability** (Weeks 3-5)
3. **Phase 3: Technical Indicator and Strategy Optimization** (Weeks 5-7)
4. **Phase 4: Testing Infrastructure Enhancement** (Weeks 7-9)

Subsequent phases (5-10) will be planned based on progress and emerging requirements.

## TDD Approach for Each Component

For each component, follow this precise TDD approach:

1. Write test cases that define expected behavior
2. Verify tests fail (red)
3. Implement minimal code to pass tests (green)
4. Refactor while keeping tests passing
5. Document implementation decisions and usage examples

## Phase 1: Core Architecture Restructuring (Weeks 1-3)

### Step 1: Package Reorganization and Module Boundaries

#### 1.1: Core Domain Model Extraction

**Files to modify:**
- Create `abidance/core/domain.py`
- Create `abidance/core/types.py` 
- Create `abidance/core/__init__.py`

**Code changes:**
1. Extract core domain entities from existing strategy and exchange modules:
```python
# abidance/core/domain.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Union, Literal

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell" 
    HOLD = "hold"

@dataclass
class Position:
    symbol: str
    side: OrderSide
    entry_price: float
    size: float
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_id: Optional[str] = None
```

**Tests to create:**
- `tests/unit/core/test_domain_models.py`:
  - Test domain entity creation with valid parameters
  - Test validation rules on domain entity creation
  - Test domain entity equality and comparison
  - Test serialization/deserialization of domain entities

**Reasoning:**
Extracting domain models establishes a clear core domain model independent of peripheral concerns, following Domain-Driven Design principles. This reduces coupling between modules and creates a clear dependency hierarchy.

#### 1.2: Consistent Module Structure Implementation

**Files to modify:**
- Create module templates for each subdomain
- Create/modify `__init__.py` files in each module
- Update import statements across codebase

**Code example for module initialization:**
```python
# abidance/strategy/__init__.py
"""
Strategy module for algorithmic trading.

This module provides various strategy implementations for
algorithmic trading, including technical indicators, signal
generation, and strategy evaluation.
"""

# Core exports
from .base import Strategy, StrategyParameters
from .indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    detect_crossover
)

# Strategy implementations
from .sma_crossover import SMACrossoverStrategy
from .rsi import RSIStrategy
from .rsi_bollinger import RSIBollingerStrategy

__all__ = [
    # Base classes
    "Strategy",
    "StrategyParameters",
    
    # Indicators
    "calculate_sma",
    "calculate_ema",
    "calculate_rsi",
    "detect_crossover",
    
    # Strategies
    "SMACrossoverStrategy",
    "RSIStrategy",
    "RSIBollingerStrategy",
]
```

**Tests to create:**
- `tests/unit/test_module_structure.py`:
  - Test each module's `__init__.py` exports the expected symbols
  - Test that imports follow the new structure
  - Test for absence of circular imports

**Reasoning:**
Consistent module structure with clear public APIs improves code organization and developer experience. The `__init__.py` files act as explicit contracts for what each module provides.

### Step 2: Dependency Inversion and Interface Extraction

#### 2.1: Strategy Interface Extraction

**Files to modify:**
- Create `abidance/strategy/protocols.py`
- Modify `abidance/strategy/base.py`

**Code changes:**
```python
# abidance/strategy/protocols.py
from typing import Protocol, runtime_checkable, Dict, Any
import pandas as pd
from abidance.core.domain import SignalType

@runtime_checkable
class Strategy(Protocol):
    """Protocol defining the interface for trading strategies."""
    
    def calculate_signal(self, data: pd.DataFrame) -> SignalType:
        """Calculate trading signal from market data."""
        ...
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters."""
        ...
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set strategy parameters."""
        ...
```

**Tests to create:**
- `tests/unit/strategy/test_strategy_protocol.py`:
  - Test that existing concrete strategies satisfy the protocol
  - Test that protocol works with runtime type checking
  - Test protocol documentation is accessible

**Reasoning:**
Using Protocol classes (structural typing) enables interface extraction without modifying existing implementations. This facilitates dependency inversion where high-level modules depend on abstractions rather than concrete implementations.

#### 2.2: Exchange Interface Extraction

**Files to modify:**
- Create `abidance/exchange/protocols.py`
- Modify `abidance/exchange/base.py`

**Code changes:**
```python
# abidance/exchange/protocols.py
from typing import Protocol, runtime_checkable, Dict, List, Optional
import pandas as pd
from datetime import datetime
from abidance.core.domain import OrderType, OrderSide, Position

@runtime_checkable
class Exchange(Protocol):
    """Protocol defining the interface for cryptocurrency exchanges."""
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, 
                   since: Optional[datetime] = None, 
                   limit: Optional[int] = None) -> pd.DataFrame:
        """Fetch OHLCV candle data from exchange."""
        ...
    
    def create_market_order(self, symbol: str, side: OrderSide, 
                           amount: float) -> Dict[str, Any]:
        """Create a market order on the exchange."""
        ...
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for a symbol if exists."""
        ...
```

**Tests to create:**
- `tests/unit/exchange/test_exchange_protocol.py`:
  - Test that existing exchange implementations satisfy the protocol
  - Test that protocol works with runtime type checking
  - Test protocol documentation is accessible

**Reasoning:**
Creating a clear exchange protocol allows for easy substitution of exchange implementations and facilitates testing through mock implementations.

### Step 3: Dependency Injection Framework

#### 3.1: Service Registry Implementation

**Files to modify:**
- Create `abidance/core/container.py`
- Modify application bootstrap code

**Code changes:**
```python
# abidance/core/container.py
from typing import Dict, Any, Type, TypeVar, Generic, get_type_hints

T = TypeVar('T')

class ServiceRegistry:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        
    def register(self, service_key: str, instance: Any) -> None:
        """Register a service instance."""
        self._services[service_key] = instance
        
    def register_factory(self, service_key: str, factory_func) -> None:
        """Register a factory function that creates a service instance."""
        self._services[service_key] = factory_func
        
    def get(self, service_key: str) -> Any:
        """Get a service instance by key."""
        service = self._services.get(service_key)
        if callable(service) and not isinstance(service, type):
            # If it's a factory function, call it to get the instance
            return service()
        return service

# Global service registry instance
registry = ServiceRegistry()
```

**Tests to create:**
- `tests/unit/core/test_service_registry.py`:
  - Test service registration and retrieval
  - Test factory function registration and lazy instantiation
  - Test handling of missing services

**Reasoning:**
A service registry facilitates dependency injection, making component dependencies explicit and easier to manage. This reduces tight coupling and improves testability.

### Step 4: Configuration Management System

#### 4.1: Environment Configuration Implementation

**Files to modify:**
- Create `abidance/core/config.py`
- Create `abidance/core/environment.py`
- Create `.env.example`

**Code changes:**
```python
# abidance/core/config.py
from typing import Any, Dict, Optional
from pathlib import Path
import os
import json
from dotenv import load_dotenv

class Configuration:
    """Configuration management system."""
    
    def __init__(self, env_file: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        self._load_environment(env_file)
        
    def _load_environment(self, env_file: Optional[str]) -> None:
        """Load environment variables from .env file."""
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, os.getenv(key, default))
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        
    def load_json(self, path: str) -> None:
        """Load configuration from JSON file."""
        with open(path, 'r') as f:
            self._config.update(json.load(f))
```

**Tests to create:**
- `tests/unit/core/test_config.py`:
  - Test environment variable loading
  - Test configuration value retrieval
  - Test JSON configuration loading
  - Test configuration value setting

**Reasoning:**
A centralized configuration system ensures consistent access to application settings and environment variables across the application.

### Step 5: Event System Implementation

#### 5.1: Event Bus Implementation

**Files to modify:**
- Create `abidance/core/events.py`
- Create `abidance/core/event_handlers.py`

**Code changes:**
```python
# abidance/core/events.py
from typing import Callable, Dict, List, Type
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    """Base class for all events."""
    timestamp: datetime = datetime.now()

class EventBus:
    """Central event bus for publishing and subscribing to events."""
    
    def __init__(self):
        self._handlers: Dict[Type[Event], List[Callable]] = {}
        
    def subscribe(self, event_type: Type[Event], 
                 handler: Callable[[Event], None]) -> None:
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
```

**Tests to create:**
- `tests/unit/core/test_events.py`:
  - Test event subscription
  - Test event publishing
  - Test multiple subscribers
  - Test event inheritance

**Reasoning:**
An event system enables loose coupling between components and facilitates communication across the application.

### Step 6: Validation Framework

#### 6.1: Data Validation Implementation

**Files to modify:**
- Create `abidance/core/validation.py`
- Create `abidance/core/validators.py`

**Code changes:**
```python
# abidance/core/validation.py
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    code: str

class Validator(ABC):
    """Base class for validators."""
    
    @abstractmethod
    def validate(self, value: Any) -> List[ValidationError]:
        """Validate a value and return list of errors."""
        pass

class ValidationContext:
    """Context for running multiple validators."""
    
    def __init__(self):
        self._validators: Dict[str, List[Validator]] = {}
        
    def add_validator(self, field: str, validator: Validator) -> None:
        """Add a validator for a field."""
        if field not in self._validators:
            self._validators[field] = []
        self._validators[field].append(validator)
        
    def validate(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate data against all registered validators."""
        errors: List[ValidationError] = []
        
        for field, validators in self._validators.items():
            if field in data:
                for validator in validators:
                    errors.extend(validator.validate(data[field]))
                    
        return errors
```

**Tests to create:**
- `tests/unit/core/test_validation.py`:
  - Test basic validation
  - Test multiple validators
  - Test validation context
  - Test custom validators

**Reasoning:**
A validation framework ensures data integrity and provides consistent validation across the application.

### Step 7: Metrics Collection System

#### 7.1: Metrics Framework Implementation

**Files to modify:**
- Create `abidance/core/metrics.py`
- Create `abidance/core/collectors.py`

**Code changes:**
```python
# abidance/core/metrics.py
from typing import Dict, Any, Optional
from datetime import datetime
import threading
from collections import defaultdict

class MetricsCollector:
    """Collector for application metrics."""
    
    def __init__(self):
        self._metrics: Dict[str, Dict[datetime, Any]] = defaultdict(dict)
        self._lock = threading.Lock()
        
    def record(self, metric_name: str, value: Any) -> None:
        """Record a metric value."""
        with self._lock:
            self._metrics[metric_name][datetime.now()] = value
            
    def get_metric(self, metric_name: str, 
                  since: Optional[datetime] = None) -> Dict[datetime, Any]:
        """Get recorded values for a metric."""
        with self._lock:
            data = self._metrics.get(metric_name, {})
            if since:
                return {ts: val for ts, val in data.items() if ts >= since}
            return data.copy()
```

**Tests to create:**
- `tests/unit/core/test_metrics.py`:
  - Test metric recording
  - Test metric retrieval
  - Test time-based filtering
  - Test concurrent access

**Reasoning:**
A metrics collection system enables monitoring and analysis of application performance and behavior.

## Phase 2: Error Handling and Observability (Weeks 3-5)

### Step 8: Advanced Logging Framework

#### 8.1: Structured Logging Implementation

**Files to modify:**
- Create `abidance/logging/structured.py`
- Create `abidance/logging/formatters.py`
- Create `abidance/logging/handlers.py`

**Code changes:**
```python
# abidance/logging/structured.py
from typing import Any, Dict, Optional
import logging
import json
from datetime import datetime
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar('request_id', default='')

class StructuredLogger:
    """Logger that outputs structured JSON logs."""
    
    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(name)
        
    def _format_log(self, level: str, message: str, 
                   extra: Optional[Dict[str, Any]] = None) -> str:
        """Format log entry as JSON."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'logger': self.name,
            'level': level,
            'message': message,
            'request_id': request_id.get(),
        }
        if extra:
            log_entry.update(extra)
        return json.dumps(log_entry)
        
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info level message."""
        self._logger.info(self._format_log('INFO', message, kwargs))
        
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error level message."""
        self._logger.error(self._format_log('ERROR', message, kwargs))
```

**Tests to create:**
- `tests/unit/logging/test_structured_logging.py`:
  - Test JSON log formatting
  - Test context variable handling
  - Test different log levels
  - Test extra fields in logs

**Reasoning:**
Structured logging enables better log analysis and integration with log management systems.

### Step 9: Performance Monitoring

#### 9.1: Performance Metrics Collection

**Files to modify:**
- Create `abidance/monitoring/performance.py`
- Create `abidance/monitoring/collectors.py`

**Code changes:**
```python
# abidance/monitoring/performance.py
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
from statistics import mean, median
from collections import deque
import threading

class PerformanceMetrics:
    """Collector for performance metrics."""
    
    def __init__(self, window_size: int = 1000):
        self._metrics: Dict[str, deque[float]] = {}
        self._window_size = window_size
        self._lock = threading.Lock()
        
    def record_timing(self, operation: str, duration: float) -> None:
        """Record operation duration."""
        with self._lock:
            if operation not in self._metrics:
                self._metrics[operation] = deque(maxlen=self._window_size)
            self._metrics[operation].append(duration)
            
    def get_statistics(self, operation: str) -> Dict[str, float]:
        """Get timing statistics for an operation."""
        with self._lock:
            if operation not in self._metrics:
                return {}
            
            values = list(self._metrics[operation])
            return {
                'count': len(values),
                'mean': mean(values),
                'median': median(values),
                'min': min(values),
                'max': max(values)
            }
```

**Tests to create:**
- `tests/unit/monitoring/test_performance_metrics.py`:
  - Test timing recording
  - Test statistics calculation
  - Test window size limiting
  - Test concurrent access

**Reasoning:**
Performance monitoring helps identify bottlenecks and track system health.

### Step 10: Tracing System

#### 10.1: Distributed Tracing Implementation

**Files to modify:**
- Create `abidance/tracing/tracer.py`
- Create `abidance/tracing/span.py`

**Code changes:**
```python
# abidance/tracing/tracer.py
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field

@dataclass
class Span:
    """Represents a single operation span."""
    trace_id: str
    span_id: str
    parent_id: Optional[str]
    operation: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class Tracer:
    """Distributed tracing system."""
    
    def __init__(self):
        self._spans: Dict[str, Span] = {}
        self._active_span: Optional[Span] = None
        
    @contextmanager
    def start_span(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Start a new trace span."""
        span_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4()) if not self._active_span else self._active_span.trace_id
        parent_id = self._active_span.span_id if self._active_span else None
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            operation=operation,
            metadata=metadata or {}
        )
        
        previous_span = self._active_span
        self._active_span = span
        self._spans[span_id] = span
        
        try:
            yield span
        finally:
            span.end_time = datetime.now()
            self._active_span = previous_span
```

**Tests to create:**
- `tests/unit/tracing/test_tracer.py`:
  - Test span creation
  - Test nested spans
  - Test span timing
  - Test metadata handling

**Reasoning:**
Distributed tracing enables tracking requests across system components and understanding system behavior.

### Step 11: Health Checking System

#### 11.1: Health Check Implementation

**Files to modify:**
- Create `abidance/health/checker.py`
- Create `abidance/health/checks.py`

**Code changes:**
```python
# abidance/health/checker.py
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import asyncio
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck:
    """System health checking framework."""
    
    def __init__(self):
        self._checks: Dict[str, Callable[[], HealthStatus]] = {}
        
    def register_check(self, name: str, check: Callable[[], HealthStatus]) -> None:
        """Register a health check."""
        self._checks[name] = check
        
    async def run_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all registered health checks."""
        results = {}
        for name, check in self._checks.items():
            try:
                status = check()
                results[name] = {
                    'status': status.value,
                    'timestamp': datetime.now().isoformat(),
                    'error': None
                }
            except Exception as e:
                results[name] = {
                    'status': HealthStatus.UNHEALTHY.value,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
        return results
```

**Tests to create:**
- `tests/unit/health/test_health_checker.py`:
  - Test health check registration
  - Test check execution
  - Test error handling
  - Test status reporting

**Reasoning:**
Health checking enables monitoring system components and detecting issues early.

## Phase 3: Technical Indicator and Strategy Optimization (Weeks 5-7)

### Step 12: Advanced Technical Indicators

#### 12.1: Momentum Indicators Implementation

**Files to modify:**
- Create `abidance/strategy/indicators/momentum.py`
- Update `abidance/strategy/indicators/__init__.py`

**Code changes:**
```python
# abidance/strategy/indicators/momentum.py
import pandas as pd
import numpy as np
from typing import Optional
from .base import Indicator

class RSI(Indicator):
    """Relative Strength Index indicator."""
    
    def __init__(self, period: int = 14, column: str = 'close'):
        self.period = period
        self.column = column
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate RSI values."""
        if self.column not in data.columns:
            raise ValueError(f"Column '{self.column}' not found in data")
            
        # Calculate price changes
        delta = data[self.column].diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        # Calculate average gain and loss
        avg_gain = gain.ewm(com=self.period-1, adjust=False).mean()
        avg_loss = loss.ewm(com=self.period-1, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @property
    def name(self) -> str:
        return f"RSI({self.period})"

class MACD(Indicator):
    """Moving Average Convergence Divergence indicator."""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, 
                signal_period: int = 9, column: str = 'close'):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.column = column
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator."""
        if self.column not in data.columns:
            raise ValueError(f"Column '{self.column}' not found in data")
            
        # Calculate EMAs
        fast_ema = data[self.column].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = data[self.column].ewm(span=self.slow_period, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = fast_ema - slow_ema
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }, index=data.index)
    
    @property
    def name(self) -> str:
        return f"MACD({self.fast_period},{self.slow_period},{self.signal_period})"
```

**Tests to create:**
- `tests/unit/strategy/indicators/test_momentum_indicators.py`:
  - Test RSI calculation with known values
  - Test RSI bounds (0-100)
  - Test MACD calculation
  - Test MACD signal line crossovers
  - Test error handling for missing data

**Reasoning:**
Momentum indicators help identify trend strength and potential reversals, providing valuable signals for trading strategies.

### Step 13: Strategy Optimization Framework

#### 13.1: Parameter Optimization Implementation

**Files to modify:**
- Create `abidance/optimization/optimizer.py`
- Create `abidance/optimization/metrics.py`

**Code changes:**
```python
# abidance/optimization/optimizer.py
from typing import Dict, Any, List, Tuple, Callable
import numpy as np
from dataclasses import dataclass
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from abidance.strategy.base import Strategy

@dataclass
class OptimizationResult:
    """Results from strategy parameter optimization."""
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    trades: pd.DataFrame

class StrategyOptimizer:
    """Optimizer for strategy parameters."""
    
    def __init__(self, strategy_class: type[Strategy],
                 parameter_ranges: Dict[str, List[Any]],
                 metric_function: Callable[[pd.DataFrame], float]):
        self.strategy_class = strategy_class
        self.parameter_ranges = parameter_ranges
        self.metric_function = metric_function
        
    def _evaluate_parameters(self, params: Dict[str, Any],
                           data: pd.DataFrame) -> OptimizationResult:
        """Evaluate a set of parameters."""
        strategy = self.strategy_class(**params)
        trades = strategy.backtest(data)
        performance = self.metric_function(trades)
        
        return OptimizationResult(
            parameters=params,
            performance_metrics={'metric': performance},
            trades=trades
        )
    
    def optimize(self, data: pd.DataFrame, 
                max_iterations: int = 100) -> List[OptimizationResult]:
        """
        Optimize strategy parameters using grid search.
        
        Args:
            data: Historical price data
            max_iterations: Maximum number of parameter combinations to try
            
        Returns:
            List of optimization results sorted by performance
        """
        # Generate parameter combinations
        param_combinations = []
        for params in self._generate_parameter_combinations():
            param_combinations.append(params)
            if len(param_combinations) >= max_iterations:
                break
                
        # Evaluate parameters in parallel
        results = []
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._evaluate_parameters, params, data)
                for params in param_combinations
            ]
            
            for future in futures:
                results.append(future.result())
                
        # Sort by performance
        results.sort(key=lambda x: x.performance_metrics['metric'], 
                    reverse=True)
        
        return results
    
    def _generate_parameter_combinations(self) -> Dict[str, Any]:
        """Generate combinations of parameters to try."""
        keys = list(self.parameter_ranges.keys())
        values = list(self.parameter_ranges.values())
        
        for combination in np.ndindex(*[len(v) for v in values]):
            yield {
                key: values[i][combination[i]]
                for i, key in enumerate(keys)
            }
```

**Tests to create:**
- `tests/unit/optimization/test_optimizer.py`:
  - Test parameter combination generation
  - Test strategy evaluation with different parameters
  - Test parallel optimization execution
  - Test result sorting and ranking

**Reasoning:**
Parameter optimization helps find the most effective settings for trading strategies across different market conditions.

### Step 14: Strategy Composition Framework

#### 14.1: Strategy Composition Implementation

**Files to modify:**
- Create `abidance/strategy/composition.py`
- Update `abidance/strategy/__init__.py`

**Code changes:**
```python
# abidance/strategy/composition.py
from typing import List, Dict, Any
import pandas as pd
from abc import ABC, abstractmethod
from .base import Strategy
from ..core.domain import SignalType

class CompositeStrategy(Strategy):
    """Base class for composite trading strategies."""
    
    def __init__(self, strategies: List[Strategy],
                 weights: List[float] = None):
        self.strategies = strategies
        self.weights = weights or [1.0] * len(strategies)
        
        if len(self.weights) != len(strategies):
            raise ValueError("Number of weights must match number of strategies")
            
        if not np.isclose(sum(self.weights), 1.0):
            raise ValueError("Weights must sum to 1.0")
    
    def calculate_signal(self, data: pd.DataFrame) -> SignalType:
        """Calculate combined signal from multiple strategies."""
        signals = [
            strategy.calculate_signal(data)
            for strategy in self.strategies
        ]
        
        # Convert signals to numeric values
        numeric_signals = [
            1 if s == SignalType.BUY else
            -1 if s == SignalType.SELL else
            0 for s in signals
        ]
        
        # Calculate weighted average
        weighted_signal = sum(
            signal * weight
            for signal, weight in zip(numeric_signals, self.weights)
        )
        
        # Convert back to SignalType
        if weighted_signal > 0.5:
            return SignalType.BUY
        elif weighted_signal < -0.5:
            return SignalType.SELL
        return SignalType.HOLD

class VotingStrategy(CompositeStrategy):
    """Strategy that uses majority voting to combine signals."""
    
    def calculate_signal(self, data: pd.DataFrame) -> SignalType:
        """Calculate signal using majority voting."""
        signals = [
            strategy.calculate_signal(data)
            for strategy in self.strategies
        ]
        
        # Count votes
        buy_votes = sum(1 for s in signals if s == SignalType.BUY)
        sell_votes = sum(1 for s in signals if s == SignalType.SELL)
        
        # Apply weighted voting
        buy_score = sum(
            weight for s, weight in zip(signals, self.weights)
            if s == SignalType.BUY
        )
        
        sell_score = sum(
            weight for s, weight in zip(signals, self.weights)
            if s == SignalType.SELL
        )
        
        # Make decision
        if buy_score > sell_score and buy_score > 0.5:
            return SignalType.BUY
        elif sell_score > buy_score and sell_score > 0.5:
            return SignalType.SELL
        return SignalType.HOLD
```

**Tests to create:**
- `tests/unit/strategy/test_composition.py`:
  - Test weighted signal combination
  - Test voting mechanism
  - Test weight validation
  - Test different strategy combinations

**Reasoning:**
Strategy composition enables combining multiple strategies to create more robust trading systems that can adapt to different market conditions.

### Step 15: Strategy Evaluation Framework

#### 15.1: Performance Metrics Implementation

**Files to modify:**
- Create `abidance/evaluation/metrics.py`
- Create `abidance/evaluation/reporting.py`

**Code changes:**
```python
# abidance/evaluation/metrics.py
from typing import Dict, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """Container for strategy performance metrics."""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    avg_trade: float
    num_trades: int

class StrategyEvaluator:
    """Evaluator for trading strategy performance."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
    
    def calculate_metrics(self, trades: pd.DataFrame) -> PerformanceMetrics:
        """Calculate performance metrics from trade history."""
        if trades.empty:
            raise ValueError("No trades to evaluate")
            
        # Calculate returns
        returns = trades['profit_pct'].values
        cumulative_returns = (1 + returns).cumprod() - 1
        
        # Calculate metrics
        total_return = cumulative_returns[-1]
        sharpe = self._calculate_sharpe_ratio(returns)
        max_dd = self._calculate_max_drawdown(cumulative_returns)
        win_rate = np.mean(returns > 0)
        
        # Separate wins and losses
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        
        profit_factor = (
            abs(wins.sum()) / abs(losses.sum())
            if len(losses) > 0 else float('inf')
        )
        
        return PerformanceMetrics(
            total_return=total_return,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_trade=np.mean(returns),
            num_trades=len(returns)
        )
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """Calculate annualized Sharpe ratio."""
        excess_returns = returns - self.risk_free_rate / 252  # Daily
        return np.sqrt(252) * (np.mean(excess_returns) / np.std(excess_returns))
    
    def _calculate_max_drawdown(self, cumulative_returns: np.ndarray) -> float:
        """Calculate maximum drawdown."""
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / (1 + peak)
        return abs(min(drawdown))
```

**Tests to create:**
- `tests/unit/evaluation/test_metrics.py`:
  - Test performance metric calculations
  - Test edge cases (no trades, all wins, all losses)
  - Test Sharpe ratio calculation
  - Test drawdown calculation

**Reasoning:**
Comprehensive performance evaluation helps assess strategy effectiveness and compare different approaches objectively.

## Phase 4: Testing Infrastructure Enhancement (Weeks 7-9)

### Step 16: Backtesting Framework

#### 16.1: Historical Data Management

**Files to modify:**
- Create `abidance/testing/data_management.py`
- Create `abidance/testing/data_loaders.py`

**Code changes:**
```python
# abidance/testing/data_management.py
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json

class HistoricalDataManager:
    """Manager for historical market data."""
    
    def __init__(self, data_dir: str = 'data/historical'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def save_ohlcv(self, symbol: str, timeframe: str, 
                   data: pd.DataFrame) -> None:
        """Save OHLCV data to disk."""
        file_path = self._get_ohlcv_path(symbol, timeframe)
        data.to_parquet(file_path)
        
    def load_ohlcv(self, symbol: str, timeframe: str,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Load OHLCV data from disk with optional date filtering."""
        file_path = self._get_ohlcv_path(symbol, timeframe)
        if not file_path.exists():
            raise FileNotFoundError(f"No data found for {symbol} {timeframe}")
            
        data = pd.read_parquet(file_path)
        
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
            
        return data
        
    def _get_ohlcv_path(self, symbol: str, timeframe: str) -> Path:
        """Get file path for OHLCV data."""
        return self.data_dir / f"{symbol}_{timeframe}.parquet"
```

**Tests to create:**
- `tests/unit/testing/test_data_management.py`:
  - Test data saving and loading
  - Test date filtering
  - Test error handling for missing data
  - Test file path generation

**Reasoning:**
Efficient historical data management is crucial for backtesting and strategy development.

### Step 17: Mock Exchange Framework

#### 17.1: Mock Exchange Implementation

**Files to modify:**
- Create `abidance/testing/mock_exchange.py`
- Create `abidance/testing/mock_data.py`

**Code changes:**
```python
# abidance/testing/mock_exchange.py
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime
from abidance.core.domain import OrderType, OrderSide, Position
from abidance.exchange.protocols import Exchange

class MockExchange(Exchange):
    """Mock exchange implementation for testing."""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.positions: Dict[str, Position] = {}
        self.orders: List[Dict[str, Any]] = []
        self.balance = initial_balance
        self._ohlcv_data: Dict[str, pd.DataFrame] = {}
        self._current_price: Dict[str, float] = {}
    
    def set_ohlcv_data(self, symbol: str, data: pd.DataFrame) -> None:
        """Set OHLCV data for a symbol."""
        self._ohlcv_data[symbol] = data.copy()
        
        # Set current price to the last close price
        if not data.empty:
            self._current_price[symbol] = data['close'].iloc[-1]
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, 
                   since: Optional[datetime] = None, 
                   limit: Optional[int] = None) -> pd.DataFrame:
        """Fetch OHLCV candle data from exchange."""
        if symbol not in self._ohlcv_data:
            raise ValueError(f"No data available for symbol {symbol}")
            
        data = self._ohlcv_data[symbol]
        
        # Filter by timestamp if since is provided
        if since is not None:
            data = data[data['timestamp'] >= since]
            
        # Limit the number of records if limit is provided
        if limit is not None:
            data = data.tail(limit)
            
        return data
    
    def create_market_order(self, symbol: str, side: OrderSide, 
                           amount: float) -> Dict[str, Any]:
        """Create a market order on the exchange."""
        if symbol not in self._current_price:
            raise ValueError(f"No price data available for symbol {symbol}")
            
        price = self._current_price[symbol]
        order_id = f"order_{len(self.orders) + 1}"
        
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'type': OrderType.MARKET,
            'amount': amount,
            'price': price,
            'timestamp': datetime.now(),
            'status': 'closed'
        }
        
        self.orders.append(order)
        
        # Update position and balance
        self._update_position(symbol, side, amount, price)
        
        return order
    
    def _update_position(self, symbol: str, side: OrderSide,
                        amount: float, price: float) -> None:
        """Update position and balance after order execution."""
        if side == OrderSide.BUY:
            # Create or update long position
            if symbol in self.positions:
                existing_pos = self.positions[symbol]
                total_amount = existing_pos.size + amount
                avg_price = (
                    (existing_pos.entry_price * existing_pos.size) +
                    (price * amount)
                ) / total_amount
                
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side=side,
                    entry_price=avg_price,
                    size=total_amount,
                    timestamp=datetime.now()
                )
            else:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side=side,
                    entry_price=price,
                    size=amount,
                    timestamp=datetime.now()
                )
            
            # Update balance
            self.balance -= price * amount
            
        elif side == OrderSide.SELL:
            # Close or reduce position
            if symbol in self.positions:
                existing_pos = self.positions[symbol]
                if existing_pos.size <= amount:
                    # Close position
                    del self.positions[symbol]
                else:
                    # Reduce position
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        side=existing_pos.side,
                        entry_price=existing_pos.entry_price,
                        size=existing_pos.size - amount,
                        timestamp=datetime.now()
                    )
                
                # Update balance
                self.balance += price * amount
            else:
                raise ValueError("Cannot sell without an existing position")
```

**Tests to create:**
- `tests/unit/testing/test_mock_exchange.py`:
  - Test order creation and execution
  - Test position management
  - Test balance updates
  - Test OHLCV data handling

**Reasoning:**
A mock exchange enables deterministic testing of trading strategies without relying on external services.

### Step 18: Property-Based Testing Framework

#### 18.1: Strategy Property Testing

**Files to modify:**
- Create `abidance/testing/properties.py`
- Create `abidance/testing/generators.py`

**Code changes:**
```python
# abidance/testing/properties.py
from typing import Any, Dict, List, Optional
from hypothesis import given, strategies as st
from hypothesis.strategies import SearchStrategy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_ohlcv_data(
    min_length: int = 100,
    max_length: int = 1000,
    min_price: float = 1.0,
    max_price: float = 1000.0,
    volatility: float = 0.02
) -> SearchStrategy[pd.DataFrame]:
    """Generate random OHLCV data for property-based testing."""
    
    @st.composite
    def inner(draw: Any) -> pd.DataFrame:
        length = draw(st.integers(min_length, max_length))
        
        # Generate timestamps
        start_date = draw(st.datetimes(
            min_value=datetime(2010, 1, 1),
            max_value=datetime(2024, 1, 1)
        ))
        timestamps = [
            start_date + timedelta(hours=i)
            for i in range(length)
        ]
        
        # Generate prices with random walk
        base_price = draw(st.floats(min_price, max_price))
        prices = [base_price]
        
        for _ in range(length - 1):
            change = draw(st.floats(-volatility, volatility))
            new_price = max(min_price, prices[-1] * (1 + change))
            prices.append(new_price)
            
        # Generate OHLCV data
        data = []
        for i, close_price in enumerate(prices):
            # Generate realistic OHLCV values
            open_price = prices[i-1] if i > 0 else close_price
            high_price = max(open_price, close_price) * (1 + abs(draw(st.floats(0, 0.005))))
            low_price = min(open_price, close_price) * (1 - abs(draw(st.floats(0, 0.005))))
            volume = draw(st.floats(100, 10000))
            
            data.append({
                'timestamp': timestamps[i],
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
            
        return pd.DataFrame(data)
    
    return inner()

# Example property test for a strategy
@given(data=generate_ohlcv_data())
def test_strategy_properties(data: pd.DataFrame) -> None:
    """Test that strategy satisfies basic properties."""
    from abidance.strategy import SMACrossoverStrategy
    
    strategy = SMACrossoverStrategy(short_window=10, long_window=30)
    signal = strategy.calculate_signal(data)
    
    # Properties that should always hold
    assert signal in {SignalType.BUY, SignalType.SELL, SignalType.HOLD}
```

**Tests to create:**
- `tests/unit/testing/test_properties.py`:
  - Test data generation properties
  - Test strategy invariants
  - Test edge cases
  - Test realistic market scenarios

**Reasoning:**
Property-based testing helps discover edge cases and ensures strategies behave correctly under various market conditions.

### Step 19: Performance Testing Framework

#### 19.1: Strategy Performance Testing

**Files to modify:**
- Create `abidance/testing/performance.py`
- Create `abidance/testing/benchmarks.py`

**Code changes:**
```python
# abidance/testing/performance.py
from typing import Dict, Any, Optional, List, Type
import pandas as pd
import numpy as np
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from abidance.strategy import Strategy
from abidance.evaluation.metrics import StrategyEvaluator

class PerformanceTester:
    """Framework for testing strategy performance."""
    
    def __init__(self, strategy_class: Type[Strategy],
                 data: pd.DataFrame,
                 evaluator: Optional[StrategyEvaluator] = None):
        self.strategy_class = strategy_class
        self.data = data
        self.evaluator = evaluator or StrategyEvaluator()
        
    def measure_execution_time(self, num_runs: int = 100,
                             **strategy_params) -> Dict[str, float]:
        """Measure strategy execution time statistics."""
        strategy = self.strategy_class(**strategy_params)
        execution_times = []
        
        for _ in range(num_runs):
            start_time = time.perf_counter()
            strategy.calculate_signal(self.data)
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)
            
        return {
            'mean': np.mean(execution_times),
            'median': np.median(execution_times),
            'std': np.std(execution_times),
            'min': np.min(execution_times),
            'max': np.max(execution_times)
        }
        
    def measure_memory_usage(self, **strategy_params) -> Dict[str, float]:
        """Measure strategy memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        strategy = self.strategy_class(**strategy_params)
        strategy.calculate_signal(self.data)
        
        final_memory = process.memory_info().rss
        
        return {
            'initial_mb': initial_memory / (1024 * 1024),
            'final_mb': final_memory / (1024 * 1024),
            'delta_mb': (final_memory - initial_memory) / (1024 * 1024)
        }
        
    def benchmark_parallel_execution(self, num_strategies: int = 10,
                                  **strategy_params) -> Dict[str, float]:
        """Benchmark parallel strategy execution."""
        strategies = [
            self.strategy_class(**strategy_params)
            for _ in range(num_strategies)
        ]
        
        start_time = time.perf_counter()
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(strategy.calculate_signal, self.data)
                for strategy in strategies
            ]
            results = [future.result() for future in futures]
        end_time = time.perf_counter()
        
        return {
            'total_time': end_time - start_time,
            'avg_time_per_strategy': (end_time - start_time) / num_strategies
        }
```

**Tests to create:**
- `tests/unit/testing/test_performance.py`:
  - Test execution time measurement
  - Test memory usage tracking
  - Test parallel execution benchmarking
  - Test performance with different data sizes

**Reasoning:**
Performance testing ensures strategies can execute efficiently in production environments.

## Phase 5: Database and Storage Optimization (Weeks 9-11)

### Step 20: Database Schema Design

#### 20.1: Core Schema Implementation

**Files to modify:**
- Create `abidance/database/models.py`
- Create `abidance/database/migrations/`
- Create `abidance/database/alembic.ini`

**Code changes:**
```python
# abidance/database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
from abidance.core.domain import OrderSide, OrderType

Base = declarative_base()

class Trade(Base):
    """Model for storing trade information."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'))
    
    strategy = relationship("Strategy", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(symbol={self.symbol}, side={self.side}, amount={self.amount})>"

class Strategy(Base):
    """Model for storing strategy configurations."""
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    trades = relationship("Trade", back_populates="strategy")
    
    def __repr__(self):
        return f"<Strategy(name={self.name})>"

class OHLCV(Base):
    """Model for storing OHLCV data."""
    __tablename__ = 'ohlcv'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp', unique=True),
    )
    
    def __repr__(self):
        return f"<OHLCV(symbol={self.symbol}, timestamp={self.timestamp})>"
```

**Tests to create:**
- `tests/unit/database/test_models.py`:
  - Test model creation and relationships
  - Test data integrity constraints
  - Test index effectiveness
  - Test model representations

**Reasoning:**
A well-designed database schema ensures data integrity and efficient querying while maintaining relationships between different entities in the trading system.

### Step 21: Repository Pattern Implementation

#### 21.1: Base Repository Implementation

**Files to modify:**
- Create `abidance/database/repository/base.py`
- Create `abidance/database/repository/trade.py`
- Create `abidance/database/repository/strategy.py`

**Code changes:**
```python
# abidance/database/repository/base.py
from typing import Generic, TypeVar, List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository implementation."""
    
    def __init__(self, session: Session, model: Type[T]):
        self._session = session
        self._model = model
    
    def add(self, entity: T) -> T:
        """Add a new entity."""
        self._session.add(entity)
        self._session.commit()
        return entity
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        return self._session.get(self._model, id)
    
    def list(self) -> List[T]:
        """List all entities."""
        return self._session.execute(
            select(self._model)
        ).scalars().all()
    
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        result = self._session.execute(
            delete(self._model).where(self._model.id == id)
        )
        self._session.commit()
        return result.rowcount > 0

# abidance/database/repository/trade.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from .base import BaseRepository
from ..models import Trade

class TradeRepository(BaseRepository[Trade]):
    """Repository for trade operations."""
    
    def __init__(self, session):
        super().__init__(session, Trade)
    
    def get_trades_by_symbol(self, symbol: str) -> List[Trade]:
        """Get all trades for a symbol."""
        return self._session.execute(
            select(Trade).where(Trade.symbol == symbol)
        ).scalars().all()
    
    def get_trades_by_date_range(self, 
                               start_date: datetime,
                               end_date: datetime) -> List[Trade]:
        """Get trades within a date range."""
        return self._session.execute(
            select(Trade).where(
                Trade.timestamp.between(start_date, end_date)
            )
        ).scalars().all()
```

**Tests to create:**
- `tests/unit/database/repository/test_base_repository.py`:
  - Test CRUD operations
  - Test error handling
  - Test transaction management
- `tests/unit/database/repository/test_trade_repository.py`:
  - Test trade-specific queries
  - Test date range filtering
  - Test symbol filtering

**Reasoning:**
The repository pattern provides a clean abstraction over data access, making it easier to maintain and test database operations.

### Step 22: Query Optimization

#### 22.1: Query Performance Enhancement

**Files to modify:**
- Create `abidance/database/queries.py`
- Create `abidance/database/indexes.py`

**Code changes:**
```python
# abidance/database/queries.py
from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .models import Trade, OHLCV, Strategy

class QueryOptimizer:
    """Optimized query implementations."""
    
    def __init__(self, session: Session):
        self._session = session
    
    def get_trade_statistics(self, symbol: str) -> Dict[str, float]:
        """Get aggregated trade statistics."""
        result = self._session.execute(
            select(
                func.count(Trade.id).label('total_trades'),
                func.sum(Trade.amount).label('total_volume'),
                func.avg(Trade.price).label('avg_price'),
                func.min(Trade.price).label('min_price'),
                func.max(Trade.price).label('max_price')
            ).where(Trade.symbol == symbol)
        ).first()
        
        return {
            'total_trades': result.total_trades,
            'total_volume': result.total_volume,
            'avg_price': result.avg_price,
            'min_price': result.min_price,
            'max_price': result.max_price
        }
    
    def get_ohlcv_with_indicators(self, symbol: str, 
                                window: int = 14) -> pd.DataFrame:
        """Get OHLCV data with pre-calculated indicators."""
        # Use window functions for efficient indicator calculation
        query = """
        WITH price_changes AS (
            SELECT 
                timestamp,
                close,
                close - LAG(close) OVER (ORDER BY timestamp) as price_change
            FROM ohlcv
            WHERE symbol = :symbol
        ),
        gains_losses AS (
            SELECT 
                timestamp,
                close,
                CASE WHEN price_change > 0 THEN price_change ELSE 0 END as gain,
                CASE WHEN price_change < 0 THEN -price_change ELSE 0 END as loss
            FROM price_changes
        )
        SELECT 
            o.*,
            AVG(close) OVER (
                ORDER BY timestamp 
                ROWS BETWEEN :window-1 PRECEDING AND CURRENT ROW
            ) as sma,
            AVG(gain) OVER (
                ORDER BY timestamp 
                ROWS BETWEEN :window-1 PRECEDING AND CURRENT ROW
            ) / NULLIF(
                AVG(loss) OVER (
                    ORDER BY timestamp 
                    ROWS BETWEEN :window-1 PRECEDING AND CURRENT ROW
                ), 0
            ) as rsi_ratio
        FROM ohlcv o
        WHERE symbol = :symbol
        ORDER BY timestamp
        """
        
        result = self._session.execute(query, {
            'symbol': symbol,
            'window': window
        })
        
        return pd.DataFrame(result.fetchall())
```

**Tests to create:**
- `tests/unit/database/test_queries.py`:
  - Test query performance with large datasets
  - Test indicator calculation accuracy
  - Test aggregation functions
  - Test query plan optimization

**Reasoning:**
Optimized queries improve system performance by reducing database load and minimizing data transfer.

### Step 23: Data Migration System

#### 23.1: Migration Framework Implementation

**Files to modify:**
- Create `abidance/database/migrations/env.py`
- Create `abidance/database/migrations/versions/`
- Update `abidance/database/alembic.ini`

**Code changes:**
```python
# abidance/database/migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from abidance.database.models import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Tests to create:**
- `tests/unit/database/test_migrations.py`:
  - Test migration creation
  - Test migration application
  - Test migration rollback
  - Test data integrity after migration

**Reasoning:**
A robust migration system ensures safe database schema evolution while preserving data integrity.

## Phase 6: Machine Learning Integration (Weeks 11-13)

### Step 24: Feature Engineering Framework

#### 24.1: Technical Feature Generation

**Files to modify:**
- Create `abidance/ml/features/technical.py`
- Create `abidance/ml/features/base.py`
- Create `abidance/ml/features/__init__.py`

**Code changes:**
```python
# abidance/ml/features/base.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Any

class FeatureGenerator(ABC):
    """Base class for feature generators."""
    
    @abstractmethod
    def generate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate features from input data."""
        pass
    
    @property
    @abstractmethod
    def feature_names(self) -> List[str]:
        """Get list of generated feature names."""
        pass

class TechnicalFeatureGenerator(FeatureGenerator):
    """Generator for technical analysis features."""
    
    def __init__(self, windows: List[int] = [5, 10, 20, 50]):
        self.windows = windows
        
    def generate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate technical indicators as features."""
        features = pd.DataFrame(index=data.index)
        
        # Price-based features
        for window in self.windows:
            # Moving averages
            features[f'sma_{window}'] = data['close'].rolling(window).mean()
            features[f'ema_{window}'] = data['close'].ewm(span=window).mean()
            
            # Volatility
            features[f'std_{window}'] = data['close'].rolling(window).std()
            
            # Momentum
            features[f'roc_{window}'] = data['close'].pct_change(window)
            
            # Volume features
            features[f'volume_sma_{window}'] = data['volume'].rolling(window).mean()
        
        # Price patterns
        features['upper_shadow'] = data['high'] - data[['open', 'close']].max(axis=1)
        features['lower_shadow'] = data[['open', 'close']].min(axis=1) - data['low']
        features['body_size'] = (data['close'] - data['open']).abs()
        
        return features.fillna(0)
    
    @property
    def feature_names(self) -> List[str]:
        """Get list of generated feature names."""
        names = []
        for window in self.windows:
            names.extend([
                f'sma_{window}',
                f'ema_{window}',
                f'std_{window}',
                f'roc_{window}',
                f'volume_sma_{window}'
            ])
        names.extend(['upper_shadow', 'lower_shadow', 'body_size'])
        return names
```

**Tests to create:**
- `tests/unit/ml/features/test_technical_features.py`:
  - Test feature generation with different window sizes
  - Test feature names consistency
  - Test handling of missing data
  - Test feature value ranges

**Reasoning:**
A robust feature engineering framework enables consistent and efficient generation of technical indicators for machine learning models.

### Step 25: Model Training Pipeline

#### 25.1: Training Pipeline Implementation

**Files to modify:**
- Create `abidance/ml/pipeline/trainer.py`
- Create `abidance/ml/pipeline/validation.py`
- Create `abidance/ml/pipeline/preprocessing.py`

**Code changes:**
```python
# abidance/ml/pipeline/trainer.py
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from .preprocessing import DataPreprocessor
from ..features.base import FeatureGenerator

class ModelTrainer:
    """Pipeline for training machine learning models."""
    
    def __init__(self, 
                 model: BaseEstimator,
                 feature_generator: FeatureGenerator,
                 n_splits: int = 5):
        self.model = model
        self.feature_generator = feature_generator
        self.preprocessor = DataPreprocessor()
        self.n_splits = n_splits
        self.scaler = StandardScaler()
        
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training."""
        # Generate features
        features = self.feature_generator.generate(data)
        
        # Prepare labels (next day returns)
        labels = data['close'].pct_change().shift(-1).fillna(0)
        labels = np.where(labels > 0, 1, 0)  # Binary classification
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        return scaled_features, labels
    
    def train(self, data: pd.DataFrame) -> Dict[str, float]:
        """Train model with time series cross-validation."""
        X, y = self.prepare_data(data)
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        metrics = []
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            score = self.model.score(X_val, y_val)
            metrics.append(score)
        
        return {
            'mean_cv_score': np.mean(metrics),
            'std_cv_score': np.std(metrics)
        }
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Generate predictions for new data."""
        features = self.feature_generator.generate(data)
        scaled_features = self.scaler.transform(features)
        return self.model.predict(scaled_features)
```

**Tests to create:**
- `tests/unit/ml/pipeline/test_trainer.py`:
  - Test parameter combination generation
  - Test strategy evaluation with different parameters
  - Test parallel optimization execution
  - Test result sorting and ranking

**Reasoning:**
A standardized training pipeline ensures consistent model training and evaluation across different strategies.

### Step 26: Model Selection Framework

#### 26.1: Model Selection Implementation

**Files to modify:**
- Create `abidance/ml/selection/evaluator.py`
- Create `abidance/ml/selection/metrics.py`

**Code changes:**
```python
# abidance/ml/selection/evaluator.py
from typing import Dict, Any, List, Type
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import precision_score, recall_score, f1_score
from ..pipeline.trainer import ModelTrainer
from ..features.base import FeatureGenerator

class ModelEvaluator:
    """Framework for evaluating and selecting models."""
    
    def __init__(self, 
                 models: List[BaseEstimator],
                 feature_generator: FeatureGenerator):
        self.models = models
        self.feature_generator = feature_generator
        self.results: Dict[str, Dict[str, float]] = {}
        
    def evaluate_models(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Evaluate all models on the dataset."""
        for model in self.models:
            trainer = ModelTrainer(
                model=model,
                feature_generator=self.feature_generator
            )
            
            # Train and evaluate
            cv_metrics = trainer.train(data)
            
            # Get predictions for final evaluation
            predictions = trainer.predict(data)
            y_true = data['close'].pct_change().shift(-1).fillna(0)
            y_true = np.where(y_true > 0, 1, 0)
            
            # Calculate metrics
            self.results[model.__class__.__name__] = {
                **cv_metrics,
                'precision': precision_score(y_true, predictions),
                'recall': recall_score(y_true, predictions),
                'f1': f1_score(y_true, predictions)
            }
        
        return self.results
    
    def select_best_model(self, metric: str = 'f1') -> BaseEstimator:
        """Select the best performing model."""
        if not self.results:
            raise ValueError("Must run evaluate_models first")
            
        best_score = -float('inf')
        best_model = None
        
        for model in self.models:
            score = self.results[model.__class__.__name__][metric]
            if score > best_score:
                best_score = score
                best_model = model
                
        return best_model
```

**Tests to create:**
- `tests/unit/ml/selection/test_evaluator.py`:
  - Test model evaluation
  - Test metric calculation
  - Test model selection
  - Test handling of different model types

**Reasoning:**
A model selection framework helps identify the best performing models for different market conditions.

### Step 27: Online Learning System

#### 27.1: Online Learning Implementation

**Files to modify:**
- Create `abidance/ml/online/learner.py`
- Create `abidance/ml/online/buffer.py`

**Code changes:**
```python
# abidance/ml/online/learner.py
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from collections import deque
from sklearn.base import BaseEstimator
from ..pipeline.trainer import ModelTrainer

class OnlineLearner:
    """System for continuous model updating."""
    
    def __init__(self, 
                 model: BaseEstimator,
                 trainer: ModelTrainer,
                 buffer_size: int = 1000,
                 update_threshold: float = 0.1):
        self.model = model
        self.trainer = trainer
        self.buffer = deque(maxlen=buffer_size)
        self.update_threshold = update_threshold
        self.performance_history: List[float] = []
        
    def update(self, new_data: pd.DataFrame) -> bool:
        """Update model with new data if necessary."""
        # Add new data to buffer
        self.buffer.extend(new_data.to_dict('records'))
        buffer_data = pd.DataFrame(list(self.buffer))
        
        # Check current performance
        current_performance = self._evaluate_performance(buffer_data)
        self.performance_history.append(current_performance)
        
        # Check if update is needed
        if self._should_update():
            # Retrain model
            self.trainer.train(buffer_data)
            return True
            
        return False
    
    def _evaluate_performance(self, data: pd.DataFrame) -> float:
        """Evaluate model performance on recent data."""
        predictions = self.trainer.predict(data)
        y_true = data['close'].pct_change().shift(-1).fillna(0)
        y_true = np.where(y_true > 0, 1, 0)
        
        return f1_score(y_true, predictions)
    
    def _should_update(self) -> bool:
        """Determine if model should be updated."""
        if len(self.performance_history) < 2:
            return False
            
        # Check for significant performance degradation
        recent_performance = np.mean(self.performance_history[-10:])
        baseline_performance = np.mean(self.performance_history[:-10])
        
        return (baseline_performance - recent_performance) > self.update_threshold
```

**Tests to create:**
- `tests/unit/ml/online/test_learner.py`:
  - Test buffer management
  - Test update triggering
  - Test performance tracking
  - Test model retraining

**Reasoning:**
Online learning enables models to adapt to changing market conditions and maintain performance over time.

## Phase 7: Web Dashboard and API (Weeks 13-15)

### Step 28: RESTful API Development

#### 28.1: API Framework Implementation

**Files to modify:**
- Create `abidance/api/app.py`
- Create `abidance/api/routes/`
- Create `abidance/api/middleware/`

**Code changes:**
```python
# abidance/api/app.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from .database import get_db
from .models import TradeResponse, StrategyResponse
from ..core.domain import SignalType

app = FastAPI(title="Abidance Trading Bot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/strategies", response_model=List[StrategyResponse])
async def list_strategies(db: Session = Depends(get_db)):
    """List all available trading strategies."""
    try:
        strategies = db.query(Strategy).all()
        return [StrategyResponse.from_orm(s) for s in strategies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trades", response_model=List[TradeResponse])
async def list_trades(
    symbol: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """List trades with optional filtering."""
    query = db.query(Trade)
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    if start_date:
        query = query.filter(Trade.timestamp >= start_date)
    if end_date:
        query = query.filter(Trade.timestamp <= end_date)
    
    trades = query.all()
    return [TradeResponse.from_orm(t) for t in trades]
```

**Tests to create:**
- `tests/unit/api/test_routes.py`:
  - Test strategy listing endpoint
  - Test trade listing with filters
  - Test error handling
  - Test response models

**Reasoning:**
A RESTful API enables external systems to interact with the trading bot and access its data.

### Step 29: Real-time WebSocket Integration

#### 29.1: WebSocket Server Implementation

**Files to modify:**
- Create `abidance/api/websocket.py`
- Create `abidance/api/events.py`

**Code changes:**
```python
# abidance/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any
import json
from datetime import datetime
from ..core.events import EventBus, Event

class WebSocketManager:
    """Manager for WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.event_bus = EventBus()
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Handle new WebSocket connection."""
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        
    async def disconnect(self, websocket: WebSocket, client_id: str):
        """Handle WebSocket disconnection."""
        self.active_connections[client_id].remove(websocket)
        if not self.active_connections[client_id]:
            del self.active_connections[client_id]
            
    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        message = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    continue

# Register WebSocket routes
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    manager = WebSocketManager()
    try:
        await manager.connect(websocket, client_id)
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        await manager.disconnect(websocket, client_id)
```

**Tests to create:**
- `tests/unit/api/test_websocket.py`:
  - Test connection management
  - Test message broadcasting
  - Test client disconnection handling
  - Test event subscription

**Reasoning:**
WebSocket support enables real-time updates and notifications for the web dashboard.

### Step 30: Dashboard Frontend Development

#### 30.1: React Dashboard Implementation

**Files to modify:**
- Create `frontend/src/components/`
- Create `frontend/src/pages/`
- Create `frontend/src/api/`

**Code changes:**
```typescript
// frontend/src/components/TradingChart.tsx
import React from 'react';
import { Line } from 'react-chartjs-2';
import { ChartData, ChartOptions } from 'chart.js';

interface TradingChartProps {
    data: ChartData;
    options?: ChartOptions;
}

export const TradingChart: React.FC<TradingChartProps> = ({ data, options }) => {
    const defaultOptions: ChartOptions = {
        responsive: true,
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'day'
                }
            },
            y: {
                type: 'linear',
                position: 'right'
            }
        },
        plugins: {
            legend: {
                position: 'top'
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        }
    };
    
    return (
        <div className="trading-chart">
            <Line data={data} options={options || defaultOptions} />
        </div>
    );
};

// frontend/src/pages/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { TradingChart } from '../components/TradingChart';
import { fetchTrades, subscribeToUpdates } from '../api/trading';

export const Dashboard: React.FC = () => {
    const [trades, setTrades] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    
    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await fetchTrades();
                setTrades(data);
            } catch (error) {
                console.error('Failed to fetch trades:', error);
            } finally {
                setIsLoading(false);
            }
        };
        
        loadData();
        
        // Subscribe to real-time updates
        const unsubscribe = subscribeToUpdates((update) => {
            setTrades(current => [...current, update]);
        });
        
        return () => unsubscribe();
    }, []);
    
    if (isLoading) {
        return <div>Loading...</div>;
    }
    
    return (
        <div className="dashboard">
            <h1>Trading Dashboard</h1>
            <TradingChart 
                data={transformTradesForChart(trades)}
            />
            <TradeList trades={trades} />
        </div>
    );
};
```

**Tests to create:**
- `tests/frontend/components/test_trading_chart.tsx`:
  - Test chart rendering
  - Test data updates
  - Test responsive behavior
- `tests/frontend/pages/test_dashboard.tsx`:
  - Test data loading
  - Test WebSocket updates
  - Test error handling

**Reasoning:**
A modern React-based dashboard provides users with real-time insights into trading activities.

### Step 31: Authentication and Authorization

#### 31.1: Security Implementation

**Files to modify:**
- Create `abidance/api/auth/`
- Create `abidance/api/middleware/auth.py`

**Code changes:**
```python
# abidance/api/auth/jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from ..models import User

# Security configuration
SECRET_KEY = "your-secret-key"  # Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = get_user(username)  # Implement user retrieval
    if user is None:
        raise credentials_exception
    return user
```

**Tests to create:**
- `tests/unit/api/auth/test_jwt.py`:
  - Test token generation
  - Test password hashing
  - Test token validation
  - Test user authentication

**Reasoning:**
Robust authentication and authorization ensure secure access to the trading bot's features.

## Phase 8: Risk Management and Portfolio Optimization (Weeks 15-17)

### Step 32: Risk Assessment Framework

#### 32.1: Risk Metrics Implementation

**Files to modify:**
- Create `abidance/risk/metrics.py`
- Create `abidance/risk/calculator.py`
- Create `abidance/risk/limits.py`

**Code changes:**
```python
# abidance/risk/metrics.py
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
from ..core.domain import Trade, Position
from ..core.exceptions import RiskLimitExceeded

@dataclass
class RiskMetrics:
    """Container for risk metrics."""
    sharpe_ratio: float
    max_drawdown: float
    value_at_risk: float
    volatility: float
    beta: float
    correlation: float

class RiskCalculator:
    """Calculate various risk metrics for portfolio analysis."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        
    def calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """Calculate Sharpe ratio for given returns."""
        excess_returns = returns - self.risk_free_rate
        if len(excess_returns) < 2:
            return 0.0
        return np.mean(excess_returns) / np.std(excess_returns, ddof=1)
        
    def calculate_max_drawdown(self, equity_curve: np.ndarray) -> float:
        """Calculate maximum drawdown from equity curve."""
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak
        return np.min(drawdown)
        
    def calculate_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Calculate Value at Risk."""
        return np.percentile(returns, (1 - confidence) * 100)
        
    def calculate_volatility(self, returns: np.ndarray) -> float:
        """Calculate annualized volatility."""
        return np.std(returns, ddof=1) * np.sqrt(252)  # Annualize daily volatility

# abidance/risk/limits.py
class RiskLimits:
    """Define and enforce risk limits."""
    
    def __init__(
        self,
        max_position_size: float,
        max_drawdown: float,
        max_leverage: float,
        max_correlation: float
    ):
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.max_leverage = max_leverage
        self.max_correlation = max_correlation
        
    def check_position_size(self, position_size: float, account_value: float) -> bool:
        """Check if position size is within limits."""
        relative_size = position_size / account_value
        return relative_size <= self.max_position_size
        
    def check_drawdown(self, current_drawdown: float) -> bool:
        """Check if drawdown is within limits."""
        return current_drawdown <= self.max_drawdown
        
    def check_leverage(self, current_leverage: float) -> bool:
        """Check if leverage is within limits."""
        return current_leverage <= self.max_leverage
```

**Tests to create:**
- `tests/unit/risk/test_metrics.py`:
  - Test Sharpe ratio calculation
  - Test maximum drawdown calculation
  - Test VaR calculation
  - Test volatility calculation
- `tests/unit/risk/test_limits.py`:
  - Test position size limits
  - Test drawdown limits
  - Test leverage limits
  - Test correlation limits

**Reasoning:**
A comprehensive risk assessment framework is crucial for protecting capital and ensuring sustainable trading performance.

### Step 33: Portfolio Optimization

#### 33.1: Portfolio Optimizer Implementation

**Files to modify:**
- Create `abidance/portfolio/optimizer.py`
- Create `abidance/portfolio/allocation.py`
- Create `abidance/portfolio/constraints.py`

**Code changes:**
```python
# abidance/portfolio/optimizer.py
from typing import List, Dict, Optional
import numpy as np
from scipy.optimize import minimize
from dataclasses import dataclass
from ..risk.metrics import RiskCalculator

@dataclass
class OptimizationResult:
    """Container for optimization results."""
    weights: np.ndarray
    expected_return: float
    expected_risk: float
    sharpe_ratio: float

class PortfolioOptimizer:
    """Optimize portfolio allocation using Modern Portfolio Theory."""
    
    def __init__(self, risk_calculator: RiskCalculator):
        self.risk_calculator = risk_calculator
        
    def optimize_sharpe_ratio(
        self,
        returns: np.ndarray,
        constraints: List[Dict],
        initial_weights: Optional[np.ndarray] = None
    ) -> OptimizationResult:
        """Optimize portfolio weights for maximum Sharpe ratio."""
        n_assets = returns.shape[1]
        if initial_weights is None:
            initial_weights = np.ones(n_assets) / n_assets
            
        def objective(weights):
            portfolio_returns = np.sum(returns.mean(axis=0) * weights)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(np.cov(returns.T), weights)))
            sharpe = (portfolio_returns - self.risk_calculator.risk_free_rate) / portfolio_risk
            return -sharpe  # Minimize negative Sharpe ratio
            
        # Constraints
        constraints.append({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})  # Weights sum to 1
        bounds = tuple((0, 1) for _ in range(n_assets))  # Long-only constraints
        
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        portfolio_return = np.sum(returns.mean(axis=0) * optimal_weights)
        portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(np.cov(returns.T), optimal_weights)))
        sharpe = (portfolio_return - self.risk_calculator.risk_free_rate) / portfolio_risk
        
        return OptimizationResult(
            weights=optimal_weights,
            expected_return=portfolio_return,
            expected_risk=portfolio_risk,
            sharpe_ratio=sharpe
        )

# abidance/portfolio/allocation.py
class PortfolioAllocator:
    """Implement portfolio allocation strategies."""
    
    def __init__(self, optimizer: PortfolioOptimizer):
        self.optimizer = optimizer
        
    def allocate_equal_weight(self, n_assets: int) -> np.ndarray:
        """Implement equal-weight allocation strategy."""
        return np.ones(n_assets) / n_assets
        
    def allocate_risk_parity(self, returns: np.ndarray) -> np.ndarray:
        """Implement risk parity allocation strategy."""
        vol = np.std(returns, axis=0)
        inv_vol = 1.0 / vol
        weights = inv_vol / np.sum(inv_vol)
        return weights
        
    def allocate_minimum_variance(self, returns: np.ndarray) -> np.ndarray:
        """Implement minimum variance allocation strategy."""
        n_assets = returns.shape[1]
        def objective(weights):
            return np.sqrt(np.dot(weights.T, np.dot(np.cov(returns.T), weights)))
            
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}
        ]
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        result = minimize(
            objective,
            np.ones(n_assets) / n_assets,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x
```

**Tests to create:**
- `tests/unit/portfolio/test_optimizer.py`:
  - Test Sharpe ratio optimization
  - Test constraint handling
  - Test optimization convergence
  - Test weight bounds
- `tests/unit/portfolio/test_allocation.py`:
  - Test equal weight allocation
  - Test risk parity allocation
  - Test minimum variance allocation
  - Test allocation constraints

**Reasoning:**
Portfolio optimization ensures efficient capital allocation across different trading strategies and assets.

### Step 34: Dynamic Risk Adjustment

#### 34.1: Risk Manager Implementation

**Files to modify:**
- Create `abidance/risk/manager.py`
- Create `abidance/risk/adjustments.py`

**Code changes:**
```python
# abidance/risk/manager.py
from typing import Dict, List, Optional
import numpy as np
from ..core.domain import Position, Trade
from .metrics import RiskCalculator
from .limits import RiskLimits

class DynamicRiskManager:
    """Manage and adjust risk parameters dynamically."""
    
    def __init__(
        self,
        risk_calculator: RiskCalculator,
        risk_limits: RiskLimits,
        adjustment_threshold: float = 0.1
    ):
        self.risk_calculator = risk_calculator
        self.risk_limits = risk_limits
        self.adjustment_threshold = adjustment_threshold
        
    def calculate_position_adjustment(
        self,
        position: Position,
        market_volatility: float,
        account_value: float
    ) -> Optional[float]:
        """Calculate position size adjustment based on market conditions."""
        current_risk = self.calculate_position_risk(position, market_volatility)
        
        if current_risk > self.risk_limits.max_position_size:
            target_size = (self.risk_limits.max_position_size * account_value) / market_volatility
            return target_size - position.size
            
        return None
        
    def adjust_strategy_weights(
        self,
        strategy_returns: Dict[str, np.ndarray],
        current_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """Adjust strategy allocation weights based on performance."""
        returns_array = np.array([returns for returns in strategy_returns.values()])
        correlation_matrix = np.corrcoef(returns_array)
        
        # Reduce weights of highly correlated strategies
        new_weights = current_weights.copy()
        for i, strategy1 in enumerate(strategy_returns.keys()):
            for j, strategy2 in enumerate(strategy_returns.keys()):
                if i != j and correlation_matrix[i, j] > self.risk_limits.max_correlation:
                    # Reduce weight of worse performing strategy
                    worse_strategy = strategy1 if np.mean(strategy_returns[strategy1]) < np.mean(strategy_returns[strategy2]) else strategy2
                    new_weights[worse_strategy] *= (1 - self.adjustment_threshold)
                    
        # Normalize weights
        total_weight = sum(new_weights.values())
        return {k: v / total_weight for k, v in new_weights.items()}

# abidance/risk/adjustments.py
class RiskAdjuster:
    """Implement risk adjustment strategies."""
    
    def __init__(self, risk_calculator: RiskCalculator):
        self.risk_calculator = risk_calculator
        
    def adjust_position_size(
        self,
        base_size: float,
        volatility: float,
        market_impact: float
    ) -> float:
        """Adjust position size based on market conditions."""
        volatility_factor = 1.0 / (1.0 + volatility)
        impact_factor = 1.0 / (1.0 + market_impact)
        return base_size * volatility_factor * impact_factor
        
    def calculate_kelly_fraction(
        self,
        win_rate: float,
        win_loss_ratio: float
    ) -> float:
        """Calculate Kelly Criterion fraction."""
        q = 1.0 - win_rate
        return (win_rate * win_loss_ratio - q) / win_loss_ratio
```

**Tests to create:**
- `tests/unit/risk/test_manager.py`:
  - Test position adjustment calculation
  - Test strategy weight adjustment
  - Test correlation-based adjustments
  - Test risk limit enforcement
- `tests/unit/risk/test_adjustments.py`:
  - Test position size adjustment
  - Test Kelly Criterion calculation
  - Test volatility-based adjustments
  - Test market impact handling

**Reasoning:**
Dynamic risk adjustment ensures the trading system adapts to changing market conditions while maintaining risk control.

### Step 35: Performance Attribution

#### 35.1: Attribution Analysis Implementation

**Files to modify:**
- Create `abidance/analysis/attribution.py`
- Create `abidance/analysis/decomposition.py`

**Code changes:**
```python
# abidance/analysis/attribution.py
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from ..core.domain import Trade
from ..risk.metrics import RiskMetrics

class PerformanceAttribution:
    """Analyze and attribute trading performance."""
    
    def __init__(self, risk_metrics: RiskMetrics):
        self.risk_metrics = risk_metrics
        
    def calculate_strategy_attribution(
        self,
        strategy_returns: Dict[str, np.ndarray],
        weights: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate performance attribution by strategy."""
        attribution = {}
        total_return = 0.0
        
        for strategy_name, returns in strategy_returns.items():
            strategy_weight = weights[strategy_name]
            strategy_return = np.mean(returns) * strategy_weight
            total_return += strategy_return
            
            attribution[strategy_name] = {
                'weight': strategy_weight,
                'return': strategy_return,
                'volatility': np.std(returns),
                'sharpe': self.risk_metrics.calculate_sharpe_ratio(returns)
            }
            
        # Calculate contribution percentages
        for strategy in attribution:
            attribution[strategy]['contribution'] = (
                attribution[strategy]['return'] / total_return
                if total_return != 0 else 0.0
            )
            
        return attribution

# abidance/analysis/decomposition.py
class ReturnDecomposition:
    """Decompose returns into various components."""
    
    def decompose_returns(
        self,
        returns: np.ndarray,
        market_returns: np.ndarray
    ) -> Dict[str, float]:
        """Decompose returns into alpha and beta components."""
        # Calculate beta
        covariance = np.cov(returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance
        
        # Calculate alpha
        alpha = np.mean(returns) - beta * np.mean(market_returns)
        
        return {
            'alpha': alpha,
            'beta': beta,
            'systematic_return': beta * np.mean(market_returns),
            'specific_return': alpha
        }
        
    def analyze_trading_costs(
        self,
        trades: List[Trade]
    ) -> Dict[str, float]:
        """Analyze impact of trading costs on performance."""
        total_volume = sum(trade.volume for trade in trades)
        total_cost = sum(trade.commission + trade.slippage for trade in trades)
        
        return {
            'total_cost': total_cost,
            'cost_per_trade': total_cost / len(trades) if trades else 0.0,
            'cost_per_volume': total_cost / total_volume if total_volume > 0 else 0.0
        }
```

**Tests to create:**
- `tests/unit/analysis/test_attribution.py`:
  - Test strategy attribution calculation
  - Test contribution analysis
  - Test performance decomposition
  - Test weight impact analysis
- `tests/unit/analysis/test_decomposition.py`:
  - Test alpha/beta decomposition
  - Test trading cost analysis
  - Test return component separation
  - Test cost metrics calculation

**Reasoning:**
Performance attribution helps understand the sources of returns and risks, enabling better strategy optimization.

## Phase 9: Deployment and DevOps (Weeks 17-19)

### Step 36: Containerization

#### 36.1: Docker Implementation

**Files to modify:**
- Create `Dockerfile`
- Create `docker-compose.yml`
- Create `deployment/docker/`

**Code changes:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -s /bin/bash trader
RUN chown -R trader:trader /app
USER trader

# Run the application
CMD ["python", "-m", "abidance.main"]

# docker-compose.yml
version: '3.8'

services:
  trading_bot:
    build: .
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    networks:
      - trading_network

  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: abidance
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - trading_network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - trading_network

networks:
  trading_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

**Tests to create:**
- `tests/integration/docker/test_container.py`:
  - Test container build
  - Test service dependencies
  - Test volume mounts
  - Test network connectivity

**Reasoning:**
Containerization ensures consistent deployment across different environments and simplifies scaling.

### Step 37: CI/CD Pipeline

#### 37.1: GitHub Actions Implementation

**Files to modify:**
- Create `.github/workflows/ci.yml`
- Create `.github/workflows/cd.yml`
- Create `scripts/deploy.sh`

**Code changes:**
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        
    - name: Run tests
      run: |
        pytest tests/ --cov=abidance --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install black isort mypy ruff
        
    - name: Run linters
      run: |
        black --check .
        isort --check-only .
        mypy abidance
        ruff check .

# .github/workflows/cd.yml
name: CD Pipeline

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ secrets.AWS_REGION }}
        
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
      
    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: abidance
        IMAGE_TAG: ${{ github.ref_name }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster abidance --service trading-bot --force-new-deployment
```

**Tests to create:**
- `tests/integration/ci/test_pipeline.py`:
  - Test build process
  - Test test execution
  - Test linting checks
  - Test deployment steps

**Reasoning:**
Automated CI/CD pipelines ensure code quality and streamline the deployment process.

### Step 38: Infrastructure as Code

#### 38.1: Terraform Implementation

**Files to modify:**
- Create `terraform/`
- Create `terraform/main.tf`
- Create `terraform/variables.tf`

**Code changes:**
```hcl
# terraform/main.tf
provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "abidance-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
  single_nat_gateway = true
}

module "ecs" {
  source = "terraform-aws-modules/ecs/aws"
  
  cluster_name = "abidance"
  
  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = "/aws/ecs/abidance"
      }
    }
  }
  
  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = 100
      }
    }
  }
}

resource "aws_ecr_repository" "abidance" {
  name = "abidance"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}

# terraform/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "abidance"
}
```

**Tests to create:**
- `tests/integration/terraform/test_infrastructure.py`:
  - Test VPC creation
  - Test ECS cluster setup
  - Test ECR repository
  - Test security groups

**Reasoning:**
Infrastructure as Code enables version-controlled, reproducible infrastructure deployment.

### Step 39: Monitoring and Logging

#### 39.1: Observability Implementation

**Files to modify:**
- Create `abidance/monitoring/`
- Create `abidance/monitoring/metrics.py`
- Create `abidance/monitoring/logging.py`

**Code changes:**
```python
# abidance/monitoring/metrics.py
from dataclasses import dataclass
from typing import Dict, List
import time
import prometheus_client as prom
from prometheus_client import Counter, Gauge, Histogram

@dataclass
class TradingMetrics:
    """Trading-specific metrics."""
    trades_executed: Counter = prom.Counter(
        'trades_executed_total',
        'Total number of trades executed',
        ['strategy', 'symbol']
    )
    position_value: Gauge = prom.Gauge(
        'position_value',
        'Current position value',
        ['symbol']
    )
    trade_latency: Histogram = prom.Histogram(
        'trade_execution_latency_seconds',
        'Time taken to execute trades',
        ['strategy']
    )
    
class MetricsCollector:
    """Collect and export trading metrics."""
    
    def __init__(self):
        self.metrics = TradingMetrics()
        
    def record_trade(self, strategy: str, symbol: str):
        """Record trade execution."""
        self.metrics.trades_executed.labels(strategy=strategy, symbol=symbol).inc()
        
    def update_position(self, symbol: str, value: float):
        """Update position value."""
        self.metrics.position_value.labels(symbol=symbol).set(value)
        
    @contextmanager
    def measure_latency(self, strategy: str):
        """Measure trade execution latency."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.metrics.trade_latency.labels(strategy=strategy).observe(duration)

# abidance/monitoring/logging.py
import logging
import json
from typing import Any, Dict
from datetime import datetime

class StructuredLogger:
    """Structured logging with JSON format."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Add JSON handler
        handler = logging.StreamHandler()
        handler.setFormatter(self._json_formatter())
        self.logger.addHandler(handler)
        
    def _json_formatter(self):
        """Create JSON formatter."""
        return logging.Formatter(
            lambda x: json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'level': x.levelname,
                'message': x.getMessage(),
                'module': x.module,
                'function': x.funcName,
                **getattr(x, 'extra', {})
            })
        )
        
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(message, extra=kwargs)
        
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message with context."""
        extra = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            **kwargs
        } if error else kwargs
        self.logger.error(message, extra=extra)
        
    def trade_event(
        self,
        event_type: str,
        strategy: str,
        symbol: str,
        quantity: float,
        price: float,
        **kwargs
    ):
        """Log trade-related event."""
        self.info(
            f"Trade event: {event_type}",
            event_type=event_type,
            strategy=strategy,
            symbol=symbol,
            quantity=quantity,
            price=price,
            **kwargs
        )
```

**Tests to create:**
- `tests/unit/monitoring/test_metrics.py`:
  - Test metric recording
  - Test latency measurement
  - Test metric export
  - Test label handling
- `tests/unit/monitoring/test_logging.py`:
  - Test JSON formatting
  - Test context inclusion
  - Test error logging
  - Test trade event logging

**Reasoning:**
Comprehensive monitoring and logging enable real-time system observability and troubleshooting.

## Phase 10: Documentation and User Guides (Weeks 19-21)

### Step 40: API Documentation

#### 40.1: API Reference Implementation

**Files to modify:**
- Create `docs/api/`
- Create `abidance/api/docs.py`
- Update `abidance/api/app.py`

**Code changes:**
```python
# abidance/api/docs.py
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from typing import Dict, Any

def custom_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema for documentation."""
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="Abidance Trading Bot API",
        version="1.0.0",
        description="API for the Abidance Crypto Trading Bot system",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    # Add response examples
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method.lower() == "get" and "responses" in openapi_schema["paths"][path][method]:
                if "200" in openapi_schema["paths"][path][method]["responses"]:
                    openapi_schema["paths"][path][method]["responses"]["200"]["content"] = {
                        "application/json": {
                            "examples": {
                                "Example response": {
                                    "value": generate_example_for_path(path)
                                }
                            }
                        }
                    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def generate_example_for_path(path: str) -> Dict[str, Any]:
    """Generate example response for a specific path."""
    if "/strategies" in path:
        return [
            {
                "id": "1",
                "name": "MovingAverageCrossover",
                "description": "Simple moving average crossover strategy",
                "parameters": {"fast_period": 10, "slow_period": 50},
                "active": True
            }
        ]
    elif "/trades" in path:
        return [
            {
                "id": "12345",
                "strategy_id": "1",
                "symbol": "BTC-USD",
                "side": "buy",
                "quantity": 0.1,
                "price": 50000.0,
                "timestamp": "2023-06-15T10:30:00Z",
                "status": "filled"
            }
        ]
    # Add more path-specific examples here
    return {"example": "data"}

# Update in abidance/api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .docs import custom_openapi_schema

app = FastAPI(title="Abidance Trading Bot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use custom OpenAPI schema
app.openapi = lambda: custom_openapi_schema(app)

# Add Swagger UI and ReDoc mount points
@app.get("/docs", include_in_schema=False)
async def get_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Abidance API Documentation"
    )

@app.get("/redoc", include_in_schema=False)
async def get_redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Abidance API Documentation"
    )
```

**Tests to create:**
- `tests/unit/api/test_docs.py`:
  - Test OpenAPI schema generation
  - Test security scheme inclusion
  - Test example generation
  - Test documentation endpoints

**Reasoning:**
Comprehensive API documentation ensures developers can effectively integrate with the trading bot.

### Step 41: User Guides

#### 41.1: User Documentation Implementation

**Files to modify:**
- Create `docs/user/`
- Create `docs/user/getting_started.md`
- Create `docs/user/configuration.md`
- Create `docs/user/strategies.md`

**Code changes:**
```markdown
<!-- docs/user/getting_started.md -->
# Getting Started with Abidance Trading Bot

## Introduction

Abidance is a powerful, extensible crypto trading bot designed for algorithmic trading across multiple exchanges. This guide will help you set up and start trading with Abidance.

## Installation

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (recommended)
- PostgreSQL database (if not using Docker)
- Redis (if not using Docker)

### Docker Installation (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/abidance.git
   cd abidance
   ```

2. Create a `.env` file with your configuration:
   ```
   EXCHANGE_API_KEY=your_api_key
   EXCHANGE_SECRET=your_secret
   DB_USER=postgres
   DB_PASSWORD=your_password
   RISK_MAX_DRAWDOWN=0.05
   ```

3. Start the containers:
   ```bash
   docker-compose up -d
   ```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/abidance.git
   cd abidance
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment variables or `.env` file.

5. Run database migrations:
   ```bash
   python -m abidance.database.migrations
   ```

6. Start the trading bot:
   ```bash
   python -m abidance.main
   ```

## Quick Start

1. Configure your trading parameters in the web dashboard or config file.
2. Select your desired trading strategies.
3. Set your risk limits.
4. Start trading!

## Next Steps

- Read the [Configuration Guide](configuration.md) for detailed configuration options.
- Explore [Trading Strategies](strategies.md) to understand available strategies.
- Learn how to [Monitor Your Bot](monitoring.md) using the dashboard.

<!-- docs/user/configuration.md -->
# Configuration Guide

## Core Configuration

The trading bot can be configured using environment variables, a `.env` file, or the web dashboard. Below are the key configuration parameters:

### Exchange Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `EXCHANGE_NAME` | Name of the exchange (e.g., binance, coinbase) | None (Required) |
| `EXCHANGE_API_KEY` | API key for the exchange | None (Required) |
| `EXCHANGE_SECRET` | API secret for the exchange | None (Required) |
| `EXCHANGE_TESTNET` | Use exchange testnet | False |

### Risk Management

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RISK_MAX_POSITION_SIZE` | Maximum position size as % of portfolio | 0.05 (5%) |
| `RISK_MAX_DRAWDOWN` | Maximum allowed drawdown | 0.10 (10%) |
| `RISK_MAX_LEVERAGE` | Maximum allowed leverage | 1.0 (no leverage) |

### Database Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | abidance |
| `DB_USER` | Database username | postgres |
| `DB_PASSWORD` | Database password | None |

## Strategy Configuration

Each strategy can be configured with specific parameters. Here's an example configuration for the Moving Average Crossover strategy:

```json
{
  "strategy": "MovingAverageCrossover",
  "parameters": {
    "fast_period": 10,
    "slow_period": 30,
    "symbol": "BTC-USD",
    "timeframe": "1h"
  },
  "risk": {
    "position_size": 0.02,
    "stop_loss_pct": 0.05
  }
}
```

<!-- docs/user/strategies.md -->
# Trading Strategies

## Available Strategies

### Moving Average Crossover

A strategy that generates buy signals when a faster moving average crosses above a slower moving average, and sell signals when the faster moving average crosses below the slower moving average.

**Parameters:**
- `fast_period`: Period for the fast moving average
- `slow_period`: Period for the slow moving average
- `symbol`: Trading pair symbol
- `timeframe`: Candle timeframe

**Example:**
```json
{
  "strategy": "MovingAverageCrossover",
  "parameters": {
    "fast_period": 10,
    "slow_period": 30,
    "symbol": "BTC-USD",
    "timeframe": "1h"
  }
}
```

### RSI Mean Reversion

A strategy that buys when RSI is oversold and sells when RSI is overbought.

**Parameters:**
- `rsi_period`: Period for RSI calculation
- `oversold`: RSI threshold for oversold condition
- `overbought`: RSI threshold for overbought condition
- `symbol`: Trading pair symbol
- `timeframe`: Candle timeframe

**Example:**
```json
{
  "strategy": "RSIMeanReversion",
  "parameters": {
    "rsi_period": 14,
    "oversold": 30,
    "overbought": 70,
    "symbol": "ETH-USD",
    "timeframe": "4h"
  }
}
```

## Creating Custom Strategies

You can create custom strategies by extending the `Strategy` base class:

```python
from abidance.strategy.base import Strategy
from abidance.core.domain import Signal, SignalType

class MyCustomStrategy(Strategy):
    def __init__(self, parameters: Dict[str, Any]):
        super().__init__(parameters)
        # Initialize your strategy-specific parameters
        
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        # Implement your signal generation logic
        signals = []
        # ...
        return signals
```
```

**Tests to create:**
- `tests/unit/docs/test_user_guides.py`:
  - Test documentation completeness
  - Test code examples
  - Test configuration examples
  - Test markdown format

**Reasoning:**
Comprehensive user guides enable users to quickly set up and effectively use the trading bot.

### Step 42: Developer Documentation

#### 42.1: Technical Documentation Implementation

**Files to modify:**
- Create `docs/developers/`
- Create `docs/developers/architecture.md`
- Create `docs/developers/contributing.md`
- Create `docs/developers/testing.md`

**Code changes:**
```markdown
<!-- docs/developers/architecture.md -->
# System Architecture

## Overview

Abidance Trading Bot follows a clean architecture approach with three main layers:

1. **Domain Layer**: Core business logic and entities
2. **Application Layer**: Use cases and services
3. **Infrastructure Layer**: External integrations

![Architecture Diagram](../images/architecture.png)

## Domain Layer

The domain layer contains the core business entities and logic:

- **Core Entities**: `Trade`, `Position`, `Order`, `Signal`
- **Value Objects**: `Symbol`, `Price`, `Quantity`
- **Domain Services**: `StrategyEvaluator`, `RiskCalculator`

This layer is independent of external frameworks and has no dependencies on the application or infrastructure layers.

## Application Layer

The application layer contains use cases and services that orchestrate the domain layer:

- **Services**: `TradingService`, `PortfolioService`, `StrategyService`
- **Use Cases**: `ExecuteTradeUseCase`, `GenerateSignalsUseCase`
- **DTOs**: Data Transfer Objects for input/output

## Infrastructure Layer

The infrastructure layer contains implementations of interfaces defined in the domain and application layers:

- **Repositories**: Database access implementations
- **Adapters**: Exchange API clients, external services
- **Frameworks**: FastAPI, SQLAlchemy, etc.

## Key Components

### Strategy System

The strategy system is designed for flexibility and extensibility:

```
abidance/strategy/
├── base.py           # Base Strategy class
├── factory.py        # Strategy Factory
├── indicators/       # Technical indicators
│   ├── trend.py      # Trend indicators
│   └── momentum.py   # Momentum indicators
└── strategies/       # Strategy implementations
    ├── moving_average.py
    └── rsi.py
```

Strategies are registered with the `StrategyFactory` and can be instantiated dynamically based on configuration.

### Risk Management

The risk management system enforces trading limits and calculates risk metrics:

```
abidance/risk/
├── metrics.py        # Risk metrics calculation
├── limits.py         # Risk limits definition
└── manager.py        # Dynamic risk management
```

### Event System

The event system provides a publish-subscribe mechanism for internal communication:

```
abidance/core/events/
├── bus.py            # Event bus
├── handlers.py       # Event handlers
└── events.py         # Event definitions
```

Events include `SignalGenerated`, `OrderExecuted`, `TradeCompleted`, etc.

<!-- docs/developers/contributing.md -->
# Contributing Guide

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/abidance.git
   cd abidance
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding standards

3. Run tests:
   ```bash
   pytest
   ```

4. Run linters:
   ```bash
   black .
   isort .
   mypy abidance
   ruff check .
   ```

5. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a Pull Request on GitHub

## Coding Standards

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write docstrings for all classes and functions
- Maintain test coverage for new code

## Pull Request Guidelines

- Include a clear description of the changes
- Link to any relevant issues
- Ensure all tests pass
- Keep changes focused on a single issue/feature

<!-- docs/developers/testing.md -->
# Testing Guide

## Test Structure

Tests are organized in the following structure:

```
tests/
├── unit/              # Unit tests for isolated components
├── integration/       # Tests for component interactions
├── performance/       # Performance benchmarks
└── e2e/               # End-to-end tests
```

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test categories:
```bash
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

Run with coverage:
```bash
pytest --cov=abidance
```

Generate HTML coverage report:
```bash
pytest --cov=abidance --cov-report=html
```

## Writing Tests

### Unit Tests

Unit tests should focus on testing a single component in isolation:

```python
def test_moving_average_strategy_signals():
    # Arrange
    data = create_test_data()
    strategy = MovingAverageStrategy({"fast_period": 10, "slow_period": 30})
    
    # Act
    signals = strategy.generate_signals(data)
    
    # Assert
    assert len(signals) > 0
    assert signals[0].type in [SignalType.BUY, SignalType.SELL]
```

### Integration Tests

Integration tests verify that components work together correctly:

```python
def test_strategy_execution_workflow():
    # Arrange
    strategy = StrategyFactory.create("MovingAverageCrossover", {
        "fast_period": 10, 
        "slow_period": 30
    })
    trading_service = TradingService(MockExchange())
    
    # Act
    signals = strategy.generate_signals(get_test_data())
    results = trading_service.execute_signals(signals)
    
    # Assert
    assert len(results) == len(signals)
    assert all(r.status == "executed" for r in results)
```

### Mocking

Use pytest's monkeypatch or unittest.mock for mocking dependencies:

```python
def test_exchange_client_error_handling(monkeypatch):
    # Arrange
    def mock_api_call(*args, **kwargs):
        raise ConnectionError("API unavailable")
    
    monkeypatch.setattr(ExchangeClient, "get_ticker", mock_api_call)
    client = ExchangeClient("test_key", "test_secret")
    
    # Act & Assert
    with pytest.raises(ExchangeConnectionError):
        client.get_ticker("BTC-USD")
```
```

**Tests to create:**
- `tests/unit/docs/test_developer_docs.py`:
  - Test architecture documentation
  - Test code examples
  - Test contributing guidelines
  - Test testing documentation

**Reasoning:**
Comprehensive developer documentation enables contributors to understand the system architecture and contribute effectively.

### Step 43: Documentation Build Pipeline

#### 43.1: Documentation Generation Implementation

**Files to modify:**
- Create `docs/mkdocs.yml`
- Create `docs/requirements.txt`
- Create `.github/workflows/docs.yml`

**Code changes:**
```yaml
# docs/mkdocs.yml
site_name: Abidance Trading Bot Documentation
site_description: Documentation for the Abidance Crypto Trading Bot
site_author: Abidance Team
repo_url: https://github.com/your-username/abidance

theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate
    - search.suggest
    - search.highlight

markdown_extensions:
  - admonition
  - codehilite
  - toc:
      permalink: true
  - pymdownx.superfences
  - pymdownx.tabbed
  - pymdownx.details

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          selection:
            docstring_style: google
          rendering:
            show_source: true
  - git-revision-date-localized

nav:
  - Home: index.md
  - User Guide:
    - Getting Started: user/getting_started.md
    - Configuration: user/configuration.md
    - Strategies: user/strategies.md
  - Developer Guide:
    - Architecture: developers/architecture.md
    - Contributing: developers/contributing.md
    - Testing: developers/testing.md
  - API Reference:
    - REST API: api/rest.md
    - WebSocket API: api/websocket.md
  - About:
    - Changelog: about/changelog.md
    - License: about/license.md

# docs/requirements.txt
mkdocs==1.3.0
mkdocs-material==8.2.15
mkdocstrings==0.19.0
mkdocs-git-revision-date-localized-plugin==1.1.0
pymdown-extensions==9.5

# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'abidance/**/*.py'
      - '.github/workflows/docs.yml'
  pull_request:
    paths:
      - 'docs/**'
      - 'abidance/**/*.py'
      - '.github/workflows/docs.yml'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r docs/requirements.txt

      - name: Build documentation
        run: |
          cd docs
          mkdocs build --strict

      - name: Deploy documentation
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          cd docs
          mkdocs gh-deploy --force
```

**Tests to create:**
- `tests/unit/docs/test_build.py`:
  - Test MkDocs configuration
  - Test documentation build process
  - Test documentation deployment
  - Test automatic generation

**Reasoning:**
A robust documentation build pipeline ensures that documentation stays up-to-date with code changes.