"""
Base Strategy Interface

This module defines the base class and interface for all trading strategies.
All strategy implementations should inherit from the Strategy abstract base class.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All strategy implementations should inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, name: str = "BaseStrategy"):
        """
        Initialize the strategy.
        
        Args:
            name: Name of the strategy
        """
        self.name = name
        self.logger = logging.getLogger(f'trading_bot.strategies.{name.lower().replace(" ", "_")}')
        self.error_logger = self.logger  # Default to same logger
        self.parameters = {}
        self.metadata = {
            'name': name,
            'description': 'Base strategy class',
            'version': '1.0.0',
            'author': 'Trading Bot',
            'created_at': datetime.now().isoformat(),
        }
    
    def set_loggers(self, trading_logger=None, error_logger=None):
        """
        Set the loggers for the strategy.
        
        Args:
            trading_logger: Logger for trading activity
            error_logger: Logger for errors
        """
        if trading_logger:
            self.logger = trading_logger
        if error_logger:
            self.error_logger = error_logger
            
    def log_info(self, message: str) -> None:
        """
        Log an informational message.
        
        Args:
            message: Message to log
        """
        self.logger.info(f"[{self.name}] {message}")
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: Message to log
        """
        self.logger.warning(f"[{self.name}] {message}")
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: Message to log
        """
        self.error_logger.error(f"[{self.name}] {message}")
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate strategy indicators on the input data.
        
        Args:
            data: DataFrame with market data
            
        Returns:
            DataFrame with added indicators
        """
        pass
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> int:
        """
        Generate trading signal from the input data.
        
        Args:
            data: DataFrame with market data and indicators
            
        Returns:
            int: Trading signal (1 for buy, -1 for sell, 0 for hold)
        """
        pass
    
    def calculate_signal(self, data: pd.DataFrame) -> int:
        """
        Calculate trading signal (alias for generate_signal).
        This method is preserved for backward compatibility.
        
        Args:
            data: DataFrame with market data
            
        Returns:
            int: Trading signal (1 for buy, -1 for sell, 0 for hold)
        """
        return self.generate_signal(data)
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters.
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        return self.parameters.copy()
    
    @abstractmethod
    def set_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Set strategy parameters.
        
        Args:
            parameters: Strategy parameters
            
        Returns:
            bool: True if parameters were set successfully, False otherwise
        """
        pass
    
    def get_signal_meaning(self, signal_value: int) -> str:
        """
        Get the meaning of a signal value.
        
        Args:
            signal_value: Signal value (1, -1, 0)
            
        Returns:
            str: Signal meaning ('buy', 'sell', 'hold')
        """
        if signal_value == 1:
            return 'buy'
        elif signal_value == -1:
            return 'sell'
        else:
            return 'hold'
    
    def calculate_signals_for_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate signals for an entire DataFrame.
        
        Args:
            df: DataFrame with market data
            
        Returns:
            DataFrame with signals column added
        """
        if df is None or df.empty:
            self.log_warning("Empty DataFrame provided for signal calculation")
            return None
        
        try:
            # Calculate indicators
            result_df = self.calculate_indicators(df.copy())
            
            if result_df is None:
                return None
            
            # Initialize signal column
            result_df['signal'] = 0  # hold
            
            # Calculate signals row by row
            for i in range(len(result_df)):
                # Use rolling window of data up to this point for signal generation
                window = result_df.iloc[:i+1]
                
                # Only generate signals after we have enough data
                if i >= self.get_min_data_points():
                    try:
                        # Generate signal for this data point
                        signal = self.generate_signal(window)
                        result_df.loc[result_df.index[i], 'signal'] = signal
                    except Exception as e:
                        self.log_error(f"Error generating signal at row {i}: {e}")
            
            return result_df
            
        except Exception as e:
            self.log_error(f"Error calculating signals for DataFrame: {e}")
            return None
    
    def get_min_data_points(self) -> int:
        """
        Get the minimum number of data points required for the strategy.
        Override this method in subclasses to specify the minimum number.
        
        Returns:
            int: Minimum number of data points
        """
        return 1  # Base implementation requires at least one data point
    
    @abstractmethod
    def backtest(self, data: pd.DataFrame, initial_capital: float = 10000.0) -> Dict[str, Any]:
        """
        Run strategy backtest on historical data.
        
        Args:
            data: DataFrame with historical market data
            initial_capital: Initial capital for the backtest
            
        Returns:
            Dict[str, Any]: Backtest results including returns, drawdown, etc.
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get strategy metadata.
        
        Returns:
            Dict[str, Any]: Strategy metadata
        """
        return self.metadata.copy()
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Set strategy metadata.
        
        Args:
            metadata: Strategy metadata
        """
        self.metadata.update(metadata)
    
    def get_name(self) -> str:
        """
        Get strategy name.
        
        Returns:
            str: Strategy name
        """
        return self.name
    
    def set_name(self, name: str) -> None:
        """
        Set strategy name.
        
        Args:
            name: Strategy name
        """
        self.name = name
        self.metadata['name'] = name
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that the input data has the required columns.
        
        Args:
            data: DataFrame with market data
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        if data is None or data.empty:
            self.log_warning("Empty DataFrame provided for validation")
            return False
        
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        # Check if all required columns are present
        for column in required_columns:
            if column not in data.columns:
                self.log_warning(f"Missing required column: {column}")
                return False
        
        return True 