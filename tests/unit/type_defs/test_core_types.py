"""
Tests for the core type definitions used throughout the Abidance trading bot.

This module tests the core type definitions for:
1. Type compatibility with expected usage patterns
2. Type annotations documentation
3. Integration with other components
"""
import pytest
from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import inspect
import sys
import os

# Add the project root to the path so we can import abidance
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import abidance

# Import the types module
from abidance.type_defs import (
    # Common types
    JSON, Timestamp, TimestampMS, TimeRange, DateRange, Numeric, PriceType,
    # Trading specific types
    OrderType, OrderSide, OrderStatus, OrderId, TimeInForce,
    Position, PositionType, PositionId, PositionSide,
    # Data types
    OHLCVData, OHLCVDataFrame, OHLCV, PriceBar,
    # Strategy types
    Signal, SignalType, SignalStrength, Strategy, StrategyId,
    # Parameter types
    ParamDict, BoundedFloat, BoundedInt,
    # Result types
    Result, ResultType, Success, Failure, Either,
    # Type conversion utilities
    to_timestamp, from_timestamp, ensure_datetime, ensure_timedelta
)


class TestCommonTypes:
    """Tests for the common type definitions."""
    
    def test_json_type_with_valid_values(self):
        """Test JSON type with valid JSON-serializable values."""
        # Test basic types
        basic_json: JSON = {
            "string": "value",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }
        
        # Verify the type hint works with complex nested structures
        complex_json: JSON = {
            "data": [
                {"id": 1, "values": [1.1, 2.2, 3.3]},
                {"id": 2, "values": [4.4, 5.5, 6.6]}
            ],
            "metadata": {
                "count": 2,
                "timestamp": 1646870400000,
                "source": "test"
            }
        }
        
        # Test edge cases 
        empty_json: JSON = {}
        array_json: JSON = [1, 2, 3]
        
        # These assertions just verify the type annotations are correct
        # In a real test with mypy, we would check that mypy doesn't raise errors
        assert isinstance(basic_json, dict)
        assert isinstance(complex_json, dict)
        assert isinstance(empty_json, dict)
        assert isinstance(array_json, list)
    
    def test_timestamp_and_timestampms_conversions(self):
        """Test Timestamp and TimestampMS type conversions."""
        # Current time
        now = datetime.now()
        
        # Convert to timestamp (seconds)
        ts: Timestamp = now.timestamp()
        assert isinstance(ts, float)
        
        # Convert to timestamp milliseconds
        ts_ms: TimestampMS = int(now.timestamp() * 1000)
        assert isinstance(ts_ms, int)
        
        # Test conversion functions
        dt1 = from_timestamp(ts)
        dt2 = from_timestamp(ts_ms / 1000)
        
        # Timestamps should convert back to nearly the same datetime
        # (allowing for minimal float precision loss)
        assert abs((dt1 - now).total_seconds()) < 0.001
        assert abs((dt2 - now).total_seconds()) < 0.001
        
        # Test conversion from datetime to timestamp
        ts1 = to_timestamp(now)
        assert abs(ts1 - ts) < 0.001
    
    def test_time_range_and_date_range_usage(self):
        """Test TimeRange and DateRange type usage patterns."""
        # Create time range (tuple of timestamps)
        start_ts = datetime.now().timestamp()
        end_ts = (datetime.now() + timedelta(days=1)).timestamp()
        time_range: TimeRange = (start_ts, end_ts)
        
        # Create date range (tuple of datetimes)
        start_date = datetime.now().date()
        end_date = (datetime.now() + timedelta(days=30)).date()
        date_range: DateRange = (start_date, end_date)
        
        # Test operations that would use these types
        assert time_range[1] > time_range[0]
        assert (date_range[1] - date_range[0]).days == 30
    
    def test_numeric_type_with_different_values(self):
        """Test Numeric type with different numeric values."""
        # Test with integer
        int_value: Numeric = 42
        assert isinstance(int_value, int)
        
        # Test with float
        float_value: Numeric = 3.14
        assert isinstance(float_value, float)
        
        # Test with numpy numeric types
        np_int_value: Numeric = np.int64(42)
        np_float_value: Numeric = np.float64(3.14)
        
        # These would be validated by mypy
        assert np.issubdtype(type(np_int_value), np.integer)
        assert np.issubdtype(type(np_float_value), np.floating)


