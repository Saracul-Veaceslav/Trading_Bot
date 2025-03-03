"""
Core type definitions for the Abidance Trading Bot.

This module defines all the core types used throughout the trading bot,
providing a consistent type system for all components.
"""
from typing import (

    Any, Callable, Dict, List, Literal, Optional, Protocol, Tuple,
    TypeVar, Union, cast, overload
)
from enum import Enum, auto
from datetime import date, datetime, timedelta
import re
from pathlib import Path
import numpy as np
import pandas as pd

# ==================================================================
# Common Types
# ==================================================================

# Basic type aliases
JSON = Dict[str, Any]  # Type alias for JSON-serializable data
Timestamp = float  # Type alias for Unix timestamp in seconds
TimestampMS = int  # Type alias for Unix timestamp in milliseconds
TimeRange = Tuple[Timestamp, Timestamp]  # Type alias for a time range (start, end)
DateRange = Tuple[date, date]  # Type alias for a date range (start, end)
Numeric = Union[int, float, np.number]  # Type alias for any numeric type


class PriceType(str, Enum):
    """Types of price data that can be used in trading operations."""
    OPEN = "OPEN"
    HIGH = "HIGH"
    LOW = "LOW"
    CLOSE = "CLOSE"
    VOLUME = "VOLUME"
    TYPICAL = "TYPICAL"  # (high + low + close) / 3
    MEDIAN = "MEDIAN"   # (high + low) / 2
    WEIGHTED = "WEIGHTED" # (high + low + close + close) / 4

    def __str__(self) -> str:
        """Return the string representation of the price type.

        :return: The name of the price type
        :rtype: str
        """
        return self.value


# ==================================================================
# Trading Types
# ==================================================================

class OrderType(str, Enum):
    """Types of orders that can be placed on exchanges."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"

    def __str__(self) -> str:
        """Return the string representation of the order type.

        :return: The name of the order type
        :rtype: str
        """
        return self.value


class OrderSide(str, Enum):
    """Sides of an order (buy or sell)."""
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self) -> str:
        """Return the string representation of the order side.

        :return: The name of the order side
        :rtype: str
        """
        return self.value

    def opposite(self) -> "OrderSide":
        """Return the opposite order side.

        :return: The opposite order side
        :rtype: OrderSide
        """
        return OrderSide.SELL if self == OrderSide.BUY else OrderSide.BUY


class OrderStatus(str, Enum):
    """Status of an order."""
    OPEN = "OPEN"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

    def __str__(self) -> str:
        """Return the string representation of the order status.

        :return: The name of the order status
        :rtype: str
        """
        return self.value


class TimeInForce(str, Enum):
    """Time in force for orders."""
    GTC = "GTC"  # Good Till Canceled
    IOC = "IOC"  # Immediate Or Cancel
    FOK = "FOK"  # Fill Or Kill

    def __str__(self) -> str:
        """Return the string representation of the time in force.

        :return: The name of the time in force
        :rtype: str
        """
        return self.value


OrderId = str  # Type alias for order IDs


class PositionSide(str, Enum):
    """Side of a position (long or short)."""
    LONG = "LONG"
    SHORT = "SHORT"

    def __str__(self) -> str:
        """Return the string representation of the position side.

        :return: The name of the position side
        :rtype: str
        """
        return self.value

    def opposite(self) -> "PositionSide":
        """Return the opposite position side.

        :return: The opposite position side
        :rtype: PositionSide
        """
        return PositionSide.SHORT if self == PositionSide.LONG else PositionSide.LONG


class PositionType(str, Enum):
    """Type of position."""
    SPOT = "SPOT"
    MARGIN = "MARGIN"
    FUTURES = "FUTURES"

    def __str__(self) -> str:
        """Return the string representation of the position type.

        :return: The name of the position type
        :rtype: str
        """
        return self.value


PositionId = str  # Type alias for position IDs


# Type definition for a position
Position = Dict[str, Any]  # Fully typed would be more complex, defined minimally for now


# ==================================================================
# Data Types
# ==================================================================

# Type for OHLCV data tuple (timestamp, open, high, low, close, volume)
OHLCV = Tuple[Timestamp, float, float, float, float, float]

# Type for a list of OHLCV tuples
OHLCVData = List[OHLCV]

# Type for a price bar represented as a dictionary
PriceBar = Dict[str, Union[Timestamp, float]]

# Type for a pandas DataFrame with OHLCV data
OHLCVDataFrame = pd.DataFrame  # With expected columns: timestamp, open, high, low, close, volume


# ==================================================================
# Strategy Types
# ==================================================================

class SignalType(str, Enum):
    """Types of trading signals."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

    def __str__(self) -> str:
        """Return the string representation of the signal type.

        :return: The name of the signal type
        :rtype: str
        """
        return self.value


