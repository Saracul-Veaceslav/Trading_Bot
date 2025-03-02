"""
Tests for the core type definitions.

This module contains tests for the core type definitions used throughout the application.
"""

import pytest
from decimal import Decimal
import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any, Callable

from abidance.core.types import (
    Timestamp,
    Price,
    Volume,
    Symbol,
    ExchangeID,
    StrategyID,
    OHLCV,
    TimeseriesData,
    Parameters,
    Metadata,
    SignalCallback,
    ErrorCallback,
    DataCallback,
    ConfigValue,
    Config,
    Result
)


def test_timestamp_type():
    """Test that Timestamp type accepts both int and float."""
    # Integer timestamp
    timestamp_int: Timestamp = 1646092800
    assert isinstance(timestamp_int, int)
    
    # Float timestamp
    timestamp_float: Timestamp = 1646092800.123
    assert isinstance(timestamp_float, float)


def test_price_type():
    """Test that Price type accepts both float and Decimal."""
    # Float price
    price_float: Price = 50000.0
    assert isinstance(price_float, float)
    
    # Decimal price
    price_decimal: Price = Decimal('50000.00')
    assert isinstance(price_decimal, Decimal)


def test_volume_type():
    """Test that Volume type accepts both float and Decimal."""
    # Float volume
    volume_float: Volume = 1.5
    assert isinstance(volume_float, float)
    
    # Decimal volume
    volume_decimal: Volume = Decimal('1.5')
    assert isinstance(volume_decimal, Decimal)


def test_symbol_type():
    """Test that Symbol type is a string."""
    symbol: Symbol = "BTC/USD"
    assert isinstance(symbol, str)


def test_exchange_id_type():
    """Test that ExchangeID type is a string."""
    exchange_id: ExchangeID = "binance"
    assert isinstance(exchange_id, str)


def test_strategy_id_type():
    """Test that StrategyID type is a string."""
    strategy_id: StrategyID = "sma_crossover"
    assert isinstance(strategy_id, str)


def test_ohlcv_type():
    """Test that OHLCV type is a tuple of 5 floats."""
    ohlcv: OHLCV = (50000.0, 51000.0, 49000.0, 50500.0, 10.5)
    assert isinstance(ohlcv, tuple)
    assert len(ohlcv) == 5
    assert all(isinstance(value, float) for value in ohlcv)


def test_timeseries_data_type():
    """Test that TimeseriesData type is a pandas DataFrame."""
    df = pd.DataFrame({
        'timestamp': [1646092800, 1646092860, 1646092920],
        'close': [50000.0, 50100.0, 50200.0]
    })
    timeseries_data: TimeseriesData = df
    assert isinstance(timeseries_data, pd.DataFrame)


def test_parameters_type():
    """Test that Parameters type is a dictionary."""
    parameters: Parameters = {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    }
    assert isinstance(parameters, dict)


def test_metadata_type():
    """Test that Metadata type is a dictionary."""
    metadata: Metadata = {
        'strategy': 'sma_crossover',
        'version': '1.0.0'
    }
    assert isinstance(metadata, dict)


def test_signal_callback_type():
    """Test that SignalCallback type is a callable."""
    def callback_function(*args):
        pass
    
    signal_callback: SignalCallback = callback_function
    assert callable(signal_callback)


def test_error_callback_type():
    """Test that ErrorCallback type is a callable that takes an Exception."""
    def callback_function(error: Exception):
        pass
    
    error_callback: ErrorCallback = callback_function
    assert callable(error_callback)


def test_data_callback_type():
    """Test that DataCallback type is a callable that takes a DataFrame."""
    def callback_function(data: pd.DataFrame):
        pass
    
    data_callback: DataCallback = callback_function
    assert callable(data_callback)


def test_config_value_type():
    """Test that ConfigValue type accepts various types."""
    # String
    config_value_str: ConfigValue = "value"
    assert isinstance(config_value_str, str)
    
    # Integer
    config_value_int: ConfigValue = 123
    assert isinstance(config_value_int, int)
    
    # Float
    config_value_float: ConfigValue = 123.45
    assert isinstance(config_value_float, float)
    
    # Boolean
    config_value_bool: ConfigValue = True
    assert isinstance(config_value_bool, bool)
    
    # List
    config_value_list: ConfigValue = [1, 2, 3]
    assert isinstance(config_value_list, list)
    
    # Dictionary
    config_value_dict: ConfigValue = {"key": "value"}
    assert isinstance(config_value_dict, dict)


def test_config_type():
    """Test that Config type is a dictionary of ConfigValue."""
    config: Config = {
        "api_key": "abc123",
        "api_secret": "xyz789",
        "debug": True,
        "timeout": 30,
        "symbols": ["BTC/USD", "ETH/USD"],
        "exchange": {
            "name": "binance",
            "url": "https://api.binance.com"
        }
    }
    assert isinstance(config, dict)


def test_result_type():
    """Test that Result type accepts various return types."""
    # Dictionary
    result_dict: Result = {"key": "value"}
    assert isinstance(result_dict, dict)
    
    # List of dictionaries
    result_list: Result = [{"key1": "value1"}, {"key2": "value2"}]
    assert isinstance(result_list, list)
    assert all(isinstance(item, dict) for item in result_list)
    
    # DataFrame
    result_df: Result = pd.DataFrame({"col1": [1, 2, 3]})
    assert isinstance(result_df, pd.DataFrame) 