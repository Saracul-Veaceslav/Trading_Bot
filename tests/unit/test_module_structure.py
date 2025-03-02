"""
Tests for the module structure.

This module contains tests to verify that the module structure follows
the expected patterns and that imports work correctly.
"""

import pytest
import importlib
import inspect
import sys


def test_abidance_package_exports():
    """Test that the abidance package exports the expected modules and classes."""
    import abidance
    
    # Check that the main modules are exported
    assert hasattr(abidance, "trading")
    assert hasattr(abidance, "exchange")
    assert hasattr(abidance, "strategy")
    assert hasattr(abidance, "data")
    assert hasattr(abidance, "core")
    assert hasattr(abidance, "utils")
    assert hasattr(abidance, "exceptions")
    
    # Check that commonly used classes are exported
    assert hasattr(abidance, "Order")
    assert hasattr(abidance, "Trade")
    assert hasattr(abidance, "Position")
    assert hasattr(abidance, "TradingEngine")
    assert hasattr(abidance, "Exchange")
    assert hasattr(abidance, "ExchangeManager")
    assert hasattr(abidance, "Strategy")
    assert hasattr(abidance, "StrategyRegistry")
    assert hasattr(abidance, "DataManager")
    
    # Check that __all__ is defined correctly
    expected_all = [
        "trading",
        "exchange",
        "strategy",
        "data",
        "ml",
        "api",
        "core",
        "utils",
        "exceptions",
        "type_defs",
        "Order",
        "Trade",
        "Position",
        "TradingEngine",
        "Exchange",
        "ExchangeManager",
        "Strategy",
        "StrategyRegistry",
        "DataManager",
    ]
    assert set(abidance.__all__) == set(expected_all)


def test_strategy_module_exports():
    """Test that the strategy module exports the expected classes and functions."""
    from abidance import strategy
    
    # Check that base classes are exported
    assert hasattr(strategy, "Strategy")
    assert hasattr(strategy, "StrategyConfig")
    
    # Check that the registry is exported
    assert hasattr(strategy, "StrategyRegistry")
    
    # Check that strategy implementations are exported
    assert hasattr(strategy, "SMAStrategy")
    assert hasattr(strategy, "SMAConfig")
    assert hasattr(strategy, "RSIStrategy")
    assert hasattr(strategy, "RSIConfig")
    
    # Check that indicators are exported
    assert hasattr(strategy, "calculate_sma")
    assert hasattr(strategy, "calculate_ema")
    assert hasattr(strategy, "calculate_rsi")
    assert hasattr(strategy, "calculate_bollinger_bands")
    assert hasattr(strategy, "calculate_macd")
    assert hasattr(strategy, "detect_crossover")
    
    # Check that __all__ is defined correctly
    expected_all = [
        "Strategy",
        "StrategyConfig",
        "StrategyRegistry",
        "SMAStrategy",
        "SMAConfig",
        "RSIStrategy",
        "RSIConfig",
        "calculate_sma",
        "calculate_ema",
        "calculate_rsi",
        "calculate_bollinger_bands",
        "calculate_macd",
        "detect_crossover",
    ]
    assert set(strategy.__all__) == set(expected_all)


def test_exchange_module_exports():
    """Test that the exchange module exports the expected classes."""
    from abidance import exchange
    
    # Check that base classes are exported
    assert hasattr(exchange, "Exchange")
    assert hasattr(exchange, "ExchangeManager")
    
    # Check that exchange implementations are exported
    assert hasattr(exchange, "BinanceExchange")
    
    # Check that __all__ is defined correctly
    expected_all = [
        "Exchange",
        "ExchangeManager",
        "BinanceExchange",
    ]
    assert set(exchange.__all__) == set(expected_all)


def test_data_module_exports():
    """Test that the data module exports the expected classes."""
    from abidance import data
    
    # Check that main classes are exported
    assert hasattr(data, "DataManager")
    assert hasattr(data, "OHLCVRepository")
    assert hasattr(data, "TradeRepository")
    assert hasattr(data, "StrategyRepository")
    
    # Check that __all__ is defined correctly
    expected_all = [
        "DataManager",
        "OHLCVRepository",
        "TradeRepository",
        "StrategyRepository",
    ]
    assert set(data.__all__) == set(expected_all)


def test_trading_module_exports():
    """Test that the trading module exports the expected classes."""
    from abidance import trading
    
    # Check that main classes are exported
    assert hasattr(trading, "Order")
    assert hasattr(trading, "Trade")
    assert hasattr(trading, "Position")
    assert hasattr(trading, "TradingEngine")
    assert hasattr(trading, "OrderSide")
    assert hasattr(trading, "OrderType")
    
    # Check that __all__ is defined correctly
    expected_all = [
        "Order",
        "Trade",
        "Position",
        "TradingEngine",
        "OrderSide",
        "OrderType",
    ]
    assert set(trading.__all__) == set(expected_all)


def test_utils_module_exports():
    """Test that the utils module exports the expected functions."""
    from abidance import utils
    
    # Check that utility functions are exported
    assert hasattr(utils, "format_timestamp")
    assert hasattr(utils, "calculate_roi")
    assert hasattr(utils, "validate_dataframe")
    
    # Check that __all__ is defined correctly
    expected_all = [
        "format_timestamp",
        "calculate_roi",
        "validate_dataframe",
    ]
    assert set(utils.__all__) == set(expected_all)