SignalStrength = float  # Type alias for signal strength (0.0 to 1.0)

# Type definition for a signal
Signal = Dict[str, Any]  # Fully typed would be more complex, defined minimally for now

StrategyId = str  # Type alias for strategy IDs


class Strategy(Protocol):
    """Protocol defining the interface for a trading strategy."""

    def generate_signal(self, data: OHLCVDataFrame) -> Signal:
        """Generate a trading signal based on the provided data.

        :param data: The OHLCV data to analyze
        :type data: OHLCVDataFrame
        :return: The generated trading signal
        :rtype: Signal
        """
        pass

    def get_parameters(self) -> "ParamDict":
        """Get the current parameters of the strategy.

        :return: A dictionary of parameter names and values
        :rtype: ParamDict
        """
        pass

    def set_parameters(self, params: "ParamDict") -> None:
        """Set the parameters of the strategy.

        :param params: A dictionary of parameter names and values
        :type params: ParamDict
        :return: None
        """
        pass


# ==================================================================
# Parameter Types
# ==================================================================

ParamName = str  # Type alias for parameter names
ParamValue = Union[int, float, bool, str, List[Any], Dict[str, Any]]  # Type alias for parameter values
ParamDict = Dict[ParamName, ParamValue]  # Type alias for parameter dictionaries


class BoundedFloat:
    """A float value with a minimum and maximum bound."""

    def __init__(self, min_value: float, max_value: float, value: float):
        """Initialize a bounded float.

        :param min_value: The minimum allowed value
        :type min_value: float
        :param max_value: The maximum allowed value
        :type max_value: float
        :param value: The initial value
        :type value: float
        :raises ValueError: If the value is outside the allowed range
        """
        if not min_value <= value <= max_value:
            raise ValueError(f"Value {value} is outside allowed range [{min_value}, {max_value}]")

        self.min_value = min_value
        self.max_value = max_value
        self.value = value

    def __repr__(self) -> str:
        """Return the string representation of the bounded float.

        :return: String representation
        :rtype: str
        """
        return f"BoundedFloat({self.min_value}, {self.max_value}, {self.value})"


class BoundedInt:
    """An integer value with a minimum and maximum bound."""

    def __init__(self, min_value: int, max_value: int, value: int):
        """Initialize a bounded integer.

        :param min_value: The minimum allowed value
        :type min_value: int
        :param max_value: The maximum allowed value
        :type max_value: int
        :param value: The initial value
        :type value: int
        :raises ValueError: If the value is outside the allowed range
        """
        if not min_value <= value <= max_value:
            raise ValueError(f"Value {value} is outside allowed range [{min_value}, {max_value}]")

        self.min_value = min_value
        self.max_value = max_value
        self.value = value

    def __repr__(self) -> str:
        """Return the string representation of the bounded integer.

        :return: String representation
        :rtype: str
        """
        return f"BoundedInt({self.min_value}, {self.max_value}, {self.value})"


