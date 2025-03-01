"""
RSI Bollinger Bands Strategy

This strategy combines RSI (Relative Strength Index) with Bollinger Bands
to generate trading signals based on overbought/oversold conditions and
price volatility.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple, List, Union

from trading_bot.strategies.base import Strategy
from trading_bot.utils.logger import get_logger

class RSIBollingerStrategy(Strategy):
    """
    RSI Bollinger Bands Strategy
    
    This strategy combines RSI (Relative Strength Index) with Bollinger Bands
    to identify potential entry and exit points. It generates buy signals when:
    1. RSI is below the oversold threshold AND
    2. Price touches or crosses below the lower Bollinger Band
    
    It generates sell signals when:
    1. RSI is above the overbought threshold AND
    2. Price touches or crosses above the upper Bollinger Band
    
    Parameters:
    - rsi_period: Period for RSI calculation (default: 14)
    - rsi_overbought: Threshold for overbought condition (default: 70)
    - rsi_oversold: Threshold for oversold condition (default: 30)
    - bb_period: Period for Bollinger Bands calculation (default: 20)
    - bb_std_dev: Standard deviation multiplier for Bollinger Bands (default: 2.0)
    - signal_threshold: Minimum signal strength to generate a trade (default: 0.5)
    """
    
    def __init__(self, 
                 rsi_period: int = 14,
                 rsi_overbought: float = 70.0,
                 rsi_oversold: float = 30.0,
                 bb_period: int = 20,
                 bb_std_dev: float = 2.0,
                 signal_threshold: float = 0.5,
                 **kwargs):
        """
        Initialize the RSI Bollinger Bands strategy.
        
        Args:
            rsi_period: Period for RSI calculation
            rsi_overbought: Threshold for overbought condition
            rsi_oversold: Threshold for oversold condition
            bb_period: Period for Bollinger Bands calculation
            bb_std_dev: Standard deviation multiplier for Bollinger Bands
            signal_threshold: Minimum signal strength to generate a trade
            **kwargs: Additional parameters to pass to the base Strategy
        """
        super().__init__(**kwargs)
        
        # Strategy parameters
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.bb_period = bb_period
        self.bb_std_dev = bb_std_dev
        self.signal_threshold = signal_threshold
        
        # Set strategy name and metadata
        self.set_name("RSI_Bollinger")
        self.set_metadata({
            "description": "RSI Bollinger Bands Strategy",
            "parameters": {
                "rsi_period": rsi_period,
                "rsi_overbought": rsi_overbought,
                "rsi_oversold": rsi_oversold,
                "bb_period": bb_period,
                "bb_std_dev": bb_std_dev,
                "signal_threshold": signal_threshold
            },
            "version": "1.0.0"
        })
        
        self.log_info(f"Initialized RSI Bollinger Bands strategy with parameters: "
                     f"RSI({rsi_period}, {rsi_oversold}/{rsi_overbought}), "
                     f"BB({bb_period}, {bb_std_dev})")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI and Bollinger Bands indicators.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators
        """
        if data is None or len(data) == 0:
            self.log_warning("No data provided for indicator calculation")
            return pd.DataFrame()
        
        try:
            # Make a copy to avoid modifying the original
            df = data.copy()
            
            # Ensure we have the required columns
            if 'close' not in df.columns:
                if 'Close' in df.columns:
                    df['close'] = df['Close']
                else:
                    self.log_error("Missing 'close' column in data")
                    return df
            
            # Calculate RSI
            # First calculate price changes
            delta = df['close'].diff()
            
            # Create gain and loss series
            gain = delta.copy()
            loss = delta.copy()
            gain[gain < 0] = 0
            loss[loss > 0] = 0
            loss = abs(loss)
            
            # Calculate average gain and loss over the specified period
            avg_gain = gain.rolling(window=self.rsi_period).mean()
            avg_loss = loss.rolling(window=self.rsi_period).mean()
            
            # Calculate RS (Relative Strength)
            rs = avg_gain / avg_loss
            
            # Calculate RSI
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Calculate Bollinger Bands
            # Middle band = n-period moving average
            df['bb_middle'] = df['close'].rolling(window=self.bb_period).mean()
            
            # Calculate standard deviation
            df['bb_std'] = df['close'].rolling(window=self.bb_period).std()
            
            # Upper band = middle band + (standard deviation * multiplier)
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * self.bb_std_dev)
            
            # Lower band = middle band - (standard deviation * multiplier)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * self.bb_std_dev)
            
            # Calculate percent B ((Price - Lower Band) / (Upper Band - Lower Band))
            df['bb_pct_b'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Calculate signal strength
            # RSI signal: 0 at oversold, 1 at overbought, linear in between
            df['rsi_signal'] = (df['rsi'] - self.rsi_oversold) / (self.rsi_overbought - self.rsi_oversold)
            df['rsi_signal'] = df['rsi_signal'].clip(0, 1)
            
            # Bollinger signal: 0 at lower band, 1 at upper band
            df['bb_signal'] = df['bb_pct_b'].clip(0, 1)
            
            # Combined signal: 0 = strong buy, 1 = strong sell, 0.5 = neutral
            df['combined_signal'] = (df['rsi_signal'] + df['bb_signal']) / 2
            
            return df
        
        except Exception as e:
            self.log_error(f"Error calculating indicators: {str(e)}")
            return data
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        """
        Generate trading signal based on RSI and Bollinger Bands.
        
        Args:
            data: DataFrame with OHLCV data and indicators
            
        Returns:
            int: Signal (BUY, SELL, or HOLD)
        """
        if data is None or len(data) < self.bb_period:
            self.log_warning(f"Insufficient data for signal generation: {len(data) if data is not None else 0} rows")
            return self.HOLD
        
        try:
            # Get the latest data point
            latest = data.iloc[-1]
            
            # Check if we have all required indicators
            required_columns = ['rsi', 'bb_upper', 'bb_lower', 'combined_signal']
            if not all(col in latest.index for col in required_columns):
                self.log_warning(f"Missing indicators for signal generation")
                return self.HOLD
            
            # Get the combined signal value
            signal_value = latest['combined_signal']
            
            # Strong buy signal
            if signal_value < 0.5 - self.signal_threshold/2:
                # Additional confirmation: RSI is below oversold and price is near/below lower band
                if latest['rsi'] < self.rsi_oversold and latest['close'] <= latest['bb_lower'] * 1.01:
                    self.log_info(f"BUY signal generated: RSI={latest['rsi']:.2f}, "
                                 f"Close={latest['close']:.2f}, BB_Lower={latest['bb_lower']:.2f}")
                    return self.BUY
            
            # Strong sell signal
            elif signal_value > 0.5 + self.signal_threshold/2:
                # Additional confirmation: RSI is above overbought and price is near/above upper band
                if latest['rsi'] > self.rsi_overbought and latest['close'] >= latest['bb_upper'] * 0.99:
                    self.log_info(f"SELL signal generated: RSI={latest['rsi']:.2f}, "
                                 f"Close={latest['close']:.2f}, BB_Upper={latest['bb_upper']:.2f}")
                    return self.SELL
            
            # No clear signal
            self.log_info(f"HOLD signal: RSI={latest['rsi']:.2f}, "
                         f"Close={latest['close']:.2f}, BB_Lower={latest['bb_lower']:.2f}, "
                         f"BB_Upper={latest['bb_upper']:.2f}")
            return self.HOLD
        
        except Exception as e:
            self.log_error(f"Error generating signal: {str(e)}")
            return self.HOLD
    
    def calculate_signal_strength(self, data: pd.DataFrame) -> float:
        """
        Calculate the strength of the current signal.
        
        Args:
            data: DataFrame with OHLCV data and indicators
            
        Returns:
            float: Signal strength between -1.0 (strong sell) and 1.0 (strong buy)
        """
        if data is None or len(data) < self.bb_period:
            return 0.0
        
        try:
            # Get the latest data point
            latest = data.iloc[-1]
            
            # Check if we have all required indicators
            if 'combined_signal' not in latest:
                return 0.0
            
            # Convert combined signal (0-1) to strength (-1 to 1)
            # 0 = strong buy (1.0), 0.5 = neutral (0.0), 1 = strong sell (-1.0)
            signal_strength = 1.0 - 2.0 * latest['combined_signal']
            
            return signal_strength
        
        except Exception as e:
            self.log_error(f"Error calculating signal strength: {str(e)}")
            return 0.0
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get the strategy parameters.
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        return {
            "rsi_period": self.rsi_period,
            "rsi_overbought": self.rsi_overbought,
            "rsi_oversold": self.rsi_oversold,
            "bb_period": self.bb_period,
            "bb_std_dev": self.bb_std_dev,
            "signal_threshold": self.signal_threshold
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set the strategy parameters.
        
        Args:
            parameters: Dictionary with parameters to set
        """
        if 'rsi_period' in parameters:
            self.rsi_period = int(parameters['rsi_period'])
        
        if 'rsi_overbought' in parameters:
            self.rsi_overbought = float(parameters['rsi_overbought'])
        
        if 'rsi_oversold' in parameters:
            self.rsi_oversold = float(parameters['rsi_oversold'])
        
        if 'bb_period' in parameters:
            self.bb_period = int(parameters['bb_period'])
        
        if 'bb_std_dev' in parameters:
            self.bb_std_dev = float(parameters['bb_std_dev'])
        
        if 'signal_threshold' in parameters:
            self.signal_threshold = float(parameters['signal_threshold'])
        
        # Update metadata
        metadata = self.get_metadata()
        metadata['parameters'] = self.get_parameters()
        self.set_metadata(metadata)
        
        self.log_info(f"Parameters updated: {self.get_parameters()}") 