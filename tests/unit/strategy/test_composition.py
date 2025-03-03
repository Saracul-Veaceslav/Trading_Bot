"""
Tests for the strategy composition framework.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from abidance.strategy import (
    Strategy, StrategyConfig, CompositeStrategy, VotingStrategy
)
from abidance.core.domain import SignalType


class MockStrategy(Strategy):
    """Mock strategy for testing composition."""
    
    def __init__(self, config, signal_type=SignalType.HOLD):
        super().__init__(config)
        self.signal_type = signal_type
        self.initialize_called = False
        
    def initialize(self) -> None:
        self.initialize_called = True
        
    def analyze(self, symbol, data):
        return {"analyzed": True, "symbol": symbol}
        
    def generate_signals(self, symbol, analysis):
        return [{
            "symbol": symbol,
            "signal_type": self.signal_type,
            "price": 100.0,
            "timestamp": datetime.now(),
            "confidence": 0.8
        }]


class TestCompositeStrategy:
    """Tests for the CompositeStrategy class."""
    
    @pytest.fixture
    def strategies(self):
        """Create a list of mock strategies."""
        config1 = StrategyConfig(name="mock1", symbols=["BTC/USD"])
        config2 = StrategyConfig(name="mock2", symbols=["BTC/USD"])
        config3 = StrategyConfig(name="mock3", symbols=["BTC/USD"])
        
        return [
            MockStrategy(config1, SignalType.BUY),
            MockStrategy(config2, SignalType.SELL),
            MockStrategy(config3, SignalType.HOLD)
        ]
    
    @pytest.fixture
    def composite_config(self):
        """Create a config for composite strategy."""
        return StrategyConfig(name="composite", symbols=["BTC/USD"])
    
    @pytest.fixture
    def sample_data(self):
        """Create sample market data."""
        dates = [datetime.now() - timedelta(hours=i) for i in range(10)]
        return pd.DataFrame({
            'open': np.random.rand(10) * 100 + 10000,
            'high': np.random.rand(10) * 100 + 10050,
            'low': np.random.rand(10) * 100 + 9950,
            'close': np.random.rand(10) * 100 + 10000,
            'volume': np.random.rand(10) * 1000
        }, index=dates)
    
    def test_init_with_default_weights(self, strategies, composite_config):
        """Test initialization with default weights."""
        composite = CompositeStrategy(composite_config, strategies)
        assert len(composite.weights) == len(strategies)
        assert np.isclose(sum(composite.weights), 1.0)
        assert all(w == 1.0/len(strategies) for w in composite.weights)
    
    def test_init_with_custom_weights(self, strategies, composite_config):
        """Test initialization with custom weights."""
        weights = [0.5, 0.3, 0.2]
        composite = CompositeStrategy(composite_config, strategies, weights)
        assert composite.weights == weights
    
    def test_init_with_invalid_weights_length(self, strategies, composite_config):
        """Test initialization with invalid weights length."""
        weights = [0.5, 0.5]  # Only 2 weights for 3 strategies
        with pytest.raises(ValueError, match="Number of weights must match"):
            CompositeStrategy(composite_config, strategies, weights)
    
    def test_init_with_invalid_weights_sum(self, strategies, composite_config):
        """Test initialization with weights that don't sum to 1."""
        weights = [0.5, 0.3, 0.1]  # Sum is 0.9
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            CompositeStrategy(composite_config, strategies, weights)
    
    def test_initialize(self, strategies, composite_config):
        """Test initialize method calls initialize on all strategies."""
        composite = CompositeStrategy(composite_config, strategies)
        composite.initialize()
        
        for strategy in strategies:
            assert strategy.initialize_called
    
    def test_analyze(self, strategies, composite_config, sample_data):
        """Test analyze method collects results from all strategies."""
        composite = CompositeStrategy(composite_config, strategies)
        result = composite.analyze("BTC/USD", sample_data)
        
        assert "component_analyses" in result
        assert len(result["component_analyses"]) == len(strategies)
        
        for i, strategy in enumerate(strategies):
            strategy_name = f"{strategy.name}_{i}"
            assert strategy_name in result["component_analyses"]
            assert result["component_analyses"][strategy_name]["analyzed"]
    
    def test_generate_signals(self, strategies, composite_config, sample_data):
        """Test generate_signals method combines signals from all strategies."""
        composite = CompositeStrategy(composite_config, strategies)
        analysis = composite.analyze("BTC/USD", sample_data)
        signals = composite.generate_signals("BTC/USD", analysis)
        
        assert len(signals) == 1
        assert "metadata" in signals[0]
        assert "component_signals" in signals[0]["metadata"]
        assert len(signals[0]["metadata"]["component_signals"]) == len(strategies)
    
    def test_calculate_signal_weighted_average(self, strategies, composite_config, sample_data):
        """Test calculate_signal method with weighted average."""
        # Set up strategies with different signals
        strategies[0].signal_type = SignalType.BUY    # Buy with weight 0.6
        strategies[1].signal_type = SignalType.SELL   # Sell with weight 0.3
        strategies[2].signal_type = SignalType.HOLD   # Hold with weight 0.1
        
        weights = [0.6, 0.3, 0.1]
        composite = CompositeStrategy(composite_config, strategies, weights)
        
        # Create signals directly for testing
        signals = [
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.HOLD}
        ]
        
        # Manual calculation: 1*0.6 + (-1)*0.3 + 0*0.1 = 0.3
        # Since 0.3 < 0.5, the expected signal is HOLD
        signal = composite.calculate_signal(None, signals)
        assert signal == SignalType.HOLD
        
        # Test with stronger BUY signals
        signals = [
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.HOLD}
        ]
        # Manual calculation: 1*0.6 + 1*0.3 + 0*0.1 = 0.9
        # Since 0.9 > 0.5, the expected signal is BUY
        signal = composite.calculate_signal(None, signals)
        assert signal == SignalType.BUY
        
        # Test with stronger SELL signals
        signals = [
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.HOLD}
        ]
        # Manual calculation: (-1)*0.6 + (-1)*0.3 + 0*0.1 = -0.9
        # Since -0.9 < -0.5, the expected signal is SELL
        signal = composite.calculate_signal(None, signals)
        assert signal == SignalType.SELL


