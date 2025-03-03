import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from abidance.testing.data_management import HistoricalDataManager
from abidance.testing.data_loaders import ExchangeDataLoader, CSVDataLoader


class TestExchangeDataLoader:
    """
    Test suite for the ExchangeDataLoader class.
    
    Feature: Exchange Data Loading
      As a trading bot developer
      I want to load historical data from exchanges
      So that I can backtest trading strategies with real market data
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
    def mock_exchange(self):
        """Create a mock exchange instance."""
        with patch('ccxt.binance') as mock_exchange_class:
            mock_exchange = MagicMock()
            mock_exchange_class.return_value = mock_exchange
            yield mock_exchange
    
    @pytest.fixture
    def exchange_loader(self, data_manager, mock_exchange):
        """Create an exchange data loader with a mock exchange."""
        with patch('abidance.testing.data_loaders.getattr') as mock_getattr:
            mock_getattr.return_value = lambda: mock_exchange
            return ExchangeDataLoader('binance', data_manager)
    
    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data for testing."""
        # Create sample data in the format returned by ccxt
        now = datetime.now()
        timestamps = [int((now - timedelta(days=i)).timestamp() * 1000) for i in range(10)]
        
        ohlcv_data = []
        for ts in timestamps:
            ohlcv_data.append([
                ts,
                np.random.rand() * 1000 + 20000,  # open
                np.random.rand() * 1000 + 21000,  # high
                np.random.rand() * 1000 + 19000,  # low
                np.random.rand() * 1000 + 20500,  # close
                np.random.rand() * 100            # volume
            ])
            
        return ohlcv_data
    
    def test_fetch_ohlcv(self, exchange_loader, mock_exchange, sample_ohlcv_data):
        """
        Test fetching OHLCV data from an exchange.
        
        Scenario: Fetching OHLCV data from exchange
          Given I have an exchange data loader
          When I fetch OHLCV data for a trading pair
          Then the data should be returned as a DataFrame with the correct format
        """
        # Configure mock to return sample data
        mock_exchange.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Fetch data
        symbol = 'BTC/USD'
        timeframe = '1d'
        df = exchange_loader.fetch_ohlcv(symbol, timeframe, save=False)
        
        # Check that the exchange API was called correctly
        mock_exchange.fetch_ohlcv.assert_called_once_with(symbol, timeframe, None, 1000, {})
        
        # Check that the returned data is a DataFrame with the expected columns
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert len(df) == len(sample_ohlcv_data)
        
    def test_fetch_ohlcv_with_datetime(self, exchange_loader, mock_exchange, sample_ohlcv_data):
        """
        Test fetching OHLCV data with a datetime since parameter.
        
        Scenario: Fetching OHLCV data with datetime parameter
          Given I have an exchange data loader
          When I fetch OHLCV data with a datetime since parameter
          Then the datetime should be converted to a timestamp for the exchange API
        """
        # Configure mock to return sample data
        mock_exchange.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Fetch data with datetime since parameter
        symbol = 'BTC/USD'
        timeframe = '1d'
        since = datetime(2023, 1, 1)
        df = exchange_loader.fetch_ohlcv(symbol, timeframe, since=since, save=False)
        
        # Check that the exchange API was called with the converted timestamp
        expected_timestamp = int(since.timestamp() * 1000)
        mock_exchange.fetch_ohlcv.assert_called_once_with(symbol, timeframe, expected_timestamp, 1000, {})
        
    def test_fetch_ohlcv_with_save(self, exchange_loader, mock_exchange, sample_ohlcv_data, data_manager):
        """
        Test that fetched OHLCV data is saved to disk.
        
        Scenario: Saving fetched OHLCV data
          Given I have an exchange data loader
          When I fetch OHLCV data with save=True
          Then the data should be saved to disk using the data manager
        """
        # Configure mock to return sample data
        mock_exchange.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Spy on the data manager's save_ohlcv method
        with patch.object(data_manager, 'save_ohlcv') as mock_save:
            # Fetch data with save=True
            symbol = 'BTC/USD'
            timeframe = '1d'
            df = exchange_loader.fetch_ohlcv(symbol, timeframe, save=True)
            
            # Check that save_ohlcv was called with the correct arguments
            mock_save.assert_called_once()
            assert mock_save.call_args[0][0] == symbol
            assert mock_save.call_args[0][1] == timeframe
            pd.testing.assert_frame_equal(mock_save.call_args[0][2], df)
            
    def test_load_or_fetch_ohlcv_from_disk(self, exchange_loader, data_manager, sample_ohlcv_data):
        """
        Test loading OHLCV data from disk when available.
        
        Scenario: Loading OHLCV data from disk
          Given I have OHLCV data saved on disk
          When I call load_or_fetch_ohlcv
          Then the data should be loaded from disk without calling the exchange API
        """
        # Convert sample data to DataFrame
        timestamps = [row[0] for row in sample_ohlcv_data]
        df = pd.DataFrame({
            'open': [row[1] for row in sample_ohlcv_data],
            'high': [row[2] for row in sample_ohlcv_data],
            'low': [row[3] for row in sample_ohlcv_data],
            'close': [row[4] for row in sample_ohlcv_data],
            'volume': [row[5] for row in sample_ohlcv_data]
        }, index=pd.to_datetime(timestamps, unit='ms'))
        
        # Save data to disk
        symbol = 'ETH/USD'
        timeframe = '4h'
        data_manager.save_ohlcv(symbol, timeframe, df)
        
        # Mock the fetch_ohlcv method to verify it's not called
        with patch.object(exchange_loader, 'fetch_ohlcv') as mock_fetch:
            # Load data
            loaded_df = exchange_loader.load_or_fetch_ohlcv(symbol, timeframe)
            
            # Check that fetch_ohlcv was not called
            mock_fetch.assert_not_called()
            
            # Check that the loaded data matches the original
            pd.testing.assert_frame_equal(df, loaded_df)
            
    def test_load_or_fetch_ohlcv_from_exchange(self, exchange_loader, mock_exchange, sample_ohlcv_data):
        """
        Test fetching OHLCV data from exchange when not available on disk.
        
        Scenario: Fetching OHLCV data when not on disk
          Given I don't have OHLCV data saved on disk
          When I call load_or_fetch_ohlcv
          Then the data should be fetched from the exchange API
        """
        # Configure mock to return sample data
        mock_exchange.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Load or fetch data for a symbol that doesn't exist on disk
        symbol = 'LTC/USD'
        timeframe = '1h'
        df = exchange_loader.load_or_fetch_ohlcv(symbol, timeframe)
        
        # Check that the exchange API was called
        mock_exchange.fetch_ohlcv.assert_called_once()
        
        # Check that the returned data is a DataFrame with the expected columns
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert len(df) == len(sample_ohlcv_data)


