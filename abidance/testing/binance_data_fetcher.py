from typing import Dict, Any, Optional, List, Union, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
import logging
import time
import concurrent.futures
from pathlib import Path

from abidance.testing.data_management import HistoricalDataManager
from abidance.testing.pylon_storage import PylonStorage

logger = logging.getLogger(__name__)

class BinanceDataFetcher:
    """
    Fetcher for historical data from Binance exchange.

    This class provides methods to fetch historical OHLCV data from Binance
    for various symbols and timeframes, with support for efficient storage
    using both the HistoricalDataManager and PylonStorage.
    """

    def __init__(self,
                data_manager: Optional[HistoricalDataManager] = None,
                api_key: Optional[str] = None,
                api_secret: Optional[str] = None):
        """
        Initialize the Binance data fetcher.

        Args:
            data_manager: Optional data manager for saving/loading data
            api_key: Optional API key for authenticated requests
            api_secret: Optional API secret for authenticated requests
        """
        self.exchange_id = 'binance'
        self.data_manager = data_manager or HistoricalDataManager()

        # Initialize exchange
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,  # Enable built-in rate limiting
            'options': {
                'defaultType': 'spot',  # Use spot market by default
            }
        })

        # Define supported symbols and timeframes
        self.supported_symbols = ['XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT', 'DOTUSDT']
        self.supported_timeframes = ['15m', '1h', '4h', '1d']

        # Configure rate limiting parameters
        self.max_retries = 5
        self.retry_delay = 2  # seconds
        self.exponential_backoff = True

    def fetch_historical_data(self,
                             symbol: str,
                             timeframe: str,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             limit: int = 1000,
                             use_pagination: bool = False,
                             save: bool = False,
                             use_pylon: bool = False) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from Binance.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe for the data (e.g., '1h', '1d')
            start_date: Optional start date for the data
            end_date: Optional end date for the data
            limit: Maximum number of candles to fetch per request
            use_pagination: Whether to use pagination for large date ranges
            save: Whether to save the data to the data manager
            use_pylon: Whether to use Pylon storage for efficient storage

        Returns:
            DataFrame with OHLCV data
        """
        # Validate inputs
        if symbol not in self.supported_symbols:
            logger.warning(f"Symbol {symbol} is not in the list of supported symbols: {self.supported_symbols}")

        if timeframe not in self.supported_timeframes:
            logger.warning(f"Timeframe {timeframe} is not in the list of supported timeframes: {self.supported_timeframes}")

        # Convert start_date to millisecond timestamp for CCXT
        since = None
        if start_date:
            since = int(start_date.timestamp() * 1000)

        # Initialize empty list for all candles
        all_candles = []

        if use_pagination:
            # Fetch data in batches with pagination
            current_since = since
            while True:
                try:
                    # Fetch a batch of candles
                    candles = self._fetch_ohlcv_with_retry(
                        symbol,
                        timeframe,
                        since=current_since,
                        limit=limit
                    )

                    if not candles or len(candles) == 0:
                        # No more data to fetch
                        break

                    # Add candles to the result
                    all_candles.extend(candles)

                    # Update since for the next batch
                    last_timestamp = candles[-1][0]
                    current_since = last_timestamp + 1  # Add 1ms to avoid duplicates

                    # Check if we've reached the end date
                    if end_date and last_timestamp >= int(end_date.timestamp() * 1000):
                        break

                    # Add a small delay to avoid rate limiting
                    time.sleep(0.2)

                except Exception as e:
                    logger.error(f"Error fetching data with pagination: {e}")
                    break
        else:
            # Fetch data in a single request
            all_candles = self._fetch_ohlcv_with_retry(
                symbol,
                timeframe,
                since=since,
                limit=limit
            )

        # Convert to DataFrame
        if not all_candles:
            logger.warning(f"No data returned for {symbol} {timeframe}")
            return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])

        df = pd.DataFrame(
            all_candles,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )

        # Convert timestamp to datetime and set as index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Filter by end_date if provided
        if end_date:
            df = df[df.index <= end_date]

        # Save data if requested or if use_pylon is True
        if save or use_pylon:
            if use_pylon:
                # Use Pylon storage for efficient storage
                pylon = PylonStorage()
                pylon.store_dataframe(df, symbol, timeframe)
            else:
                # Use regular data manager
                self.data_manager.save_ohlcv(symbol, timeframe, df)

        return df

    def _fetch_ohlcv_with_retry(self,
                               symbol: str,
                               timeframe: str,
                               since: Optional[int] = None,
                               limit: int = 1000) -> List[List[float]]:
        """
        Fetch OHLCV data with retry logic for handling rate limits.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe for the data
            since: Optional start time as millisecond timestamp
            limit: Maximum number of candles to fetch

        Returns:
            List of OHLCV candles
        """
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                # Fetch data from exchange
                candles = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=since,
                    limit=limit
                )
                return candles

            except ccxt.RateLimitExceeded as e:
                retry_count += 1
                if retry_count >= self.max_retries:
                    logger.error(f"Max retries exceeded for {symbol} {timeframe}: {e}")
                    raise

                # Calculate delay with exponential backoff if enabled
                delay = self.retry_delay
                if self.exponential_backoff:
                    delay = self.retry_delay * (2 ** (retry_count - 1))

                logger.warning(f"Rate limit exceeded, retrying in {delay}s ({retry_count}/{self.max_retries})")
                time.sleep(delay)

            except (ccxt.NetworkError, ccxt.ExchangeError) as e:
                logger.error(f"Error fetching data for {symbol} {timeframe}: {e}")
                raise

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise

        # If we get here, all retries failed
        return []

    def fetch_multiple_symbols(self,
                              symbols: List[str],
                              timeframe: str,
                              **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple symbols.

        Args:
            symbols: List of trading pair symbols
            timeframe: Timeframe for the data
            **kwargs: Additional arguments to pass to fetch_historical_data

        Returns:
            Dictionary mapping symbols to their respective DataFrames
        """
        results = {}
        for symbol in symbols:
            try:
                df = self.fetch_historical_data(symbol, timeframe, **kwargs)
                results[symbol] = df
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                results[symbol] = pd.DataFrame()  # Empty DataFrame for failed fetches

        return results

    def fetch_multiple_timeframes(self,
                                 symbol: str,
                                 timeframes: List[str],
                                 **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple timeframes.

        Args:
            symbol: Trading pair symbol
            timeframes: List of timeframes
            **kwargs: Additional arguments to pass to fetch_historical_data

        Returns:
            Dictionary mapping timeframes to their respective DataFrames
        """
        results = {}
        for timeframe in timeframes:
            try:
                df = self.fetch_historical_data(symbol, timeframe, **kwargs)
                results[timeframe] = df
            except Exception as e:
                logger.error(f"Error fetching data for {timeframe}: {e}")
                results[timeframe] = pd.DataFrame()  # Empty DataFrame for failed fetches

        return results

    def fetch_all_data(self, **kwargs) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Fetch historical data for all supported symbols and timeframes.

        Args:
            **kwargs: Additional arguments to pass to fetch_historical_data

        Returns:
            Nested dictionary mapping symbols to timeframes to DataFrames
        """
        results = {}
        for symbol in self.supported_symbols:
            results[symbol] = {}
            for timeframe in self.supported_timeframes:
                try:
                    df = self.fetch_historical_data(symbol, timeframe, **kwargs)
                    results[symbol][timeframe] = df
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol} {timeframe}: {e}")
                    results[symbol][timeframe] = pd.DataFrame()  # Empty DataFrame for failed fetches

        return results

    def fetch_multiple_symbols_parallel(self,
                                       symbols: List[str],
                                       timeframe: str,
                                       max_workers: int = 5,
                                       **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple symbols in parallel.

        Args:
            symbols: List of trading pair symbols
            timeframe: Timeframe for the data
            max_workers: Maximum number of parallel workers
            **kwargs: Additional arguments to pass to fetch_historical_data

        Returns:
            Dictionary mapping symbols to their respective DataFrames
        """
        results = {}

        # Define a worker function for each symbol
        def fetch_symbol(symbol):
            try:
                df = self.fetch_historical_data(symbol, timeframe, **kwargs)
                return symbol, df
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                return symbol, pd.DataFrame()

        # Use ThreadPoolExecutor for parallel fetching
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        try:
            # Submit tasks
            futures = [executor.submit(fetch_symbol, symbol) for symbol in symbols]

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    symbol, df = future.result()
                    results[symbol] = df
                except Exception as e:
                    logger.error(f"Error processing result: {e}")
        finally:
            # Make sure to shut down the executor
            executor.shutdown(wait=False)

        return results

    def fetch_with_pylon_storage(self,
                                symbol: str,
                                timeframe: str,
                                pylon_path: str = 'data/pylon',
                                **kwargs) -> pd.DataFrame:
        """
        Fetch historical data and store it using Pylon storage.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe for the data
            pylon_path: Path for Pylon storage
            **kwargs: Additional arguments to pass to fetch_historical_data

        Returns:
            DataFrame with OHLCV data
        """
        # Initialize Pylon storage
        pylon = PylonStorage(base_path=pylon_path)

        # Try to load existing data
        try:
            # Get date range from kwargs
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')

            # Load existing data
            df = pylon.load_dataframe(symbol, timeframe, start_date, end_date)

            # If we have all the data we need, return it
            if start_date and end_date and df.index.min() <= start_date and df.index.max() >= end_date:
                return df

            # If we're missing some data, fetch only what we need
            if start_date and df.index.min() > start_date:
                # Need to fetch earlier data
                earlier_df = self.fetch_historical_data(
                    symbol,
                    timeframe,
                    start_date=start_date,
                    end_date=df.index.min() - timedelta(seconds=1),
                    **kwargs
                )
                if not earlier_df.empty:
                    # Append to existing data
                    pylon.append_dataframe(earlier_df, symbol, timeframe)
                    # Reload the combined data
                    df = pylon.load_dataframe(symbol, timeframe, start_date, end_date)

            if end_date and df.index.max() < end_date:
                # Need to fetch later data
                later_df = self.fetch_historical_data(
                    symbol,
                    timeframe,
                    start_date=df.index.max() + timedelta(seconds=1),
                    end_date=end_date,
                    **kwargs
                )
                if not later_df.empty:
                    # Append to existing data
                    pylon.append_dataframe(later_df, symbol, timeframe)
                    # Reload the combined data
                    df = pylon.load_dataframe(symbol, timeframe, start_date, end_date)

            return df

        except FileNotFoundError:
            # No existing data, fetch all
            df = self.fetch_historical_data(symbol, timeframe, **kwargs)
            if not df.empty:
                pylon.store_dataframe(df, symbol, timeframe)
            return df

    def update_all_data(self,
                       days_lookback: int = 30,
                       use_pylon: bool = True,
                       pylon_path: str = 'data/pylon') -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Update all historical data for all supported symbols and timeframes.

        Args:
            days_lookback: Number of days to look back for updates
            use_pylon: Whether to use Pylon storage
            pylon_path: Path for Pylon storage

        Returns:
            Nested dictionary mapping symbols to timeframes to DataFrames
        """
        start_date = datetime.now() - timedelta(days=days_lookback)
        end_date = datetime.now()

        results = {}
        for symbol in self.supported_symbols:
            results[symbol] = {}
            for timeframe in self.supported_timeframes:
                try:
                    if use_pylon:
                        df = self.fetch_with_pylon_storage(
                            symbol,
                            timeframe,
                            pylon_path=pylon_path,
                            start_date=start_date,
                            end_date=end_date,
                            use_pagination=True
                        )
                    else:
                        df = self.fetch_historical_data(
                            symbol,
                            timeframe,
                            start_date=start_date,
                            end_date=end_date,
                            use_pagination=True,
                            save=True
                        )
                    results[symbol][timeframe] = df
                except Exception as e:
                    logger.error(f"Error updating data for {symbol} {timeframe}: {e}")
                    results[symbol][timeframe] = pd.DataFrame()