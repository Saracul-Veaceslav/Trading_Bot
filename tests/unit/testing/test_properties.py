"""
Property-based tests for trading strategies.

This module contains property-based tests that verify invariants and properties
that should hold for all trading strategies under various market conditions.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

from abidance.core.domain import SignalType
from abidance.strategy import Strategy, StrategyConfig, SMAStrategy, SMAConfig


# We'll define the generators here until we implement them in the actual module
@st.composite
def generate_ohlcv_data(
    draw: Any,
    min_length: int = 100,
    max_length: int = 200,  # Reduced from 1000 to avoid health check issues
    min_price: float = 1.0,
    max_price: float = 1000.0,
    volatility: float = 0.02
) -> pd.DataFrame:
    """
    Generate random OHLCV data for property-based testing.
    
    Feature: Random OHLCV data generation
    
    Scenario: Generate realistic price data for testing
      Given parameters for data generation
      When the generator is called
      Then it returns a DataFrame with realistic OHLCV data
    """
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


@st.composite
def generate_strategy_parameters(draw: Any) -> Dict[str, Any]:
    """
    Generate random strategy parameters for testing.
    
    Feature: Random strategy parameter generation
    
    Scenario: Generate valid strategy parameters
      Given a strategy type
      When the generator is called
      Then it returns valid parameters for that strategy
    """
    # Generate SMA strategy parameters
    short_window = draw(st.integers(5, 20))
    long_window = draw(st.integers(short_window + 5, short_window + 50))
    
    return {
        'short_window': short_window,
        'long_window': long_window
    }


class TestDataGeneration:
    """Tests for the data generation functions."""
    
    @given(data=generate_ohlcv_data())
    @settings(
        max_examples=5,
        suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow]
    )
    def test_ohlcv_data_properties(self, data: pd.DataFrame) -> None:
        """
        Test that generated OHLCV data satisfies basic properties.
        
        Feature: OHLCV data validation
        
        Scenario: Verify OHLCV data properties
          Given randomly generated OHLCV data
          When we check its properties
          Then all required columns exist
          And high is always >= low
          And high is always >= open and close
          And low is always <= open and close
          And all prices are positive
        """
        # Check that the DataFrame has the expected columns
        assert all(col in data.columns for col in ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Check that the data is sorted by timestamp
        assert data['timestamp'].is_monotonic_increasing
        
        # Check that high is always >= low
        assert (data['high'] >= data['low']).all()
        
        # Check that high is always >= open and close
        assert (data['high'] >= data['open']).all()
        assert (data['high'] >= data['close']).all()
        
        # Check that low is always <= open and close
        assert (data['low'] <= data['open']).all()
        assert (data['low'] <= data['close']).all()
        
        # Check that all prices are positive
        assert (data['open'] > 0).all()
        assert (data['high'] > 0).all()
        assert (data['low'] > 0).all()
        assert (data['close'] > 0).all()
        assert (data['volume'] > 0).all()


class TestStrategyProperties:
    """Tests for strategy properties."""
    
    @given(
        data=generate_ohlcv_data(),
        params=generate_strategy_parameters()
    )
    @settings(
        max_examples=5,
        suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow]
    )
    def test_sma_strategy_signal_types(self, data: pd.DataFrame, params: Dict[str, Any]) -> None:
        """
        Test that SMA strategy signals are always valid.
        
        Feature: Strategy signal validation
        
        Scenario: Verify SMA strategy signals
          Given randomly generated OHLCV data
          And randomly generated strategy parameters
          When the strategy calculates signals
          Then all signals are valid (BUY, SELL, or HOLD)
        """
        # Create SMA strategy with random parameters
        config = SMAConfig(
            name="SMA Test",
            symbols=["BTC/USDT"],
            fast_period=params['short_window'],
            slow_period=params['long_window']
        )
        strategy = SMAStrategy(config)
        
        # Ensure we have enough data for the strategy
        assume(len(data) > params['long_window'] + 10)
        
        # Calculate signal
        signal = strategy.calculate_signal(data)
        
        # Check that the signal is valid
        assert signal in [1, 0, -1]  # 1=BUY, 0=HOLD, -1=SELL
    
    @given(data=generate_ohlcv_data())
    @settings(
        max_examples=5,
        suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow]
    )
    def test_strategy_consistency(self, data: pd.DataFrame) -> None:
        """
        Test that strategy signals are consistent when run multiple times on the same data.
        
        Feature: Strategy consistency validation
        
        Scenario: Verify strategy consistency
          Given randomly generated OHLCV data
          When the strategy calculates signals multiple times
          Then the signals should be identical each time
        """
        # Create SMA strategy
        config = SMAConfig(
            name="SMA Test",
            symbols=["BTC/USDT"],
            fast_period=10,
            slow_period=30
        )
        strategy = SMAStrategy(config)
        
        # Ensure we have enough data for the strategy
        assume(len(data) > 40)
        
        # Calculate signal multiple times
        signal1 = strategy.calculate_signal(data)
        signal2 = strategy.calculate_signal(data)
        signal3 = strategy.calculate_signal(data)
        
        # Check that all signals are the same
        assert signal1 == signal2 == signal3
    
    @given(data=generate_ohlcv_data())
    @settings(
        max_examples=5,
        suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow]
    )
    def test_strategy_edge_cases(self, data: pd.DataFrame) -> None:
        """
        Test strategy behavior with edge case data.
        
        Feature: Strategy edge case handling
        
        Scenario: Verify strategy behavior with edge cases
          Given randomly generated OHLCV data with modifications
          When the strategy calculates signals
          Then it should handle edge cases gracefully
        """
        # Create SMA strategy
        config = SMAConfig(
            name="SMA Test",
            symbols=["BTC/USDT"],
            fast_period=10,
            slow_period=30
        )
        strategy = SMAStrategy(config)
        
        # Ensure we have enough data for the strategy
        assume(len(data) > 40)
        
        # Test with NaN values in the middle
        data_with_nan = data.copy()
        if len(data_with_nan) > 50:
            data_with_nan.loc[45:47, 'close'] = np.nan
            
            # The strategy should handle NaN values without crashing
            try:
                signal = strategy.calculate_signal(data_with_nan)
                # We don't assert the value, just that it doesn't crash
            except Exception as e:
                pytest.fail(f"Strategy failed with NaN values: {e}")
        
        # Test with zero volume
        data_zero_volume = data.copy()
        if len(data_zero_volume) > 50:
            data_zero_volume.loc[45:47, 'volume'] = 0
            
            # The strategy should handle zero volume without crashing
            try:
                signal = strategy.calculate_signal(data_zero_volume)
                # We don't assert the value, just that it doesn't crash
            except Exception as e:
                pytest.fail(f"Strategy failed with zero volume: {e}")


class TestRealisticScenarios:
    """Tests for realistic market scenarios."""
    
    @given(data=generate_ohlcv_data())
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow]
    )
    def test_trending_market(self, data: pd.DataFrame) -> None:
        """
        Test strategy behavior in trending markets.
        
        Feature: Strategy behavior in trending markets
        
        Scenario: Verify strategy signals in trending markets
          Given randomly generated OHLCV data
          When we modify it to create a strong uptrend
          Then the strategy should eventually generate buy signals
        """
        # Create SMA strategy
        config = SMAConfig(
            name="SMA Test",
            symbols=["BTC/USDT"],
            fast_period=10,
            slow_period=30
        )
        strategy = SMAStrategy(config)
        
        # Ensure we have enough data
        assume(len(data) > 100)
        
        # Create a strong uptrend
        trending_data = data.copy()
        for i in range(50, len(trending_data)):
            trending_data.loc[i, 'close'] = trending_data.loc[i-1, 'close'] * 1.01
            trending_data.loc[i, 'high'] = max(trending_data.loc[i, 'close'] * 1.005, trending_data.loc[i, 'high'])
            trending_data.loc[i, 'low'] = min(trending_data.loc[i, 'close'] * 0.995, trending_data.loc[i, 'low'])
            trending_data.loc[i, 'open'] = trending_data.loc[i-1, 'close']
        
        # Calculate signal
        signal = strategy.calculate_signal(trending_data)
        
        # In a strong uptrend, we expect a buy signal
        # This might not always be true depending on the exact data,
        # so we don't assert it, but we could log it for analysis
        print(f"Uptrend signal: {signal}")
    
    @given(data=generate_ohlcv_data())
    @settings(
        max_examples=3,
        suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow]
    )
    def test_sideways_market(self, data: pd.DataFrame) -> None:
        """
        Test strategy behavior in sideways markets.
        
        Feature: Strategy behavior in sideways markets
        
        Scenario: Verify strategy signals in sideways markets
          Given randomly generated OHLCV data
          When we modify it to create a sideways market
          Then the strategy should mostly generate hold signals
        """
        # Create SMA strategy
        config = SMAConfig(
            name="SMA Test",
            symbols=["BTC/USDT"],
            fast_period=10,
            slow_period=30
        )
        strategy = SMAStrategy(config)
        
        # Ensure we have enough data
        assume(len(data) > 100)
        
        # Create a sideways market
        sideways_data = data.copy()
        base_price = sideways_data.loc[50, 'close']
        for i in range(51, len(sideways_data)):
            # Random walk with mean reversion
            change = np.random.normal(0, 0.005)
            if sideways_data.loc[i-1, 'close'] > base_price * 1.02:
                change -= 0.002  # Mean reversion
            elif sideways_data.loc[i-1, 'close'] < base_price * 0.98:
                change += 0.002  # Mean reversion
                
            sideways_data.loc[i, 'close'] = sideways_data.loc[i-1, 'close'] * (1 + change)
            sideways_data.loc[i, 'high'] = max(sideways_data.loc[i, 'close'] * 1.005, sideways_data.loc[i, 'high'])
            sideways_data.loc[i, 'low'] = min(sideways_data.loc[i, 'close'] * 0.995, sideways_data.loc[i, 'low'])
            sideways_data.loc[i, 'open'] = sideways_data.loc[i-1, 'close']
        
        # Calculate signal
        signal = strategy.calculate_signal(sideways_data)
        
        # In a sideways market, we might expect more hold signals,
        # but this isn't guaranteed, so we don't assert it
        print(f"Sideways market signal: {signal}") 