class TestTradingTypes:
    """Tests for the trading-specific type definitions."""
    
    def test_order_type_enumeration(self):
        """Test OrderType enumeration values and operations."""
        # Check available order types
        assert OrderType.MARKET in OrderType.__members__.values()
        assert OrderType.LIMIT in OrderType.__members__.values()
        assert OrderType.STOP in OrderType.__members__.values()
        assert OrderType.STOP_LIMIT in OrderType.__members__.values()
        
        # Test string representation
        assert str(OrderType.MARKET) == "MARKET"
        
        # Test conversion from string
        assert OrderType("MARKET") == OrderType.MARKET
        
        # Test using in dictionary
        order_handlers = {
            OrderType.MARKET: "market_handler",
            OrderType.LIMIT: "limit_handler"
        }
        assert order_handlers[OrderType.MARKET] == "market_handler"
    
    def test_order_side_enumeration(self):
        """Test OrderSide enumeration values and operations."""
        # Check available sides
        assert OrderSide.BUY in OrderSide.__members__.values()
        assert OrderSide.SELL in OrderSide.__members__.values()
        
        # Test string representation
        assert str(OrderSide.BUY) == "BUY"
        
        # Test conversion from string
        assert OrderSide("SELL") == OrderSide.SELL
        
        # Test opposite side function (assuming it exists)
        assert OrderSide.BUY.opposite() == OrderSide.SELL
        assert OrderSide.SELL.opposite() == OrderSide.BUY
    
    def test_position_with_valid_data(self):
        """Test Position type with valid position data."""
        # Create a position dictionary
        position: Position = {
            "id": "pos123",
            "symbol": "BTC/USDT",
            "side": PositionSide.LONG,
            "amount": 0.1,
            "entry_price": 40000.0,
            "current_price": 42000.0,
            "unrealized_pnl": 200.0,
            "realized_pnl": 0.0,
            "timestamp": datetime.now().timestamp()
        }
        
        # Test position operations
        assert position["side"] == PositionSide.LONG
        assert position["amount"] > 0
        
        # Test with short position
        short_position: Position = {
            "id": "pos456",
            "symbol": "ETH/USDT",
            "side": PositionSide.SHORT,
            "amount": 1.0,
            "entry_price": 3000.0,
            "current_price": 2900.0,
            "unrealized_pnl": 100.0,
            "realized_pnl": 0.0,
            "timestamp": datetime.now().timestamp()
        }
        
        assert short_position["side"] == PositionSide.SHORT
        assert short_position["unrealized_pnl"] > 0  # Profit for short


