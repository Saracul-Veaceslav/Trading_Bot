"""
TradingView strategy adapter for the Trading Bot.

This module provides adapters for popular TradingView strategies,
allowing them to be used with the Trading Bot framework.
"""
import pandas as pd
import numpy as np
import logging

# Try to import TA-Lib, but provide fallback implementations if not available
try:
    import talib
    TALIB_AVAILABLE = True
    logging.getLogger('trading').info("TA-Lib is available, using native functions")
except ImportError:
    TALIB_AVAILABLE = False
    logging.getLogger('trading').warning(
        "TA-Lib is not available. Using pandas/numpy implementations instead. "
        "For better performance, install TA-Lib: brew install ta-lib && pip install TA-Lib"
    )

class TradingViewStrategyAdapter:
    """Base class for TradingView strategy adapters."""

    def __init__(self, strategy_name, parameters=None):
        """
        Initialize the TradingView strategy adapter.
        
        Args:
            strategy_name (str): The name of the strategy
            parameters (dict, optional): Strategy parameters
        """
        self.strategy_name = strategy_name
        self.parameters = parameters or {}
        self.trading_logger = None
        self.error_logger = None

    def set_loggers(self, trading_logger, error_logger=None):
        """
        Set the loggers for the strategy.
        
        Args:
            trading_logger: Logger for trading activities
            error_logger: Logger for errors
        """
        self.trading_logger = trading_logger
        self.error_logger = error_logger

    def prepare_data(self, df):
        """
        Prepare data for strategy calculation.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pandas.DataFrame: Prepared DataFrame
        """
        # Ensure required columns exist
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        if not all(col in df.columns for col in required_columns):
            if self.error_logger:
                self.error_logger.error(f"DataFrame missing required columns. Required: {required_columns}, Got: {df.columns}")
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
        
        # Ensure the DataFrame is sorted by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df

    def calculate_signal(self, df):
        """
        Calculate the trading signal based on the strategy.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            int: Trading signal (1 for buy, -1 for sell, 0 for hold)
        """
        try:
            prepared_df = self.prepare_data(df)
            indicator_df = self.calculate_indicators(prepared_df)
            
            # Derived classes should implement this logic
            return 0
        except Exception as e:
            if self.error_logger:
                self.error_logger.error(f"Error calculating signal: {str(e)}")
            return 0

    def calculate_indicators(self, df):
        """
        Calculate indicators for the strategy.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pandas.DataFrame: DataFrame with indicators
        """
        # Derived classes should implement this logic
        return df

    def get_parameters(self):
        """
        Get the strategy parameters.
        
        Returns:
            dict: Strategy parameters
        """
        return self.parameters

    def set_parameters(self, parameters):
        """
        Set the strategy parameters.
        
        Args:
            parameters (dict): Strategy parameters
        """
        if not isinstance(parameters, dict):
            if self.error_logger:
                self.error_logger.error(f"Parameters must be a dictionary, got {type(parameters)}")
            return
            
        self.parameters = parameters


