"""
Core type definitions for the Abidance trading bot.

This module defines common type aliases and custom types used throughout the application.
"""

from decimal import Decimal
from typing import Dict, List, Union, Any, TypeVar, Callable, Optional, Tuple

import numpy as np
import pandas as pd


# Type aliases for common types
Timestamp = Union[int, float]  # Unix timestamp
Price = Union[float, Decimal]  # Price value
Volume = Union[float, Decimal]  # Volume value
Symbol = str  # Trading pair symbol (e.g., "BTC/USD")
ExchangeID = str  # Exchange identifier
StrategyID = str  # Strategy identifier

# Type aliases for complex structures
OHLCV = Tuple[float, float, float, float, float]  # Open, High, Low, Close, Volume
TimeseriesData = pd.DataFrame  # Timeseries data (e.g., price history)
Parameters = Dict[str, Any]  # Generic parameters dictionary
Metadata = Dict[str, Any]  # Generic metadata dictionary

# Type variables for generic functions
T = TypeVar('T')
U = TypeVar('U')

# Callback type definitions
SignalCallback = Callable[..., None]
ErrorCallback = Callable[[Exception], None]
DataCallback = Callable[[pd.DataFrame], None]

# Configuration types
ConfigValue = Union[str, int, float, bool, List[Any], Dict[str, Any]]
Config = Dict[str, ConfigValue]

# Result types
Result = Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]