class TestDataTypes:
    """Tests for data-related type definitions."""
    
    def test_ohlcv_tuple_format(self):
        """Test OHLCV tuple format and operations."""
        # Create an OHLCV tuple
        timestamp = datetime.now().timestamp()
        ohlcv: OHLCV = (timestamp, 40000.0, 41000.0, 39500.0, 40500.0, 100.0)
        
        # Test accessing components
        assert len(ohlcv) == 6
        assert ohlcv[0] == timestamp  # timestamp
        assert ohlcv[1] == 40000.0    # open
        assert ohlcv[2] == 41000.0    # high
        assert ohlcv[3] == 39500.0    # low
        assert ohlcv[4] == 40500.0    # close
        assert ohlcv[5] == 100.0      # volume
        
        # Test unpacking
        ts, open_price, high, low, close, volume = ohlcv
        assert ts == timestamp
        assert open_price == 40000.0
        assert high == 41000.0
        assert low == 39500.0
        assert close == 40500.0
        assert volume == 100.0
    
    def test_ohlcv_dataframe_structure(self):
        """Test OHLCVDataFrame structure and operations."""
        # Create sample data
        data = {
            'timestamp': [1646870400, 1646874000, 1646877600],
            'open': [40000.0, 40500.0, 41000.0],
            'high': [40800.0, 41200.0, 41500.0],
            'low': [39800.0, 40300.0, 40800.0],
            'close': [40500.0, 41000.0, 41200.0],
            'volume': [100.0, 120.0, 90.0]
        }
        
        # Create DataFrame
        df: OHLCVDataFrame = pd.DataFrame(data)
        
        # Test DataFrame structure
        assert 'timestamp' in df.columns
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns
        
        # Test DataFrame operations
        assert len(df) == 3
        assert df['high'].max() == 41500.0
        assert df['low'].min() == 39800.0
        
        # Test calculating typical price (if that's a common operation)
        df['typical'] = (df['high'] + df['low'] + df['close']) / 3
        assert 'typical' in df.columns
        assert abs(df['typical'].iloc[0] - ((40800.0 + 39800.0 + 40500.0) / 3)) < 0.001
    
    def test_price_bar_dictionary(self):
        """Test PriceBar dictionary structure and operations."""
        # Create a price bar
        timestamp = datetime.now().timestamp()
        bar: PriceBar = {
            'timestamp': timestamp,
            'open': 40000.0,
            'high': 40800.0,
            'low': 39800.0,
            'close': 40500.0,
            'volume': 100.0
        }
        
        # Test accessing components
        assert bar['timestamp'] == timestamp
        assert bar['open'] == 40000.0
        assert bar['high'] == 40800.0
        assert bar['low'] == 39800.0
        assert bar['close'] == 40500.0
        assert bar['volume'] == 100.0
        
        # Test operations
        assert bar['high'] - bar['low'] == 1000.0  # Range
        assert bar['close'] > bar['open']  # Bullish bar
        
        # Test with additional fields
        extended_bar: PriceBar = {
            **bar,
            'vwap': 40300.0,
            'trades': 500
        }
        
        assert 'vwap' in extended_bar
        assert extended_bar['vwap'] == 40300.0


class TestStrategyTypes:
    """Tests for strategy-related type definitions."""
    
    def test_signal_type_enumeration(self):
        """Test SignalType enumeration values and operations."""
        # Check available signal types
        assert SignalType.BUY in SignalType.__members__.values()
        assert SignalType.SELL in SignalType.__members__.values()
        assert SignalType.HOLD in SignalType.__members__.values()
        
        # Test string representation
        assert str(SignalType.BUY) == "BUY"
        
        # Test conversion from string
        assert SignalType("SELL") == SignalType.SELL
    
    def test_signal_with_valid_data(self):
        """Test Signal type with valid signal data."""
        # Create a signal dictionary
        signal: Signal = {
            "type": SignalType.BUY,
            "symbol": "BTC/USDT",
            "strength": 0.8,
            "price": 40000.0,
            "timestamp": datetime.now().timestamp(),
            "metadata": {
                "strategy": "SMA Crossover",
                "fast_period": 10,
                "slow_period": 30
            }
        }
        
        # Test signal operations
        assert signal["type"] == SignalType.BUY
        assert 0 <= signal["strength"] <= 1.0
        
        # Test with sell signal
        sell_signal: Signal = {
            "type": SignalType.SELL,
            "symbol": "ETH/USDT",
            "strength": 0.6,
            "price": 3000.0,
            "timestamp": datetime.now().timestamp(),
            "metadata": {
                "strategy": "RSI Overbought",
                "period": 14,
                "threshold": 70
            }
        }
        
        assert sell_signal["type"] == SignalType.SELL
        assert sell_signal["metadata"]["strategy"] == "RSI Overbought"
    
    def test_strategy_protocol_compatibility(self):
        """Test Strategy protocol compatibility with a minimal implementation."""
        # Define a minimal strategy class that implements the Strategy protocol
        class MinimalStrategy:
            def generate_signal(self, data: OHLCVDataFrame) -> Signal:
                """Generate a trading signal based on the provided data."""
                # Simple implementation that always returns a HOLD signal
                return {
                    "type": SignalType.HOLD,
                    "symbol": "BTC/USDT",
                    "strength": 0.0,
                    "price": data['close'].iloc[-1],
                    "timestamp": data['timestamp'].iloc[-1]
                }
            
            def get_parameters(self) -> ParamDict:
                """Get the current parameters of the strategy."""
                return {}
            
            def set_parameters(self, params: ParamDict) -> None:
                """Set the parameters of the strategy."""
                pass
        
        # Create an instance of the strategy
        strategy = MinimalStrategy()
        
        # Create sample data
        data = pd.DataFrame({
            'timestamp': [1646870400, 1646874000, 1646877600],
            'open': [40000.0, 40500.0, 41000.0],
            'high': [40800.0, 41200.0, 41500.0],
            'low': [39800.0, 40300.0, 40800.0],
            'close': [40500.0, 41000.0, 41200.0],
            'volume': [100.0, 120.0, 90.0]
        })
        
        # Generate a signal
        signal = strategy.generate_signal(data)
        
        # Test the signal
        assert signal["type"] == SignalType.HOLD
        assert signal["price"] == 41200.0


