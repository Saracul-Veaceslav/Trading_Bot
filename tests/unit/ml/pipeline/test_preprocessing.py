"""
Unit tests for the DataPreprocessor class.

This module contains tests for data preprocessing functionality, including
data cleaning, normalization, and handling of missing values.
"""
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from abidance.ml.pipeline.preprocessing import DataPreprocessor


@pytest.fixture
def sample_data():
    """Create sample data with missing values and outliers."""
    # Create data with some missing values and outliers
    data = pd.DataFrame({
        'open': [100, 101, np.nan, 103, 104],
        'high': [102, 103, 104, np.nan, 106],
        'low': [98, 99, 100, 101, np.nan],
        'close': [101, 102, 103, 104, 105],
        'volume': [1000, 1100, 1200, np.nan, 1400]
    }, index=pd.date_range(start='2023-01-01', periods=5))
    
    # Add an outlier
    data.loc[data.index[3], 'volume'] = 100000
    
    return data


@pytest.fixture
def preprocessor():
    """Create a DataPreprocessor instance."""
    return DataPreprocessor()


class TestDataPreprocessor:
    """Tests for the DataPreprocessor class."""
    
    def test_initialization(self, preprocessor):
        """Test that the preprocessor initializes correctly."""
        assert preprocessor is not None
    
    def test_handle_missing_values(self, preprocessor, sample_data):
        """Test handling of missing values."""
        # Process the data
        processed_data = preprocessor.handle_missing_values(sample_data)
        
        # Check that there are no missing values
        assert not processed_data.isnull().any().any()
        
        # Check that the shape is preserved
        assert processed_data.shape == sample_data.shape
        
        # Check that the index is preserved
        assert all(processed_data.index == sample_data.index)
    
    def test_remove_outliers(self, preprocessor, sample_data):
        """Test removal of outliers."""
        # Create a simple test case with a very extreme outlier
        test_data = pd.DataFrame({
            'col1': [1, 2, 3, 1000, 2, 3]  # 1000 is a very extreme outlier
        })
        
        # Calculate mean and std
        mean = test_data['col1'].mean()
        std = test_data['col1'].std()
        
        # Process the data with a lower threshold to ensure the outlier is detected
        result = preprocessor.remove_outliers(test_data, threshold=2.0)
        
        # The outlier should be modified
        assert result.loc[3, 'col1'] < 1000
        
        # Check that the shape is preserved
        assert result.shape == test_data.shape
    
    def test_normalize_data(self, preprocessor, sample_data):
        """Test data normalization."""
        # Fill missing values first to avoid issues
        clean_data = sample_data.ffill().bfill()
        
        # Process the data
        normalized_data = preprocessor.normalize_data(clean_data)
        
        # Check that values are normalized (between -1 and 1)
        epsilon = 1e-10  # Small tolerance for floating-point comparison
        for column in normalized_data.columns:
            assert normalized_data[column].min() >= -1 - epsilon
            assert normalized_data[column].max() <= 1 + epsilon
        
        # Check that the shape is preserved
        assert normalized_data.shape == clean_data.shape
    
    def test_process_pipeline(self, preprocessor, sample_data):
        """Test the full preprocessing pipeline."""
        # Process the data
        processed_data = preprocessor.process(sample_data)
        
        # Check that there are no missing values
        assert not processed_data.isnull().any().any()
        
        # Check that the shape is preserved
        assert processed_data.shape == sample_data.shape
        
        # Check that the index is preserved
        assert all(processed_data.index == sample_data.index)
        
        # Check that values are reasonable (not extreme)
        for column in processed_data.columns:
            assert processed_data[column].min() >= -10
            assert processed_data[column].max() <= 10


# Feature: Data Preprocessing Pipeline
# 
#   Scenario: Handling missing values in financial data
#     Given a dataset with some missing OHLCV values
#     When I run the data preprocessing pipeline
#     Then all missing values should be appropriately filled
#     And the data shape should remain unchanged
#
#   Scenario: Removing outliers from volume data
#     Given a dataset with volume outliers
#     When I apply the outlier removal process
#     Then extreme volume values should be handled
#     And the resulting data should have a more normal distribution 