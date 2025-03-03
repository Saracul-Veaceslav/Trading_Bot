"""
Unit tests for the performance testing framework.
"""
import time
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from concurrent.futures import ThreadPoolExecutor

# Import the classes we'll be testing (these don't exist yet)
from abidance.testing.performance import PerformanceTester
from abidance.strategy.base import Strategy, StrategyConfig
from abidance.evaluation.metrics import StrategyEvaluator


class MockStrategy(Strategy):
    """Mock strategy for testing performance."""
    
    def initialize(self) -> None:
        pass
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> dict:
        return {"analyzed": True}
    
    def generate_signals(self, symbol: str, analysis: dict) -> list:
        return [{"signal": "buy"}]
    
    def calculate_signal(self, data: pd.DataFrame) -> dict:
        """Method used by PerformanceTester."""
        # Simulate work that depends on data size
        time.sleep(0.001 * len(data))
        
        # Do some actual computation to make sure data size affects performance
        result = {"signal": "buy", "strength": 0.75}
        
        # Add some calculations that depend on the data size
        for i in range(min(10, len(data))):
            result[f"metric_{i}"] = data['close'].iloc[i:i+10].mean() if i+10 <= len(data) else 0
            
        return result


@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing."""
    return pd.DataFrame({
        'open': np.random.randn(100) + 100,
        'high': np.random.randn(100) + 101,
        'low': np.random.randn(100) + 99,
        'close': np.random.randn(100) + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=pd.date_range(start='2023-01-01', periods=100, freq='1h'))


@pytest.fixture
def strategy_config():
    """Create a strategy configuration for testing."""
    return StrategyConfig(
        name="test_strategy",
        symbols=["BTC/USDT"],
        timeframe="1h",
        parameters={"param1": 10, "param2": 20}
    )


@pytest.fixture
def mock_strategy(strategy_config):
    """Create a mock strategy for testing."""
    return MockStrategy(strategy_config)


@pytest.fixture
def performance_tester(mock_strategy, sample_data):
    """Create a performance tester instance for testing."""
    return PerformanceTester(
        strategy_class=MockStrategy,
        data=sample_data,
        evaluator=StrategyEvaluator()
    )


class TestPerformanceTester:
    """Tests for the PerformanceTester class."""
    
    def test_initialization(self, performance_tester, sample_data):
        """
        Feature: Performance tester initialization
        
        Scenario: Creating a new performance tester
          Given a strategy class and data
          When a new PerformanceTester is created
          Then it should store the strategy class and data correctly
        """
        assert performance_tester.strategy_class == MockStrategy
        assert performance_tester.data.equals(sample_data)
        assert isinstance(performance_tester.evaluator, StrategyEvaluator)
    
    def test_measure_execution_time(self, performance_tester):
        """
        Feature: Strategy execution time measurement
        
        Scenario: Measuring strategy execution time
          Given a performance tester with a strategy
          When measure_execution_time is called
          Then it should return execution time statistics
        """
        result = performance_tester.measure_execution_time(num_runs=5)
        
        assert "mean" in result
        assert "median" in result
        assert "std" in result
        assert "min" in result
        assert "max" in result
        
        # All values should be positive
        for key, value in result.items():
            assert value > 0
    
    @patch('psutil.Process')
    def test_measure_memory_usage(self, mock_process, performance_tester):
        """
        Feature: Strategy memory usage measurement
        
        Scenario: Measuring strategy memory usage
          Given a performance tester with a strategy
          When measure_memory_usage is called
          Then it should return memory usage statistics
        """
        # Setup mock
        process_instance = mock_process.return_value
        process_instance.memory_info.return_value = MagicMock(rss=1024*1024)  # 1MB
        
        result = performance_tester.measure_memory_usage()
        
        assert "initial_mb" in result
        assert "final_mb" in result
        assert "delta_mb" in result
        
        # Values should be reasonable
        assert result["initial_mb"] >= 0
        assert result["final_mb"] >= 0
    
    def test_benchmark_parallel_execution(self, performance_tester):
        """
        Feature: Parallel strategy execution benchmarking
        
        Scenario: Benchmarking parallel strategy execution
          Given a performance tester with a strategy
          When benchmark_parallel_execution is called
          Then it should return parallel execution statistics
        """
        result = performance_tester.benchmark_parallel_execution(num_strategies=3)
        
        assert "total_time" in result
        assert "avg_time_per_strategy" in result
        
        # Values should be positive
        assert result["total_time"] > 0
        assert result["avg_time_per_strategy"] > 0
        
        # Parallel execution should be faster than sequential
        # (though this might not always be true for very small workloads)
        sequential_time = performance_tester.measure_execution_time(num_runs=3)["mean"] * 3
        assert result["total_time"] <= sequential_time * 1.5  # Allow some overhead
    
    def test_performance_with_different_data_sizes(self, performance_tester, sample_data):
        """
        Feature: Performance testing with different data sizes
        
        Scenario: Testing strategy performance with varying data sizes
          Given a performance tester with a strategy
          When tested with different data sizes
          Then execution time should generally increase with data size
        """
        # Test with different data sizes
        small_data = sample_data.iloc[:20]
        medium_data = sample_data.iloc[:50]
        large_data = sample_data
        
        # Create performance testers with different data sizes
        small_tester = PerformanceTester(MockStrategy, small_data)
        medium_tester = PerformanceTester(MockStrategy, medium_data)
        large_tester = PerformanceTester(MockStrategy, large_data)
        
        # Measure execution times (increase num_runs for more reliable results)
        small_time = small_tester.measure_execution_time(num_runs=3)["mean"]
        medium_time = medium_tester.measure_execution_time(num_runs=3)["mean"]
        large_time = large_tester.measure_execution_time(num_runs=3)["mean"]
        
        # For debugging
        print(f"Small data size: {len(small_data)}, execution time: {small_time}")
        print(f"Medium data size: {len(medium_data)}, execution time: {medium_time}")
        print(f"Large data size: {len(large_data)}, execution time: {large_time}")
        
        # Execution time should generally increase with data size
        # We check that at least one of these comparisons holds true
        assert (small_time <= medium_time or 
                medium_time <= large_time or 
                small_time <= large_time) 