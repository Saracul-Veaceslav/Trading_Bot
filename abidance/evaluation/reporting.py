from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime
import os

from abidance.evaluation.metrics import PerformanceMetrics, StrategyEvaluator

class PerformanceReport:
    """Generate and save performance reports for trading strategies."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the performance report generator.
        
        Args:
            output_dir: Directory to save reports. Defaults to 'reports/'.
        """
        self.output_dir = output_dir or 'reports/'
        os.makedirs(self.output_dir, exist_ok=True)
        self.evaluator = StrategyEvaluator()
    
    def generate_report(self, 
                        trades: pd.DataFrame, 
                        strategy_name: str,
                        parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a performance report for a trading strategy.
        
        Args:
            trades: DataFrame containing trade history with at least 'profit_pct' column
            strategy_name: Name of the strategy
            parameters: Strategy parameters used for this run
            
        Returns:
            Dictionary containing report data
        """
        # Calculate metrics
        try:
            metrics = self.evaluator.calculate_metrics(trades)
        except ValueError as e:
            # Handle case with no trades
            return {
                'strategy_name': strategy_name,
                'parameters': parameters or {},
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'metrics': None,
                'charts': None
            }
        
        # Generate equity curve data
        equity_curve = self._generate_equity_curve(trades)
        
        # Create report data
        report_data = {
            'strategy_name': strategy_name,
            'parameters': parameters or {},
            'timestamp': datetime.now().isoformat(),
            'metrics': self._metrics_to_dict(metrics),
            'equity_curve': equity_curve.to_dict() if equity_curve is not None else None
        }
        
        return report_data
    
    def save_report(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save report data to a JSON file.
        
        Args:
            report_data: Report data dictionary
            filename: Optional filename, defaults to strategy_name_timestamp.json
            
        Returns:
            Path to the saved report file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            strategy_name = report_data['strategy_name'].replace(' ', '_').lower()
            filename = f"{strategy_name}_{timestamp}.json"
        
        file_path = os.path.join(self.output_dir, filename)
        
        # Convert any non-serializable objects
        serializable_report = self._make_serializable(report_data)
        
        with open(file_path, 'w') as f:
            json.dump(serializable_report, f, indent=2)
        
        return file_path
    
    def plot_equity_curve(self, 
                          trades: pd.DataFrame, 
                          save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot equity curve from trade history.
        
        Args:
            trades: DataFrame containing trade history
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure and axes objects
        """
        if trades.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "No trades to plot", ha='center', va='center')
            return fig, ax
        
        equity_curve = self._generate_equity_curve(trades)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(equity_curve.index, equity_curve['equity'], label='Equity Curve')
        
        # Add drawdown as a filled area below
        drawdowns = self._calculate_drawdowns(equity_curve['equity'])
        ax.fill_between(equity_curve.index, 0, drawdowns, alpha=0.3, color='red', label='Drawdown')
        
        ax.set_title('Strategy Equity Curve')
        ax.set_xlabel('Trade Number')
        ax.set_ylabel('Equity')
        ax.legend()
        ax.grid(True)
        
        if save_path:
            plt.savefig(save_path)
        
        return fig, ax
    
    def _metrics_to_dict(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Convert metrics dataclass to dictionary."""
        return {
            'total_return': metrics.total_return,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'win_rate': metrics.win_rate,
            'profit_factor': metrics.profit_factor,
            'avg_trade': metrics.avg_trade,
            'num_trades': metrics.num_trades
        }
    
    def _generate_equity_curve(self, trades: pd.DataFrame) -> pd.DataFrame:
        """Generate equity curve from trade history."""
        if trades.empty:
            return None
        
        # Ensure trades are sorted by date if available
        if 'date' in trades.columns:
            trades = trades.sort_values('date')
        
        # Calculate cumulative returns
        returns = trades['profit_pct'].values
        cumulative_returns = (1 + returns).cumprod() - 1
        
        # Create equity curve DataFrame
        equity_curve = pd.DataFrame({
            'trade_id': range(1, len(trades) + 1),
            'equity': (1 + cumulative_returns)
        })
        
        equity_curve.set_index('trade_id', inplace=True)
        return equity_curve
    
    def _calculate_drawdowns(self, equity_series: pd.Series) -> pd.Series:
        """Calculate drawdowns from equity series."""
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak
        return drawdown
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert non-serializable objects to serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (pd.DataFrame, pd.Series)):
            return obj.to_dict()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.float64)):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj 