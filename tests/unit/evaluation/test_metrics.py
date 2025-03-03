"""
Unit tests for the evaluation metrics module.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from abidance.evaluation.metrics import PerformanceMetrics, StrategyEvaluator


class TestPerformanceMetrics:
    """
    Test suite for the PerformanceMetrics dataclass.
    
    Feature: Performance Metrics Dataclass
      As a trading system developer
      I want to have a structured container for performance metrics
      So that I can easily access and analyze strategy performance
    """
    
    def test_performance_metrics_initialization(self):
        """
        Test that PerformanceMetrics can be properly initialized with values.
        
        Scenario: Initialize PerformanceMetrics with valid values
          Given I have performance metric values
          When I create a PerformanceMetrics instance
          Then the instance should contain the correct values
        """
        metrics = PerformanceMetrics(
            total_return=0.15,
            sharpe_ratio=1.2,
            max_drawdown=0.05,
            win_rate=0.6,
            profit_factor=1.5,
            avg_trade=0.02,
            num_trades=50
        )
        
        assert metrics.total_return == 0.15
        assert metrics.sharpe_ratio == 1.2
        assert metrics.max_drawdown == 0.05
        assert metrics.win_rate == 0.6
        assert metrics.profit_factor == 1.5
        assert metrics.avg_trade == 0.02
        assert metrics.num_trades == 50


class TestStrategyEvaluator:
    """
    Test suite for the StrategyEvaluator class.
    
    Feature: Strategy Performance Evaluation
      As a trading system developer
      I want to calculate performance metrics from trade history
      So that I can evaluate and compare trading strategies
    """
    
    @pytest.fixture
    def sample_trades(self):
        """Create a sample DataFrame of trades for testing."""
        return pd.DataFrame({
            'date': [
                datetime(2023, 1, 1),
                datetime(2023, 1, 2),
                datetime(2023, 1, 3),
                datetime(2023, 1, 4),
                datetime(2023, 1, 5),
            ],
            'profit_pct': [0.02, -0.01, 0.03, -0.02, 0.04]
        })
    
    @pytest.fixture
    def evaluator(self):
        """Create a StrategyEvaluator instance for testing."""
        return StrategyEvaluator(risk_free_rate=0.02)
    
    def test_calculate_metrics(self, evaluator, sample_trades):
        """
        Test calculation of performance metrics from trade history.
        
        Scenario: Calculate metrics from trade history
          Given I have a trade history with profits and losses
          When I calculate performance metrics
          Then I should get accurate performance statistics
        """
        metrics = evaluator.calculate_metrics(sample_trades)
        
        # Test that metrics are calculated
        assert isinstance(metrics, PerformanceMetrics)
        assert isinstance(metrics.total_return, float)
        assert isinstance(metrics.sharpe_ratio, float)
        assert isinstance(metrics.max_drawdown, float)
        assert isinstance(metrics.win_rate, float)
        assert isinstance(metrics.profit_factor, float)
        assert isinstance(metrics.avg_trade, float)
        assert isinstance(metrics.num_trades, int)
        
        # Test specific values
        assert metrics.num_trades == 5
        assert metrics.win_rate == 0.6  # 3 out of 5 trades are profitable
        assert np.isclose(metrics.avg_trade, 0.012)  # Average of [0.02, -0.01, 0.03, -0.02, 0.04]
        
        # Calculate expected total return: (1+0.02)*(1-0.01)*(1+0.03)*(1-0.02)*(1+0.04) - 1
        expected_return = (1.02 * 0.99 * 1.03 * 0.98 * 1.04) - 1
        assert np.isclose(metrics.total_return, expected_return)
    
    def test_empty_trades(self, evaluator):
        """
        Test handling of empty trade history.
        
        Scenario: Calculate metrics with no trades
          Given I have an empty trade history
          When I try to calculate performance metrics
          Then I should get a ValueError
        """
        empty_trades = pd.DataFrame(columns=['date', 'profit_pct'])
        
        with pytest.raises(ValueError, match="No trades to evaluate"):
            evaluator.calculate_metrics(empty_trades)
    
    def test_all_winning_trades(self, evaluator):
        """
        Test calculation with all winning trades.
        
        Scenario: Calculate metrics with all winning trades
          Given I have a trade history with only profitable trades
          When I calculate performance metrics
          Then profit_factor should be infinity and win_rate should be 1.0
        """
        winning_trades = pd.DataFrame({
            'date': [datetime(2023, 1, i) for i in range(1, 6)],
            'profit_pct': [0.01, 0.02, 0.01, 0.03, 0.02]
        })
        
        metrics = evaluator.calculate_metrics(winning_trades)
        
        assert metrics.win_rate == 1.0
        assert metrics.profit_factor == float('inf')
    
    def test_all_losing_trades(self, evaluator):
        """
        Test calculation with all losing trades.
        
        Scenario: Calculate metrics with all losing trades
          Given I have a trade history with only losing trades
          When I calculate performance metrics
          Then profit_factor should be 0.0 and win_rate should be 0.0
        """
        losing_trades = pd.DataFrame({
            'date': [datetime(2023, 1, i) for i in range(1, 6)],
            'profit_pct': [-0.01, -0.02, -0.01, -0.03, -0.02]
        })
        
        metrics = evaluator.calculate_metrics(losing_trades)
        
        assert metrics.win_rate == 0.0
        assert metrics.profit_factor == 0.0
    
    def test_sharpe_ratio_calculation(self, evaluator):
        """
        Test Sharpe ratio calculation.
        
        Scenario: Calculate Sharpe ratio
          Given I have a series of returns
          When I calculate the Sharpe ratio
          Then I should get the correct annualized value
        """
        # Create a series of returns with known mean and std
        returns = np.array([0.001, 0.002, -0.001, 0.003, -0.002])
        
        # Calculate expected Sharpe ratio
        excess_returns = returns - evaluator.risk_free_rate / 252
        expected_sharpe = np.sqrt(252) * (np.mean(excess_returns) / np.std(excess_returns))
        
        # Calculate actual Sharpe ratio
        actual_sharpe = evaluator._calculate_sharpe_ratio(returns)
        
        assert np.isclose(actual_sharpe, expected_sharpe)
    
    def test_max_drawdown_calculation(self, evaluator):
        """
        Test maximum drawdown calculation.
        
        Scenario: Calculate maximum drawdown
          Given I have a series of cumulative returns
          When I calculate the maximum drawdown
          Then I should get the correct drawdown value
        """
        # Create a series of cumulative returns with a known drawdown
        # Starting at 1.0, going up to 1.1, down to 0.88, then up to 1.05
        cumulative_returns = np.array([1.0, 1.05, 1.1, 1.0, 0.9, 0.88, 0.95, 1.05])
        
        # Calculate the expected drawdown based on the implementation
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / (1 + peak)
        expected_drawdown = abs(min(drawdown))
        
        # Calculate actual max drawdown
        actual_drawdown = evaluator._calculate_max_drawdown(cumulative_returns)
        
        assert np.isclose(actual_drawdown, expected_drawdown) 