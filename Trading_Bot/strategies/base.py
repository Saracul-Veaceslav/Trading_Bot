"""
Base Strategy Interface

This module defines the base class and interface for all trading strategies.
All strategy implementations should inherit from the Strategy abstract base class.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol, Type, Union
import pandas as pd
import numpy as np
from datetime import datetime

from trading_bot.utils.logger import get_strategy_logger


class StrategyProtocol(Protocol):
    """Protocol defining the interface for trading strategies."""
    
    def calculate_signal(self, data: pd.DataFrame) -> int:
        """
        Calculate trading signal from data.
        
        Args:
            data: DataFrame containing market data
            
        Returns:
            int: Signal value (1=buy, -1=sell, 0=hold)
        """
        ...
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters.
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        ...
    
    def set_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Set strategy parameters.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            bool: True if parameters were set successfully, False otherwise
        """
        ...


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All strategy implementations should inherit from this class and implement
    the required abstract methods.
    """
    
    # Signal constants
    BUY = 1
    SELL = -1
    HOLD = 0
    
    def __init__(self, name: str = "BaseStrategy", **kwargs):
        """
        Initialize the strategy.
        
        Args:
            name: Name of the strategy
            **kwargs: Additional keyword arguments
        """
        self.name = name
        self.logger = kwargs.get('trading_logger') or get_strategy_logger(name)
        self.error_logger = kwargs.get('error_logger') or self.logger
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
            message: The message to log
        """
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
        """
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
        """
        self.error_logger.error(message)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators needed for the strategy.
        Default implementation returns the data unchanged.
        
        Args:
            data: DataFrame containing market data
            
        Returns:
            DataFrame: Data with added indicators
        """
        return data
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        """
        Generate trading signal based on indicators.
        Default implementation returns HOLD (0).
        
        Args:
            data: DataFrame with indicators
            
        Returns:
            int: Signal value (1=buy, -1=sell, 0=hold)
        """
        return self.HOLD
    
    def calculate_signal(self, data: pd.DataFrame) -> int:
        """
        Calculate trading signal from data.
        
        Args:
            data: DataFrame containing market data
            
        Returns:
            int: Signal value (1=buy, -1=sell, 0=hold)
        """
        try:
            # Check if we have enough data
            if not self.validate_data(data):
                self.log_warning(f"Insufficient data for signal calculation. Required: {self.get_min_data_points()}, actual: {len(data)}.")
                return self.HOLD
                
            # Calculate indicators
            data_with_indicators = self.calculate_indicators(data)
            
            # Generate signal
            signal = self.generate_signal(data_with_indicators)
            
            return signal
        except Exception as e:
            self.log_error(f"Error calculating signal: {str(e)}")
            return self.HOLD
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters.
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        return self.parameters.copy()
    
    def set_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Set strategy parameters.
        Default implementation simply updates the parameters dictionary.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            bool: True if parameters were set successfully, False otherwise
        """
        try:
            self.parameters.update(parameters)
            return True
        except Exception as e:
            self.log_error(f"Error setting parameters: {str(e)}")
            return False
    
    def get_signal_meaning(self, signal_value: int) -> str:
        """
        Get the meaning of a signal value.
        
        Args:
            signal_value: Signal value (1=buy, -1=sell, 0=hold)
            
        Returns:
            str: Signal meaning
        """
        if signal_value == self.BUY:
            return 'buy'
        elif signal_value == self.SELL:
            return 'sell'
        elif signal_value == self.HOLD:
            return 'hold'
        else:
            return 'unknown'
    
    def calculate_signals_for_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate signals for each row in a DataFrame.
        
        Args:
            df: DataFrame containing market data
            
        Returns:
            DataFrame: Data with added 'signal' column
        """
        if len(df) == 0:
            self.log_warning("Empty DataFrame provided to calculate_signals_for_dataframe.")
            return df
            
        # Make a copy to avoid modifying the original
        result_df = df.copy()
        
        try:
            # Calculate indicators for the entire dataframe
            result_df = self.calculate_indicators(result_df)
            
            # Initialize the signal column
            result_df['signal'] = self.HOLD
            
            # Check if we have enough data for the minimum window
            min_points = self.get_min_data_points()
            
            if len(result_df) < min_points:
                self.log_warning(f"Insufficient data for signal calculation in calculate_signals_for_dataframe. Required: {min_points}, actual: {len(result_df)}.")
                return result_df
            
            # Calculate signals only from the point where we have enough data
            # This is a vectorized implementation for efficiency
            for i in range(min_points - 1, len(result_df)):
                # Get the window of data needed for this signal
                window = result_df.iloc[max(0, i - min_points + 1):i + 1]
                
                # Generate the signal for this window
                result_df.loc[result_df.index[i], 'signal'] = self.generate_signal(window)
            
            return result_df
        except Exception as e:
            self.log_error(f"Error calculating signals for dataframe: {str(e)}")
            return df
    
    def get_min_data_points(self) -> int:
        """
        Get the minimum number of data points required for this strategy.
        
        Returns:
            int: Minimum number of data points
        """
        return 1
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 10000.0) -> Dict[str, Any]:
        """
        Run a backtest of the strategy on historical data.
        
        Args:
            data: DataFrame containing market data
            initial_capital: Initial capital for the backtest
            
        Returns:
            Dict[str, Any]: Backtest results
        """
        # Default implementation with simple metrics
        try:
            # Calculate signals
            signals_df = self.calculate_signals_for_dataframe(data)
            
            # Initialize backtest variables
            capital = initial_capital
            position = 0  # 0=no position, 1=long position
            entry_price = 0.0
            trades = []
            
            # Run backtest
            for i in range(1, len(signals_df)):
                current_price = signals_df.iloc[i]['close']
                signal = signals_df.iloc[i]['signal']
                
                # Check for trade entry
                if signal == self.BUY and position == 0:
                    # Enter long position
                    entry_price = current_price
                    position = 1
                    trade = {
                        'type': 'buy',
                        'time': signals_df.index[i],
                        'price': entry_price,
                        'capital': capital
                    }
                    trades.append(trade)
                
                # Check for trade exit
                elif (signal == self.SELL or signal == self.HOLD) and position == 1:
                    # Exit long position
                    exit_price = current_price
                    pnl = (exit_price - entry_price) / entry_price
                    capital *= (1 + pnl)
                    position = 0
                    trade = {
                        'type': 'sell',
                        'time': signals_df.index[i],
                        'price': exit_price,
                        'pnl': pnl,
                        'capital': capital
                    }
                    trades.append(trade)
            
            # Close any open positions at the end
            if position == 1:
                exit_price = signals_df.iloc[-1]['close']
                pnl = (exit_price - entry_price) / entry_price
                capital *= (1 + pnl)
                trade = {
                    'type': 'sell',
                    'time': signals_df.index[-1],
                    'price': exit_price,
                    'pnl': pnl,
                    'capital': capital
                }
                trades.append(trade)
            
            # Calculate backtest metrics
            returns = capital / initial_capital - 1
            
            return {
                'initial_capital': initial_capital,
                'final_capital': capital,
                'returns': returns,
                'trades': trades,
                'signals': signals_df
            }
            
        except Exception as e:
            self.log_error(f"Error during backtest: {str(e)}")
            return {
                'error': str(e),
                'initial_capital': initial_capital,
                'final_capital': initial_capital,
                'returns': 0.0,
                'trades': [],
                'signals': data
            }
    
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
            metadata: Dictionary of metadata values
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
        Validate data for use with this strategy.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        if len(data) < self.get_min_data_points():
            return False
            
        for col in required_columns:
            if col not in data.columns:
                return False
                
        return True 