"""
Data buffer module for online learning.

This module provides a buffer for storing and managing data used in online learning,
with fixed-size FIFO (First-In-First-Out) behavior.
"""
from typing import Dict, Any, List
import pandas as pd


class DataBuffer:
    """
    Buffer for storing and managing data for online learning.

    This class provides a fixed-size buffer with FIFO behavior for storing
    market data records. It supports adding data in batches or individual records,
    and converting the buffer contents to a pandas DataFrame for analysis.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize the data buffer.

        Args:
            max_size: Maximum number of records to store in the buffer
        """
        self.max_size = max_size
        self.data: List[Dict[str, Any]] = []

    def add(self, data: pd.DataFrame) -> None:
        """
        Add multiple records to the buffer.

        Args:
            data: DataFrame containing records to add
        """
        # Convert DataFrame to list of dictionaries
        records = data.to_dict('records')

        # Add records to buffer
        self.data.extend(records)

        # Remove oldest records if buffer is full
        if len(self.data) > self.max_size:
            self.data = self.data[-self.max_size:]

    def add_record(self, record: Dict[str, Any]) -> None:
        """
        Add a single record to the buffer.

        Args:
            record: Dictionary containing a single data record
        """
        # Add record to buffer
        self.data.append(record)

        # Remove oldest records if buffer is full
        if len(self.data) > self.max_size:
            self.data = self.data[-self.max_size:]

    def clear(self) -> None:
        """Clear all data from the buffer."""
        self.data = []

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert buffer contents to a pandas DataFrame.

        Returns:
            DataFrame containing all records in the buffer
        """
        return pd.DataFrame(self.data) if self.data else pd.DataFrame()

    def is_full(self) -> bool:
        """
        Check if the buffer is at maximum capacity.

        Returns:
            True if buffer is full, False otherwise
        """
        return len(self.data) >= self.max_size

    def get_recent(self, n: int) -> pd.DataFrame:
        """
        Get the most recent n records from the buffer.

        Args:
            n: Number of recent records to retrieve

        Returns:
            DataFrame containing the n most recent records
        """
        # Ensure n is not larger than buffer size
        n = min(n, len(self.data))

        # Get the most recent n records
        recent_data = self.data[-n:] if n > 0 else []

        return pd.DataFrame(recent_data) if recent_data else pd.DataFrame()

    def __len__(self) -> int:
        """
        Get the number of records in the buffer.

        Returns:
            Number of records in the buffer
        """
        return len(self.data)
