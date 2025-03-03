"""
Performance metrics for strategy evaluation.

This module provides functions for calculating various performance metrics
from trading results, which can be used to evaluate and compare strategies.
"""

import numpy as np
import pandas as pd
from typing import Optional, Union, List, Dict, Any


def calculate_sharpe_ratio(trades: pd.DataFrame,
                          risk_free_rate: float = 0.0,
                          annualization_factor: int = 252) -> float:
    """
    Calculate the Sharpe ratio from a trades DataFrame.

    The Sharpe ratio measures the performance of an investment compared to a risk-free asset,
    after adjusting for its risk.

    Args:
        trades: DataFrame containing trade information
        risk_free_rate: Annual risk-free rate (default: 0.0)
        annualization_factor: Number of trading days in a year (default: 252)

    Returns:
        Sharpe ratio
    """
    if trades.empty:
        return float('-inf')

    # Extract returns from trades
    if 'returns' in trades.columns:
        returns = trades['returns']
    elif 'profit' in trades.columns and 'cost' in trades.columns:
        # Calculate returns from profit and cost
        returns = trades['profit'] / trades['cost']
    else:
        raise ValueError("Trades DataFrame must contain 'returns' column or 'profit' and 'cost' columns")

    # Calculate daily returns
    daily_returns = returns.resample('D').sum()

    # Calculate annualized Sharpe ratio
    excess_returns = daily_returns - (risk_free_rate / annualization_factor)
    if len(excess_returns) < 2:
        return float('-inf')

    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(annualization_factor)
    return float(sharpe)


def calculate_sortino_ratio(trades: pd.DataFrame,
                           risk_free_rate: float = 0.0,
                           annualization_factor: int = 252) -> float:
    """
    Calculate the Sortino ratio from a trades DataFrame.

    The Sortino ratio is a variation of the Sharpe ratio that only considers
    downside risk (negative returns).

    Args:
        trades: DataFrame containing trade information
        risk_free_rate: Annual risk-free rate (default: 0.0)
        annualization_factor: Number of trading days in a year (default: 252)

    Returns:
        Sortino ratio
    """
    if trades.empty:
        return float('-inf')

    # Extract returns from trades
    if 'returns' in trades.columns:
        returns = trades['returns']
    elif 'profit' in trades.columns and 'cost' in trades.columns:
        # Calculate returns from profit and cost
        returns = trades['profit'] / trades['cost']
    else:
        raise ValueError("Trades DataFrame must contain 'returns' column or 'profit' and 'cost' columns")

    # Calculate daily returns
    daily_returns = returns.resample('D').sum()

    # Calculate annualized Sortino ratio
    excess_returns = daily_returns - (risk_free_rate / annualization_factor)
    if len(excess_returns) < 2:
        return float('-inf')

    # Calculate downside deviation (standard deviation of negative returns only)
    negative_returns = excess_returns[excess_returns < 0]
    if len(negative_returns) == 0:
        # If there are no negative returns, return a very high Sortino ratio
        return float('inf')

    downside_deviation = np.sqrt(np.mean(negative_returns**2)) * np.sqrt(annualization_factor)
    if downside_deviation == 0:
        return float('inf')

    sortino = excess_returns.mean() * annualization_factor / downside_deviation
    return float(sortino)


def calculate_max_drawdown(trades: pd.DataFrame) -> float:
    """
    Calculate the maximum drawdown from a trades DataFrame.

    Maximum drawdown measures the largest peak-to-trough decline in the value of a portfolio.

    Args:
        trades: DataFrame containing trade information

    Returns:
        Maximum drawdown as a positive percentage (0 to 1)
    """
    if trades.empty:
        return 1.0  # Worst possible drawdown

    # Extract cumulative returns or equity curve
    if 'cumulative_returns' in trades.columns:
        equity_curve = trades['cumulative_returns']
    elif 'equity' in trades.columns:
        equity_curve = trades['equity']
    elif 'returns' in trades.columns:
        # Calculate cumulative returns from individual returns
        equity_curve = (1 + trades['returns']).cumprod()
    else:
        raise ValueError("Trades DataFrame must contain 'cumulative_returns', 'equity', or 'returns' column")

    # Calculate running maximum
    running_max = equity_curve.cummax()

    # Calculate drawdown
    drawdown = (running_max - equity_curve) / running_max

    # Get maximum drawdown
    max_drawdown = drawdown.max()

    return float(max_drawdown)


def calculate_win_rate(trades: pd.DataFrame) -> float:
    """
    Calculate the win rate from a trades DataFrame.

    Win rate is the percentage of trades that are profitable.

    Args:
        trades: DataFrame containing trade information

    Returns:
        Win rate as a percentage (0 to 1)
    """
    if trades.empty:
        return 0.0

    # Determine profitable trades
    if 'profit' in trades.columns:
        profitable_trades = trades[trades['profit'] > 0]
    elif 'returns' in trades.columns:
        profitable_trades = trades[trades['returns'] > 0]
    else:
        raise ValueError("Trades DataFrame must contain 'profit' or 'returns' column")

    # Calculate win rate
    win_rate = len(profitable_trades) / len(trades)

    return float(win_rate)


def calculate_profit_factor(trades: pd.DataFrame) -> float:
    """
    Calculate the profit factor from a trades DataFrame.

    Profit factor is the ratio of gross profits to gross losses.

    Args:
        trades: DataFrame containing trade information

    Returns:
        Profit factor
    """
    if trades.empty:
        return 0.0

    # Extract profits and losses
    if 'profit' in trades.columns:
        profits = trades[trades['profit'] > 0]['profit'].sum()
        losses = abs(trades[trades['profit'] < 0]['profit'].sum())
    elif 'returns' in trades.columns:
        profits = trades[trades['returns'] > 0]['returns'].sum()
        losses = abs(trades[trades['returns'] < 0]['returns'].sum())
    else:
        raise ValueError("Trades DataFrame must contain 'profit' or 'returns' column")

    # Calculate profit factor
    if losses == 0:
        return float('inf') if profits > 0 else 0.0

    profit_factor = profits / losses

    return float(profit_factor)