class TestVotingStrategy:
    """Tests for the VotingStrategy class."""
    
    @pytest.fixture
    def strategies(self):
        """Create a list of mock strategies."""
        config1 = StrategyConfig(name="mock1", symbols=["BTC/USD"])
        config2 = StrategyConfig(name="mock2", symbols=["BTC/USD"])
        config3 = StrategyConfig(name="mock3", symbols=["BTC/USD"])
        config4 = StrategyConfig(name="mock4", symbols=["BTC/USD"])
        config5 = StrategyConfig(name="mock5", symbols=["BTC/USD"])
        
        return [
            MockStrategy(config1, SignalType.BUY),
            MockStrategy(config2, SignalType.BUY),
            MockStrategy(config3, SignalType.SELL),
            MockStrategy(config4, SignalType.SELL),
            MockStrategy(config5, SignalType.HOLD)
        ]
    
    @pytest.fixture
    def voting_config(self):
        """Create a config for voting strategy."""
        return StrategyConfig(name="voting", symbols=["BTC/USD"])
    
    @pytest.fixture
    def sample_data(self):
        """Create sample market data."""
        dates = [datetime.now() - timedelta(hours=i) for i in range(10)]
        return pd.DataFrame({
            'open': np.random.rand(10) * 100 + 10000,
            'high': np.random.rand(10) * 100 + 10050,
            'low': np.random.rand(10) * 100 + 9950,
            'close': np.random.rand(10) * 100 + 10000,
            'volume': np.random.rand(10) * 1000
        }, index=dates)
    
    def test_calculate_signal_equal_weights(self, strategies, voting_config, sample_data):
        """Test voting with equal weights."""
        # 2 BUY, 2 SELL, 1 HOLD with equal weights
        voting = VotingStrategy(voting_config, strategies)
        
        # Create signals directly for testing
        signals = [
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.HOLD}
        ]
        
        # With equal weights (0.2 each), no signal has > 0.5 weight
        signal = voting.calculate_signal(None, signals)
        assert signal == SignalType.HOLD
    
    def test_calculate_signal_weighted_buy(self, strategies, voting_config, sample_data):
        """Test voting with weights favoring buy signals."""
        # 2 BUY, 2 SELL, 1 HOLD with weights favoring BUY
        weights = [0.3, 0.3, 0.15, 0.15, 0.1]  # BUY total: 0.6, SELL total: 0.3
        voting = VotingStrategy(voting_config, strategies, weights)
        
        # Create signals directly for testing
        signals = [
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.HOLD}
        ]
        
        signal = voting.calculate_signal(None, signals)
        assert signal == SignalType.BUY
    
    def test_calculate_signal_weighted_sell(self, strategies, voting_config, sample_data):
        """Test voting with weights favoring sell signals."""
        # 2 BUY, 2 SELL, 1 HOLD with weights favoring SELL
        weights = [0.15, 0.15, 0.3, 0.3, 0.1]  # BUY total: 0.3, SELL total: 0.6
        voting = VotingStrategy(voting_config, strategies, weights)
        
        # Create signals directly for testing
        signals = [
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.BUY},
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.SELL},
            {"signal_type": SignalType.HOLD}
        ]
        
        signal = voting.calculate_signal(None, signals)
        assert signal == SignalType.SELL
    
    def test_calculate_signal_with_provided_signals(self, voting_config):
        """Test voting with explicitly provided signals."""
        voting = VotingStrategy(voting_config, [])  # Empty strategies list
        
        # Create signal dictionaries
        signals = [
            {"signal_type": SignalType.BUY, "confidence": 0.8},
            {"signal_type": SignalType.BUY, "confidence": 0.7},
            {"signal_type": SignalType.SELL, "confidence": 0.6}
        ]
        
        # Set weights manually for the test
        voting.weights = [0.4, 0.3, 0.3]
        signal = voting.calculate_signal(None, signals)
        assert signal == SignalType.BUY
        
        # With weights favoring SELL
        voting.weights = [0.2, 0.2, 0.6]
        signal = voting.calculate_signal(None, signals)
        assert signal == SignalType.SELL 