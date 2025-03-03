"""
Base classes for feature generation.

This module provides abstract base classes for feature generators used in machine learning models.
"""
from abc import ABC, abstractmethod
from typing import List

import pandas as pd


class FeatureGenerator(ABC):
    """
    Base class for feature generators.

    This abstract class defines the interface for all feature generators.
    Subclasses must implement the generate and feature_names methods.
    """

    @abstractmethod
    def generate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate features from input data.

        Args:
            data: Input DataFrame containing raw data (e.g., OHLCV data)

        Returns:
            DataFrame containing generated features
        """

    @property
    @abstractmethod
    def feature_names(self) -> List[str]:
        """
        Get list of generated feature names.

        Returns:
            List of feature names that this generator produces
        """
