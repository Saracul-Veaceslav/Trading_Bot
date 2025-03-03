"""
Data preprocessing module for machine learning pipelines.

This module provides functionality for cleaning, transforming, and preparing
data for machine learning models.
"""
from typing import List, Optional, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class DataPreprocessor:
    """
    Data preprocessing pipeline for financial time series data.
    
    This class provides methods for handling missing values, removing outliers,
    and normalizing data for machine learning models.
    """
    
    def __init__(self):
        """Initialize the data preprocessor."""
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
    
    def handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the data.
        
        Args:
            data: Input DataFrame with potentially missing values
            
        Returns:
            DataFrame with missing values filled
        """
        # First try forward fill (use previous values)
        filled_data = data.ffill()
        
        # Then try backward fill for any remaining NaNs
        filled_data = filled_data.bfill()
        
        # If there are still NaNs (e.g., at the beginning or end), fill with column mean
        if filled_data.isnull().any().any():
            column_means = filled_data.mean()
            filled_data = filled_data.fillna(column_means)
        
        return filled_data
    
    def remove_outliers(self, data: pd.DataFrame, columns: Optional[List[str]] = None,
                       threshold: float = 3.0) -> pd.DataFrame:
        """
        Remove or replace outliers in the data.
        
        Args:
            data: Input DataFrame
            columns: List of columns to check for outliers (if None, check all numeric columns)
            threshold: Z-score threshold for outlier detection (default: 3.0)
            
        Returns:
            DataFrame with outliers handled
        """
        if columns is None:
            # Only consider numeric columns
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        result = data.copy()
        
        for column in columns:
            if column not in data.columns:
                continue
                
            # Calculate z-scores
            mean = data[column].mean()
            std = data[column].std()
            
            if std == 0 or np.isnan(std):  # Skip if standard deviation is zero or NaN
                continue
                
            z_scores = (data[column] - mean) / std
            
            # Identify outliers
            outliers = abs(z_scores) > threshold
            
            if outliers.any():
                # For extreme outliers (z-score > 10), replace with the mean
                extreme_outliers = abs(z_scores) > 10
                if extreme_outliers.any():
                    # Cast to the appropriate dtype before assignment
                    result.loc[extreme_outliers, column] = mean.astype(data[column].dtype)
                
                # For moderate outliers, cap at threshold * std
                moderate_outliers = outliers & ~extreme_outliers
                if moderate_outliers.any():
                    # Cast to the appropriate dtype before assignment
                    upper_bound = (mean + threshold * std).astype(data[column].dtype)
                    lower_bound = (mean - threshold * std).astype(data[column].dtype)
                    
                    result.loc[moderate_outliers & (data[column] > mean), column] = upper_bound
                    result.loc[moderate_outliers & (data[column] < mean), column] = lower_bound
                    
                # Ensure integer columns remain integers
                if pd.api.types.is_integer_dtype(data[column]):
                    result[column] = result[column].astype(int)
        
        return result
    
    def normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data using MinMaxScaler to range [-1, 1].
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with normalized values
        """
        # Fit the scaler on the data
        scaled_values = self.scaler.fit_transform(data)
        
        # Create a new DataFrame with the scaled values
        normalized_data = pd.DataFrame(
            scaled_values,
            index=data.index,
            columns=data.columns
        )
        
        return normalized_data
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the full preprocessing pipeline.
        
        Args:
            data: Input DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        # Handle missing values
        clean_data = self.handle_missing_values(data)
        
        # Remove outliers
        clean_data = self.remove_outliers(clean_data)
        
        # Normalize data
        normalized_data = self.normalize_data(clean_data)
        
        return normalized_data 