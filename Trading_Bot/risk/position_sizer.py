"""
Position Sizing Module

This module provides position sizing strategies for risk management.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union, List
import logging
from abc import ABC, abstractmethod

from trading_bot.utils.logger import get_logger

logger = get_logger('trading_bot.risk.position_sizer')

class PositionSizer(ABC):
    """
    Abstract base class for position sizing strategies.
    
    Position sizers determine the appropriate position size for trades
    based on account balance, risk tolerance, and market conditions.
    """
    
    def __init__(self, 
                 max_position_size: float = 0.1, 
                 min_position_size: float = 0.01,
                 risk_logger=None):
        """
        Initialize the position sizer.
        
        Args:
            max_position_size: Maximum position size as a fraction of account balance (default: 0.1)
            min_position_size: Minimum position size as a fraction of account balance (default: 0.01)
            risk_logger: Logger for risk management
        """
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        self.logger = risk_logger if risk_logger else get_logger('trading_bot.risk.position_sizer')
    
    @abstractmethod
    def calculate_position_size(self, 
                               account_balance: float, 
                               current_price: float, 
                               **kwargs) -> float:
        """
        Calculate the position size for a trade.
        
        Args:
            account_balance: Current account balance
            current_price: Current price of the asset
            **kwargs: Additional parameters specific to the sizing strategy
            
        Returns:
            float: Position size in base currency units
        """
        pass
    
    def validate_position_size(self, 
                              position_size: float, 
                              account_balance: float, 
                              current_price: float) -> float:
        """
        Validate and adjust the position size if necessary.
        
        Args:
            position_size: Calculated position size
            account_balance: Current account balance
            current_price: Current price of the asset
            
        Returns:
            float: Validated position size
        """
        # Calculate position value
        position_value = position_size * current_price
        
        # Calculate position size as a fraction of account balance
        position_fraction = position_value / account_balance if account_balance > 0 else 0
        
        # Apply maximum position size constraint
        if position_fraction > self.max_position_size:
            adjusted_position_size = (self.max_position_size * account_balance) / current_price
            self.logger.warning(
                f"Position size reduced from {position_size:.6f} to {adjusted_position_size:.6f} "
                f"({position_fraction:.2%} -> {self.max_position_size:.2%} of balance)"
            )
            position_size = adjusted_position_size
        
        # Apply minimum position size constraint
        min_position_value = self.min_position_size * account_balance
        min_position_size = min_position_value / current_price if current_price > 0 else 0
        
        if position_size < min_position_size and position_size > 0:
            self.logger.warning(
                f"Position size increased from {position_size:.6f} to {min_position_size:.6f} "
                f"(minimum {self.min_position_size:.2%} of balance)"
            )
            position_size = min_position_size
        
        return position_size


class FixedRiskPositionSizer(PositionSizer):
    """
    Fixed risk position sizer.
    
    This strategy risks a fixed percentage of the account balance on each trade.
    The position size is calculated based on the distance to the stop loss.
    """
    
    def __init__(self, 
                 risk_per_trade: float = 0.01, 
                 max_position_size: float = 0.1, 
                 min_position_size: float = 0.01,
                 risk_logger=None):
        """
        Initialize the fixed risk position sizer.
        
        Args:
            risk_per_trade: Percentage of account balance to risk per trade (default: 0.01 = 1%)
            max_position_size: Maximum position size as a fraction of account balance (default: 0.1)
            min_position_size: Minimum position size as a fraction of account balance (default: 0.01)
            risk_logger: Logger for risk management
        """
        super().__init__(max_position_size, min_position_size, risk_logger)
        self.risk_per_trade = risk_per_trade
        self.logger.info(f"Fixed risk position sizer initialized with {risk_per_trade:.2%} risk per trade")
    
    def calculate_position_size(self, 
                               account_balance: float, 
                               current_price: float, 
                               stop_loss_price: Optional[float] = None, 
                               **kwargs) -> float:
        """
        Calculate the position size based on fixed risk.
        
        Args:
            account_balance: Current account balance
            current_price: Current price of the asset
            stop_loss_price: Price at which to place the stop loss
            **kwargs: Additional parameters
            
        Returns:
            float: Position size in base currency units
        """
        if account_balance <= 0 or current_price <= 0:
            self.logger.warning(f"Invalid account balance ({account_balance}) or price ({current_price})")
            return 0
        
        # If no stop loss is provided, use a default risk percentage of the current price
        if stop_loss_price is None or stop_loss_price <= 0:
            default_stop_pct = kwargs.get('default_stop_pct', 0.05)  # Default 5% stop
            is_long = kwargs.get('is_long', True)
            
            if is_long:
                stop_loss_price = current_price * (1 - default_stop_pct)
            else:
                stop_loss_price = current_price * (1 + default_stop_pct)
            
            self.logger.info(f"Using default stop loss at {stop_loss_price:.2f} ({default_stop_pct:.2%} from entry)")
        
        # Calculate risk amount in account currency
        risk_amount = account_balance * self.risk_per_trade
        
        # Calculate risk per unit
        is_long = kwargs.get('is_long', True)
        if is_long:
            # For long positions, stop loss is below entry
            if current_price <= stop_loss_price:
                self.logger.warning(f"Stop loss ({stop_loss_price}) is above entry price ({current_price}) for long position")
                return 0
            
            risk_per_unit = current_price - stop_loss_price
        else:
            # For short positions, stop loss is above entry
            if current_price >= stop_loss_price:
                self.logger.warning(f"Stop loss ({stop_loss_price}) is below entry price ({current_price}) for short position")
                return 0
            
            risk_per_unit = stop_loss_price - current_price
        
        # Calculate position size
        if risk_per_unit > 0:
            position_size = risk_amount / risk_per_unit
        else:
            self.logger.warning(f"Risk per unit is zero or negative: {risk_per_unit}")
            return 0
        
        # Validate position size
        position_size = self.validate_position_size(position_size, account_balance, current_price)
        
        self.logger.info(
            f"Calculated position size: {position_size:.6f} units "
            f"(risking {risk_amount:.2f} with {risk_per_unit:.2f} per unit)"
        )
        
        return position_size


class VolatilityPositionSizer(PositionSizer):
    """
    Volatility-based position sizer.
    
    This strategy adjusts position size based on market volatility.
    Higher volatility leads to smaller positions, and vice versa.
    """
    
    def __init__(self, 
                 risk_per_trade: float = 0.01, 
                 volatility_lookback: int = 20,
                 volatility_factor: float = 1.0,
                 max_position_size: float = 0.1, 
                 min_position_size: float = 0.01,
                 risk_logger=None):
        """
        Initialize the volatility position sizer.
        
        Args:
            risk_per_trade: Percentage of account balance to risk per trade (default: 0.01 = 1%)
            volatility_lookback: Number of periods to calculate volatility (default: 20)
            volatility_factor: Factor to adjust position size based on volatility (default: 1.0)
            max_position_size: Maximum position size as a fraction of account balance (default: 0.1)
            min_position_size: Minimum position size as a fraction of account balance (default: 0.01)
            risk_logger: Logger for risk management
        """
        super().__init__(max_position_size, min_position_size, risk_logger)
        self.risk_per_trade = risk_per_trade
        self.volatility_lookback = volatility_lookback
        self.volatility_factor = volatility_factor
        self.logger.info(
            f"Volatility position sizer initialized with {risk_per_trade:.2%} risk per trade, "
            f"{volatility_lookback} period lookback, and {volatility_factor} volatility factor"
        )
    
    def calculate_position_size(self, 
                               account_balance: float, 
                               current_price: float, 
                               price_history: Optional[pd.DataFrame] = None,
                               **kwargs) -> float:
        """
        Calculate the position size based on volatility.
        
        Args:
            account_balance: Current account balance
            current_price: Current price of the asset
            price_history: DataFrame with historical prices
            **kwargs: Additional parameters
            
        Returns:
            float: Position size in base currency units
        """
        if account_balance <= 0 or current_price <= 0:
            self.logger.warning(f"Invalid account balance ({account_balance}) or price ({current_price})")
            return 0
        
        # Calculate risk amount in account currency
        risk_amount = account_balance * self.risk_per_trade
        
        # Calculate volatility
        volatility = self._calculate_volatility(price_history, current_price)
        
        # If volatility is too low, use a minimum value
        min_volatility = kwargs.get('min_volatility', 0.005)  # Minimum 0.5% volatility
        if volatility < min_volatility:
            self.logger.info(f"Using minimum volatility: {min_volatility:.2%} (was {volatility:.2%})")
            volatility = min_volatility
        
        # Calculate position size based on volatility
        # Higher volatility = smaller position
        position_size = (risk_amount / (current_price * volatility)) * self.volatility_factor
        
        # Validate position size
        position_size = self.validate_position_size(position_size, account_balance, current_price)
        
        self.logger.info(
            f"Calculated position size: {position_size:.6f} units "
            f"(volatility: {volatility:.2%}, risking {risk_amount:.2f})"
        )
        
        return position_size
    
    def _calculate_volatility(self, 
                             price_history: Optional[pd.DataFrame], 
                             current_price: float) -> float:
        """
        Calculate market volatility.
        
        Args:
            price_history: DataFrame with historical prices
            current_price: Current price of the asset
            
        Returns:
            float: Volatility as a decimal (e.g., 0.05 for 5%)
        """
        # If no price history is provided, use a default volatility
        if price_history is None or len(price_history) < 2:
            default_volatility = 0.02  # Default 2% volatility
            self.logger.warning(f"No price history provided, using default volatility: {default_volatility:.2%}")
            return default_volatility
        
        try:
            # Make sure we have a 'close' column
            if 'close' not in price_history.columns and 'Close' in price_history.columns:
                price_history = price_history.copy()
                price_history['close'] = price_history['Close']
            
            # Calculate daily returns
            returns = price_history['close'].pct_change().dropna()
            
            # Use only the most recent data points
            if len(returns) > self.volatility_lookback:
                returns = returns.iloc[-self.volatility_lookback:]
            
            # Calculate volatility (standard deviation of returns)
            volatility = returns.std()
            
            # If volatility is NaN, use a default value
            if np.isnan(volatility) or volatility == 0:
                volatility = 0.02  # Default 2% volatility
                self.logger.warning(f"Could not calculate volatility, using default: {volatility:.2%}")
            
            return volatility
        
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return 0.02  # Default 2% volatility


class KellyPositionSizer(PositionSizer):
    """
    Kelly Criterion position sizer.
    
    This strategy uses the Kelly Criterion to determine optimal position size
    based on the probability of winning and the win/loss ratio.
    """
    
    def __init__(self, 
                 max_position_size: float = 0.1, 
                 min_position_size: float = 0.01,
                 kelly_fraction: float = 0.5,  # Use half Kelly for safety
                 risk_logger=None):
        """
        Initialize the Kelly position sizer.
        
        Args:
            max_position_size: Maximum position size as a fraction of account balance (default: 0.1)
            min_position_size: Minimum position size as a fraction of account balance (default: 0.01)
            kelly_fraction: Fraction of the full Kelly to use (default: 0.5)
            risk_logger: Logger for risk management
        """
        super().__init__(max_position_size, min_position_size, risk_logger)
        self.kelly_fraction = kelly_fraction
        self.logger.info(f"Kelly position sizer initialized with {kelly_fraction:.2f} Kelly fraction")
    
    def calculate_position_size(self, 
                               account_balance: float, 
                               current_price: float, 
                               win_probability: float = 0.5,
                               win_loss_ratio: float = 2.0,
                               **kwargs) -> float:
        """
        Calculate the position size using the Kelly Criterion.
        
        Args:
            account_balance: Current account balance
            current_price: Current price of the asset
            win_probability: Probability of a winning trade (default: 0.5)
            win_loss_ratio: Ratio of average win to average loss (default: 2.0)
            **kwargs: Additional parameters
            
        Returns:
            float: Position size in base currency units
        """
        if account_balance <= 0 or current_price <= 0:
            self.logger.warning(f"Invalid account balance ({account_balance}) or price ({current_price})")
            return 0
        
        # Validate win probability
        if win_probability <= 0 or win_probability >= 1:
            self.logger.warning(f"Invalid win probability: {win_probability}, using default 0.5")
            win_probability = 0.5
        
        # Validate win/loss ratio
        if win_loss_ratio <= 0:
            self.logger.warning(f"Invalid win/loss ratio: {win_loss_ratio}, using default 2.0")
            win_loss_ratio = 2.0
        
        # Calculate Kelly percentage
        # Kelly % = (bp - q) / b
        # where:
        # b = odds received on the bet (win/loss ratio)
        # p = probability of winning
        # q = probability of losing (1 - p)
        kelly_pct = (win_probability * win_loss_ratio - (1 - win_probability)) / win_loss_ratio
        
        # Apply Kelly fraction for safety
        kelly_pct *= self.kelly_fraction
        
        # Kelly can be negative if edge is negative
        if kelly_pct <= 0:
            self.logger.warning(
                f"Negative Kelly percentage: {kelly_pct:.2%} "
                f"(win prob: {win_probability:.2%}, win/loss ratio: {win_loss_ratio:.2f})"
            )
            return 0
        
        # Calculate position value
        position_value = account_balance * kelly_pct
        
        # Convert to position size
        position_size = position_value / current_price
        
        # Validate position size
        position_size = self.validate_position_size(position_size, account_balance, current_price)
        
        self.logger.info(
            f"Calculated position size: {position_size:.6f} units "
            f"(Kelly: {kelly_pct:.2%}, win prob: {win_probability:.2%}, win/loss ratio: {win_loss_ratio:.2f})"
        )
        
        return position_size


class PositionSizerFactory:
    """Factory for creating position sizers."""
    
    @staticmethod
    def create_position_sizer(sizer_type: str, **kwargs) -> PositionSizer:
        """
        Create a position sizer of the specified type.
        
        Args:
            sizer_type: Type of position sizer ('fixed_risk', 'volatility', 'kelly')
            **kwargs: Parameters for the position sizer
            
        Returns:
            PositionSizer: Instance of the requested position sizer
        """
        sizer_type = sizer_type.lower()
        
        if sizer_type == 'fixed_risk':
            return FixedRiskPositionSizer(**kwargs)
        elif sizer_type == 'volatility':
            return VolatilityPositionSizer(**kwargs)
        elif sizer_type == 'kelly':
            return KellyPositionSizer(**kwargs)
        else:
            logger.warning(f"Unknown position sizer type: {sizer_type}, using fixed risk")
            return FixedRiskPositionSizer(**kwargs) 