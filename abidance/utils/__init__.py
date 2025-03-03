"""
Utilities module for the Abidance trading bot.

This module provides utility functions used throughout the application.
"""

import datetime as dt

import pandas as pd



def format_timestamp(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Format a timestamp.

    Args:
        timestamp: Timestamp to format (can be int, float, or datetime)
        format_str: Format string

    Returns:
        Formatted timestamp string
    """
    if isinstance(timestamp, (int, float)):
        datetime_obj = dt.datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e10 else timestamp)
    elif isinstance(timestamp, dt.datetime):
        datetime_obj = timestamp
    else:
        raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")

    return datetime_obj.strftime(format_str)


def calculate_roi(entry_price, exit_price, position_type="long"):
    """
    Calculate return on investment.

    Args:
        entry_price: Entry price
        exit_price: Exit price
        position_type: Position type ("long" or "short")

    Returns:
        ROI as a percentage
    """
    if position_type.lower() == "long":
        return ((exit_price - entry_price) / entry_price) * 100
    if position_type.lower() == "short":
        return ((entry_price - exit_price) / entry_price) * 100
    
        raise ValueError(f"Unsupported position type: {position_type}")


def validate_dataframe(df, required_columns=None):
    """
    Validate a pandas DataFrame.

    Args:
        df: DataFrame to validate
        required_columns: List of required columns

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(df, pd.DataFrame):
        return False

    if required_columns is not None:
        return all(col in df.columns for col in required_columns)

    return True


# Define what's available when doing "from abidance.utils import *"
__all__ = [
    "format_timestamp",
    "calculate_roi",
    "validate_dataframe",
]