# ==================================================================
# Result Types
# ==================================================================

T = TypeVar('T')  # Success type
E = TypeVar('E')  # Error type


class ResultType(str, Enum):
    """Types of results."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

    def __str__(self) -> str:
        """Return the string representation of the result type.

        :return: The name of the result type
        :rtype: str
        """
        return self.value


class Result(Protocol[T]):
    """Protocol defining the interface for a result type."""

    def is_success(self) -> bool:
        """Check if the result is a success.

        :return: True if the result is a success, False otherwise
        :rtype: bool
        """
        pass

    def is_failure(self) -> bool:
        """Check if the result is a failure.

        :return: True if the result is a failure, False otherwise
        :rtype: bool
        """
        pass

    def unwrap(self) -> T:
        """Get the value if the result is a success.

        :return: The success value
        :rtype: T
        :raises Exception: If the result is a failure
        """
        pass

    def unwrap_or(self, default: T) -> T:
        """Get the value if the result is a success, or a default value if it's a failure.

        :param default: The default value to return if the result is a failure
        :type default: T
        :return: The success value or the default value
        :rtype: T
        """
        pass

    def unwrap_error(self) -> Exception:
        """Get the error if the result is a failure.

        :return: The error
        :rtype: Exception
        :raises Exception: If the result is a success
        """
        pass

    def map(self, f: Callable[[T], T]) -> "Result[T]":
        """Apply a function to the success value.

        :param f: The function to apply
        :type f: Callable[[T], T]
        :return: A new result with the function applied to the success value, or the original failure
        :rtype: Result[T]
        """
        pass


class Success(Result[T]):
    """A success result."""

    def __init__(self, value: T):
        """Initialize a success result.

        :param value: The success value
        :type value: T
        """
        self.value = value

    def is_success(self) -> bool:
        """Check if the result is a success.

        :return: Always True for a Success
        :rtype: bool
        """
        return True

    def is_failure(self) -> bool:
        """Check if the result is a failure.

        :return: Always False for a Success
        :rtype: bool
        """
        return False

    def unwrap(self) -> T:
        """Get the success value.

        :return: The success value
        :rtype: T
        """
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get the success value.

        :param default: The default value (ignored for Success)
        :type default: T
        :return: The success value
        :rtype: T
        """
        return self.value

    def unwrap_error(self) -> Exception:
        """Get the error (not applicable for Success).

        :raises Exception: Always raises an exception for a Success
        """
        raise Exception("Cannot unwrap error from a Success")

    def map(self, f: Callable[[T], T]) -> "Result[T]":
        """Apply a function to the success value.

        :param f: The function to apply
        :type f: Callable[[T], T]
        :return: A new Success with the function applied to the value
        :rtype: Result[T]
        """
        return Success(f(self.value))


class Failure(Result[T]):
    """A failure result."""

    def __init__(self, error: Exception):
        """Initialize a failure result.

        :param error: The error that caused the failure
        :type error: Exception
        """
        self.error = error

    def is_success(self) -> bool:
        """Check if the result is a success.

        :return: Always False for a Failure
        :rtype: bool
        """
        return False

    def is_failure(self) -> bool:
        """Check if the result is a failure.

        :return: Always True for a Failure
        :rtype: bool
        """
        return True

    def unwrap(self) -> T:
        """Get the success value (not applicable for Failure).

        :raises Exception: Always raises the stored error for a Failure
        """
        raise self.error

    def unwrap_or(self, default: T) -> T:
        """Get a default value.

        :param default: The default value to return
        :type default: T
        :return: The default value
        :rtype: T
        """
        return default

    def unwrap_error(self) -> Exception:
        """Get the error.

        :return: The error that caused the failure
        :rtype: Exception
        """
        return self.error

    def map(self, f: Callable[[T], T]) -> "Result[T]":
        """Apply a function to the success value (not applicable for Failure).

        :param f: The function to apply (ignored for Failure)
        :type f: Callable[[T], T]
        :return: The same Failure
        :rtype: Result[T]
        """
        return self


