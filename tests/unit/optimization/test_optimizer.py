"""
Tests for the strategy optimizer module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from abidance.optimization.optimizer import StrategyOptimizer, OptimizationResult
from abidance.strategy.base import Strategy


class MockStrategy(Strategy):
    """Mock strategy for testing the optimizer."""
    
    def __init__(self, **kwargs):
        self.params = kwargs
        self.backtest_called = False
    
    def initialize(self):
        pass
    
    def analyze(self, symbol, data):
        return {}
    
    def generate_signals(self, symbol, analysis):
        return []
    
    def backtest(self, data):
        """Mock backtest method that returns a DataFrame with performance based on parameters."""
        self.backtest_called = True
        
        # Create a simple trades DataFrame
        dates = pd.date_range(start='2023-01-01', periods=10)
        trades = pd.DataFrame({
            'timestamp': dates,
            'returns': [
                # Generate returns based on parameters
                0.01 * self.params.get('param1', 0) - 0.005 * self.params.get('param2', 0) + np.random.normal(0, 0.001)
                for _ in range(10)
            ]
        })
        trades.set_index('timestamp', inplace=True)
        
        return trades


def test_optimization_result_dataclass():
    """
    Test the OptimizationResult dataclass.
    
    Feature: OptimizationResult Dataclass
    
    Scenario: Creating and accessing OptimizationResult fields
      Given parameters, metrics, and trades data
      When an OptimizationResult is created
      Then the fields should be accessible and match the input values
    """
    # Arrange
    params = {'param1': 10, 'param2': 5}
    metrics = {'sharpe': 1.5, 'sortino': 2.0}
    trades = pd.DataFrame({'a': [1, 2, 3]})
    
    # Act
    result = OptimizationResult(
        parameters=params,
        performance_metrics=metrics,
        trades=trades
    )
    
    # Assert
    assert result.parameters == params
    assert result.performance_metrics == metrics
    assert result.trades.equals(trades)


def test_generate_parameter_combinations():
    """
    Test parameter combination generation.
    
    Feature: Parameter Combination Generation
    
    Scenario: Generating all possible parameter combinations
      Given parameter ranges for multiple parameters
      When _generate_parameter_combinations is called
      Then all possible combinations should be generated
    """
    # Arrange
    parameter_ranges = {
        'param1': [1, 2, 3],
        'param2': [4, 5]
    }
    
    optimizer = StrategyOptimizer(
        strategy_class=MockStrategy,
        parameter_ranges=parameter_ranges,
        metric_function=lambda x: x['returns'].mean()
    )
    
    # Act
    combinations = list(optimizer._generate_parameter_combinations())
    
    # Assert
    assert len(combinations) == 6  # 3 * 2 = 6 combinations
    
    # Check that all expected combinations are present
    expected_combinations = [
        {'param1': 1, 'param2': 4},
        {'param1': 1, 'param2': 5},
        {'param1': 2, 'param2': 4},
        {'param1': 2, 'param2': 5},
        {'param1': 3, 'param2': 4},
        {'param1': 3, 'param2': 5}
    ]
    
    for expected in expected_combinations:
        assert expected in combinations


def test_evaluate_parameters():
    """
    Test strategy evaluation with different parameters.
    
    Feature: Strategy Parameter Evaluation
    
    Scenario: Evaluating a strategy with specific parameters
      Given a strategy class and parameters
      When _evaluate_parameters is called
      Then the strategy should be instantiated with the parameters and backtest should be called
    """
    # Arrange
    params = {'param1': 10, 'param2': 5}
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=10),
        'open': np.random.rand(10) * 100,
        'high': np.random.rand(10) * 100,
        'low': np.random.rand(10) * 100,
        'close': np.random.rand(10) * 100,
        'volume': np.random.rand(10) * 1000
    })
    data.set_index('timestamp', inplace=True)
    
    optimizer = StrategyOptimizer(
        strategy_class=MockStrategy,
        parameter_ranges={'param1': [5, 10], 'param2': [3, 5]},
        metric_function=lambda x: x['returns'].mean()
    )
    
    # Act
    result = optimizer._evaluate_parameters(params, data)
    
    # Assert
    assert isinstance(result, OptimizationResult)
    assert result.parameters == params
    assert 'metric' in result.performance_metrics
    assert isinstance(result.trades, pd.DataFrame)
    assert not result.trades.empty


def test_optimize_max_iterations():
    """
    Test that optimize respects the max_iterations parameter.
    
    Feature: Optimization with Maximum Iterations
    
    Scenario: Limiting the number of parameter combinations to evaluate
      Given parameter ranges that would generate many combinations
      When optimize is called with a max_iterations limit
      Then only the specified number of combinations should be evaluated
    """
    # Arrange
    parameter_ranges = {
        'param1': list(range(10)),  # 10 values
        'param2': list(range(10))   # 10 values
    }
    # This would generate 100 combinations, but we'll limit to 5
    
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=10),
        'open': np.random.rand(10) * 100,
        'high': np.random.rand(10) * 100,
        'low': np.random.rand(10) * 100,
        'close': np.random.rand(10) * 100,
        'volume': np.random.rand(10) * 1000
    })
    data.set_index('timestamp', inplace=True)
    
    optimizer = StrategyOptimizer(
        strategy_class=MockStrategy,
        parameter_ranges=parameter_ranges,
        metric_function=lambda x: x['returns'].mean()
    )
    
    # Act
    results = optimizer.optimize(data, max_iterations=5, n_jobs=1)
    
    # Assert
    assert len(results) == 5


def test_parallel_optimization_execution():
    """
    Test parallel optimization execution.
    
    Feature: Parallel Optimization Execution
    
    Scenario: Running optimization in parallel
      Given parameter ranges and multiple CPU cores
      When optimize is called with n_jobs > 1
      Then the optimization should run in parallel and return correct results
    """
    # Arrange
    parameter_ranges = {
        'param1': [1, 2, 3],
        'param2': [4, 5]
    }
    
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=10),
        'open': np.random.rand(10) * 100,
        'high': np.random.rand(10) * 100,
        'low': np.random.rand(10) * 100,
        'close': np.random.rand(10) * 100,
        'volume': np.random.rand(10) * 1000
    })
    data.set_index('timestamp', inplace=True)
    
    optimizer = StrategyOptimizer(
        strategy_class=MockStrategy,
        parameter_ranges=parameter_ranges,
        metric_function=lambda x: x['returns'].mean()
    )
    
    # Act
    results = optimizer.optimize(data, n_jobs=2)
    
    # Assert
    assert len(results) == 6  # All combinations should be evaluated
    
    # Check that results are sorted by performance
    for i in range(len(results) - 1):
        assert results[i].performance_metrics['metric'] >= results[i+1].performance_metrics['metric']


def test_result_sorting_and_ranking():
    """
    Test result sorting and ranking.
    
    Feature: Result Sorting and Ranking
    
    Scenario: Sorting optimization results by performance
      Given multiple optimization results with different performance metrics
      When optimize returns the results
      Then the results should be sorted in descending order by the performance metric
    """
    # Create a mock optimizer with predetermined results
    optimizer = StrategyOptimizer(
        strategy_class=MockStrategy,
        parameter_ranges={'param1': [1, 2], 'param2': [3, 4]},
        metric_function=lambda x: 0  # Dummy function, not used in this test
    )
    
    # Create mock results with known metrics
    mock_results = [
        OptimizationResult(
            parameters={'param1': 1, 'param2': 3},
            performance_metrics={'metric': 0.5},
            trades=pd.DataFrame()
        ),
        OptimizationResult(
            parameters={'param1': 2, 'param2': 3},
            performance_metrics={'metric': 0.8},
            trades=pd.DataFrame()
        ),
        OptimizationResult(
            parameters={'param1': 1, 'param2': 4},
            performance_metrics={'metric': 0.2},
            trades=pd.DataFrame()
        ),
        OptimizationResult(
            parameters={'param1': 2, 'param2': 4},
            performance_metrics={'metric': 0.6},
            trades=pd.DataFrame()
        )
    ]
    
    # Mock the _evaluate_parameters method to return our predetermined results
    with patch.object(optimizer, '_evaluate_parameters') as mock_evaluate:
        mock_evaluate.side_effect = mock_results
        
        # Mock the _generate_parameter_combinations method
        with patch.object(optimizer, '_generate_parameter_combinations') as mock_generate:
            mock_generate.return_value = [
                {'param1': 1, 'param2': 3},
                {'param1': 2, 'param2': 3},
                {'param1': 1, 'param2': 4},
                {'param1': 2, 'param2': 4}
            ]
            
            # Act
            results = optimizer.optimize(pd.DataFrame(), n_jobs=1)
    
    # Assert
    assert len(results) == 4
    
    # Check that results are sorted by performance metric in descending order
    assert results[0].performance_metrics['metric'] == 0.8
    assert results[1].performance_metrics['metric'] == 0.6
    assert results[2].performance_metrics['metric'] == 0.5
    assert results[3].performance_metrics['metric'] == 0.2
    
    # Check that the parameters match the expected order
    assert results[0].parameters == {'param1': 2, 'param2': 3}
    assert results[1].parameters == {'param1': 2, 'param2': 4}
    assert results[2].parameters == {'param1': 1, 'param2': 3}
    assert results[3].parameters == {'param1': 1, 'param2': 4} 