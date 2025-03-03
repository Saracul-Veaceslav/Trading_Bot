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
        ...

    def get_parameters(self) -> "ParamDict":
        """Get the current parameters of the strategy.

        :return: A dictionary of parameter names and values
        :rtype: ParamDict
        """
        ...

    def set_parameters(self, params: "ParamDict") -> None:
        """Set the parameters of the strategy.

        :param params: A dictionary of parameter names and values
        :type params: ParamDict
        :return: None
        """
        ...


# ==================================================================
# Parameter Types
# ==================================================================

# Type variable for generic parameter types
P = TypeVar('P')

# Type alias for parameter dictionaries
ParamDict = Dict[str, Any]

# Type alias for parameter validation functions
ParamValidator = Callable[[Any], bool]


class BoundedFloat:
    """A float value with minimum and maximum bounds."""

    def __init__(self, min_value: float, max_value: float, value: float):
        """Initialize a bounded float.

        :param min_value: The minimum allowed value
        :type min_value: float
        :param max_value: The maximum allowed value
        :type max_value: float
        :param value: The initial value
        :type value: float
        :raises ValueError: If value is outside the allowed range
        """
        if not min_value <= value <= max_value:
            raise ValueError(f"Value {value} is outside the allowed range [{min_value}, {max_value}]")
        self.min_value = min_value
        self.max_value = max_value
        self.value = value

    def __repr__(self) -> str:
        """Return a string representation of the bounded float.

        :return: A string representation
        :rtype: str
        """
        return f"BoundedFloat({self.min_value}, {self.max_value}, {self.value})"


class BoundedInt:
    """An integer value with minimum and maximum bounds."""

    def __init__(self, min_value: int, max_value: int, value: int):
        """Initialize a bounded integer.

        :param min_value: The minimum allowed value
        :type min_value: int
        :param max_value: The maximum allowed value
        :type max_value: int
        :param value: The initial value
        :type value: int
        :raises ValueError: If value is outside the allowed range
        """
        if not min_value <= value <= max_value:
            raise ValueError(f"Value {value} is outside the allowed range [{min_value}, {max_value}]")
        self.min_value = min_value
        self.max_value = max_value
        self.value = value

    def __repr__(self) -> str:
        """Return a string representation of the bounded integer.

        :return: A string representation
        :rtype: str
        """
        return f"BoundedInt({self.min_value}, {self.max_value}, {self.value})"


# ==================================================================
# Result Types
# ==================================================================

# Type variable for generic result types
T = TypeVar('T')
E = TypeVar('E', bound=Exception)


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
    """Protocol for a result type that can be either a success or a failure."""

    def is_success(self) -> bool:
        """Check if the result is a success.

        :return: True if the result is a success, False otherwise
        :rtype: bool
        """
        ...

    def is_failure(self) -> bool:
        """Check if the result is a failure.

        :return: True if the result is a failure, False otherwise
        :rtype: bool
        """
        ...

    def unwrap(self) -> T:
        """Unwrap the result to get the value.

        :return: The value if the result is a success
        :rtype: T
        :raises Exception: If the result is a failure
        """
        ...

    def unwrap_or(self, default: T) -> T:
        """Unwrap the result to get the value, or return a default value if it's a failure.

        :param default: The default value to return if the result is a failure
        :type default: T
        :return: The value if the result is a success, or the default value if it's a failure
        :rtype: T
        """
        ...

    def unwrap_error(self) -> Exception:
        """Unwrap the result to get the error.

        :return: The error if the result is a failure
        :rtype: Exception
        :raises ValueError: If the result is a success
        """
        ...

    def map(self, f: Callable[[T], T]) -> "Result[T]":
        """Apply a function to the value if the result is a success.

        :param f: The function to apply
        :type f: Callable[[T], T]
        :return: A new result with the function applied to the value if the result is a success,
                 or the same failure if the result is a failure
        :rtype: Result[T]
        """
        ...


