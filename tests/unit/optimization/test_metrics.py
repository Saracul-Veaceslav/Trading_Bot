"""
Tests for the strategy optimization metrics module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from abidance.optimization.metrics import (
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_win_rate,
    calculate_profit_factor
)


@pytest.fixture
def sample_trades_df():
    """Create a sample trades DataFrame for testing metrics."""
    dates = pd.date_range(start='2023-01-01', periods=10)
    
    # Create a DataFrame with both positive and negative returns
    df = pd.DataFrame({
        'timestamp': dates,
        'returns': [0.01, -0.005, 0.02, -0.01, 0.015, 0.005, -0.02, 0.01, 0.005, -0.005],
        'profit': [100, -50, 200, -100, 150, 50, -200, 100, 50, -50],
        'cost': [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000],
        'cumulative_returns': [1.01, 1.005, 1.025, 1.015, 1.03, 1.035, 1.015, 1.025, 1.03, 1.025]
    })
    
    df.set_index('timestamp', inplace=True)
    return df


@pytest.fixture
def empty_trades_df():
    """Create an empty trades DataFrame."""
    return pd.DataFrame(columns=['timestamp', 'returns', 'profit', 'cost'])


def test_calculate_sharpe_ratio(sample_trades_df, empty_trades_df):
    """
    Test the Sharpe ratio calculation.
    
    Feature: Sharpe Ratio Calculation
    
    Scenario: Calculating Sharpe ratio from trades data
      Given a DataFrame of trades with returns
      When calculate_sharpe_ratio is called
      Then the correct Sharpe ratio should be returned
    """
    # Test with sample data
    sharpe = calculate_sharpe_ratio(sample_trades_df)
    assert isinstance(sharpe, float)
    
    # Test with empty DataFrame
    empty_sharpe = calculate_sharpe_ratio(empty_trades_df)
    assert empty_sharpe == float('-inf')
    
    # Test with different risk-free rate
    sharpe_with_rf = calculate_sharpe_ratio(sample_trades_df, risk_free_rate=0.02)
    assert sharpe_with_rf < sharpe  # Higher risk-free rate should lower Sharpe ratio
    
    # Test with different annualization factor
    sharpe_annual = calculate_sharpe_ratio(sample_trades_df, annualization_factor=365)
    assert abs(sharpe_annual) > abs(sharpe)  # Higher annualization should increase absolute Sharpe


def test_calculate_sortino_ratio(sample_trades_df, empty_trades_df):
    """
    Test the Sortino ratio calculation.
    
    Feature: Sortino Ratio Calculation
    
    Scenario: Calculating Sortino ratio from trades data
      Given a DataFrame of trades with returns
      When calculate_sortino_ratio is called
      Then the correct Sortino ratio should be returned
    """
    # Test with sample data
    sortino = calculate_sortino_ratio(sample_trades_df)
    assert isinstance(sortino, float)
    
    # Test with empty DataFrame
    empty_sortino = calculate_sortino_ratio(empty_trades_df)
    assert empty_sortino == float('-inf')
    
    # Create a DataFrame with only positive returns
    positive_df = sample_trades_df.copy()
    positive_df['returns'] = abs(positive_df['returns'])
    
    # Test with all positive returns (should return inf)
    positive_sortino = calculate_sortino_ratio(positive_df)
    assert positive_sortino == float('inf')


def test_calculate_max_drawdown(sample_trades_df, empty_trades_df):
    """
    Test the maximum drawdown calculation.
    
    Feature: Maximum Drawdown Calculation
    
    Scenario: Calculating maximum drawdown from trades data
      Given a DataFrame of trades with cumulative returns
      When calculate_max_drawdown is called
      Then the correct maximum drawdown should be returned
    """
    # Test with sample data using cumulative_returns
    drawdown = calculate_max_drawdown(sample_trades_df)
    assert isinstance(drawdown, float)
    assert 0 <= drawdown <= 1  # Drawdown should be between 0 and 1
    
    # Test with empty DataFrame
    empty_drawdown = calculate_max_drawdown(empty_trades_df)
    assert empty_drawdown == 1.0  # Worst possible drawdown
    
    # Create a DataFrame with only the 'returns' column
    returns_df = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=5),
        'returns': [0.01, 0.02, -0.03, 0.01, 0.02]
    })
    returns_df.set_index('timestamp', inplace=True)
    
    # Test with returns column
    returns_drawdown = calculate_max_drawdown(returns_df)
    assert isinstance(returns_drawdown, float)
    assert 0 <= returns_drawdown <= 1


def test_calculate_win_rate(sample_trades_df, empty_trades_df):
    """
    Test the win rate calculation.
    
    Feature: Win Rate Calculation
    
    Scenario: Calculating win rate from trades data
      Given a DataFrame of trades with profits
      When calculate_win_rate is called
      Then the correct win rate should be returned
    """
    # Test with sample data
    win_rate = calculate_win_rate(sample_trades_df)
    assert isinstance(win_rate, float)
    assert 0 <= win_rate <= 1  # Win rate should be between 0 and 1
    
    # Expected win rate: 6 profitable trades out of 10
    expected_win_rate = 0.6
    assert abs(win_rate - expected_win_rate) < 0.001
    
    # Test with empty DataFrame
    empty_win_rate = calculate_win_rate(empty_trades_df)
    assert empty_win_rate == 0.0
    
    # Create a DataFrame with all profitable trades
    all_win_df = sample_trades_df.copy()
    all_win_df['profit'] = abs(all_win_df['profit'])
    all_win_df['returns'] = abs(all_win_df['returns'])
    
    # Test with all profitable trades
    all_win_rate = calculate_win_rate(all_win_df)
    assert all_win_rate == 1.0


def test_calculate_profit_factor(sample_trades_df, empty_trades_df):
    """
    Test the profit factor calculation.
    
    Feature: Profit Factor Calculation
    
    Scenario: Calculating profit factor from trades data
      Given a DataFrame of trades with profits and losses
      When calculate_profit_factor is called
      Then the correct profit factor should be returned
    """
    # Test with sample data
    profit_factor = calculate_profit_factor(sample_trades_df)
    assert isinstance(profit_factor, float)
    assert profit_factor >= 0  # Profit factor should be non-negative
    
    # Expected profit factor: sum of profits / sum of losses
    # Profits: 100 + 200 + 150 + 50 + 100 + 50 = 650
    # Losses: 50 + 100 + 200 + 50 = 400
    # Expected profit factor: 650 / 400 = 1.625
    expected_profit_factor = 1.625
    assert abs(profit_factor - expected_profit_factor) < 0.001
    
    # Test with empty DataFrame
    empty_profit_factor = calculate_profit_factor(empty_trades_df)
    assert empty_profit_factor == 0.0
    
    # Create a DataFrame with only profitable trades
    all_profit_df = sample_trades_df.copy()
    all_profit_df['profit'] = abs(all_profit_df['profit'])
    all_profit_df['returns'] = abs(all_profit_df['returns'])
    
    # Test with all profitable trades (should return inf)
    all_profit_factor = calculate_profit_factor(all_profit_df)
    assert all_profit_factor == float('inf')
    
    # Create a DataFrame with only losing trades
    all_loss_df = sample_trades_df.copy()
    all_loss_df['profit'] = -abs(all_loss_df['profit'])
    all_loss_df['returns'] = -abs(all_loss_df['returns'])
    
    # Test with all losing trades
    all_loss_factor = calculate_profit_factor(all_loss_df)
    assert all_loss_factor == 0.0 