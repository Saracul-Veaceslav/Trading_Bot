from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.dataset as ds
import os

logger = logging.getLogger(__name__)

class PylonStorage:
    """
    Efficient data storage system using Apache Arrow and Parquet.

    Pylon provides optimized storage for time series data with:
    - Columnar storage for efficient queries
    - Compression for reduced storage size
    - Partitioning for faster data access
    - Schema enforcement for data consistency
    - Memory-mapped files for faster reads
    """

    def __init__(self, base_path: str = 'data/pylon'):
        """
        Initialize the Pylon storage system.

        Args:
            base_path: Base directory for storing data
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def store_dataframe(self, df, symbol, timeframe, partition_cols=None):
        """
        Store a DataFrame in Pylon format.

        Args:
            df (pd.DataFrame): DataFrame to store
            symbol (str): The trading symbol
            timeframe (str): The timeframe of the data
            partition_cols (list, optional): List of columns to partition by. Defaults to ['year', 'month'].
        """
        try:
            # Make a copy to avoid modifying the original
            df = df.copy()

            # Ensure DataFrame has timestamp column
            if isinstance(df.index, pd.DatetimeIndex):
                # Reset index to get timestamp as column
                df = df.reset_index()
            elif 'timestamp' not in df.columns:
                raise ValueError("DataFrame must have a timestamp column or DatetimeIndex")

            # Ensure timestamp is datetime
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Add year and month columns for partitioning if not provided
            if partition_cols is None:
                if 'year' not in df.columns:
                    df['year'] = df['timestamp'].dt.year
                if 'month' not in df.columns:
                    df['month'] = df['timestamp'].dt.month
                partition_cols = ['year', 'month']

            # Create directory for this symbol and timeframe
            safe_symbol = symbol.replace('/', '_')
            dataset_path = self.base_path / safe_symbol / timeframe
            os.makedirs(dataset_path, exist_ok=True)

            # Write to parquet with partitioning
            pq.write_to_dataset(
                pa.Table.from_pandas(df),
                root_path=str(dataset_path),
                partition_cols=partition_cols,
                compression='snappy'
            )

            logger.info(f"Successfully stored {len(df)} rows for {symbol} {timeframe}")
        except Exception as e:
            logger.error(f"Error storing data: {e}")
            raise

    def load_dataframe(self, symbol, timeframe, start_date=None, end_date=None, columns=None):
        """
        Load a DataFrame from Pylon storage.

        Args:
            symbol (str): The trading symbol
            timeframe (str): The timeframe of the data
            start_date (str, optional): Start date for filtering
            end_date (str, optional): End date for filtering
            columns (list, optional): List of columns to load

        Returns:
            pd.DataFrame: The loaded DataFrame
        """
        try:
            # Build filters for date range if provided
            filters = []
            if start_date:
                filters.append(('timestamp', '>=', pd.Timestamp(start_date)))
            if end_date:
                filters.append(('timestamp', '<=', pd.Timestamp(end_date)))

            # Create dataset path
            safe_symbol = symbol.replace('/', '_')
            dataset_path = self.base_path / safe_symbol / timeframe

            # Check if dataset exists
            if not dataset_path.exists():
                raise FileNotFoundError(f"Dataset not found for {symbol} {timeframe}")

            # Read the dataset with filters and column projection
            table = pq.read_table(
                str(dataset_path),
                filters=filters if filters else None,
                columns=columns
            )

            # Convert to DataFrame
            df = table.to_pandas()

            # Set timestamp as index
            if 'timestamp' in df.columns:
                df = df.set_index('timestamp')

            # Sort by index to ensure chronological order
            df = df.sort_index()

            # Remove partitioning columns if they exist
            if 'year' in df.columns:
                df = df.drop(columns=['year'])
            if 'month' in df.columns:
                df = df.drop(columns=['month'])

            # Try to infer and set frequency only if it's compatible
            try:
                # Map timeframe to pandas frequency
                timeframe_to_freq = {
                    '1m': 'T', '5m': '5T', '15m': '15T', '30m': '30T',
                    '1h': 'h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h',
                    '1d': 'D', '3d': '3D', '1w': 'W', '1M': 'M'
                }

                freq = timeframe_to_freq.get(timeframe)
                if freq:
                    # Check if the data conforms to the frequency before setting it
                    inferred_freq = pd.infer_freq(df.index)

                    # Only set the frequency if it's compatible or if there's no inferred frequency
                    if inferred_freq is None or inferred_freq == freq:
                        df.index.freq = pd.tseries.frequencies.to_offset(freq)
            except Exception as e:
                logger.warning(f"Could not set frequency for {symbol} {timeframe}: {e}")

            return df
        except Exception as e:
            logger.error(f"Error loading data from Pylon: {e}")
            raise

    def append_dataframe(self, df, symbol, timeframe):
        """
        Append data to an existing dataset.

        Args:
            df (pd.DataFrame): DataFrame to append
            symbol (str): The trading symbol
            timeframe (str): The timeframe of the data
        """
        try:
            # Make a copy to avoid modifying the original
            df = df.copy()

            # Ensure DataFrame has timestamp column
            if isinstance(df.index, pd.DatetimeIndex):
                # Reset index to get timestamp as column
                df = df.reset_index()
            elif 'timestamp' not in df.columns:
                raise ValueError("DataFrame must have a timestamp column or DatetimeIndex")

            # Check if dataset exists
            safe_symbol = symbol.replace('/', '_')
            dataset_path = self.base_path / safe_symbol / timeframe

            if not dataset_path.exists():
                # If dataset doesn't exist, just store the dataframe
                self.store_dataframe(df, symbol, timeframe)
                return

            try:
                # Load existing data
                existing_df = None
                try:
                    # Try to load without setting frequency to avoid errors
                    table = pq.read_table(str(dataset_path))
                    existing_df = table.to_pandas()
                except Exception as e:
                    logger.error(f"Error loading existing data for append: {e}")
                    # If we can't load existing data, just store the new data
                    self.store_dataframe(df, symbol, timeframe)
                    return

                # Ensure both DataFrames have timestamp as column
                if isinstance(existing_df.index, pd.DatetimeIndex) and 'timestamp' not in existing_df.columns:
                    existing_df = existing_df.reset_index()

                # Combine DataFrames
                combined_df = pd.concat([existing_df, df], ignore_index=True)

                # Remove duplicates based on timestamp
                combined_df = combined_df.drop_duplicates(subset=['timestamp'], keep='last')

                # Sort by timestamp
                combined_df = combined_df.sort_values('timestamp')

                # Add year and month columns for partitioning
                combined_df['year'] = combined_df['timestamp'].dt.year
                combined_df['month'] = combined_df['timestamp'].dt.month

                # Create directory if it doesn't exist
                os.makedirs(dataset_path, exist_ok=True)

                # Write to parquet with partitioning
                pq.write_to_dataset(
                    pa.Table.from_pandas(combined_df),
                    root_path=str(dataset_path),
                    partition_cols=['year', 'month'],
                    existing_data_behavior='delete_matching',
                    compression='snappy'
                )

                logger.info(f"Successfully appended data for {symbol} {timeframe}")
            except Exception as e:
                logger.error(f"Error appending data: {e}")
                raise
        except Exception as e:
            logger.error(f"Error in append_dataframe: {e}")
            raise

    def list_available_symbols(self) -> List[str]:
        """
        List all available symbols in the Pylon storage.

        Returns:
            List of symbol names
        """
        symbols = []
        for path in self.base_path.iterdir():
            if path.is_dir():
                symbols.append(path.name.replace('_', '/'))
        return symbols

    def list_available_timeframes(self, symbol: str) -> List[str]:
        """
        List all available timeframes for a symbol.

        Args:
            symbol: Trading pair symbol

        Returns:
            List of timeframe names
        """
        safe_symbol = symbol.replace('/', '_')
        symbol_path = self.base_path / safe_symbol

        if not symbol_path.exists():
            return []

        timeframes = []
        for path in symbol_path.iterdir():
            if path.is_dir():
                timeframes.append(path.name)
        return timeframes

    def get_dataset_info(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Get information about a dataset.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe of the data

        Returns:
            Dictionary with dataset information
        """
        safe_symbol = symbol.replace('/', '_')
        dataset_path = self.base_path / safe_symbol / timeframe

        if not dataset_path.exists():
            raise FileNotFoundError(f"No data found for {symbol} {timeframe}")

        # Create dataset
        dataset = ds.dataset(str(dataset_path), format='parquet')

        # Get schema
        schema = dataset.schema

        # Get row count
        table = dataset.to_table()
        row_count = len(table)

        # Get date range
        df = table.to_pandas()
        if 'timestamp' in df.columns:
            min_date = df['timestamp'].min()
            max_date = df['timestamp'].max()
        else:
            min_date = None
            max_date = None

        # Get file size
        total_size = 0
        for root, dirs, files in os.walk(str(dataset_path)):
            for file in files:
                if file.endswith('.parquet'):
                    total_size += os.path.getsize(os.path.join(root, file))

        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'row_count': row_count,
            'min_date': min_date,
            'max_date': max_date,
            'schema': str(schema),
            'size_bytes': total_size,
            'size_mb': total_size / (1024 * 1024)
        }

    def delete_dataset(self, symbol: str, timeframe: str) -> bool:
        """
        Delete a dataset.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe of the data

        Returns:
            True if successful, False otherwise
        """
        import shutil

        safe_symbol = symbol.replace('/', '_')
        dataset_path = self.base_path / safe_symbol / timeframe

        if not dataset_path.exists():
            return False

        try:
            shutil.rmtree(dataset_path)

            # Remove symbol directory if empty
            symbol_path = self.base_path / safe_symbol
            if symbol_path.exists() and not any(symbol_path.iterdir()):
                symbol_path.rmdir()

            return True

        except Exception as e:
            logger.error(f"Error deleting dataset: {e}")
            return False