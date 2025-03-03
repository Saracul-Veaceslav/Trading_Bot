"""
SMA Crossover Strategy

This module implements a Simple Moving Average (SMA) crossover strategy.
Buy signals are generated when the short SMA crosses above the long SMA.
Sell signals are generated when the short SMA crosses below the long SMA.
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union

from trading_bot.strategies.base import Strategy
from trading_bot.strategies.exceptions import (
    StrategyParameterError,
    InsufficientDataError,
    IndicatorCalculationError, 
    SignalGenerationError
)

logger = logging.getLogger('trading_bot.strategies.sma_crossover')

class SMAcrossover(Strategy):
    """
    Simple Moving Average (SMA) crossover trading strategy.
    """
    
    def __init__(self, short_window: int = 10, long_window: int = 50, **kwargs):
        """
        Initialize the SMA crossover strategy.
        
        Args:
            short_window: Period for the short SMA
            long_window: Period for the long SMA
            **kwargs: Additional arguments for the base Strategy class
        """
        # Call the parent constructor with strategy name
        super().__init__(name="SMA Crossover", **kwargs)
        
        # Store strategy parameters
        self.short_window = short_window
        self.long_window = long_window
        
        # Validate parameters
        if self.short_window >= self.long_window:
            raise StrategyParameterError(
                f"Short window ({short_window}) must be less than long window ({long_window})"
            )
        
        # Set required data length for this strategy
        self.min_required_candles = self.long_window + 1
        
        # Set loggers if provided in kwargs (for test compatibility)
        if 'trading_logger' in kwargs:
            self.logger = kwargs['trading_logger']
        if 'error_logger' in kwargs:
            self.error_logger = kwargs['error_logger']
        
        logger.info(f"Initialized SMA Crossover strategy with short_window={short_window}, long_window={long_window}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the strategy.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        try:
            # Create a copy of the dataframe to avoid SettingWithCopyWarning
            result_df = df.copy()
            
            # Check if we have enough data
            if len(result_df) < self.min_required_candles:
                self.log_warning(f"Not enough data for SMA calculation. Need {self.min_required_candles} candles, got {len(result_df)}")
                return result_df
            
            # Calculate short and long SMAs
            result_df['short_sma'] = result_df['close'].rolling(window=self.short_window).mean()
            result_df['long_sma'] = result_df['close'].rolling(window=self.long_window).mean()
            
            # Calculate the difference between SMAs
            result_df['sma_diff'] = result_df['short_sma'] - result_df['long_sma']
            
            return result_df
        except Exception as e:
            self.log_error(f"Error calculating indicators: {e}")
            raise IndicatorCalculationError(f"Failed to calculate SMA indicators: {e}")
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generate a trading signal based on SMA crossover.
        
        Args:
            df: DataFrame with OHLCV data and indicators
            
        Returns:
            int: 1 for buy, -1 for sell, 0 for hold
        """
        try:
            # Check if DataFrame is empty
            if df.empty:
                self.log_warning("Empty DataFrame provided to generate_signal")
                return 0
            
            # Check if we have enough data points
            if len(df) < self.min_required_candles:
                self.log_warning(f"Not enough data for signal generation. Need {self.min_required_candles} candles, got {len(df)}")
                return 0
            
            # Make sure indicators are calculated
            if 'short_sma' not in df.columns or 'long_sma' not in df.columns:
                self.log_warning("Indicators not found in DataFrame, calculating now")
                df = self.calculate_indicators(df)
                # Check again after calculating
                if 'short_sma' not in df.columns or 'long_sma' not in df.columns:
                    self.log_warning("Could not calculate required indicators")
                    return 0
            
            # Get the last two rows to check for a crossover
            if len(df) < 2:
                self.log_warning("Need at least 2 rows to check for crossover")
                return 0
            
            # Extract the last two rows for easier access
            prev_row = df.iloc[-2]
            curr_row = df.iloc[-1]
            
            # Check for NaN values in the indicators
            if pd.isna(prev_row['short_sma']) or pd.isna(prev_row['long_sma']) or \
               pd.isna(curr_row['short_sma']) or pd.isna(curr_row['long_sma']):
                self.log_warning("NaN values found in SMA calculations")
                return 0
            
            # Check for buy signal: short SMA crosses above long SMA
            if prev_row['short_sma'] <= prev_row['long_sma'] and curr_row['short_sma'] > curr_row['long_sma']:
                self.log_info("BUY signal generated: short SMA crossed above long SMA")
                return 1
            
            # Check for sell signal: short SMA crosses below long SMA
            elif prev_row['short_sma'] >= prev_row['long_sma'] and curr_row['short_sma'] < curr_row['long_sma']:
                self.log_info("SELL signal generated: short SMA crossed below long SMA")
                return -1
            
            # No crossover, return hold signal
            else:
                return 0
                
        except Exception as e:
            self.log_error(f"Error generating signal: {e}")
            # Return hold signal (0) in case of error
            return 0
    
    def calculate_signal(self, df: pd.DataFrame) -> int:
        """
        Alias for generate_signal to maintain compatibility with older code.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Signal (1 for buy, -1 for sell, 0 for hold/None)
        """
        return self.generate_signal(df)
    
    def calculate_signals_for_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate signals for the entire DataFrame, useful for backtesting.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added signal column
        """
        # Make a copy to avoid modifying original data
        df = df.copy()
        
        # Calculate indicators first
        df = self.calculate_indicators(df)
        
        # For test compatibility, add aliases for column names
        if 'short_sma' in df.columns:
            df['sma_short'] = df['short_sma']
        if 'long_sma' in df.columns:
            df['sma_long'] = df['long_sma']
        
        # Initialize signal column
        df['signal'] = np.nan
        
        # We need at least two rows with both SMAs calculated (non-NaN)
        if len(df) < self.long_window + 2:
            self.logger.warning(f"Not enough data for calculating signals. Need at least {self.long_window + 2} rows.")
            return df
        
        try:
            # Start from the first row where both SMAs are available
            start_idx = self.long_window + 1
            
            # Process each row where we have the previous row available
            for i in range(start_idx, len(df)):
                current = df.iloc[i]
                previous = df.iloc[i-1]
                
                # Buy when short SMA crosses above long SMA
                if previous['short_sma'] <= previous['long_sma'] and current['short_sma'] > current['long_sma']:
                    df.loc[df.index[i], 'signal'] = 1  # 1 for buy
                
                # Sell when short SMA crosses below long SMA
                elif previous['short_sma'] >= previous['long_sma'] and current['short_sma'] < current['long_sma']:
                    df.loc[df.index[i], 'signal'] = -1  # -1 for sell
                    
            self.log_info(f"Calculated signals for entire dataframe of length {len(df)}")
            
        except Exception as e:
            self.log_error(f"Error calculating signals for dataframe: {str(e)}")
            if hasattr(self.error_logger, 'exception'):
                self.error_logger.exception("Exception during dataframe signal calculation")
        
        return df
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 10000.0) -> Dict[str, Any]:
        """
        Perform backtesting of the strategy on historical data.
        
        Args:
            data: DataFrame with OHLCV data
            initial_capital: Initial capital for backtesting
            
        Returns:
            Dictionary with backtesting results
        """
        # Make a copy to avoid modifying original data
        df = data.copy()
        
        # Calculate signals
        df = self.calculate_signals_for_dataframe(df)
        
        # Initialize portfolio and holdings
        portfolio = pd.DataFrame(index=df.index)
        portfolio['holdings'] = 0.0
        portfolio['cash'] = initial_capital
        portfolio['total'] = initial_capital
        portfolio['returns'] = 0.0
        
        # Track positions
        position = 0
        entry_price = 0.0
        
        # Process each signal
        for i in range(len(df)):
            if pd.isna(df.iloc[i]['signal']):
                # No signal, portfolio remains the same
                portfolio.iloc[i] = portfolio.iloc[i-1] if i > 0 else portfolio.iloc[i]
                continue
                
            signal = df.iloc[i]['signal']
            price = df.iloc[i]['close']
            
            if signal == 1 and position == 0:  # Buy signal and no position
                # Calculate position size (simplified, using all available cash)
                shares = portfolio.iloc[i-1]['cash'] / price if i > 0 else initial_capital / price
                position = shares
                entry_price = price
                
                # Update portfolio
                portfolio.loc[df.index[i], 'holdings'] = position * price
                portfolio.loc[df.index[i], 'cash'] = portfolio.iloc[i-1]['cash'] - position * price if i > 0 else initial_capital - position * price
                
            elif signal == -1 and position > 0:  # Sell signal and has position
                # Calculate profit/loss
                pnl = position * (price - entry_price)
                
                # Update portfolio
                portfolio.loc[df.index[i], 'holdings'] = 0
                portfolio.loc[df.index[i], 'cash'] = portfolio.iloc[i-1]['cash'] + position * price if i > 0 else initial_capital + position * price
                
                # Reset position
                position = 0
                entry_price = 0
            
            else:
                # No trade, update holdings value
                portfolio.loc[df.index[i], 'holdings'] = position * price
                portfolio.loc[df.index[i], 'cash'] = portfolio.iloc[i-1]['cash'] if i > 0 else initial_capital
            
            # Calculate total value and returns
            portfolio.loc[df.index[i], 'total'] = portfolio.loc[df.index[i], 'holdings'] + portfolio.loc[df.index[i], 'cash']
            portfolio.loc[df.index[i], 'returns'] = (portfolio.loc[df.index[i], 'total'] / initial_capital) - 1
        
        # Calculate performance metrics
        total_return = portfolio['returns'].iloc[-1]
        max_drawdown = (portfolio['total'] / portfolio['total'].cummax() - 1).min()
        
        # Count trades
        buy_signals = (df['signal'] == 1).sum()
        sell_signals = (df['signal'] == -1).sum()
        
        # Return results
        results = {
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'final_balance': portfolio['total'].iloc[-1],
            'portfolio': portfolio
        }
        
        self.log_info(f"Backtest completed: Return: {total_return:.2%}, Max Drawdown: {max_drawdown:.2%}, Trades: {buy_signals + sell_signals}")
        
        return results
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get the strategy parameters.
        
        Returns:
            Dictionary of strategy parameters
        """
        return {
            'short_window': self.short_window,
            'long_window': self.long_window
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Set strategy parameters.
        
        Args:
            parameters: Dictionary of parameters to set
            
        Returns:
            bool: True if parameters were set successfully, False otherwise
        """
        try:
            # Store original values in case validation fails
            original_short_window = self.short_window
            original_long_window = self.long_window
            
            # Extract new parameters
            new_short_window = parameters.get('short_window', self.short_window)
            new_long_window = parameters.get('long_window', self.long_window)
            
            # Validate parameters before setting them
            if new_short_window >= new_long_window:
                self.log_warning(f"Invalid parameters: short_window ({new_short_window}) must be less than long_window ({new_long_window})")
                return False
            
            # If validation passes, set the parameters
            self.short_window = new_short_window
            self.long_window = new_long_window
            
            # Update min required candles
            self.min_required_candles = self.long_window + 1
            
            self.log_info(f"Updated parameters: short_window={self.short_window}, long_window={self.long_window}")
            return True
        except Exception as e:
            self.log_error(f"Failed to set parameters: {str(e)}")
            return False
    
    def get_plot_config(self) -> Dict[str, Any]:
        """
        Get configuration for plotting strategy indicators.
        
        Returns:
            Dictionary with plotting configuration
        """
        return {
            'main_plot': {
                'short_sma': {'color': 'blue', 'width': 1.5, 'label': f'Short SMA ({self.short_window})'},
                'long_sma': {'color': 'red', 'width': 1.5, 'label': f'Long SMA ({self.long_window})'}
            },
            'sub_plots': {
                'sma_diff': {'color': 'green', 'type': 'line', 'panel': 1, 'label': 'SMA Difference'}
            },
            'buy_markers': {
                'marker': '^', 'color': 'green', 'size': 10, 'label': 'Buy Signal'
            },
            'sell_markers': {
                'marker': 'v', 'color': 'red', 'size': 10, 'label': 'Sell Signal'
            }
        }
