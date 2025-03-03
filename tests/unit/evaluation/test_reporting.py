"""
Unit tests for the evaluation reporting module.
"""
import pytest
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path

from abidance.evaluation.reporting import PerformanceReport
from abidance.evaluation.metrics import PerformanceMetrics


class TestPerformanceReport:
    """
    Test suite for the PerformanceReport class.
    
    Feature: Performance Reporting
      As a trading system developer
      I want to generate and save performance reports
      So that I can analyze and share strategy results
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
    def empty_trades(self):
        """Create an empty DataFrame of trades for testing."""
        return pd.DataFrame(columns=['date', 'profit_pct'])
    
    @pytest.fixture
    def test_output_dir(self, tmp_path):
        """Create a temporary directory for test outputs."""
        return str(tmp_path / "test_reports")
    
    @pytest.fixture
    def report_generator(self, test_output_dir):
        """Create a PerformanceReport instance for testing."""
        return PerformanceReport(output_dir=test_output_dir)
    
    def test_generate_report(self, report_generator, sample_trades):
        """
        Test generation of performance report.
        
        Scenario: Generate performance report from trade history
          Given I have a trade history with profits and losses
          When I generate a performance report
          Then I should get a report with metrics and equity curve data
        """
        report_data = report_generator.generate_report(
            trades=sample_trades,
            strategy_name="Test Strategy",
            parameters={"param1": 10, "param2": "value"}
        )
        
        # Check report structure
        assert report_data["strategy_name"] == "Test Strategy"
        assert report_data["parameters"] == {"param1": 10, "param2": "value"}
        assert "timestamp" in report_data
        assert "metrics" in report_data
        assert "equity_curve" in report_data
        
        # Check metrics
        metrics = report_data["metrics"]
        assert "total_return" in metrics
        assert "sharpe_ratio" in metrics
        assert "max_drawdown" in metrics
        assert "win_rate" in metrics
        assert "profit_factor" in metrics
        assert "avg_trade" in metrics
        assert "num_trades" in metrics
        
        # Check equity curve
        equity_curve = report_data["equity_curve"]
        assert equity_curve is not None
    
    def test_generate_report_empty_trades(self, report_generator, empty_trades):
        """
        Test generation of performance report with empty trades.
        
        Scenario: Generate performance report with no trades
          Given I have an empty trade history
          When I generate a performance report
          Then I should get a report with an error message
        """
        report_data = report_generator.generate_report(
            trades=empty_trades,
            strategy_name="Empty Strategy"
        )
        
        # Check report structure
        assert report_data["strategy_name"] == "Empty Strategy"
        assert "error" in report_data
        assert report_data["metrics"] is None
        assert report_data["charts"] is None
    
    def test_save_report(self, report_generator, sample_trades, test_output_dir):
        """
        Test saving of performance report.
        
        Scenario: Save performance report to file
          Given I have generated a performance report
          When I save the report to a file
          Then the file should contain the correct report data
        """
        # Generate report
        report_data = report_generator.generate_report(
            trades=sample_trades,
            strategy_name="Test Strategy"
        )
        
        # Save report
        file_path = report_generator.save_report(report_data, filename="test_report.json")
        
        # Check file exists
        assert os.path.exists(file_path)
        
        # Check file content
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["strategy_name"] == "Test Strategy"
        assert "metrics" in saved_data
        assert "equity_curve" in saved_data
    
    def test_save_report_auto_filename(self, report_generator, sample_trades, test_output_dir):
        """
        Test automatic filename generation when saving reports.
        
        Scenario: Save report with auto-generated filename
          Given I have generated a performance report
          When I save the report without specifying a filename
          Then a file should be created with an auto-generated name
        """
        # Generate report
        report_data = report_generator.generate_report(
            trades=sample_trades,
            strategy_name="Auto Filename Test"
        )
        
        # Save report with auto filename
        file_path = report_generator.save_report(report_data)
        
        # Check file exists
        assert os.path.exists(file_path)
        assert "auto_filename_test_" in file_path.lower()
    
    def test_plot_equity_curve(self, report_generator, sample_trades, test_output_dir):
        """
        Test plotting of equity curve.
        
        Scenario: Plot equity curve from trade history
          Given I have a trade history with profits and losses
          When I plot the equity curve
          Then I should get a matplotlib figure with the curve
        """
        # Plot equity curve
        fig, ax = report_generator.plot_equity_curve(sample_trades)
        
        # Check figure and axes
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        
        # Check plot elements
        assert len(ax.lines) >= 1  # At least one line (equity curve)
        assert len(ax.collections) >= 1  # At least one collection (drawdown area)
        
        # Save plot to file
        save_path = os.path.join(test_output_dir, "equity_curve_test.png")
        fig.savefig(save_path)
        
        # Check file exists
        assert os.path.exists(save_path)
    
    def test_plot_equity_curve_empty_trades(self, report_generator, empty_trades):
        """
        Test plotting of equity curve with empty trades.
        
        Scenario: Plot equity curve with no trades
          Given I have an empty trade history
          When I plot the equity curve
          Then I should get a figure with a message about no trades
        """
        # Plot equity curve with empty trades
        fig, ax = report_generator.plot_equity_curve(empty_trades)
        
        # Check figure and axes
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        
        # Check for text about no trades
        texts = ax.texts
        assert len(texts) > 0
        assert any("No trades" in text.get_text() for text in texts)
    
    def test_metrics_to_dict(self, report_generator):
        """
        Test conversion of metrics to dictionary.
        
        Scenario: Convert metrics to dictionary
          Given I have a PerformanceMetrics instance
          When I convert it to a dictionary
          Then I should get a dictionary with all metrics
        """
        # Create metrics
        metrics = PerformanceMetrics(
            total_return=0.15,
            sharpe_ratio=1.2,
            max_drawdown=0.05,
            win_rate=0.6,
            profit_factor=1.5,
            avg_trade=0.02,
            num_trades=50
        )
        
        # Convert to dict
        metrics_dict = report_generator._metrics_to_dict(metrics)
        
        # Check dict
        assert metrics_dict["total_return"] == 0.15
        assert metrics_dict["sharpe_ratio"] == 1.2
        assert metrics_dict["max_drawdown"] == 0.05
        assert metrics_dict["win_rate"] == 0.6
        assert metrics_dict["profit_factor"] == 1.5
        assert metrics_dict["avg_trade"] == 0.02
        assert metrics_dict["num_trades"] == 50 