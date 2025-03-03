import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import tempfile
import shutil

from abidance.testing.data_management import HistoricalDataManager


class TestHistoricalDataManager:
    """
    Test suite for the HistoricalDataManager class.
    
    Feature: Historical Data Management
      As a trading bot developer
      I want to efficiently manage historical market data
      So that I can backtest trading strategies with accurate data
    """
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
        
    @pytest.fixture
    def data_manager(self, temp_data_dir):
        """Create a data manager instance with a temporary data directory."""
        return HistoricalDataManager(data_dir=temp_data_dir)
        
    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data for testing."""
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        data = {
            'open': np.random.rand(10) * 1000 + 20000,
            'high': np.random.rand(10) * 1000 + 21000,
            'low': np.random.rand(10) * 1000 + 19000,
            'close': np.random.rand(10) * 1000 + 20500,
            'volume': np.random.rand(10) * 100
        }
        df = pd.DataFrame(data, index=dates)
        return df
        
    def test_init_creates_directory(self, temp_data_dir):
        """
        Test that the data directory is created during initialization.
        
        Scenario: Data directory creation
          Given I need to store historical market data
          When I initialize the HistoricalDataManager with a specific directory
          Then the directory should be created if it doesn't exist
        """
        # Create a subdirectory path that doesn't exist
        subdir = os.path.join(temp_data_dir, 'test_subdir')
        
        # Initialize manager with this path
        manager = HistoricalDataManager(data_dir=subdir)
        
        # Check that the directory was created
        assert os.path.exists(subdir)
        assert os.path.isdir(subdir)
        
    def test_save_and_load_ohlcv(self, data_manager, sample_ohlcv_data):
        """
        Test saving and loading OHLCV data.
        
        Scenario: Saving and loading OHLCV data
          Given I have OHLCV data for a trading pair
          When I save the data and then load it back
          Then the loaded data should match the original data
        """
        symbol = 'BTC/USD'
        timeframe = '1d'
        
        # Save the data
        data_manager.save_ohlcv(symbol, timeframe, sample_ohlcv_data)
        
        # Check that the file was created
        file_path = data_manager._get_ohlcv_path(symbol, timeframe)
        assert file_path.exists()
        
        # Load the data back
        loaded_data = data_manager.load_ohlcv(symbol, timeframe)
        
        # Check that the loaded data matches the original (ignoring frequency)
        pd.testing.assert_frame_equal(
            sample_ohlcv_data.reset_index(drop=True), 
            loaded_data.reset_index(drop=True)
        )
        
        # Check that the index values match
        pd.testing.assert_index_equal(
            sample_ohlcv_data.index, 
            loaded_data.index,
            check_names=True  # Check names but not frequency
        )
        
    def test_load_with_date_filtering(self, data_manager, sample_ohlcv_data):
        """
        Test loading OHLCV data with date filtering.
        
        Scenario: Date filtering when loading data
          Given I have saved OHLCV data for a trading pair
          When I load the data with start and end date filters
          Then only data within the date range should be returned
        """
        symbol = 'ETH/USD'
        timeframe = '1h'
        
        # Save the data
        data_manager.save_ohlcv(symbol, timeframe, sample_ohlcv_data)
        
        # Define date range for filtering
        start_date = sample_ohlcv_data.index[2]
        end_date = sample_ohlcv_data.index[7]
        
        # Load with date filtering
        filtered_data = data_manager.load_ohlcv(
            symbol, timeframe, start_date=start_date, end_date=end_date
        )
        
        # Check that only data within the date range was loaded
        expected_data = sample_ohlcv_data.loc[start_date:end_date]
        
        # Check that the data matches (ignoring frequency)
        pd.testing.assert_frame_equal(
            expected_data.reset_index(drop=True), 
            filtered_data.reset_index(drop=True)
        )
        
        # Check that the index values match
        pd.testing.assert_index_equal(
            expected_data.index, 
            filtered_data.index,
            check_names=True  # Check names but not frequency
        )
        
    def test_error_handling_for_missing_data(self, data_manager):
        """
        Test error handling when trying to load non-existent data.
        
        Scenario: Error handling for missing data
          Given I try to load data for a symbol that doesn't exist
          When I call the load_ohlcv method
          Then a FileNotFoundError should be raised
        """
        symbol = 'NONEXISTENT/USD'
        timeframe = '1d'
        
        # Try to load non-existent data
        with pytest.raises(FileNotFoundError):
            data_manager.load_ohlcv(symbol, timeframe)
            
    def test_file_path_generation(self, data_manager):
        """
        Test file path generation for OHLCV data.
        
        Scenario: File path generation
          Given I have a symbol and timeframe
          When I generate the file path for OHLCV data
          Then the path should follow the expected format with safe symbol name
        """
        symbol = 'LTC/USD'
        timeframe = '4h'
        
        # Generate file path
        file_path = data_manager._get_ohlcv_path(symbol, timeframe)
        
        # Check path format with safe symbol name (/ replaced with _)
        safe_symbol = symbol.replace('/', '_')
        expected_path = Path(data_manager.data_dir) / f"{safe_symbol}_{timeframe}.parquet"
        assert file_path == expected_path 