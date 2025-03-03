"""
Base indicator module for trading strategies.

This module provides the base class for all technical indicators
used in trading strategies.
"""
from abc import ABC, abstractmethod

import pandas as pd


class Indicator(ABC):
    """
    Abstract base class for technical indicators.

    All indicator implementations should inherit from this class
    and implement the required methods.
    """

    @abstractmethod
    def calculate(self, data: pd.DataFrame):
        """
        Calculate the indicator values.

        Args:
            data: OHLCV data as a pandas DataFrame

        Returns:
            Indicator values (Series or DataFrame depending on the indicator)
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of the indicator.

        Returns:
            String representation of the indicator name
        """

    def __str__(self) -> str:
        """String representation of the indicator."""
        return self.name
