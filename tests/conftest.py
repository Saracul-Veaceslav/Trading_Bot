"""
Global pytest configuration file.

This file configures pytest for all test sessions and provides common fixtures.
"""
import pytest
import warnings


def pytest_configure(config):
    """
    Configure pytest - specifically suppress specific deprecation warnings from dependencies.
    
    This function runs at the beginning of test session and configures warning filters
    to ignore specific deprecation warnings from third-party libraries that we cannot fix.
    """
    # Suppress websockets deprecation warnings from the Binance library
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="binance")
    
    # Log that warnings have been configured
    print("Configured warning filters to suppress third-party library deprecation warnings.") 