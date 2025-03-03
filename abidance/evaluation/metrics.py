from typing import Dict, Any

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class PerformanceMetrics:
    """Container for strategy performance metrics."""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    avg_trade: float
    num_trades: int

class StrategyEvaluator:
    """Evaluator for trading strategy performance."""

    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def calculate_metrics(self, trades: pd.DataFrame) -> PerformanceMetrics:
        """Calculate performance metrics from trade history."""
        if trades.empty:
            raise ValueError("No trades to evaluate")

        # Calculate returns
        returns = trades['profit_pct'].values
        cumulative_returns = (1 + returns).cumprod() - 1

        # Calculate metrics
        total_return = cumulative_returns[-1]
        sharpe = self._calculate_sharpe_ratio(returns)
        max_dd = self._calculate_max_drawdown(cumulative_returns)
        win_rate = np.mean(returns > 0)

        # Separate wins and losses
        wins = returns[returns > 0]
        losses = returns[returns < 0]

        profit_factor = (
            abs(wins.sum()) / abs(losses.sum())
            if len(losses) > 0 else float('inf')
        )

        return PerformanceMetrics(
            total_return=total_return,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_trade=np.mean(returns),
            num_trades=len(returns)
        )

    def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """Calculate annualized Sharpe ratio."""
        excess_returns = returns - self.risk_free_rate / 252  # Daily
        return np.sqrt(252) * (np.mean(excess_returns) / np.std(excess_returns))

    def _calculate_max_drawdown(self, cumulative_returns: np.ndarray) -> float:
        """Calculate maximum drawdown."""
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / (1 + peak)
        return abs(min(drawdown))