def test_exceptions_module_exports():
    """Test that the exceptions module exports the expected exceptions."""
    from abidance import exceptions
    
    # Check that base exceptions are exported
    assert hasattr(exceptions, "AbidanceError")
    
    # Check that domain exceptions are exported
    assert hasattr(exceptions, "ConfigError")
    assert hasattr(exceptions, "ExchangeError")
    assert hasattr(exceptions, "StrategyError")
    assert hasattr(exceptions, "DataError")
    assert hasattr(exceptions, "TradeError")
    assert hasattr(exceptions, "OrderError")
    assert hasattr(exceptions, "PositionError")
    
    # Check that specialized exceptions are exported
    assert hasattr(exceptions, "AuthenticationError")
    assert hasattr(exceptions, "RateLimitError")
    assert hasattr(exceptions, "InsufficientFundsError")
    
    # Check that error handling utilities are exported
    assert hasattr(exceptions, "ErrorContext")
    assert hasattr(exceptions, "error_boundary")
    assert hasattr(exceptions, "retry")
    assert hasattr(exceptions, "fallback")
    assert hasattr(exceptions, "CircuitBreaker")


def test_core_module_exports():
    """Test that the core module exports the expected classes and types."""
    from abidance import core
    
    # Check that core classes are exported
    assert hasattr(core, "ConfigManager")
    assert hasattr(core, "Logger")
    assert hasattr(core, "EventSystem")
    
    # Check that domain entities are exported
    assert hasattr(core, "OrderSide")
    assert hasattr(core, "OrderType")
    assert hasattr(core, "SignalType")
    assert hasattr(core, "Position")
    assert hasattr(core, "Order")
    assert hasattr(core, "Signal")
    assert hasattr(core, "Candle")
    assert hasattr(core, "Trade")
    
    # Check that type definitions are exported
    assert hasattr(core, "Timestamp")
    assert hasattr(core, "Price")
    assert hasattr(core, "Volume")
    assert hasattr(core, "Symbol")
    assert hasattr(core, "TimeseriesData")
    assert hasattr(core, "Parameters")
    assert hasattr(core, "Metadata")


def test_api_module_exports():
    """Test that the API module exports the expected classes and functions."""
    from abidance import api
    
    # Check that the module has __all__ defined
    assert hasattr(api, "__all__"), "API module is missing __all__"
    
    # Check that __all__ is a list or tuple of strings
    assert isinstance(api.__all__, (list, tuple)), "API module __all__ is not a list or tuple"
    assert all(isinstance(item, str) for item in api.__all__), "API module __all__ contains non-string items"


def test_ml_module_exports():
    """Test that the ML module exports the expected classes and functions."""
    from abidance import ml
    
    # Check that the module has __all__ defined
    assert hasattr(ml, "__all__"), "ML module is missing __all__"
    
    # Check that __all__ is a list or tuple of strings
    assert isinstance(ml.__all__, (list, tuple)), "ML module __all__ is not a list or tuple"
    assert all(isinstance(item, str) for item in ml.__all__), "ML module __all__ contains non-string items"


def test_type_defs_module_exports():
    """Test that the type_defs module exports the expected types."""
    from abidance import type_defs
    
    # Check that the module has __all__ defined
    assert hasattr(type_defs, "__all__"), "type_defs module is missing __all__"
    
    # Check that __all__ is a list or tuple of strings
    assert isinstance(type_defs.__all__, (list, tuple)), "type_defs module __all__ is not a list or tuple"
    assert all(isinstance(item, str) for item in type_defs.__all__), "type_defs module __all__ contains non-string items"


def test_typing_module_exports():
    """Test that the typing module exports the expected types."""
    from abidance import typing
    
    # Check that the module has __all__ defined
    assert hasattr(typing, "__all__"), "typing module is missing __all__"
    
    # Check that __all__ is a list or tuple of strings
    assert isinstance(typing.__all__, (list, tuple)), "typing module __all__ is not a list or tuple"
    assert all(isinstance(item, str) for item in typing.__all__), "typing module __all__ contains non-string items"


def test_no_circular_imports():
    """Test that there are no circular imports in the module structure."""
    modules_to_check = [
        "abidance",
        "abidance.core",
        "abidance.strategy",
        "abidance.exchange",
        "abidance.data",
        "abidance.trading",
        "abidance.utils",
        "abidance.exceptions",
        "abidance.api",
        "abidance.ml",
        "abidance.type_defs",
        "abidance.typing",
    ]
    
    for module_name in modules_to_check:
        # Force reload the module to ensure we're testing the current state
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)


def test_consistent_import_pattern():
    """Test that imports follow a consistent pattern across modules."""
    modules_to_check = [
        "abidance.strategy",
        "abidance.exchange",
        "abidance.data",
        "abidance.trading",
        "abidance.utils",
        "abidance.exceptions",
        "abidance.core",
        "abidance.api",
        "abidance.ml",
        "abidance.type_defs",
        "abidance.typing",
    ]
    
    for module_name in modules_to_check:
        module = importlib.import_module(module_name)
        
        # Check that the module has a docstring
        assert module.__doc__ is not None, f"Module {module_name} is missing a docstring"
        
        # Check that the module has __all__ defined
        assert hasattr(module, "__all__"), f"Module {module_name} is missing __all__"
        
        # Check that __all__ is a list or tuple of strings
        assert isinstance(module.__all__, (list, tuple)), f"Module {module_name}.__all__ is not a list or tuple"
        assert all(isinstance(item, str) for item in module.__all__), f"Module {module_name}.__all__ contains non-string items" 