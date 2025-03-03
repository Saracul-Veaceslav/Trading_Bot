"""
Base indicator module defining the abstract Indicator interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import pandas as pd


class Indicator(ABC):
    """
    Abstract base class for technical indicators.
    
    All indicator implementations must inherit from this class and implement
    its abstract methods to provide a consistent interface.
    """
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """
        Calculate the indicator values.
        
        Args:
            data: OHLCV data as a pandas DataFrame
            
        Returns:
            Series or DataFrame with indicator values
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of the indicator.
        
        Returns:
            String representation of the indicator name with parameters
        """
        pass
    
    def __str__(self) -> str:
        """String representation of the indicator."""
        return self.name 