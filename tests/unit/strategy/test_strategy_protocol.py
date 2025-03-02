"""
Tests for the strategy protocol implementation.

This module tests that existing strategy implementations satisfy the Strategy protocol.
"""

import pytest
import pandas as pd
from typing import Dict, Any, List, Optional, cast

from abidance.strategy.protocols import Strategy, StrategyFactory
from abidance.strategy.base import StrategyConfig
from abidance.strategy.sma import SMAStrategy, SMAConfig
from abidance.strategy.rsi import RSIStrategy, RSIConfig
from abidance.trading.order import Order


class TestStrategyProtocol:
    """Tests for the Strategy protocol."""
    
    def test_sma_strategy_satisfies_protocol(self):
        """Test that SMAStrategy satisfies the Strategy protocol."""
        # Create a strategy instance
        config = SMAConfig(
            name="SMA Test",
            symbols=["BTC/USDT"],
            timeframe="1h",
            fast_period=5,
            slow_period=20,
            volume_factor=1.5
        )
        strategy = SMAStrategy(config)
        
        # Check that the strategy satisfies the protocol
        assert isinstance(strategy, Strategy)
    
    def test_rsi_strategy_satisfies_protocol(self):
        """Test that RSIStrategy satisfies the Strategy protocol."""
        # Create a strategy instance
        config = RSIConfig(
            name="RSI Test",
            symbols=["BTC/USDT"],
            timeframe="1h",
            rsi_period=14,
            oversold_threshold=30,
            overbought_threshold=70
        )
        strategy = RSIStrategy(config)
        
        # Check that the strategy satisfies the protocol
        assert isinstance(strategy, Strategy)
    
    def test_protocol_runtime_checking(self):
        """Test that the protocol works with runtime type checking."""
        # Create a strategy instance
        config = SMAConfig(
            name="SMA Test",
            symbols=["BTC/USDT"],
            timeframe="1h",
            fast_period=5,
            slow_period=20,
            volume_factor=1.5
        )
        strategy = SMAStrategy(config)
        
        # Use the strategy through the protocol
        protocol_strategy = cast(Strategy, strategy)
        
        # Check that we can access attributes and methods through the protocol
        assert protocol_strategy.name == "SMA Test"
        assert protocol_strategy.symbols == ["BTC/USDT"]
        assert protocol_strategy.timeframe == "1h"
        assert isinstance(protocol_strategy.parameters, dict)
        assert protocol_strategy.is_running is False
    
    def test_protocol_documentation(self):
        """Test that protocol documentation is accessible."""
        # Check that the protocol has a docstring
        assert Strategy.__doc__ is not None
        
        # Check that method docstrings are accessible
        assert Strategy.initialize.__doc__ is not None
        assert Strategy.analyze.__doc__ is not None
        assert Strategy.generate_signals.__doc__ is not None
        assert Strategy.create_order.__doc__ is not None
        assert Strategy.update.__doc__ is not None
        assert Strategy.start.__doc__ is not None
        assert Strategy.stop.__doc__ is not None
        assert Strategy.get_state.__doc__ is not None
        assert Strategy.set_state.__doc__ is not None


class MockStrategy:
    """Mock strategy implementation for testing."""
    
    def __init__(self, name: str, symbols: List[str], timeframe: str):
        self.name = name
        self.symbols = symbols
        self.timeframe = timeframe
        self.parameters = {}
        self.is_running = False
    
    def initialize(self) -> None:
        """Initialize the strategy."""
        pass
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market data."""
        return {"analyzed": True}
    
    def generate_signals(self, symbol: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals."""
        return [{"signal": "buy"}]
    
    def create_order(self, signal: Dict[str, Any]) -> Optional[Order]:
        """Create an order from a signal."""
        return None
    
    def update(self, symbol: str, data: pd.DataFrame) -> List[Order]:
        """Update the strategy with new data."""
        return []
    
    def start(self) -> None:
        """Start the strategy."""
        self.is_running = True
    
    def stop(self) -> None:
        """Stop the strategy."""
        self.is_running = False
    
    def get_state(self) -> Dict[str, Any]:
        """Get the strategy state."""
        return {"name": self.name}
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the strategy state."""
        pass


class TestCustomStrategyImplementation:
    """Tests for custom strategy implementations."""
    
    def test_custom_strategy_satisfies_protocol(self):
        """Test that a custom strategy satisfies the Strategy protocol."""
        # Create a custom strategy
        strategy = MockStrategy("Custom", ["BTC/USDT"], "1h")
        
        # Check that it satisfies the protocol
        assert isinstance(strategy, Strategy)
    
    def test_custom_strategy_methods(self):
        """Test that custom strategy methods work as expected."""
        # Create a custom strategy
        strategy = MockStrategy("Custom", ["BTC/USDT"], "1h")
        
        # Test methods
        strategy.initialize()
        assert strategy.analyze("BTC/USDT", pd.DataFrame()) == {"analyzed": True}
        assert strategy.generate_signals("BTC/USDT", {}) == [{"signal": "buy"}]
        assert strategy.create_order({}) is None
        assert strategy.update("BTC/USDT", pd.DataFrame()) == []
        
        strategy.start()
        assert strategy.is_running is True
        
        strategy.stop()
        assert strategy.is_running is False
        
        assert strategy.get_state() == {"name": "Custom"}
        strategy.set_state({})


class MockStrategyFactory:
    """Mock strategy factory implementation for testing."""
    
    def create_strategy(self, config: Dict[str, Any]) -> Strategy:
        """Create a strategy from configuration."""
        return MockStrategy(
            name=config.get("name", "Default"),
            symbols=config.get("symbols", ["BTC/USDT"]),
            timeframe=config.get("timeframe", "1h")
        )


class TestStrategyFactoryProtocol:
    """Tests for the StrategyFactory protocol."""
    
    def test_factory_satisfies_protocol(self):
        """Test that a factory satisfies the StrategyFactory protocol."""
        # Create a factory
        factory = MockStrategyFactory()
        
        # Check that it satisfies the protocol
        assert isinstance(factory, StrategyFactory)
    
    def test_factory_creates_strategy(self):
        """Test that the factory creates a strategy."""
        # Create a factory
        factory = MockStrategyFactory()
        
        # Create a strategy
        config = {"name": "Test", "symbols": ["ETH/USDT"], "timeframe": "4h"}
        strategy = factory.create_strategy(config)
        
        # Check that the strategy was created correctly
        assert isinstance(strategy, Strategy)
        assert strategy.name == "Test"
        assert strategy.symbols == ["ETH/USDT"]
        assert strategy.timeframe == "4h" 