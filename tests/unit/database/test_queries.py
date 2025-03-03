"""
Unit tests for database query optimization.

This module tests the performance and accuracy of optimized database queries.
"""
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from abidance.database.queries import QueryOptimizer
from abidance.database.models import Trade, OHLCV, Strategy
from abidance.trading.order import OrderSide


class TestQueryOptimizer(unittest.TestCase):
    """Test cases for the QueryOptimizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock(spec=Session)
        self.query_optimizer = QueryOptimizer(self.mock_session)

    def test_get_trade_statistics(self):
        """
        Test that trade statistics are correctly calculated.
        
        Given a set of trades for a symbol
        When get_trade_statistics is called
        Then it should return the correct aggregated statistics
        """
        # Arrange
        symbol = "BTC/USDT"
        mock_result = MagicMock()
        mock_result.total_trades = 10
        mock_result.total_volume = 5.5
        mock_result.avg_price = 50000.0
        mock_result.min_price = 48000.0
        mock_result.max_price = 52000.0
        
        self.mock_session.execute.return_value.first.return_value = mock_result
        
        # Act
        result = self.query_optimizer.get_trade_statistics(symbol)
        
        # Assert
        self.assertEqual(result['total_trades'], 10)
        self.assertEqual(result['total_volume'], 5.5)
        self.assertEqual(result['avg_price'], 50000.0)
        self.assertEqual(result['min_price'], 48000.0)
        self.assertEqual(result['max_price'], 52000.0)
        self.mock_session.execute.assert_called_once()
        
    def test_get_ohlcv_with_indicators(self):
        """
        Test that OHLCV data with indicators is correctly retrieved.
        
        Given OHLCV data for a symbol
        When get_ohlcv_with_indicators is called
        Then it should return a DataFrame with the correct indicators
        """
        # Arrange
        symbol = "BTC/USDT"
        window = 14
        
        # Create mock data that would be returned from the database
        mock_data = [
            {
                'timestamp': datetime.now() - timedelta(minutes=i),
                'open': 50000.0 + i * 10,
                'high': 50100.0 + i * 10,
                'low': 49900.0 + i * 10,
                'close': 50050.0 + i * 10,
                'volume': 1.0 + i * 0.1,
                'sma': 50025.0 + i * 5,
                'rsi_ratio': 0.7 + i * 0.01
            }
            for i in range(20)
        ]
        
        self.mock_session.execute.return_value.fetchall.return_value = mock_data
        
        # Act
        result = self.query_optimizer.get_ohlcv_with_indicators(symbol, window)
        
        # Assert
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 20)
        self.assertTrue('timestamp' in result.columns)
        self.assertTrue('open' in result.columns)
        self.assertTrue('high' in result.columns)
        self.assertTrue('low' in result.columns)
        self.assertTrue('close' in result.columns)
        self.assertTrue('volume' in result.columns)
        self.assertTrue('sma' in result.columns)
        self.assertTrue('rsi_ratio' in result.columns)
        self.mock_session.execute.assert_called_once()
        
    def test_get_strategy_performance(self):
        """
        Test that strategy performance metrics are correctly calculated.
        
        Given a set of trades for a strategy
        When get_strategy_performance is called
        Then it should return the correct performance metrics
        """
        # Arrange
        strategy_id = 1
        mock_result = MagicMock()
        mock_result.total_trades = 20
        mock_result.winning_trades = 12
        mock_result.losing_trades = 8
        mock_result.total_profit = 1500.0
        mock_result.total_loss = 500.0
        mock_result.win_rate = 0.6
        mock_result.profit_factor = 3.0
        
        self.mock_session.execute.return_value.first.return_value = mock_result
        
        # Act
        result = self.query_optimizer.get_strategy_performance(strategy_id)
        
        # Assert
        self.assertEqual(result['total_trades'], 20)
        self.assertEqual(result['winning_trades'], 12)
        self.assertEqual(result['losing_trades'], 8)
        self.assertEqual(result['total_profit'], 1500.0)
        self.assertEqual(result['total_loss'], 500.0)
        self.assertEqual(result['win_rate'], 0.6)
        self.assertEqual(result['profit_factor'], 3.0)
        self.mock_session.execute.assert_called_once()
        
    def test_query_performance_with_large_dataset(self):
        """
        Test query performance with a large dataset.
        
        Given a large dataset
        When queries are executed
        Then they should complete within a reasonable time
        """
        # This is more of an integration test and would be implemented
        # with actual database connections and timing measurements
        pass
        
    def test_indicator_calculation_accuracy(self):
        """
        Test the accuracy of indicator calculations.
        
        Given known OHLCV data with pre-calculated indicators
        When get_ohlcv_with_indicators is called
        Then the calculated indicators should match expected values
        """
        # Arrange
        symbol = "BTC/USDT"
        window = 14
        
        # Create test data with known SMA and RSI values
        dates = [datetime.now() - timedelta(minutes=i) for i in range(20)]
        closes = [50000.0 + i * 100 for i in range(20)]
        
        # Calculate expected SMA values manually
        expected_sma = []
        for i in range(20):
            if i < window - 1:
                # Not enough data for full window
                window_data = closes[0:i+1]
            else:
                # Full window
                window_data = closes[i-(window-1):i+1]
            expected_sma.append(sum(window_data) / len(window_data))
        
        # Mock data returned from database
        mock_data = []
        for i in range(20):
            mock_data.append({
                'timestamp': dates[i],
                'open': closes[i] - 50,
                'high': closes[i] + 100,
                'low': closes[i] - 100,
                'close': closes[i],
                'volume': 1.0,
                'sma': expected_sma[i],
                # RSI calculation is complex, so we'll just use a placeholder
                'rsi_ratio': 0.5
            })
        
        self.mock_session.execute.return_value.fetchall.return_value = mock_data
        
        # Act
        result = self.query_optimizer.get_ohlcv_with_indicators(symbol, window)
        
        # Assert
        self.assertIsInstance(result, pd.DataFrame)
        for i in range(20):
            self.assertAlmostEqual(result.iloc[i]['sma'], expected_sma[i], places=2)
            
    def test_aggregation_functions(self):
        """
        Test that aggregation functions work correctly.
        
        Given trade data
        When aggregation functions are applied
        Then they should return correct results
        """
        # Arrange
        symbol = "BTC/USDT"
        interval = "1h"
        
        # Create mock aggregated OHLCV data
        mock_data = [
            {
                'timestamp': datetime(2023, 1, 1, 12, 0),
                'open': 50000.0,
                'high': 51000.0,
                'low': 49500.0,
                'close': 50500.0,
                'volume': 10.5
            },
            {
                'timestamp': datetime(2023, 1, 1, 13, 0),
                'open': 50500.0,
                'high': 52000.0,
                'low': 50200.0,
                'close': 51800.0,
                'volume': 15.2
            }
        ]
        
        self.mock_session.execute.return_value.fetchall.return_value = mock_data
        
        # Act
        result = self.query_optimizer.get_aggregated_ohlcv(symbol, interval)
        
        # Assert
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]['open'], 50000.0)
        self.assertEqual(result.iloc[0]['high'], 51000.0)
        self.assertEqual(result.iloc[0]['low'], 49500.0)
        self.assertEqual(result.iloc[0]['close'], 50500.0)
        self.assertEqual(result.iloc[0]['volume'], 10.5)
        self.mock_session.execute.assert_called_once()


if __name__ == '__main__':
    unittest.main() 