class Either:
    """An Either monad that can be either a left (error) or right (success) value."""

    def __init__(self, is_right: bool, right_value: Optional[T] = None, left_value: Optional[E] = None):
        """Initialize an Either monad.

        :param is_right: Whether this is a right (success) value
        :type is_right: bool
        :param right_value: The right (success) value
        :type right_value: Optional[T]
        :param left_value: The left (error) value
        :type left_value: Optional[E]
        """
        self._is_right = is_right
        self._right_value = right_value
        self._left_value = left_value

    @classmethod
    def right(cls, value: T) -> "Either[E, T]":
        """Create a right (success) Either.

        :param value: The right (success) value
        :type value: T
        :return: A right Either
        :rtype: Either[E, T]
        """
        return cls(True, right_value=value)

    @classmethod
    def left(cls, value: E) -> "Either[E, T]":
        """Create a left (error) Either.

        :param value: The left (error) value
        :type value: E
        :return: A left Either
        :rtype: Either[E, T]
        """
        return cls(False, left_value=value)

    def is_right(self) -> bool:
        """Check if this is a right (success) Either.

        :return: True if this is a right Either, False otherwise
        :rtype: bool
        """
        return self._is_right

    def is_left(self) -> bool:
        """Check if this is a left (error) Either.

        :return: True if this is a left Either, False otherwise
        :rtype: bool
        """
        return not self._is_right

    def unwrap_right(self) -> T:
        """Get the right (success) value.

        :return: The right value
        :rtype: T
        :raises Exception: If this is a left Either
        """
        if not self._is_right:
            raise Exception("Cannot unwrap right value from a left Either")
        return cast(T, self._right_value)

    def unwrap_left(self) -> E:
        """Get the left (error) value.

        :return: The left value
        :rtype: E
        :raises Exception: If this is a right Either
        """
        if self._is_right:
            raise Exception("Cannot unwrap left value from a right Either")
        return cast(E, self._left_value)

    def map(self, f: Callable[[T], T]) -> "Either[E, T]":
        """Apply a function to the right (success) value.

        :param f: The function to apply
        :type f: Callable[[T], T]
        :return: A new Either with the function applied to the right value, or the original left Either
        :rtype: Either[E, T]
        """
        if self._is_right:
            return Either.right(f(cast(T, self._right_value)))
        return self

    def bind(self, f: Callable[[T], "Either[E, T]"]) -> "Either[E, T]":
        """Apply a function that returns an Either to the right (success) value.

        :param f: The function to apply
        :type f: Callable[[T], Either[E, T]]
        :return: The result of applying the function to the right value, or the original left Either
        :rtype: Either[E, T]
        """
        if self._is_right:
            return f(cast(T, self._right_value))
        return self


# ==================================================================
# Exchange Types
# ==================================================================

ExchangeName = str  # Type alias for exchange names
ExchangeId = str  # Type alias for exchange IDs
ExchangeCredentials = Dict[str, str]  # Type alias for exchange credentials
ExchangeConfig = Dict[str, Any]  # Type alias for exchange configuration


# ==================================================================
# Type Conversion Utilities
# ==================================================================

def to_timestamp(value: Union[datetime, date, Timestamp, TimestampMS], unit: str = 's') -> Timestamp:
    """Convert a value to a Unix timestamp.

    :param value: The value to convert (datetime, date, timestamp, or timestamp in milliseconds)
    :type value: Union[datetime, date, Timestamp, TimestampMS]
    :param unit: The unit of the timestamp ('s' for seconds, 'ms' for milliseconds)
    :type unit: str
    :return: The Unix timestamp in seconds
    :rtype: Timestamp
    """
    if isinstance(value, datetime):
        return value.timestamp()
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time()).timestamp()
    if isinstance(value, (int, float)):
        if unit == 'ms':
            return value / 1000.0
        return value

    raise TypeError(f"Cannot convert {type(value)} to timestamp")


