"""
Unit tests for the DataBuffer class.

This module contains tests for the data buffer used in online learning,
including data storage, retrieval, and management.
"""
import unittest
import numpy as np
import pandas as pd
from abidance.ml.online.buffer import DataBuffer


class TestDataBuffer(unittest.TestCase):
    """Test cases for the DataBuffer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample data
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [102, 103, 104, 105, 106],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # Create the DataBuffer instance
        self.buffer = DataBuffer(max_size=10)

    def test_init(self):
        """Test initialization of DataBuffer."""
        self.assertEqual(self.buffer.max_size, 10)
        self.assertEqual(len(self.buffer), 0)
        self.assertIsInstance(self.buffer.data, list)

    def test_add_data(self):
        """Test adding data to the buffer."""
        # Add sample data
        self.buffer.add(self.sample_data)
        
        # Check that data was added
        self.assertEqual(len(self.buffer), 5)
        
        # Add more data
        self.buffer.add(self.sample_data)
        
        # Check that all data was added
        self.assertEqual(len(self.buffer), 10)
        
        # Add more data that would exceed the buffer size
        more_data = pd.DataFrame({
            'open': [110, 111, 112, 113, 114],
            'high': [115, 116, 117, 118, 119],
            'low': [105, 106, 107, 108, 109],
            'close': [112, 113, 114, 115, 116],
            'volume': [2000, 2100, 2200, 2300, 2400]
        })
        self.buffer.add(more_data)
        
        # Check that buffer size is maintained
        self.assertEqual(len(self.buffer), 10)
        
        # Check that the oldest data was removed (FIFO)
        buffer_data = self.buffer.to_dataframe()
        # The first 5 records should be the last 5 from sample_data (second batch)
        self.assertEqual(buffer_data.iloc[0]['open'], 100)  # First row of second batch
        self.assertEqual(buffer_data.iloc[4]['open'], 104)  # Last row of second batch
        # The last 5 records should be from more_data
        self.assertEqual(buffer_data.iloc[5]['open'], 110)  # First row of more_data
        self.assertEqual(buffer_data.iloc[9]['open'], 114)  # Last row of more_data

    def test_add_single_record(self):
        """Test adding a single record to the buffer."""
        # Add a single record
        record = {'open': 100, 'high': 105, 'low': 95, 'close': 102, 'volume': 1000}
        self.buffer.add_record(record)
        
        # Check that record was added
        self.assertEqual(len(self.buffer), 1)
        
        # Check record values
        buffer_data = self.buffer.to_dataframe()
        self.assertEqual(buffer_data.iloc[0]['open'], 100)
        self.assertEqual(buffer_data.iloc[0]['close'], 102)

    def test_clear(self):
        """Test clearing the buffer."""
        # Add data
        self.buffer.add(self.sample_data)
        self.assertEqual(len(self.buffer), 5)
        
        # Clear buffer
        self.buffer.clear()
        
        # Check that buffer is empty
        self.assertEqual(len(self.buffer), 0)

    def test_to_dataframe(self):
        """Test converting buffer to DataFrame."""
        # Add data
        self.buffer.add(self.sample_data)
        
        # Convert to DataFrame
        df = self.buffer.to_dataframe()
        
        # Check that DataFrame has correct shape and values
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (5, 5))
        self.assertEqual(df.iloc[0]['open'], 100)
        self.assertEqual(df.iloc[-1]['close'], 106)

    def test_is_full(self):
        """Test checking if buffer is full."""
        # Empty buffer
        self.assertFalse(self.buffer.is_full())
        
        # Add data but not fill
        self.buffer.add(self.sample_data)
        self.assertFalse(self.buffer.is_full())
        
        # Fill buffer
        self.buffer.add(self.sample_data)
        self.assertTrue(self.buffer.is_full())

    def test_get_recent(self):
        """Test getting recent data from buffer."""
        # Add data
        self.buffer.add(self.sample_data)
        
        # Get recent data (3 records)
        recent = self.buffer.get_recent(3)
        
        # Check recent data
        self.assertIsInstance(recent, pd.DataFrame)
        self.assertEqual(recent.shape, (3, 5))
        self.assertEqual(recent.iloc[0]['open'], 102)  # Third row of sample data
        self.assertEqual(recent.iloc[-1]['close'], 106)  # Last row of sample data


if __name__ == '__main__':
    unittest.main()

# Feature: Data Buffer for Online Learning
# 
#   Scenario: Buffer maintains fixed size with FIFO behavior
#     Given a data buffer with maximum size of 10 records
#     When more than 10 records are added to the buffer
#     Then the buffer should maintain exactly 10 records
#     And the oldest records should be removed first 