class TestParameterTypes:
    """Tests for parameter-related type definitions."""
    
    def test_param_dict_operations(self):
        """Test ParamDict operations and usage patterns."""
        # Create a parameter dictionary
        params: ParamDict = {
            "fast_period": 10,
            "slow_period": 30,
            "signal_threshold": 0.5,
            "use_close_price": True,
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "advanced_settings": {
                "max_lookback": 100,
                "min_volume": 1000.0
            }
        }
        
        # Test accessing parameters
        assert params["fast_period"] == 10
        assert params["slow_period"] == 30
        assert params["signal_threshold"] == 0.5
        assert params["use_close_price"] is True
        assert "BTC/USDT" in params["symbols"]
        assert params["advanced_settings"]["max_lookback"] == 100
        
        # Test modifying parameters
        params["fast_period"] = 5
        assert params["fast_period"] == 5
        
        # Test adding new parameters
        params["new_param"] = "value"
        assert params["new_param"] == "value"
        
        # Test nested modification
        params["advanced_settings"]["max_lookback"] = 200
        assert params["advanced_settings"]["max_lookback"] == 200
    
    def test_bounded_numeric_types(self):
        """Test BoundedFloat and BoundedInt types."""
        # Test BoundedFloat
        bf = BoundedFloat(0.0, 1.0, 0.5)
        assert bf.value == 0.5
        assert bf.min_value == 0.0
        assert bf.max_value == 1.0
        
        # Test BoundedInt
        bi = BoundedInt(1, 100, 50)
        assert bi.value == 50
        assert bi.min_value == 1
        assert bi.max_value == 100
        
        # Test validation on initialization
        with pytest.raises(ValueError):
            BoundedFloat(0.0, 1.0, 1.5)  # Value exceeds max
        
        with pytest.raises(ValueError):
            BoundedInt(1, 100, 0)  # Value below min
        
        # Test string representation
        assert str(bf) == "BoundedFloat(0.0, 1.0, 0.5)" or repr(bf) == "BoundedFloat(0.0, 1.0, 0.5)"
        assert str(bi) == "BoundedInt(1, 100, 50)" or repr(bi) == "BoundedInt(1, 100, 50)"


