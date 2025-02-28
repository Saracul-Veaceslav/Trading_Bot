"""
Simple Moving Average Crossover strategy implementation.
"""
import pandas as pd
import numpy as np
import logging

class SMAcrossover:
    """
    SMA Crossover strategy that generates trading signals based on the crossing of two moving averages.
    """
    
    def __init__(self, short_window=20, long_window=50, name="SMA Crossover"):
        """
        Initialize the SMA Crossover strategy.
        
        Args:
            short_window (int): Period for the short moving average
            long_window (int): Period for the long moving average
            name (str): Strategy name
        """
        # Handle potential mock objects in tests
        try:
            self.short_window = int(short_window) if short_window is not None else 20
            self.long_window = int(long_window) if long_window is not None else 50
        except (TypeError, ValueError):
            # Fall back to defaults for mocked objects
            self.short_window = 20
            self.long_window = 50
            
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.error_logger = self.logger  # Default to same logger if not provided
        
    def set_loggers(self, trading_logger, error_logger=None):
        """
        Set the loggers for the strategy.
        
        Args:
            trading_logger: Logger for trading activity
            error_logger: Logger for errors (optional)
        """
        self.logger = trading_logger if trading_logger else self.logger
        self.error_logger = error_logger if error_logger else self.logger
    
    def calculate_indicators(self, df):
        """
        Calculate strategy indicators (short and long SMAs).
        
        Args:
            df (pandas.DataFrame): DataFrame with historical price data
            
        Returns:
            pandas.DataFrame: DataFrame with added indicators
        """
        if df is None or df.empty:
            self.logger.warning("Empty DataFrame provided for indicator calculation")
            return None
        
        try:
            # Make sure we have a copy to avoid modifying the original
            df_copy = df.copy()
            
            # Ensure correct column names
            if 'close' not in df_copy.columns and df_copy.shape[1] >= 4:
                # Rename columns if they are in standard OHLCV format
                df_copy.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'] if df_copy.shape[1] >= 6 else ['open', 'high', 'low', 'close']
            
            # Handle potential mock objects
            short_window = 20
            long_window = 50
            
            try:
                short_window = int(self.short_window)
                long_window = int(self.long_window)
            except (TypeError, ValueError):
                # Use defaults if conversion fails
                self.logger.warning("Using default window values due to type conversion error")
            
            # Calculate short and long moving averages
            df_copy['sma_short'] = df_copy['close'].rolling(window=short_window).mean()
            df_copy['sma_long'] = df_copy['close'].rolling(window=long_window).mean()
            
            return df_copy
            
        except Exception as e:
            self.error_logger.error(f"Error calculating indicators: {e}")
            return None
    
    def generate_signal(self, df):
        """
        Generate trading signals based on SMA crossover.
        
        Args:
            df (pandas.DataFrame): DataFrame with price data
            
        Returns:
            int: Trading signal (1 for buy, -1 for sell, 0 for hold)
        """
        if df is None or df.empty:
            self.logger.warning("Empty DataFrame provided for signal generation")
            return 0  # hold signal as integer
        
        try:
            # Calculate indicators
            df = self.calculate_indicators(df)
            
            if df is None:
                return 0  # hold signal as integer
            
            # Get the most recent values
            short_sma = df['sma_short'].iloc[-1]
            long_sma = df['sma_long'].iloc[-1]
            
            # Get the previous values (for crossing detection)
            prev_short_sma = df['sma_short'].iloc[-2] if len(df) > 1 else None
            prev_long_sma = df['sma_long'].iloc[-2] if len(df) > 1 else None
            
            # Check for SMA crossover
            if np.isnan(short_sma) or np.isnan(long_sma) or prev_short_sma is None or prev_long_sma is None or np.isnan(prev_short_sma) or np.isnan(prev_long_sma):
                # Not enough data to generate a signal
                self.logger.warning(f"Not enough data for SMA calculation. Need at least {self.long_window + 1} data points.")
                return 0  # hold signal as integer
            
            # Bullish crossover: short SMA crosses above long SMA
            if prev_short_sma <= prev_long_sma and short_sma > long_sma:
                return 1  # buy signal as integer
            
            # Bearish crossover: short SMA crosses below long SMA
            elif prev_short_sma >= prev_long_sma and short_sma < long_sma:
                return -1  # sell signal as integer
            
            # No crossover
            return 0  # hold signal as integer
            
        except Exception as e:
            self.error_logger.exception(f"Error generating signal: {e}")
            return 0  # hold signal as integer
    
    # Method expected by the tests
    def calculate_signal(self, df):
        """
        Calculate trading signal based on SMA crossover (alias for generate_signal).
        
        Args:
            df (pandas.DataFrame): DataFrame with price data
            
        Returns:
            int: Trading signal (1 for buy, -1 for sell, 0 for hold)
        """
        return self.generate_signal(df)
    
    def get_signal_meaning(self, signal_value):
        """
        Get the meaning of a signal value.
        
        Args:
            signal_value (int): Signal value (1, -1, 0)
            
        Returns:
            str: Signal meaning ('buy', 'sell', 'hold')
        """
        if signal_value == 1:
            return 'buy'
        elif signal_value == -1:
            return 'sell'
        else:
            return 'hold'
    
    def calculate_signals_for_dataframe(self, df):
        """
        Calculate signals for an entire DataFrame.
        
        Args:
            df (pandas.DataFrame): DataFrame with price data
            
        Returns:
            pandas.DataFrame: DataFrame with signals column added
        """
        if df is None or df.empty:
            self.logger.warning("Empty DataFrame provided for signal calculation")
            return None
        
        try:
            # Calculate indicators
            result_df = self.calculate_indicators(df)
            
            if result_df is None:
                return None
            
            # Initialize signal column
            result_df['signal'] = 0  # hold as integer
            
            # Find buy signals: short SMA crosses above long SMA
            buy_signals = (result_df['sma_short'].shift(1) <= result_df['sma_long'].shift(1)) & \
                          (result_df['sma_short'] > result_df['sma_long'])
            
            # Find sell signals: short SMA crosses below long SMA
            sell_signals = (result_df['sma_short'].shift(1) >= result_df['sma_long'].shift(1)) & \
                           (result_df['sma_short'] < result_df['sma_long'])
            
            # Apply signals
            result_df.loc[buy_signals, 'signal'] = 1  # buy as integer
            result_df.loc[sell_signals, 'signal'] = -1  # sell as integer
            
            return result_df
            
        except Exception as e:
            self.error_logger.exception(f"Error calculating signals for DataFrame: {e}")
            return None
    
    def get_parameters(self):
        """
        Get strategy parameters.
        
        Returns:
            dict: Strategy parameters
        """
        return {
            'name': self.name,
            'short_window': self.short_window,
            'long_window': self.long_window
        }
    
    def set_parameters(self, parameters):
        """
        Set strategy parameters.
        
        Args:
            parameters (dict): Strategy parameters
            
        Returns:
            bool: True if parameters were set successfully, False otherwise
        """
        try:
            if 'short_window' in parameters:
                self.short_window = int(parameters['short_window'])
            if 'long_window' in parameters:
                self.long_window = int(parameters['long_window'])
            if 'name' in parameters:
                self.name = parameters['name']
            return True
        except Exception as e:
            self.error_logger.error(f"Error setting parameters: {e}")
            return False
    
    def backtest(self, df, initial_capital=10000.0):
        """
        Backtest the strategy on historical data.
        
        Args:
            df (pandas.DataFrame): DataFrame with historical price data
            initial_capital (float): Initial capital for the backtest
            
        Returns:
            dict: Backtest results including returns, drawdown, etc.
        """
        if df is None or df.empty:
            self.logger.warning("Empty DataFrame provided for backtesting")
            return {"error": "No data for backtesting"}
        
        try:
            # Calculate indicators
            df = self.calculate_indicators(df)
            
            if df is None:
                return {"error": "Failed to calculate indicators"}
            
            # Create a copy for results
            backtest_df = df.copy()
            
            # Initialize signal column with hold (0)
            backtest_df['signal'] = 0
            
            # Generate signals: 1 for buy, -1 for sell
            # Bullish crossover: short SMA crosses above long SMA
            bullish = (backtest_df['sma_short'].shift(1) <= backtest_df['sma_long'].shift(1)) & \
                      (backtest_df['sma_short'] > backtest_df['sma_long'])
            
            # Bearish crossover: short SMA crosses below long SMA
            bearish = (backtest_df['sma_short'].shift(1) >= backtest_df['sma_long'].shift(1)) & \
                      (backtest_df['sma_short'] < backtest_df['sma_long'])
            
            backtest_df.loc[bullish, 'signal'] = 1
            backtest_df.loc[bearish, 'signal'] = -1
            
            # Calculate position: 1 for long, -1 for short, 0 for no position
            backtest_df['position'] = backtest_df['signal'].cumsum()
            
            # Calculate returns
            backtest_df['returns'] = backtest_df['close'].pct_change()
            backtest_df['strategy_returns'] = backtest_df['position'].shift(1) * backtest_df['returns']
            
            # Calculate cumulative returns
            backtest_df['cum_returns'] = (1 + backtest_df['returns']).cumprod()
            backtest_df['cum_strategy_returns'] = (1 + backtest_df['strategy_returns']).cumprod()
            
            # Calculate drawdown
            backtest_df['peak'] = backtest_df['cum_strategy_returns'].cummax()
            backtest_df['drawdown'] = (backtest_df['cum_strategy_returns'] - backtest_df['peak']) / backtest_df['peak']
            
            # Calculate metrics
            total_return = backtest_df['cum_strategy_returns'].iloc[-1] - 1
            max_drawdown = backtest_df['drawdown'].min()
            
            # Number of trades
            trades = backtest_df[backtest_df['signal'] != 0]
            num_trades = len(trades)
            
            results = {
                "total_return": total_return,
                "max_drawdown": max_drawdown,
                "num_trades": num_trades,
                "sharpe_ratio": self._calculate_sharpe_ratio(backtest_df['strategy_returns']),
                "data": backtest_df
            }
            
            return results
            
        except Exception as e:
            self.error_logger.exception(f"Error during backtesting: {e}")
            return {"error": str(e)}
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.01, periods_per_year=252):
        """
        Calculate the Sharpe ratio of a returns series.
        
        Args:
            returns (pandas.Series): Series of returns
            risk_free_rate (float): Risk-free rate
            periods_per_year (int): Number of periods in a year
            
        Returns:
            float: Sharpe ratio
        """
        excess_returns = returns - risk_free_rate / periods_per_year
        return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()