class Success(Result[T]):
    """A successful result containing a value."""

    def __init__(self, value: T):
        """Initialize a successful result.

        :param value: The value
        :type value: T
        """
        self.value = value

    def is_success(self) -> bool:
        """Check if the result is a success.

        :return: True
        :rtype: bool
        """
        return True

    def is_failure(self) -> bool:
        """Check if the result is a failure.

        :return: False
        :rtype: bool
        """
        return False

    def unwrap(self) -> T:
        """Unwrap the result to get the value.

        :return: The value
        :rtype: T
        """
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Unwrap the result to get the value, or return a default value if it's a failure.

        :param default: The default value to return if the result is a failure
        :type default: T
        :return: The value
        :rtype: T
        """
        return self.value

    def unwrap_error(self) -> Exception:
        """Unwrap the result to get the error.

        :raises ValueError: Always, because the result is a success
        """
        raise ValueError("Cannot unwrap error from a successful result")

    def map(self, f: Callable[[T], T]) -> "Result[T]":
        """Apply a function to the value.

        :param f: The function to apply
        :type f: Callable[[T], T]
        :return: A new successful result with the function applied to the value
        :rtype: Result[T]
        """
        return Success(f(self.value))


class Failure(Result[T]):
    """A failed result containing an error."""

    def __init__(self, error: Exception):
        """Initialize a failed result.

        :param error: The error
        :type error: Exception
        """
        self.error = error

    def is_success(self) -> bool:
        """Check if the result is a success.

        :return: False
        :rtype: bool
        """
        return False

    def is_failure(self) -> bool:
        """Check if the result is a failure.

        :return: True
        :rtype: bool
        """
        return True

    def unwrap(self) -> T:
        """Unwrap the result to get the value.

        :raises Exception: The error
        """
        raise self.error

    def unwrap_or(self, default: T) -> T:
        """Unwrap the result to get the value, or return a default value if it's a failure.

        :param default: The default value to return
        :type default: T
        :return: The default value
        :rtype: T
        """
        return default

    def unwrap_error(self) -> Exception:
        """Unwrap the result to get the error.

        :return: The error
        :rtype: Exception
        """
        return self.error

    def map(self, f: Callable[[T], T]) -> "Result[T]":
        """Apply a function to the value if the result is a success.

        :param f: The function to apply
        :type f: Callable[[T], T]
        :return: The same failure
        :rtype: Result[T]
        """
        return self


class Either:
    """A type that can be either a left value or a right value."""

    def __init__(self, is_right: bool, right_value: Optional[T] = None, left_value: Optional[E] = None):
        """Initialize an Either type.

        :param is_right: Whether the value is a right value
        :type is_right: bool
        :param right_value: The right value, if is_right is True
        :type right_value: Optional[T]
        :param left_value: The left value, if is_right is False
        :type left_value: Optional[E]
        :raises ValueError: If is_right is True but right_value is None,
                           or if is_right is False but left_value is None
        """
        if is_right and right_value is None:
            raise ValueError("Right value cannot be None for a right Either")
        if not is_right and left_value is None:
            raise ValueError("Left value cannot be None for a left Either")
        self.is_right_value = is_right
        self.right_value = right_value
        self.left_value = left_value

    @classmethod
    def right(cls, value: T) -> "Either[E, T]":
        """Create a right Either.

        :param value: The right value
        :type value: T
        :return: A right Either
        :rtype: Either[E, T]
        :raises ValueError: If value is None
        """
        if value is None:
            raise ValueError("Right value cannot be None")
        return cls(True, right_value=value)

    @classmethod
    def left(cls, value: E) -> "Either[E, T]":
        """Create a left Either.

        :param value: The left value
        :type value: E
        :return: A left Either
        :rtype: Either[E, T]
        :raises ValueError: If value is None
        """
        if value is None:
            raise ValueError("Left value cannot be None")
        return cls(False, left_value=value)

    def is_right(self) -> bool:
        """Check if the Either is a right value.

        :return: True if the Either is a right value, False otherwise
        :rtype: bool
        """
        return self.is_right_value

    def is_left(self) -> bool:
        """Check if the Either is a left value.

        :return: True if the Either is a left value, False otherwise
        :rtype: bool
        """
        return not self.is_right_value

    def unwrap_right(self) -> T:
        """Unwrap the Either to get the right value.

        :return: The right value
        :rtype: T
        :raises ValueError: If the Either is a left value
        """
        if not self.is_right_value:
            raise ValueError("Cannot unwrap right value from a left Either")
        return cast(T, self.right_value)

    def unwrap_left(self) -> E:
        """Unwrap the Either to get the left value.

        :return: The left value
        :rtype: E
        :raises ValueError: If the Either is a right value
        """
        if self.is_right_value:
            raise ValueError("Cannot unwrap left value from a right Either")
        return cast(E, self.left_value)

    def map(self, f: Callable[[T], T]) -> "Either[E, T]":
        """Apply a function to the right value if the Either is a right value.

        :param f: The function to apply
        :type f: Callable[[T], T]
        :return: A new Either with the function applied to the right value if the Either is a right value,
                 or the same left value if the Either is a left value
        :rtype: Either[E, T]
        """
        if self.is_right_value:
            return Either.right(f(cast(T, self.right_value)))
        return self

    def bind(self, f: Callable[[T], "Either[E, T]"]) -> "Either[E, T]":
        """Apply a function that returns an Either to the right value if the Either is a right value.

        :param f: The function to apply
        :type f: Callable[[T], Either[E, T]]
        :return: The result of applying the function to the right value if the Either is a right value,
                 or the same left value if the Either is a left value
        :rtype: Either[E, T]
        """
        if self.is_right_value:
            return f(cast(T, self.right_value))
        return self


# ==================================================================
# Type Utilities
# ==================================================================

def to_timestamp(value: Union[datetime, date, Timestamp, TimestampMS], unit: str = 's') -> Timestamp:
    """Convert a datetime, date, or timestamp to a Unix timestamp.

    :param value: The value to convert
    :type value: Union[datetime, date, Timestamp, TimestampMS]
    :param unit: The unit of the timestamp ('s' for seconds, 'ms' for milliseconds)
    :type unit: str
    :return: The Unix timestamp in seconds
    :rtype: Timestamp
    :raises ValueError: If the unit is not 's' or 'ms'
    """
    if isinstance(value, (int, float)):
        if unit == 's':
            return float(value)
        elif unit == 'ms':
            return float(value) / 1000.0
        else:
            raise ValueError(f"Invalid unit: {unit}")
    elif isinstance(value, datetime):
        return value.timestamp()
    elif isinstance(value, date):
        return datetime.combine(value, datetime.min.time()).timestamp()
    else:
        raise TypeError(f"Cannot convert {type(value)} to timestamp")


def from_timestamp(value: Union[Timestamp, TimestampMS, str], unit: str = 's') -> datetime:
    """Convert a Unix timestamp to a datetime.

    :param value: The timestamp to convert
    :type value: Union[Timestamp, TimestampMS, str]
    :param unit: The unit of the timestamp ('s' for seconds, 'ms' for milliseconds)
    :type unit: str
    :return: The datetime
    :rtype: datetime
    :raises ValueError: If the unit is not 's' or 'ms'
    """
    if isinstance(value, str):
        value = float(value)

    if unit == 's':
        return datetime.fromtimestamp(value)
    elif unit == 'ms':
        return datetime.fromtimestamp(value / 1000.0)
    else:
        raise ValueError(f"Invalid unit: {unit}")


def ensure_datetime(value: Union[datetime, Timestamp, TimestampMS, str]) -> datetime:
    """Ensure that a value is a datetime.

    :param value: The value to convert
    :type value: Union[datetime, Timestamp, TimestampMS, str]
    :return: The datetime
    :rtype: datetime
    :raises ValueError: If the value cannot be converted to a datetime
    """
    if isinstance(value, datetime):
        return value
    elif isinstance(value, (int, float)):
        # Heuristic: if the value is greater than 1e10, it's probably milliseconds
        if value > 1e10:
            return from_timestamp(value, 'ms')
        else:
            return from_timestamp(value, 's')
    elif isinstance(value, str):
        # Try to parse as ISO format
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            # Try to parse as timestamp
            try:
                return from_timestamp(float(value), 's')
            except ValueError:
                raise ValueError(f"Cannot parse {value} as datetime")
    else:
        raise TypeError(f"Cannot convert {type(value)} to datetime")


def ensure_timedelta(value: Union[timedelta, int, float, Dict[str, int], str]) -> timedelta:
    """Ensure that a value is a timedelta.

    :param value: The value to convert
    :type value: Union[timedelta, int, float, Dict[str, int], str]
    :return: The timedelta
    :rtype: timedelta
    :raises ValueError: If the value cannot be converted to a timedelta
    """
    if isinstance(value, timedelta):
        return value
    elif isinstance(value, (int, float)):
        # Assume seconds
        return timedelta(seconds=value)
    elif isinstance(value, dict):
        # Assume a dict with keys like 'days', 'seconds', etc.
        return timedelta(**value)
    elif isinstance(value, str):
        # Try to parse as a string like '1d2h3m4s'
        pattern = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        match = re.match(pattern, value)
        if match and match.group(0):  # Ensure we matched something
            days = int(match.group(1) or 0)
            hours = int(match.group(2) or 0)
            minutes = int(match.group(3) or 0)
            seconds = int(match.group(4) or 0)

            # Ensure at least one value is non-zero
            if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
                raise ValueError(f"Cannot parse '{value}' as timedelta: no valid time components found")

            return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        else:
            raise ValueError(f"Cannot parse '{value}' as timedelta")
    else:
        raise TypeError(f"Cannot convert {type(value)} to timedelta")


# Define what's available when doing "from abidance.type_defs import *"
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