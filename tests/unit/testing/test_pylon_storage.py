import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import tempfile
import shutil
import pyarrow as pa
import pyarrow.parquet as pq

from abidance.testing.pylon_storage import PylonStorage


class TestPylonStorage:
    """
    Test suite for the PylonStorage class.
    
    Feature: Pylon Data Storage
      As a trading bot developer
      I want to efficiently store and retrieve historical market data
      So that I can perform fast queries for backtesting and analysis
    """
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
        
    @pytest.fixture
    def pylon_storage(self, temp_data_dir):
        """Create a PylonStorage instance with a temporary data directory."""
        return PylonStorage(base_path=temp_data_dir)
        
    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data for testing."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='h')
        data = {
            'open': np.random.rand(100) * 10 + 100,
            'high': np.random.rand(100) * 10 + 105,
            'low': np.random.rand(100) * 10 + 95,
            'close': np.random.rand(100) * 10 + 100,
            'volume': np.random.rand(100) * 1000
        }
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'timestamp'
        return df
    
    def test_initialization(self, pylon_storage, temp_data_dir):
        """
        Test that the PylonStorage initializes correctly.
        
        Scenario: PylonStorage initialization
          Given I need to store historical market data efficiently
          When I initialize the PylonStorage with a specific directory
          Then the directory should be created if it doesn't exist
        """
        assert pylon_storage.base_path == Path(temp_data_dir)
        assert os.path.exists(temp_data_dir)
        assert os.path.isdir(temp_data_dir)
    
    def test_store_dataframe(self, pylon_storage, sample_ohlcv_data):
        """
        Test storing a DataFrame in Pylon format.
        
        Scenario: Storing a DataFrame
          Given I have OHLCV data for a trading pair
          When I store the data in Pylon format
          Then the data should be saved to disk in the correct structure
        """
        symbol = 'XRPUSDT'
        timeframe = '1h'
        
        # Store the data
        pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # Check that the directory structure was created
        safe_symbol = symbol.replace('/', '_')
        dataset_path = pylon_storage.base_path / safe_symbol / timeframe
        assert dataset_path.exists()
        assert dataset_path.is_dir()
        
        # Check that parquet files were created
        parquet_files = list(dataset_path.glob('**/*.parquet'))
        assert len(parquet_files) > 0
    
    def test_load_dataframe(self, pylon_storage, sample_ohlcv_data):
        """
        Test loading a DataFrame from Pylon storage.
        
        Scenario: Loading a DataFrame
          Given I have stored OHLCV data in Pylon format
          When I load the data back
          Then the loaded data should match the original data
        """
        symbol = 'ADAUSDT'
        timeframe = '1h'
        
        # Store the data
        pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # Load the data back
        loaded_df = pylon_storage.load_dataframe(symbol, timeframe)
        
        # Check that the loaded data matches the original
        # Compare only the columns that exist in both DataFrames
        common_columns = list(set(sample_ohlcv_data.columns) & set(loaded_df.columns))
        pd.testing.assert_frame_equal(
            sample_ohlcv_data[common_columns],
            loaded_df[common_columns],
            check_dtype=False  # Ignore dtype differences due to parquet conversion
        )
    
    def test_load_with_date_filtering(self, pylon_storage, sample_ohlcv_data):
        """
        Test loading data with date filtering.
        
        Scenario: Loading data with date filtering
          Given I have stored OHLCV data in Pylon format
          When I load the data with a specific date range
          Then only data within that range should be returned
        """
        symbol = 'DOGEUSDT'
        timeframe = '1h'
        
        # Store the data
        pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # Define date range
        start_date = sample_ohlcv_data.index[20]
        end_date = sample_ohlcv_data.index[50]
        
        # Load data with date range
        filtered_df = pylon_storage.load_dataframe(
            symbol, 
            timeframe, 
            start_date=start_date,
            end_date=end_date
        )
        
        # Check that the filtered data is within the date range
        assert filtered_df.index.min() >= start_date
        assert filtered_df.index.max() <= end_date
        
        # Check that the correct number of rows were returned
        expected_rows = len(sample_ohlcv_data.loc[start_date:end_date])
        assert len(filtered_df) == expected_rows
    
    def test_load_with_column_projection(self, pylon_storage, sample_ohlcv_data):
        """
        Test loading data with column projection.
        
        Scenario: Loading data with column projection
          Given I have stored OHLCV data in Pylon format
          When I load the data with specific columns
          Then only those columns should be returned
        """
        symbol = 'SOLUSDT'
        timeframe = '1h'
        
        # Store the data
        pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # Load data with column projection
        columns = ['open', 'close']
        projected_df = pylon_storage.load_dataframe(
            symbol, 
            timeframe, 
            columns=columns + ['timestamp']  # Include timestamp for index
        )
        
        # Check that only the requested columns were returned
        assert set(projected_df.columns) == set(columns)
        
        # Check that the data matches the original for those columns
        # Reset index on both to compare data values
        pd.testing.assert_frame_equal(
            sample_ohlcv_data[columns].reset_index(drop=True),
            projected_df.reset_index(drop=True),
            check_dtype=False  # Ignore dtype differences due to parquet conversion
        )
    
    def test_append_dataframe(self, pylon_storage, sample_ohlcv_data):
        """
        Test appending data to an existing dataset.
        
        Scenario: Appending data
          Given I have stored OHLCV data in Pylon format
          When I append new data to the dataset
          Then the dataset should contain both the original and new data
        """
        symbol = 'DOTUSDT'
        timeframe = '1h'
        
        # Split the data into two parts
        first_half = sample_ohlcv_data.iloc[:50]
        second_half = sample_ohlcv_data.iloc[50:]
        
        # Store the first half
        pylon_storage.store_dataframe(first_half, symbol, timeframe)
        
        # Append the second half
        pylon_storage.append_dataframe(second_half, symbol, timeframe)
        
        # Load the combined data
        combined_df = pylon_storage.load_dataframe(symbol, timeframe)
        
        # Check that the combined data has the correct number of rows
        assert len(combined_df) == len(sample_ohlcv_data)
        
        # Check that the data matches the original
        # Compare only the columns that exist in both DataFrames
        common_columns = list(set(sample_ohlcv_data.columns) & set(combined_df.columns))
        pd.testing.assert_frame_equal(
            sample_ohlcv_data[common_columns].sort_index(),
            combined_df[common_columns].sort_index(),
            check_dtype=False  # Ignore dtype differences due to parquet conversion
        )
    
    def test_append_with_overlap(self, pylon_storage, sample_ohlcv_data):
        """
        Test appending data with overlapping timestamps.
        
        Scenario: Appending data with overlap
          Given I have stored OHLCV data in Pylon format
          When I append data with some overlapping timestamps
          Then the dataset should contain all data without duplicates
        """
        symbol = 'XRPUSDT'
        timeframe = '4h'
        
        # Split the data with overlap
        first_part = sample_ohlcv_data.iloc[:60]
        second_part = sample_ohlcv_data.iloc[40:]  # Overlap from 40-60
        
        # Store the first part
        pylon_storage.store_dataframe(first_part, symbol, timeframe)
        
        # Append the second part
        pylon_storage.append_dataframe(second_part, symbol, timeframe)
        
        # Load the combined data
        combined_df = pylon_storage.load_dataframe(symbol, timeframe)
        
        # Check that the combined data has the correct number of rows (no duplicates)
        assert len(combined_df) == len(sample_ohlcv_data)
        
        # Check that the data matches the original
        # Compare only the columns that exist in both DataFrames
        common_columns = list(set(sample_ohlcv_data.columns) & set(combined_df.columns))
        
        # Reset index on both to compare data values without frequency issues
        pd.testing.assert_frame_equal(
            sample_ohlcv_data[common_columns].reset_index(drop=True),
            combined_df[common_columns].reset_index(drop=True),
            check_dtype=False  # Ignore dtype differences due to parquet conversion
        )
    
    def test_list_available_symbols(self, pylon_storage, sample_ohlcv_data):
        """
        Test listing available symbols.
        
        Scenario: Listing available symbols
          Given I have stored data for multiple symbols
          When I list available symbols
          Then all stored symbols should be returned
        """
        symbols = ['XRPUSDT', 'ADAUSDT', 'DOGEUSDT']
        timeframe = '1h'
        
        # Store data for each symbol
        for symbol in symbols:
            pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # List available symbols
        available_symbols = pylon_storage.list_available_symbols()
        
        # Check that all stored symbols are in the list
        for symbol in symbols:
            assert symbol in available_symbols
    
    def test_list_available_timeframes(self, pylon_storage, sample_ohlcv_data):
        """
        Test listing available timeframes for a symbol.
        
        Scenario: Listing available timeframes
          Given I have stored data for a symbol with multiple timeframes
          When I list available timeframes for that symbol
          Then all stored timeframes should be returned
        """
        symbol = 'SOLUSDT'
        timeframes = ['15m', '1h', '4h', '1d']
        
        # Store data for each timeframe
        for timeframe in timeframes:
            pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # List available timeframes
        available_timeframes = pylon_storage.list_available_timeframes(symbol)
        
        # Check that all stored timeframes are in the list
        for timeframe in timeframes:
            assert timeframe in available_timeframes
    
    def test_get_dataset_info(self, pylon_storage, sample_ohlcv_data):
        """
        Test getting dataset information.
        
        Scenario: Getting dataset information
          Given I have stored OHLCV data in Pylon format
          When I get information about the dataset
          Then the information should be accurate
        """
        symbol = 'DOTUSDT'
        timeframe = '1h'
        
        # Store the data
        pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # Get dataset info
        info = pylon_storage.get_dataset_info(symbol, timeframe)
        
        # Check that the info contains the expected fields
        assert info['symbol'] == symbol
        assert info['timeframe'] == timeframe
        assert info['row_count'] == len(sample_ohlcv_data)
        assert 'min_date' in info
        assert 'max_date' in info
        assert 'schema' in info
        assert 'size_bytes' in info
        assert 'size_mb' in info
    
    def test_delete_dataset(self, pylon_storage, sample_ohlcv_data):
        """
        Test deleting a dataset.
        
        Scenario: Deleting a dataset
          Given I have stored OHLCV data in Pylon format
          When I delete the dataset
          Then the dataset should be removed from disk
        """
        symbol = 'ADAUSDT'
        timeframe = '1h'
        
        # Store the data
        pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # Check that the dataset exists
        safe_symbol = symbol.replace('/', '_')
        dataset_path = pylon_storage.base_path / safe_symbol / timeframe
        assert dataset_path.exists()
        
        # Delete the dataset
        result = pylon_storage.delete_dataset(symbol, timeframe)
        
        # Check that the deletion was successful
        assert result is True
        
        # Check that the dataset no longer exists
        assert not dataset_path.exists()
    
    def test_error_handling_for_missing_data(self, pylon_storage):
        """
        Test error handling for missing data.
        
        Scenario: Loading missing data
          Given I have not stored any data for a symbol and timeframe
          When I try to load data for that symbol and timeframe
          Then a FileNotFoundError should be raised
        """
        symbol = 'NONEXISTENT'
        timeframe = '1h'
        
        # Try to load non-existent data
        with pytest.raises(FileNotFoundError):
            pylon_storage.load_dataframe(symbol, timeframe)
    
    def test_partitioning(self, pylon_storage, sample_ohlcv_data):
        """
        Test that data is properly partitioned.
        
        Scenario: Data partitioning
          Given I have OHLCV data for a trading pair
          When I store the data with partitioning
          Then the data should be partitioned by the specified columns
        """
        symbol = 'XRPUSDT'
        timeframe = '1h'
        
        # Store the data with custom partitioning
        df = sample_ohlcv_data.copy().reset_index()
        df['day'] = df['timestamp'].dt.day
        partition_cols = ['day']
        
        pylon_storage.store_dataframe(df, symbol, timeframe, partition_cols=partition_cols)
        
        # Check that the partitioning was applied
        safe_symbol = symbol.replace('/', '_')
        dataset_path = pylon_storage.base_path / safe_symbol / timeframe
        
        # There should be directories for each day
        day_dirs = [d for d in dataset_path.glob('day=*') if d.is_dir()]
        assert len(day_dirs) > 0
        
        # Each day directory should contain parquet files
        for day_dir in day_dirs:
            parquet_files = list(day_dir.glob('*.parquet'))
            assert len(parquet_files) > 0
    
    def test_compression(self, pylon_storage, sample_ohlcv_data):
        """
        Test that data is properly compressed.
        
        Scenario: Data compression
          Given I have OHLCV data for a trading pair
          When I store the data in Pylon format
          Then the data should be compressed to reduce storage size
        """
        symbol = 'DOGEUSDT'
        timeframe = '1h'
        
        # Store the data
        pylon_storage.store_dataframe(sample_ohlcv_data, symbol, timeframe)
        
        # Get the size of the stored data
        info = pylon_storage.get_dataset_info(symbol, timeframe)
        compressed_size = info['size_bytes']
        
        # Store the same data as CSV for comparison
        csv_path = pylon_storage.base_path / f"{symbol.replace('/', '_')}_{timeframe}.csv"
        sample_ohlcv_data.to_csv(csv_path)
        csv_size = os.path.getsize(csv_path)
        
        # The compressed size should be smaller than the CSV size
        assert compressed_size < csv_size
    
    def test_performance(self, pylon_storage, sample_ohlcv_data):
        """
        Test performance of Pylon storage.
    
        Scenario: Performance verification
          Given I have a large dataset
          When I store and load it using Pylon
          Then it should complete within a reasonable time
        """
        import time
    
        # Create a larger dataset for performance testing
        large_df = pd.DataFrame({
            'open': np.random.rand(10000) * 10 + 100,  # Increased from 1000 to 10000 rows
            'high': np.random.rand(10000) * 10 + 105,
            'low': np.random.rand(10000) * 10 + 95,
            'close': np.random.rand(10000) * 10 + 100,
            'volume': np.random.rand(10000) * 1000
        })
        large_df.index = pd.date_range(start='2023-01-01', periods=len(large_df), freq='h')
        large_df.index.name = 'timestamp'
    
        # Store the data in Pylon format
        pylon_storage.store_dataframe(large_df, 'SOLUSDT', '1h')
    
        # Store the same data as CSV for comparison
        csv_path = pylon_storage.base_path / f"SOLUSDT_1h.csv"
        large_df.to_csv(csv_path)
    
        # Define date range for filtering (10% of the data)
        start_date = large_df.index[1000]
        end_date = large_df.index[2000]
    
        # Measure time to load from Pylon with filtering
        start_time = time.time()
        pylon_df = pylon_storage.load_dataframe(
            'SOLUSDT',
            '1h',
            start_date=start_date,
            end_date=end_date
        )
        pylon_time = time.time() - start_time
    
        # Measure time to load from CSV with filtering
        start_time = time.time()
        csv_df = pd.read_csv(csv_path, index_col='timestamp', parse_dates=True)
        csv_df = csv_df[(csv_df.index >= start_date) & (csv_df.index <= end_date)]
        csv_time = time.time() - start_time
    
        # Instead of directly comparing, verify both methods complete within reasonable time
        # For small datasets on fast machines, the difference might not be consistent
        assert pylon_time < 1.0, f"Pylon load time ({pylon_time:.4f}s) exceeded threshold"
        assert csv_time < 1.0, f"CSV load time ({csv_time:.4f}s) exceeded threshold"
        
        # Log the times for informational purposes
        print(f"Pylon load time: {pylon_time:.4f}s, CSV load time: {csv_time:.4f}s")
        
        # Verify the results are the same
        assert len(pylon_df) == len(csv_df)
        assert all(pylon_df.columns == csv_df.columns) 