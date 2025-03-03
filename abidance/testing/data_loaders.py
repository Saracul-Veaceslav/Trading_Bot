from typing import Dict, Any, Optional, List, Union, Callable
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
import logging
from pathlib import Path

from abidance.testing.data_management import HistoricalDataManager

logger = logging.getLogger(__name__)

class ExchangeDataLoader:
    """Load historical data from exchanges."""

    def __init__(self, exchange_id: str, data_manager: Optional[HistoricalDataManager] = None):
        """
        Initialize the exchange data loader.

        Args:
            exchange_id: The ID of the exchange to load data from
            data_manager: Optional data manager for saving/loading data
        """
        self.exchange_id = exchange_id
        self.exchange = getattr(ccxt, exchange_id)()
        self.data_manager = data_manager or HistoricalDataManager()

    def fetch_ohlcv(self,
                    symbol: str,
                    timeframe: str = '1d',
                    since: Optional[Union[datetime, int]] = None,
                    limit: int = 1000,
                    params: Dict[str, Any] = None,
                    save: bool = True) -> pd.DataFrame:
        """
        Fetch OHLCV data from the exchange.

        Args:
            symbol: The trading pair symbol
            timeframe: The timeframe for the data
            since: The start time for the data
            limit: The maximum number of candles to fetch
            params: Additional parameters for the exchange API
            save: Whether to save the data to disk

        Returns:
            DataFrame with OHLCV data
        """
        params = params or {}

        # Convert datetime to timestamp if needed
        if isinstance(since, datetime):
            since = int(since.timestamp() * 1000)

        try:
            # Fetch data from exchange
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit, params)

            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Save data if requested
            if save and self.data_manager:
                self.data_manager.save_ohlcv(symbol, timeframe, df)

            return df

        except Exception as e:
            logger.error(f"Error fetching OHLCV data: {e}")
            raise

    def load_or_fetch_ohlcv(self,
                           symbol: str,
                           timeframe: str = '1d',
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           force_fetch: bool = False) -> pd.DataFrame:
        """
        Load OHLCV data from disk or fetch from exchange if not available.

        Args:
            symbol: The trading pair symbol
            timeframe: The timeframe for the data
            start_date: The start date for the data
            end_date: The end date for the data
            force_fetch: Whether to force fetching from the exchange

        Returns:
            DataFrame with OHLCV data
        """
        try:
            if not force_fetch:
                # Try to load from disk first
                data = self.data_manager.load_ohlcv(symbol, timeframe, start_date, end_date)
                return data
        except FileNotFoundError:
            # Data not found on disk, will fetch from exchange
            pass

        # Calculate since parameter for exchange API
        since = None
        if start_date:
            since = start_date

        # Fetch data from exchange
        data = self.fetch_ohlcv(symbol, timeframe, since=since, save=True)

        # Apply date filters
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]

        return data


class CSVDataLoader:
    """Load historical data from CSV files."""

    def __init__(self, data_manager: Optional[HistoricalDataManager] = None):
        """
        Initialize the CSV data loader.

        Args:
            data_manager: Optional data manager for saving loaded data
        """
        self.data_manager = data_manager or HistoricalDataManager()

    def load_csv(self,
                file_path: Union[str, Path],
                symbol: str,
                timeframe: str,
                date_column: str = 'timestamp',
                date_format: Optional[str] = None,
                save: bool = True) -> pd.DataFrame:
        """
        Load OHLCV data from a CSV file.

        Args:
            file_path: Path to the CSV file
            symbol: The trading pair symbol to associate with the data
            timeframe: The timeframe to associate with the data
            date_column: The name of the date/timestamp column
            date_format: Optional date format string for parsing dates
            save: Whether to save the data to the data manager

        Returns:
            DataFrame with OHLCV data
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        # Load CSV file
        df = pd.read_csv(file_path)

        # Convert date column to datetime and set as index
        if date_format:
            df[date_column] = pd.to_datetime(df[date_column], format=date_format)
        else:
            df[date_column] = pd.to_datetime(df[date_column])

        df.set_index(date_column, inplace=True)

        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"CSV file missing required columns: {missing_columns}")

        # Save data if requested
        if save and self.data_manager:
            self.data_manager.save_ohlcv(symbol, timeframe, df)

        return df