class RSIStrategy(TradingViewStrategyAdapter):
    """RSI (Relative Strength Index) strategy from TradingView."""

    def __init__(self, parameters=None):
        """Initialize the RSI strategy with default parameters."""
        default_params = {
            "rsi_period": 14,
            "overbought": 70,
            "oversold": 30
        }
        super().__init__("RSI Strategy", parameters or default_params)

    def calculate_indicators(self, df):
        """
        Calculate RSI indicator.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pandas.DataFrame: DataFrame with RSI indicator
        """
        try:
            # Make a copy of the dataframe to avoid modifying the original
            result_df = df.copy()
            
            # Calculate RSI
            if TALIB_AVAILABLE:
                # Use TA-Lib for RSI calculation if available
                result_df['rsi'] = talib.RSI(result_df['close'], timeperiod=self.parameters['rsi_period'])
            else:
                # Fallback implementation using pandas
                delta = result_df['close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                
                avg_gain = gain.rolling(window=self.parameters['rsi_period']).mean()
                avg_loss = loss.rolling(window=self.parameters['rsi_period']).mean()
                
                rs = avg_gain / avg_loss
                result_df['rsi'] = 100 - (100 / (1 + rs))
            
            if self.trading_logger:
                self.trading_logger.info(f"Calculated RSI with period={self.parameters['rsi_period']}")
                
            return result_df
            
        except Exception as e:
            if self.error_logger:
                self.error_logger.error(f"Error calculating RSI: {str(e)}")
            return df

    def calculate_signal(self, df):
        """
        Calculate trading signal based on RSI.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            int: Trading signal (1 for buy, -1 for sell, 0 for hold)
        """
        try:
            # Calculate indicators
            result_df = self.calculate_indicators(df)
            
            # Get the last two RSI values
            if len(result_df) < 2:
                if self.trading_logger:
                    self.trading_logger.warning("Not enough data for RSI signal")
                return 0
                
            rsi_current = result_df['rsi'].iloc[-1]
            rsi_previous = result_df['rsi'].iloc[-2]
            
            # Buy signal: RSI crosses above oversold level
            if rsi_previous < self.parameters['oversold'] and rsi_current >= self.parameters['oversold']:
                if self.trading_logger:
                    self.trading_logger.info(f"RSI buy signal: {rsi_current} crossed above {self.parameters['oversold']}")
                return 1
                
            # Sell signal: RSI crosses below overbought level
            if rsi_previous > self.parameters['overbought'] and rsi_current <= self.parameters['overbought']:
                if self.trading_logger:
                    self.trading_logger.info(f"RSI sell signal: {rsi_current} crossed below {self.parameters['overbought']}")
                return -1
                
            # Hold signal
            return 0
            
        except Exception as e:
            if self.error_logger:
                self.error_logger.error(f"Error calculating RSI signal: {str(e)}")
            return 0


class MACDStrategy(TradingViewStrategyAdapter):
    """MACD (Moving Average Convergence Divergence) strategy from TradingView."""

    def __init__(self, parameters=None):
        """Initialize the MACD strategy with default parameters."""
        default_params = {
            "fast_length": 12,
            "slow_length": 26,
            "signal_length": 9
        }
        super().__init__("MACD Strategy", parameters or default_params)

    def calculate_indicators(self, df):
        """
        Calculate MACD indicators.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pandas.DataFrame: DataFrame with MACD indicators
        """
        try:
            # Make a copy of the dataframe to avoid modifying the original
            result_df = df.copy()
            
            # Calculate MACD
            if TALIB_AVAILABLE:
                # Use TA-Lib for MACD calculation if available
                macd, signal, hist = talib.MACD(
                    result_df['close'],
                    fastperiod=self.parameters['fast_length'],
                    slowperiod=self.parameters['slow_length'],
                    signalperiod=self.parameters['signal_length']
                )
                result_df['macd'] = macd
                result_df['macd_signal'] = signal
                result_df['macd_hist'] = hist
            else:
                # Fallback implementation using pandas
                fast_ema = result_df['close'].ewm(span=self.parameters['fast_length'], adjust=False).mean()
                slow_ema = result_df['close'].ewm(span=self.parameters['slow_length'], adjust=False).mean()
                result_df['macd'] = fast_ema - slow_ema
                result_df['macd_signal'] = result_df['macd'].ewm(span=self.parameters['signal_length'], adjust=False).mean()
                result_df['macd_hist'] = result_df['macd'] - result_df['macd_signal']
            
            if self.trading_logger:
                self.trading_logger.info(f"Calculated MACD with fast={self.parameters['fast_length']}, "
                                        f"slow={self.parameters['slow_length']}, "
                                        f"signal={self.parameters['signal_length']}")
                
            return result_df
            
        except Exception as e:
            if self.error_logger:
                self.error_logger.error(f"Error calculating MACD: {str(e)}")
            return df

    def calculate_signal(self, df):
        """
        Calculate trading signal based on MACD.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            int: Trading signal (1 for buy, -1 for sell, 0 for hold)
        """
        try:
            # Calculate indicators
            result_df = self.calculate_indicators(df)
            
            # Get the last two MACD and signal values
            if len(result_df) < 2:
                if self.trading_logger:
                    self.trading_logger.warning("Not enough data for MACD signal")
                return 0
                
            macd_current = result_df['macd'].iloc[-1]
            macd_previous = result_df['macd'].iloc[-2]
            signal_current = result_df['macd_signal'].iloc[-1]
            signal_previous = result_df['macd_signal'].iloc[-2]
            
            # Buy signal: MACD crosses above signal line
            if macd_previous < signal_previous and macd_current >= signal_current:
                if self.trading_logger:
                    self.trading_logger.info(f"MACD buy signal: {macd_current} crossed above {signal_current}")
                return 1
                
            # Sell signal: MACD crosses below signal line
            if macd_previous > signal_previous and macd_current <= signal_current:
                if self.trading_logger:
                    self.trading_logger.info(f"MACD sell signal: {macd_current} crossed below {signal_current}")
                return -1
                
            # Hold signal
            return 0
            
        except Exception as e:
            if self.error_logger:
                self.error_logger.error(f"Error calculating MACD signal: {str(e)}")
            return 0


class BollingerBandsStrategy(TradingViewStrategyAdapter):
    """Bollinger Bands strategy from TradingView."""

    def __init__(self, parameters=None):
        """Initialize the Bollinger Bands strategy with default parameters."""
        default_params = {
            "length": 20,
            "std_dev": 2
        }
        super().__init__("Bollinger Bands Strategy", parameters or default_params)

    def calculate_indicators(self, df):
        """
        Calculate Bollinger Bands indicators.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pandas.DataFrame: DataFrame with Bollinger Bands indicators
        """
        try:
            # Make a copy of the dataframe to avoid modifying the original
            result_df = df.copy()
            
            # Calculate Bollinger Bands
            if TALIB_AVAILABLE:
                # Use TA-Lib for Bollinger Bands calculation if available
                upper, middle, lower = talib.BBANDS(
                    result_df['close'],
                    timeperiod=self.parameters['length'],
                    nbdevup=self.parameters['std_dev'],
                    nbdevdn=self.parameters['std_dev']
                )
                result_df['bb_upper'] = upper
                result_df['bb_middle'] = middle
                result_df['bb_lower'] = lower
            else:
                # Fallback implementation using pandas
                result_df['bb_middle'] = result_df['close'].rolling(window=self.parameters['length']).mean()
                rolling_std = result_df['close'].rolling(window=self.parameters['length']).std()
                result_df['bb_upper'] = result_df['bb_middle'] + (rolling_std * self.parameters['std_dev'])
                result_df['bb_lower'] = result_df['bb_middle'] - (rolling_std * self.parameters['std_dev'])
            
            # Calculate %B (percent bandwidth)
            result_df['pct_b'] = (result_df['close'] - result_df['bb_lower']) / (result_df['bb_upper'] - result_df['bb_lower'])
            
            if self.trading_logger:
                self.trading_logger.info(f"Calculated Bollinger Bands with length={self.parameters['length']}, "
                                        f"std_dev={self.parameters['std_dev']}")
                
            return result_df
            
        except Exception as e:
            if self.error_logger:
                self.error_logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return df

    def calculate_signal(self, df):
        """
        Calculate trading signal based on Bollinger Bands.
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLCV data
            
        Returns:
            int: Trading signal (1 for buy, -1 for sell, 0 for hold)
        """
        try:
            # Calculate indicators
            result_df = self.calculate_indicators(df)
            
            # Get the last two values
            if len(result_df) < 2:
                if self.trading_logger:
                    self.trading_logger.warning("Not enough data for Bollinger Bands signal")
                return 0
                
            close_current = result_df['close'].iloc[-1]
            close_previous = result_df['close'].iloc[-2]
            lower_current = result_df['bb_lower'].iloc[-1]
            lower_previous = result_df['bb_lower'].iloc[-2]
            upper_current = result_df['bb_upper'].iloc[-1]
            upper_previous = result_df['bb_upper'].iloc[-2]
            
            # Buy signal: Price crosses below lower band and then starts rising
            if close_previous < lower_previous and close_current > lower_current:
                if self.trading_logger:
                    self.trading_logger.info(f"Bollinger Bands buy signal: Price {close_current} bounced off lower band {lower_current}")
                return 1
                
            # Sell signal: Price crosses above upper band and then starts falling
            if close_previous > upper_previous and close_current < upper_current:
                if self.trading_logger:
                    self.trading_logger.info(f"Bollinger Bands sell signal: Price {close_current} bounced off upper band {upper_current}")
                return -1
                
            # Hold signal
            return 0
            
        except Exception as e:
            if self.error_logger:
                self.error_logger.error(f"Error calculating Bollinger Bands signal: {str(e)}")
            return 0


def get_strategy(strategy_name, parameters=None):
    """
    Factory function to get a strategy by name.
    
    Args:
        strategy_name (str): Name of the strategy
        parameters (dict, optional): Strategy parameters
        
    Returns:
        TradingViewStrategyAdapter: Strategy instance
    """
    strategy_map = {
        "rsi_strategy": RSIStrategy,
        "macd_strategy": MACDStrategy,
        "bollinger_bands_strategy": BollingerBandsStrategy
    }
    
    if strategy_name not in strategy_map:
        logging.getLogger('error').error(f"Strategy {strategy_name} not found")
        return None
        
    strategy_class = strategy_map[strategy_name]
    return strategy_class(parameters) 