class TestCSVDataLoader:
    """
    Test suite for the CSVDataLoader class.
    
    Feature: CSV Data Loading
      As a trading bot developer
      I want to load historical data from CSV files
      So that I can backtest trading strategies with custom data
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
    def csv_loader(self, data_manager):
        """Create a CSV data loader."""
        return CSVDataLoader(data_manager)
    
    @pytest.fixture
    def sample_csv_file(self, temp_data_dir):
        """Create a sample CSV file for testing."""
        # Create sample data
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        data = {
            'timestamp': dates,
            'open': np.random.rand(10) * 1000 + 20000,
            'high': np.random.rand(10) * 1000 + 21000,
            'low': np.random.rand(10) * 1000 + 19000,
            'close': np.random.rand(10) * 1000 + 20500,
            'volume': np.random.rand(10) * 100
        }
        df = pd.DataFrame(data)
        
        # Save to CSV
        file_path = os.path.join(temp_data_dir, 'sample_data.csv')
        df.to_csv(file_path, index=False)
        
        return file_path
    
    def test_load_csv(self, csv_loader, sample_csv_file):
        """
        Test loading data from a CSV file.
        
        Scenario: Loading data from CSV file
          Given I have a CSV file with OHLCV data
          When I load the data using the CSV loader
          Then the data should be returned as a DataFrame with the correct format
        """
        # Load data from CSV
        symbol = 'BTC/USD'
        timeframe = '1d'
        df = csv_loader.load_csv(sample_csv_file, symbol, timeframe, save=False)
        
        # Check that the returned data is a DataFrame with the expected columns
        assert isinstance(df, pd.DataFrame)
        assert set(df.columns) == {'open', 'high', 'low', 'close', 'volume'}
        assert len(df) == 10
        
    def test_load_csv_with_date_format(self, temp_data_dir, csv_loader):
        """
        Test loading data from a CSV file with a custom date format.
        
        Scenario: Loading data with custom date format
          Given I have a CSV file with dates in a custom format
          When I load the data with the specified date format
          Then the dates should be parsed correctly
        """
        # Create sample data with custom date format
        dates = ['01/01/2023', '01/02/2023', '01/03/2023']
        data = {
            'timestamp': dates,
            'open': [20000, 21000, 22000],
            'high': [21000, 22000, 23000],
            'low': [19000, 20000, 21000],
            'close': [20500, 21500, 22500],
            'volume': [100, 110, 120]
        }
        df = pd.DataFrame(data)
        
        # Save to CSV
        file_path = os.path.join(temp_data_dir, 'custom_dates.csv')
        df.to_csv(file_path, index=False)
        
        # Load data with custom date format
        symbol = 'ETH/USD'
        timeframe = '1d'
        loaded_df = csv_loader.load_csv(
            file_path, symbol, timeframe, 
            date_format='%m/%d/%Y', save=False
        )
        
        # Check that dates were parsed correctly
        assert loaded_df.index[0].strftime('%Y-%m-%d') == '2023-01-01'
        assert loaded_df.index[1].strftime('%Y-%m-%d') == '2023-01-02'
        assert loaded_df.index[2].strftime('%Y-%m-%d') == '2023-01-03'
        
    def test_load_csv_with_save(self, csv_loader, sample_csv_file, data_manager):
        """
        Test that loaded CSV data is saved to disk.
        
        Scenario: Saving loaded CSV data
          Given I have a CSV file with OHLCV data
          When I load the data with save=True
          Then the data should be saved to disk using the data manager
        """
        # Spy on the data manager's save_ohlcv method
        with patch.object(data_manager, 'save_ohlcv') as mock_save:
            # Load data with save=True
            symbol = 'BTC/USD'
            timeframe = '1d'
            df = csv_loader.load_csv(sample_csv_file, symbol, timeframe, save=True)
            
            # Check that save_ohlcv was called with the correct arguments
            mock_save.assert_called_once()
            assert mock_save.call_args[0][0] == symbol
            assert mock_save.call_args[0][1] == timeframe
            pd.testing.assert_frame_equal(mock_save.call_args[0][2], df)
            
    def test_load_csv_missing_file(self, csv_loader):
        """
        Test error handling when the CSV file doesn't exist.
        
        Scenario: Error handling for missing file
          Given I try to load data from a non-existent CSV file
          When I call the load_csv method
          Then a FileNotFoundError should be raised
        """
        # Try to load non-existent file
        with pytest.raises(FileNotFoundError):
            csv_loader.load_csv('nonexistent.csv', 'BTC/USD', '1d')
            
    def test_load_csv_missing_columns(self, temp_data_dir, csv_loader):
        """
        Test error handling when the CSV file is missing required columns.
        
        Scenario: Error handling for missing columns
          Given I have a CSV file missing required OHLCV columns
          When I call the load_csv method
          Then a ValueError should be raised
        """
        # Create sample data with missing columns
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        data = {
            'timestamp': dates,
            'open': np.random.rand(5) * 1000 + 20000,
            'close': np.random.rand(5) * 1000 + 20500,
            # Missing 'high', 'low', 'volume'
        }
        df = pd.DataFrame(data)
        
        # Save to CSV
        file_path = os.path.join(temp_data_dir, 'missing_columns.csv')
        df.to_csv(file_path, index=False)
        
        # Try to load file with missing columns
        with pytest.raises(ValueError) as excinfo:
            csv_loader.load_csv(file_path, 'BTC/USD', '1d')
            
        # Check error message
        assert "missing required columns" in str(excinfo.value) 