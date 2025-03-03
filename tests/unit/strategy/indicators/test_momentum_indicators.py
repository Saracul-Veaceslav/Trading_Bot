"""
Unit tests for momentum indicators.
"""
import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal, assert_frame_equal

from abidance.strategy.indicators import RSI, MACD


class TestRSI:
    """Tests for the RSI indicator."""
    
    def test_rsi_calculation(self):
        """Test RSI calculation with known values."""
        # Create sample data
        data = pd.DataFrame({
            'close': [10, 11, 10.5, 10, 10.5, 11.5, 12, 12.5, 12, 11]
        })
        
        # Initialize RSI indicator
        rsi = RSI(period=3)
        
        # Calculate RSI
        result = rsi.calculate(data)
        
        # Check that result is a Series
        assert isinstance(result, pd.Series)
        
        # Check that result has the same length as input data
        assert len(result) == len(data)
        
        # Check that the first values are NaN (due to the diff and rolling window)
        assert pd.isna(result.iloc[0])
        
        # Check that later values are calculated
        assert not pd.isna(result.iloc[-1])
    
    def test_rsi_bounds(self):
        """Test that RSI values are bounded between 0 and 100."""
        # Create sample data with strong up and down trends
        up_trend = pd.DataFrame({
            'close': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        })
        
        down_trend = pd.DataFrame({
            'close': [20, 19, 18, 17, 16, 15, 14, 13, 12, 11]
        })
        
        # Initialize RSI indicator
        rsi = RSI(period=3)
        
        # Calculate RSI for up trend
        up_rsi = rsi.calculate(up_trend)
        
        # Calculate RSI for down trend
        down_rsi = rsi.calculate(down_trend)
        
        # Check bounds for up trend (should approach 100)
        assert all((0 <= val <= 100) for val in up_rsi.dropna())
        assert up_rsi.iloc[-1] > 70  # Strong up trend should have high RSI
        
        # Check bounds for down trend (should approach 0)
        assert all((0 <= val <= 100) for val in down_rsi.dropna())
        assert down_rsi.iloc[-1] < 30  # Strong down trend should have low RSI
    
    def test_rsi_custom_column(self):
        """Test RSI calculation with a custom column."""
        # Create sample data with multiple columns
        data = pd.DataFrame({
            'close': [10, 11, 12, 13, 14],
            'adjusted': [9.8, 10.8, 11.8, 12.8, 13.8]
        })
        
        # Initialize RSI indicator with custom column
        rsi = RSI(period=2, column='adjusted')
        
        # Calculate RSI
        result = rsi.calculate(data)
        
        # Check that the calculation used the correct column
        # We can't easily check the exact values, but we can check that it's not NaN
        assert not pd.isna(result.iloc[-1])
    
    def test_rsi_missing_column(self):
        """Test error handling for missing column."""
        # Create sample data
        data = pd.DataFrame({
            'close': [10, 11, 12, 13, 14]
        })
        
        # Initialize RSI indicator with non-existent column
        rsi = RSI(column='non_existent')
        
        # Check that it raises a ValueError
        with pytest.raises(ValueError, match="Column 'non_existent' not found in data"):
            rsi.calculate(data)
    
    def test_rsi_name(self):
        """Test the name property of RSI."""
        rsi = RSI(period=14)
        assert rsi.name == "RSI(14)"
        
        rsi = RSI(period=7)
        assert rsi.name == "RSI(7)"


class TestMACD:
    """Tests for the MACD indicator."""
    
    def test_macd_calculation(self):
        """Test MACD calculation with sample data."""
        # Create sample data
        data = pd.DataFrame({
            'close': [10, 11, 10.5, 10, 10.5, 11.5, 12, 12.5, 12, 11, 
                      10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 13.5, 13]
        })
        
        # Initialize MACD indicator
        macd = MACD(fast_period=3, slow_period=6, signal_period=2)
        
        # Calculate MACD
        result = macd.calculate(data)
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check that result has the expected columns
        assert set(result.columns) == {'macd', 'signal', 'histogram'}
        
        # Check that result has the same length as input data
        assert len(result) == len(data)
        
        # Check that the first values are NaN (due to the EMA windows)
        assert pd.isna(result['macd'].iloc[0])
        
        # Check that later values are calculated
        assert not pd.isna(result['macd'].iloc[-1])
        assert not pd.isna(result['signal'].iloc[-1])
        assert not pd.isna(result['histogram'].iloc[-1])
    
    def test_macd_signal_line_crossovers(self):
        """Test MACD signal line crossovers."""
        # Create sample data with a trend reversal
        data = pd.DataFrame({
            'close': [10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 13.5, 
                      13, 12.5, 12, 11.5, 11, 10.5, 10, 9.5, 9, 8.5]
        })
        
        # Initialize MACD indicator
        macd = MACD(fast_period=3, slow_period=6, signal_period=2)
        
        # Calculate MACD
        result = macd.calculate(data)
        
        # Find crossovers (where histogram changes sign)
        crossovers = (result['histogram'] * result['histogram'].shift(1) < 0).fillna(False)
        
        # Check that there is at least one crossover
        assert crossovers.any()
    
    def test_macd_missing_column(self):
        """Test error handling for missing column."""
        # Create sample data
        data = pd.DataFrame({
            'close': [10, 11, 12, 13, 14]
        })
        
        # Initialize MACD indicator with non-existent column
        macd = MACD(column='non_existent')
        
        # Check that it raises a ValueError
        with pytest.raises(ValueError, match="Column 'non_existent' not found in data"):
            macd.calculate(data)
    
    def test_macd_name(self):
        """Test the name property of MACD."""
        macd = MACD(fast_period=12, slow_period=26, signal_period=9)
        assert macd.name == "MACD(12,26,9)"
        
        macd = MACD(fast_period=5, slow_period=15, signal_period=5)
        assert macd.name == "MACD(5,15,5)" 