class TestResultTypes:
    """Tests for result-related type definitions."""
    
    def test_result_type_with_success(self):
        """Test Result type with successful operations."""
        # Create a success result
        result: Result[int] = Success(42)
        
        # Test result properties
        assert result.is_success()
        assert not result.is_failure()
        
        # Test unwrapping
        assert result.unwrap() == 42
        assert result.unwrap_or(0) == 42
        
        # Test mapping
        mapped_result = result.map(lambda x: x * 2)
        assert mapped_result.is_success()
        assert mapped_result.unwrap() == 84
        
        # Test error unwrapping (should raise)
        with pytest.raises(ValueError):
            result.unwrap_error()
    
    def test_result_type_with_failure(self):
        """Test Result type with failed operations."""
        # Create an error
        error = ValueError("Test error")
        
        # Create a failure result
        result: Result[int] = Failure(error)
        
        # Test result properties
        assert not result.is_success()
        assert result.is_failure()
        
        # Test unwrapping
        with pytest.raises(ValueError):
            result.unwrap()
        
        assert result.unwrap_or(0) == 0
        
        # Test error unwrapping
        assert result.unwrap_error() == error
        
        # Test mapping (should not change the error)
        mapped_result = result.map(lambda x: x * 2)
        assert mapped_result.is_failure()
        assert mapped_result.unwrap_error() == error
    
    def test_either_monad_operations(self):
        """Test Either monad operations."""
        # Create a right (success) Either
        right: Either = Either.right(42)
        
        # Test Either properties
        assert right.is_right()
        assert not right.is_left()
        
        # Test unwrapping
        assert right.unwrap_right() == 42
        
        with pytest.raises(ValueError):
            right.unwrap_left()
        
        # Test mapping
        mapped_right = right.map(lambda x: x * 2)
        assert mapped_right.is_right()
        assert mapped_right.unwrap_right() == 84
        
        # Create a left (error) Either
        error = ValueError("Test error")
        left: Either = Either.left(error)
        
        # Test Either properties
        assert not left.is_right()
        assert left.is_left()
        
        # Test unwrapping
        assert left.unwrap_left() == error
        
        with pytest.raises(ValueError):
            left.unwrap_right()
        
        # Test mapping (should not change the error)
        mapped_left = left.map(lambda x: x * 2)
        assert mapped_left.is_left()
        assert mapped_left.unwrap_left() == error
        
        # Test binding
        def double_if_even(x: int) -> Either:
            if x % 2 == 0:
                return Either.right(x * 2)
            else:
                return Either.left(ValueError("Odd number"))
        
        bound_right = right.bind(double_if_even)
        assert bound_right.is_right()
        assert bound_right.unwrap_right() == 84
        
        odd_right = Either.right(43)
        bound_odd = odd_right.bind(double_if_even)
        assert bound_odd.is_left()
        assert isinstance(bound_odd.unwrap_left(), ValueError)


class TestTypeUtilities:
    """Tests for type utility functions."""
    
    def test_to_timestamp_with_different_inputs(self):
        """Test to_timestamp function with different input types."""
        # Test with datetime
        dt = datetime(2022, 3, 10, 12, 0, 0)
        ts = to_timestamp(dt)
        assert isinstance(ts, float)
        # Don't test exact timestamp value as it depends on timezone
        
        # Test with date
        d = dt.date()
        ts = to_timestamp(d)
        assert isinstance(ts, float)
        
        # Test with existing timestamp
        ts1 = 1646913600.0
        ts2 = to_timestamp(ts1)
        assert ts2 == ts1
        
        # Test with millisecond timestamp
        ts_ms = 1646913600000
        ts = to_timestamp(ts_ms, unit='ms')
        assert abs(ts - 1646913600) < 0.001
    
    def test_from_timestamp_with_different_inputs(self):
        """Test from_timestamp function with different input types."""
        # Test with second timestamp
        ts = 1646913600.0
        dt = from_timestamp(ts)
        assert isinstance(dt, datetime)
        
        # Convert back to timestamp to compare (avoiding timezone issues)
        ts2 = dt.timestamp()
        assert abs(ts - ts2) < 1  # Allow for timezone differences
        
        # Test with millisecond timestamp
        ts_ms = 1646913600000
        dt = from_timestamp(ts_ms / 1000)
        assert isinstance(dt, datetime)
        
        # Test with string timestamp
        ts_str = "1646913600"
        dt = from_timestamp(ts_str)
        assert isinstance(dt, datetime)
        
        # Test with invalid unit
        with pytest.raises(ValueError):
            from_timestamp(ts, unit='invalid')
    
    def test_ensure_datetime_with_different_inputs(self):
        """Test ensure_datetime function with different input types."""
        # Reference datetime
        ref_dt = datetime(2022, 3, 10, 12, 0, 0)
        
        # Test with datetime
        dt1 = ensure_datetime(ref_dt)
        assert dt1 == ref_dt
        
        # Test with timestamp (seconds)
        ts = ref_dt.timestamp()
        dt2 = ensure_datetime(ts)
        assert abs((dt2 - ref_dt).total_seconds()) < 1  # Allow for timezone differences
        
        # Test with timestamp (milliseconds)
        ts_ms = int(ref_dt.timestamp() * 1000)
        dt3 = ensure_datetime(ts_ms)
        assert abs((dt3 - ref_dt).total_seconds()) < 1  # Allow for timezone differences
        
        # Test with ISO format string
        iso_str = ref_dt.isoformat()
        dt4 = ensure_datetime(iso_str)
        assert abs((dt4 - ref_dt).total_seconds()) < 1  # Allow for timezone differences
        
        # Test with timestamp string
        ts_str = str(ref_dt.timestamp())
        dt5 = ensure_datetime(ts_str)
        assert abs((dt5 - ref_dt).total_seconds()) < 1  # Allow for timezone differences
    
    def test_ensure_timedelta_with_different_inputs(self):
        """Test ensure_timedelta function with different input types."""
        # Test with timedelta
        td1 = timedelta(days=1, hours=2, minutes=3, seconds=4)
        td1_result = ensure_timedelta(td1)
        assert td1_result == td1
        
        # Test with seconds
        seconds = 3600  # 1 hour
        td2 = ensure_timedelta(seconds)
        assert td2 == timedelta(seconds=seconds)
        
        # Test with dictionary
        td_dict = {'days': 1, 'hours': 2, 'minutes': 3, 'seconds': 4}
        td3 = ensure_timedelta(td_dict)
        assert td3 == timedelta(days=1, hours=2, minutes=3, seconds=4)
        
        # Test with string format
        td_str = "1d2h3m4s"
        td4 = ensure_timedelta(td_str)
        assert td4 == timedelta(days=1, hours=2, minutes=3, seconds=4)
        
        # Test with invalid string
        try:
            ensure_timedelta("invalid")
            pytest.fail("Should have raised ValueError")
        except ValueError:
            pass  # Expected behavior