def from_timestamp(value: Union[Timestamp, TimestampMS, str], unit: str = 's') -> datetime:
    """Convert a Unix timestamp to a datetime.

    :param value: The timestamp to convert (seconds, milliseconds, or string representation)
    :type value: Union[Timestamp, TimestampMS, str]
    :param unit: The unit of the timestamp ('s' for seconds, 'ms' for milliseconds)
    :type unit: str
    :return: The datetime object
    :rtype: datetime
    """
    if isinstance(value, str):
        value = float(value)

    if unit == 'ms':
        return datetime.fromtimestamp(value / 1000.0)
    return datetime.fromtimestamp(value)


def ensure_datetime(value: Union[datetime, Timestamp, TimestampMS, str]) -> datetime:
    """Ensure a value is a datetime.

    :param value: The value to convert (datetime, timestamp, timestamp in milliseconds, or string)
    :type value: Union[datetime, Timestamp, TimestampMS, str]
    :return: The datetime object
    :rtype: datetime
    :raises ValueError: If the value cannot be parsed as a datetime
    :raises TypeError: If the value type is not supported
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        # Determine if it's a timestamp in seconds or milliseconds
        if value > 1e10:  # If it's larger than 10 billion, it's probably in milliseconds
            return from_timestamp(value, unit='ms')
        return from_timestamp(value)
    if isinstance(value, str):
        # Try parsing as ISO format first
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            # Try parsing as timestamp
            try:
                return from_timestamp(float(value))
            except ValueError:
                raise ValueError(f"Cannot parse {value} as datetime")

    raise TypeError(f"Cannot convert {type(value)} to datetime")


def ensure_timedelta(value: Union[timedelta, int, float, Dict[str, int], str]) -> timedelta:
    """Ensure a value is a timedelta.

    :param value: The value to convert (timedelta, seconds, dictionary with time units, or string)
    :type value: Union[timedelta, int, float, Dict[str, int], str]
    :return: The timedelta object
    :rtype: timedelta
    :raises ValueError: If the value cannot be parsed as a timedelta
    :raises TypeError: If the value type is not supported
    """
    if isinstance(value, timedelta):
        return value
    if isinstance(value, (int, float)):
        return timedelta(seconds=value)
    if isinstance(value, dict):
        return timedelta(**value)
    if isinstance(value, str):
        # Parse string like "1d 2h 3m 4s"
        pattern = r'(?:(\d+)([dhms]))'
        matches = re.findall(pattern, value)

        if not matches:
            raise ValueError(f"Cannot parse {value} as timedelta")

        time_dict = {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}

        for amount, unit in matches:
            if unit == 'd':
                time_dict['days'] += int(amount)
            elif unit == 'h':
                time_dict['hours'] += int(amount)
            elif unit == 'm':
                time_dict['minutes'] += int(amount)
            elif unit == 's':
                time_dict['seconds'] += int(amount)

        return timedelta(**time_dict)

    raise TypeError(f"Cannot convert {type(value)} to timedelta")


# Define what's available when doing "from abidance.typing import *"
__all__ = [
    # Basic type aliases
    "JSON",
    "Timestamp",
    "TimestampMS",
    "TimeRange",
    "DateRange",
    "Numeric",

    # Enums
    "PriceType",
    "OrderType",
    "OrderSide",
    "OrderStatus",
    "TimeInForce",
    "PositionSide",
    "PositionType",
    "SignalType",
    "ResultType",

    # Protocols
    "Strategy",
    "Result",

    # Classes
    "BoundedFloat",
    "BoundedInt",
    "Success",
    "Failure",
    "Either",

    # Functions
    "to_timestamp",
    "from_timestamp",
    "ensure_datetime",
    "ensure_timedelta",
]
