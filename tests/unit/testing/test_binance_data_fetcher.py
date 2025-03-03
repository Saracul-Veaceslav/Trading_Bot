import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock, ANY
import ccxt

from abidance.testing.data_management import HistoricalDataManager
from abidance.testing.binance_data_fetcher import BinanceDataFetcher


class TestBinanceDataFetcher:
    """
    Test suite for the BinanceDataFetcher class.
    
    Feature: Binance Historical Data Import
      As a trading bot developer
      I want to efficiently fetch and store historical data from Binance
      So that I can backtest trading strategies with accurate market data
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
    def mock_ccxt_binance(self):
        """Create a mock Binance exchange instance."""
        with patch('ccxt.binance') as mock_exchange_class:
            mock_exchange = MagicMock()
            mock_exchange_class.return_value = mock_exchange
            yield mock_exchange
    
    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data for testing."""
        # Create sample data in the format returned by ccxt
        now = datetime.now()
        timestamps = [int((now - timedelta(hours=i)).timestamp() * 1000) for i in range(100)]
        
        ohlcv_data = []
        for ts in timestamps:
            ohlcv_data.append([
                ts,
                np.random.rand() * 10 + 100,  # open
                np.random.rand() * 10 + 105,  # high
                np.random.rand() * 10 + 95,   # low
                np.random.rand() * 10 + 100,  # close
                np.random.rand() * 1000       # volume
            ])
            
        return ohlcv_data
    
    @pytest.fixture
    def binance_fetcher(self, data_manager, mock_ccxt_binance):
        """Create a BinanceDataFetcher instance with mocked dependencies."""
        # Import here to avoid circular import during test collection
        return BinanceDataFetcher(data_manager=data_manager)
    
    def test_initialization(self, binance_fetcher, data_manager):
        """
        Test that the BinanceDataFetcher initializes correctly.
        
        Scenario: BinanceDataFetcher initialization
          Given I need to fetch historical data from Binance
          When I initialize the BinanceDataFetcher
          Then it should be properly configured with the correct exchange and data manager
        """
        assert binance_fetcher.exchange_id == 'binance'
        assert binance_fetcher.data_manager == data_manager
        assert hasattr(binance_fetcher, 'exchange')
        assert binance_fetcher.supported_timeframes == ['15m', '1h', '4h', '1d']
        assert binance_fetcher.supported_symbols == ['XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT', 'DOTUSDT']
    
    def test_fetch_historical_data(self, binance_fetcher, mock_ccxt_binance, sample_ohlcv_data):
        """
        Test fetching historical data for a single symbol and timeframe.
        
        Scenario: Fetching historical data
          Given I have a BinanceDataFetcher
          When I fetch historical data for a symbol and timeframe
          Then the data should be returned as a DataFrame with the correct format
        """
        # Configure mock to return sample data
        mock_ccxt_binance.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Fetch data
        symbol = 'XRPUSDT'
        timeframe = '1h'
        df = binance_fetcher.fetch_historical_data(symbol, timeframe)
        
        # Check that the exchange API was called correctly
        mock_ccxt_binance.fetch_ohlcv.assert_called_with(symbol, timeframe, since=ANY, limit=1000)
        
        # Check that the returned data is a DataFrame with the expected columns
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert len(df) == len(sample_ohlcv_data)
        
        # Check that the index is a DatetimeIndex
        assert isinstance(df.index, pd.DatetimeIndex)
    
    def test_fetch_with_date_range(self, binance_fetcher, mock_ccxt_binance, sample_ohlcv_data):
        """
        Test fetching historical data with a specific date range.
        
        Scenario: Fetching data with date range
          Given I have a BinanceDataFetcher
          When I fetch historical data with a specific date range
          Then only data within that range should be returned
        """
        # Configure mock to return sample data
        mock_ccxt_binance.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Fetch data with date range
        symbol = 'ADAUSDT'
        timeframe = '4h'
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        df = binance_fetcher.fetch_historical_data(
            symbol, 
            timeframe, 
            start_date=start_date,
            end_date=end_date
        )
        
        # Check that the exchange API was called with the correct since parameter
        mock_ccxt_binance.fetch_ohlcv.assert_called_with(
            symbol, 
            timeframe, 
            since=int(start_date.timestamp() * 1000),
            limit=1000
        )
        
        # Check that the returned data is filtered by the end date
        if not df.empty:
            assert df.index.min() >= pd.Timestamp(start_date)
            assert df.index.max() <= pd.Timestamp(end_date)
    
    def test_fetch_with_pagination(self, binance_fetcher, mock_ccxt_binance):
        """
        Test fetching historical data with pagination for large date ranges.
        
        Scenario: Fetching data with pagination
          Given I have a BinanceDataFetcher
          When I fetch historical data for a large date range
          Then the data should be fetched in multiple batches and combined
        """
        # Create two batches of sample data with different timestamps
        batch1 = [[int((datetime.now() - timedelta(days=i)).timestamp() * 1000), 100, 105, 95, 101, 1000] 
                 for i in range(10, 0, -1)]
        batch2 = [[int((datetime.now() - timedelta(days=i)).timestamp() * 1000), 102, 107, 97, 103, 1200] 
                 for i in range(20, 10, -1)]
        
        # Configure mock to return different batches on consecutive calls
        mock_ccxt_binance.fetch_ohlcv.side_effect = [batch1, batch2, []]
        
        # Fetch data with a large date range
        symbol = 'DOGEUSDT'
        timeframe = '1d'
        start_date = datetime.now() - timedelta(days=30)
        
        df = binance_fetcher.fetch_historical_data(
            symbol, 
            timeframe, 
            start_date=start_date,
            use_pagination=True
        )
        
        # Check that the exchange API was called multiple times
        assert mock_ccxt_binance.fetch_ohlcv.call_count >= 2
        
        # Check that the returned data contains all batches
        assert len(df) == len(batch1) + len(batch2)
    
    def test_save_to_data_manager(self, binance_fetcher, mock_ccxt_binance, sample_ohlcv_data, data_manager):
        """
        Test that fetched data is saved to the data manager.
        
        Scenario: Saving fetched data
          Given I have a BinanceDataFetcher
          When I fetch historical data with save=True
          Then the data should be saved to the data manager
        """
        # Configure mock to return sample data
        mock_ccxt_binance.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Spy on the data_manager.save_ohlcv method
        with patch.object(data_manager, 'save_ohlcv', wraps=data_manager.save_ohlcv) as mock_save:
            # Fetch data with save=True
            symbol = 'SOLUSDT'
            timeframe = '1h'
            df = binance_fetcher.fetch_historical_data(symbol, timeframe, save=True)
            
            # Check that save_ohlcv was called with the correct arguments
            mock_save.assert_called_once_with(symbol, timeframe, df)
            
            # Check that the file was created
            file_path = data_manager._get_ohlcv_path(symbol, timeframe)
            assert file_path.exists()
    
    def test_fetch_multiple_symbols(self, binance_fetcher, mock_ccxt_binance, sample_ohlcv_data):
        """
        Test fetching historical data for multiple symbols.
        
        Scenario: Fetching data for multiple symbols
          Given I have a BinanceDataFetcher
          When I fetch historical data for multiple symbols
          Then data for all symbols should be fetched and returned
        """
        # Configure mock to return sample data
        mock_ccxt_binance.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Fetch data for multiple symbols
        symbols = ['XRPUSDT', 'ADAUSDT']
        timeframe = '1h'
        
        results = binance_fetcher.fetch_multiple_symbols(symbols, timeframe)
        
        # Check that the exchange API was called for each symbol
        assert mock_ccxt_binance.fetch_ohlcv.call_count == len(symbols)
        
        # Check that results contains data for all symbols
        assert len(results) == len(symbols)
        assert all(symbol in results for symbol in symbols)
        assert all(isinstance(df, pd.DataFrame) for df in results.values())
    
    def test_fetch_multiple_timeframes(self, binance_fetcher, mock_ccxt_binance, sample_ohlcv_data):
        """
        Test fetching historical data for multiple timeframes.
        
        Scenario: Fetching data for multiple timeframes
          Given I have a BinanceDataFetcher
          When I fetch historical data for multiple timeframes
          Then data for all timeframes should be fetched and returned
        """
        # Configure mock to return sample data
        mock_ccxt_binance.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Fetch data for multiple timeframes
        symbol = 'DOTUSDT'
        timeframes = ['15m', '1h']
        
        results = binance_fetcher.fetch_multiple_timeframes(symbol, timeframes)
        
        # Check that the exchange API was called for each timeframe
        assert mock_ccxt_binance.fetch_ohlcv.call_count == len(timeframes)
        
        # Check that results contains data for all timeframes
        assert len(results) == len(timeframes)
        assert all(timeframe in results for timeframe in timeframes)
        assert all(isinstance(df, pd.DataFrame) for df in results.values())
    
    def test_fetch_all_data(self, binance_fetcher, mock_ccxt_binance, sample_ohlcv_data):
        """
        Test fetching all historical data for all supported symbols and timeframes.
        
        Scenario: Fetching all data
          Given I have a BinanceDataFetcher
          When I fetch all historical data
          Then data for all supported symbols and timeframes should be fetched
        """
        # Configure mock to return sample data
        mock_ccxt_binance.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Fetch all data
        results = binance_fetcher.fetch_all_data()
        
        # Check that the exchange API was called for each symbol and timeframe combination
        expected_calls = len(binance_fetcher.supported_symbols) * len(binance_fetcher.supported_timeframes)
        assert mock_ccxt_binance.fetch_ohlcv.call_count == expected_calls
        
        # Check that results contains data for all symbols and timeframes
        assert len(results) == len(binance_fetcher.supported_symbols)
        assert all(symbol in results for symbol in binance_fetcher.supported_symbols)
        assert all(len(results[symbol]) == len(binance_fetcher.supported_timeframes) 
                  for symbol in binance_fetcher.supported_symbols)
    
    def test_handle_rate_limits(self, binance_fetcher, mock_ccxt_binance):
        """
        Test handling of rate limits when fetching data.
        
        Scenario: Handling rate limits
          Given I have a BinanceDataFetcher
          When I encounter rate limit errors
          Then the fetcher should implement backoff and retry logic
        """
        # Configure mock to raise rate limit error on first call, then succeed
        rate_limit_error = ccxt.RateLimitExceeded('Rate limit exceeded')
        mock_ccxt_binance.fetch_ohlcv.side_effect = [rate_limit_error, [[1, 100, 105, 95, 101, 1000]]]
        
        # Patch time.sleep to avoid waiting during tests
        with patch('time.sleep'):
            # Fetch data
            symbol = 'XRPUSDT'
            timeframe = '1h'
            df = binance_fetcher.fetch_historical_data(symbol, timeframe)
            
            # Check that the exchange API was called twice (once failing, once succeeding)
            assert mock_ccxt_binance.fetch_ohlcv.call_count == 2
            
            # Check that data was returned despite the rate limit error
            assert not df.empty
    
    def test_error_handling(self, binance_fetcher, mock_ccxt_binance):
        """
        Test handling of various errors when fetching data.
        
        Scenario: Error handling
          Given I have a BinanceDataFetcher
          When I encounter various errors
          Then the fetcher should handle them gracefully
        """
        # Configure mock to raise different types of errors
        errors = [
            ccxt.NetworkError('Network error'),
            ccxt.ExchangeError('Exchange error'),
            ccxt.InvalidNonce('Invalid nonce'),
            Exception('Generic error')
        ]
        
        for error in errors:
            mock_ccxt_binance.fetch_ohlcv.side_effect = error
            
            # Fetch data with error handling
            symbol = 'XRPUSDT'
            timeframe = '1h'
            
            # The method should raise the error or return empty DataFrame depending on implementation
            try:
                df = binance_fetcher.fetch_historical_data(symbol, timeframe)
                # If it returns a DataFrame, it should be empty
                assert df.empty
            except Exception as e:
                # If it raises an error, it should be the same type
                assert isinstance(e, type(error))
    
    def test_pylon_integration(self, binance_fetcher, mock_ccxt_binance, sample_ohlcv_data):
        """
        Test integration with Pylon for efficient data storage.
        
        Scenario: Pylon integration
          Given I have a BinanceDataFetcher with Pylon integration
          When I fetch and store historical data
          Then the data should be stored in Pylon format
        """
        # Configure mock to return sample data
        mock_ccxt_binance.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Mock the Pylon storage method
        with patch('abidance.testing.binance_data_fetcher.PylonStorage') as mock_pylon:
            mock_pylon_instance = MagicMock()
            mock_pylon.return_value = mock_pylon_instance
            
            # Fetch data with Pylon storage
            symbol = 'XRPUSDT'
            timeframe = '1h'
            df = binance_fetcher.fetch_historical_data(
                symbol, 
                timeframe, 
                use_pylon=True
            )
            
            # Check that Pylon storage was used
            mock_pylon_instance.store_dataframe.assert_called_once()
            
            # Check that the correct data was passed to Pylon
            args, kwargs = mock_pylon_instance.store_dataframe.call_args
            stored_df = args[0]
            assert isinstance(stored_df, pd.DataFrame)
            assert len(stored_df) == len(sample_ohlcv_data)
    
    def test_parallel_fetching(self, binance_fetcher, mock_ccxt_binance, sample_ohlcv_data):
        """
        Test parallel fetching of historical data.
        
        Scenario: Parallel fetching
          Given I have a BinanceDataFetcher
          When I fetch data for multiple symbols in parallel
          Then the data should be fetched concurrently for better performance
        """
        # Configure mock to return sample data
        mock_ccxt_binance.fetch_ohlcv.return_value = sample_ohlcv_data
        
        # Create a sample dataframe for testing
        sample_df = pd.DataFrame(
            sample_ohlcv_data, 
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        ).set_index('timestamp')
        
        # Mock the fetch_historical_data method to return the sample dataframe
        with patch.object(binance_fetcher, 'fetch_historical_data', return_value=sample_df) as mock_fetch:
            # Fetch data in parallel
            symbols = ['XRPUSDT', 'ADAUSDT', 'DOGEUSDT']
            timeframe = '1h'
            results = binance_fetcher.fetch_multiple_symbols_parallel(symbols, timeframe)
            
            # Check that fetch_historical_data was called for each symbol
            assert mock_fetch.call_count == len(symbols)
            
            # Check that results contains data for all symbols
            assert len(results) == len(symbols)
            assert all(symbol in results for symbol in symbols) 