class TestTypeAnnotationDocumentation:
    """Tests for type annotation documentation."""
    
    def test_type_annotation_docstrings(self):
        """Test that type definitions have proper docstrings."""
        # Check enum classes
        for enum_class in [PriceType, OrderType, OrderSide, OrderStatus, TimeInForce, 
                          PositionSide, PositionType, SignalType, ResultType]:
            assert enum_class.__doc__ is not None
            assert len(enum_class.__doc__) > 0
        
        # Check class docstrings
        for cls in [BoundedFloat, BoundedInt, Result, Success, Failure, Either]:
            assert cls.__doc__ is not None
            assert len(cls.__doc__) > 0
        
        # Check method docstrings for a sample class
        for method_name in ['is_success', 'is_failure', 'unwrap', 'unwrap_or', 'unwrap_error', 'map']:
            method = getattr(Success, method_name)
            assert method.__doc__ is not None
            assert len(method.__doc__) > 0
        
        # Check utility function docstrings
        for func in [to_timestamp, from_timestamp, ensure_datetime, ensure_timedelta]:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 0
            
            # Check that the docstring includes parameter and return type info
            assert ':param' in func.__doc__
            assert ':return:' in func.__doc__
    
    def test_type_hint_comments(self):
        """Test that type aliases have explanatory comments."""
        # This is a bit harder to test programmatically, so we'll check the module source code
        module_source = inspect.getsource(sys.modules['abidance.type_defs'])
        
        # Check for comments near type aliases
        type_aliases = ['JSON', 'Timestamp', 'TimestampMS', 'TimeRange', 'DateRange', 
                        'Numeric', 'OrderId', 'PositionId', 'SignalStrength', 'StrategyId']
        
        for alias in type_aliases:
            # Find the line defining the alias
            alias_pattern = f"{alias} = "
            assert alias_pattern in module_source
            
            # Check that there's a comment on the same line
            alias_line = [line for line in module_source.split('\n') if alias_pattern in line][0]
            assert '#' in alias_line
    
    def test_function_docstrings(self):
        """Test that functions have proper docstrings with parameter and return type information."""
        for func in [to_timestamp, from_timestamp, ensure_datetime, ensure_timedelta]:
            docstring = func.__doc__
            
            # Check for parameter documentation
            for param_name in inspect.signature(func).parameters:
                assert f':param {param_name}:' in docstring
                assert f':type {param_name}:' in docstring
            
            # Check for return type documentation
            assert ':return:' in docstring
            assert ':rtype:' in docstring
            
            # Check for raises documentation if applicable
            if 'raise' in docstring.lower():
                assert ':raises' in docstring 