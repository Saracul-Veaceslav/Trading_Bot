"""
SMA Crossover Strategy Module

This module implements a Simple Moving Average (SMA) Crossover strategy, which is a 
popular trading strategy often used on TradingView.
"""

import pandas as pd

from bot.config.settings import STRATEGY_PARAMS


class SMAcrossover:
    """
    SMA Crossover Strategy.
    
    Buy signal: Short SMA crosses above Long SMA
    Sell signal: Short SMA crosses below Long SMA
    """
    
    def __init__(self, trading_logger, error_logger):
        """
        Initialize the SMA Crossover strategy.
        
        Args:
            trading_logger: Logger for trading activities
            error_logger: Logger for errors
        """
        self.trading_logger = trading_logger
        self.error_logger = error_logger
        self.params = STRATEGY_PARAMS['sma_crossover']
    
    def calculate_signal(self, df: pd.DataFrame) -> int:
        """
        Calculate the trading signal based on SMA crossover.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            int: 1 for buy, -1 for sell, 0 for hold
            
        Raises:
            Exception: If calculation fails
        """
        try:
            # Check if we have enough data
            if len(df) < self.params['SMA_LONG']:
                self.trading_logger.warning(f"Not enough data for SMA calculation")
                return 0
            
            # Calculate SMAs
            df = df.copy()
            df['sma_short'] = df['close'].rolling(window=self.params['SMA_SHORT']).mean()
            df['sma_long'] = df['close'].rolling(window=self.params['SMA_LONG']).mean()
            
            # Get the last two complete rows
            df = df.dropna().tail(2)
            if len(df) < 2:
                return 0
            
            # Check for crossover
            prev_short, prev_long = df['sma_short'].iloc[-2], df['sma_long'].iloc[-2]
            curr_short, curr_long = df['sma_short'].iloc[-1], df['sma_long'].iloc[-1]
            
            # Buy: Short crosses above Long
            if prev_short < prev_long and curr_short > curr_long:
                self.trading_logger.info(f"BUY Signal: Short SMA crossed above Long SMA")
                return 1
            
            # Sell: Short crosses below Long
            elif prev_short > prev_long and curr_short < curr_long:
                self.trading_logger.info(f"SELL Signal: Short SMA crossed below Long SMA")
                return -1
            
            # No crossover
            return 0
                
        except Exception as e:
            self.error_logger.exception(f"Error calculating signal: {str(e)}")
            return 0
    
    def calculate_signals_for_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMA crossover signals for an entire DataFrame.
        
        This is useful for backtesting or visualization.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            pd.DataFrame: DataFrame with added SMA and signal columns
        """
        try:
            result_df = df.copy()
            
            # Calculate SMAs
            result_df['sma_short'] = result_df['close'].rolling(window=self.params['SMA_SHORT']).mean()
            result_df['sma_long'] = result_df['close'].rolling(window=self.params['SMA_LONG']).mean()
            
            # Initialize signal column
            result_df['signal'] = 0
            
            # Generate crossover signals
            result_df['short_above_long'] = result_df['sma_short'] > result_df['sma_long']
            
            # Buy signal: Short SMA crosses above Long SMA
            crossover_up = (result_df['short_above_long'] != result_df['short_above_long'].shift(1)) & result_df['short_above_long']
            result_df.loc[crossover_up, 'signal'] = 1
            
            # Sell signal: Short SMA crosses below Long SMA
            crossover_down = (result_df['short_above_long'] != result_df['short_above_long'].shift(1)) & ~result_df['short_above_long']
            result_df.loc[crossover_down, 'signal'] = -1
            
            # Drop temporary column
            result_df = result_df.drop('short_above_long', axis=1)
            
            return result_df
            
        except Exception as e:
            self.error_logger.exception(f"Error calculating signals for DataFrame: {str(e)}")
            return df 