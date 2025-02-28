"""
Risk Management Module

This module provides risk management functionality including position sizing,
stop loss calculation, risk per trade, and overall capital allocation.
"""
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger('trading_bot.risk.manager')

class RiskManager:
    """
    Manages risk parameters for trading operations including position sizing,
    stop losses, and overall risk exposure.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the RiskManager with configuration.
        
        Args:
            config: Configuration dictionary with risk parameters
        """
        self.config = config
        
        # Extract risk parameters with defaults
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.01)  # 1% per trade
        self.max_risk_total = config.get('max_risk_total', 0.05)  # 5% total portfolio
        self.max_open_trades = config.get('max_open_trades', 5)
        self.default_stop_loss_pct = config.get('default_stop_loss_pct', 0.03)  # 3%
        self.use_trailing_stop = config.get('use_trailing_stop', False)
        self.trailing_stop_activation_pct = config.get('trailing_stop_activation_pct', 0.02)  # 2%
        self.trailing_stop_distance_pct = config.get('trailing_stop_distance_pct', 0.015)  # 1.5%
        self.target_profit_pct = config.get('target_profit_pct', 0.05)  # 5%
        self.use_atr_for_stops = config.get('use_atr_for_stops', False)
        self.atr_multiplier = config.get('atr_multiplier', 2.0)
        self.atr_period = config.get('atr_period', 14)
        self.use_dynamic_position_sizing = config.get('use_dynamic_position_sizing', False)
        self.portfolio_heat = config.get('portfolio_heat', 0.5)  # 50% of capital in use max
        self.risk_free_rate = config.get('risk_free_rate', 0.02)  # 2% annual risk-free rate
        self.volatility_lookback = config.get('volatility_lookback', 20)
        
        # Current state of risk exposure
        self.open_positions = {}
        self.total_risk_exposure = 0.0
        
        logger.info(f"Risk Manager initialized with max risk per trade: {self.max_risk_per_trade*100}%, " +
                  f"max risk total: {self.max_risk_total*100}%")
    
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss_price: float, 
                               capital: float, risk_multiplier: float = 1.0) -> float:
        """
        Calculate appropriate position size based on risk parameters.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price
            capital: Available capital
            risk_multiplier: Multiplier to adjust risk (0.5 = half risk, 2.0 = double risk)
            
        Returns:
            Position size to trade
        """
        # Calculate risk per trade in currency units
        risk_amount = capital * self.max_risk_per_trade * risk_multiplier
        
        # Calculate risk per unit (stop distance)
        if entry_price <= 0 or stop_loss_price <= 0:
            logger.warning(f"Invalid prices for position sizing: entry={entry_price}, stop={stop_loss_price}")
            return 0.0
        
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit <= 0:
            logger.warning(f"Zero or negative risk per unit for {symbol}")
            return 0.0
        
        # Calculate position size
        position_size = risk_amount / risk_per_unit
        
        # Apply dynamic position sizing if enabled
        if self.use_dynamic_position_sizing:
            # Could adjust based on volatility, market conditions, etc.
            volatility_factor = self.calculate_volatility_factor(symbol)
            position_size *= volatility_factor
        
        logger.info(f"Calculated position size for {symbol}: {position_size:.6f} units " +
                  f"(risk: ${risk_amount:.2f}, risk per unit: ${risk_per_unit:.2f})")
        
        return position_size
    
    def calculate_volatility_factor(self, symbol: str) -> float:
        """
        Calculate a volatility adjustment factor for position sizing.
        Higher volatility = lower position size.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Volatility adjustment factor (typically 0.5-1.5)
        """
        # Placeholder - in a real implementation, this would analyze recent price data
        # Could calculate based on ATR, standard deviation of returns, etc.
        # For now, just return 1.0 (neutral)
        return 1.0
    
    def calculate_stop_loss(self, symbol: str, entry_price: float, 
                           side: str, ohlcv_data: Optional[pd.DataFrame] = None) -> float:
        """
        Calculate stop loss price based on risk parameters.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the trade
            side: Trade side ('buy' or 'sell')
            ohlcv_data: Optional OHLCV data for ATR-based calculation
            
        Returns:
            Stop loss price
        """
        if self.use_atr_for_stops and ohlcv_data is not None and len(ohlcv_data) > self.atr_period:
            # Calculate ATR
            atr = self.calculate_atr(ohlcv_data, self.atr_period)
            
            # Calculate stop distance based on ATR
            stop_distance = atr * self.atr_multiplier
            
            if side.lower() == 'buy':
                stop_price = entry_price - stop_distance
            else:
                stop_price = entry_price + stop_distance
                
            logger.info(f"Calculated ATR-based stop loss for {symbol}: {stop_price:.8f} " +
                      f"(ATR: {atr:.8f}, distance: {stop_distance:.8f})")
        else:
            # Use percentage-based stop loss
            if side.lower() == 'buy':
                stop_price = entry_price * (1 - self.default_stop_loss_pct)
            else:
                stop_price = entry_price * (1 + self.default_stop_loss_pct)
                
            logger.info(f"Calculated percentage-based stop loss for {symbol}: {stop_price:.8f} " +
                      f"({self.default_stop_loss_pct*100:.1f}% from entry)")
                
        return stop_price
    
    def calculate_take_profit(self, symbol: str, entry_price: float, 
                             side: str, risk_reward_ratio: float = 2.0) -> float:
        """
        Calculate take profit price based on risk parameters.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the trade
            side: Trade side ('buy' or 'sell')
            risk_reward_ratio: Desired risk:reward ratio (default 2.0)
            
        Returns:
            Take profit price
        """
        # Calculate stop loss first (for risk distance)
        stop_loss = self.calculate_stop_loss(symbol, entry_price, side)
        
        # Calculate risk distance
        risk_distance = abs(entry_price - stop_loss)
        
        # Calculate reward distance based on risk-reward ratio
        reward_distance = risk_distance * risk_reward_ratio
        
        # Calculate take profit price
        if side.lower() == 'buy':
            take_profit = entry_price + reward_distance
        else:
            take_profit = entry_price - reward_distance
            
        logger.info(f"Calculated take profit for {symbol}: {take_profit:.8f} " +
                  f"(R:R ratio: {risk_reward_ratio:.1f})")
            
        return take_profit
    
    def calculate_atr(self, ohlcv_data: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range (ATR) from OHLCV data.
        
        Args:
            ohlcv_data: DataFrame with OHLCV data
            period: ATR period
            
        Returns:
            ATR value
        """
        if len(ohlcv_data) < period + 1:
            logger.warning(f"Not enough data for ATR calculation ({len(ohlcv_data)} < {period+1})")
            return 0.0
        
        # Ensure we have high, low, close columns
        required_columns = ['high', 'low', 'close']
        if not all(col in ohlcv_data.columns for col in required_columns):
            logger.error(f"OHLCV data missing required columns for ATR calculation")
            return 0.0
            
        # Calculate true range
        tr1 = ohlcv_data['high'] - ohlcv_data['low']
        tr2 = abs(ohlcv_data['high'] - ohlcv_data['close'].shift(1))
        tr3 = abs(ohlcv_data['low'] - ohlcv_data['close'].shift(1))
        
        # True range is the max of the three
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR (simple average for this implementation)
        atr = tr.rolling(period).mean().iloc[-1]
        
        return atr
    
    def update_trailing_stop(self, symbol: str, current_price: float, 
                            side: str, current_stop: float) -> float:
        """
        Update trailing stop price if conditions are met.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            side: Trade side ('buy' or 'sell')
            current_stop: Current stop loss price
            
        Returns:
            Updated stop loss price
        """
        if not self.use_trailing_stop:
            return current_stop
            
        if side.lower() == 'buy':
            # For long positions
            # Calculate the activation threshold
            activation_threshold = self.open_positions[symbol]['entry_price'] * (1 + self.trailing_stop_activation_pct)
            
            # If price has moved up enough, activate or update trailing stop
            if current_price >= activation_threshold:
                # Calculate new stop based on trailing distance
                new_stop = current_price * (1 - self.trailing_stop_distance_pct)
                
                # Only move stop up, never down
                if new_stop > current_stop:
                    logger.info(f"Updating trailing stop for {symbol} from {current_stop:.8f} to {new_stop:.8f}")
                    return new_stop
        else:
            # For short positions
            # Calculate the activation threshold
            activation_threshold = self.open_positions[symbol]['entry_price'] * (1 - self.trailing_stop_activation_pct)
            
            # If price has moved down enough, activate or update trailing stop
            if current_price <= activation_threshold:
                # Calculate new stop based on trailing distance
                new_stop = current_price * (1 + self.trailing_stop_distance_pct)
                
                # Only move stop down, never up
                if new_stop < current_stop:
                    logger.info(f"Updating trailing stop for {symbol} from {current_stop:.8f} to {new_stop:.8f}")
                    return new_stop
        
        # No update needed
        return current_stop
    
    def register_position(self, symbol: str, entry_price: float, 
                         position_size: float, side: str, 
                         stop_loss: float, take_profit: float) -> None:
        """
        Register a new position with the risk manager.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            position_size: Position size
            side: Trade side ('buy' or 'sell')
            stop_loss: Stop loss price
            take_profit: Take profit price
        """
        # Calculate risk for this position
        risk_amount = position_size * abs(entry_price - stop_loss)
        
        # Add to open positions
        self.open_positions[symbol] = {
            'entry_price': entry_price,
            'position_size': position_size,
            'side': side,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_amount': risk_amount,
            'entry_time': datetime.now(),
            'max_price': entry_price if side.lower() == 'buy' else float('-inf'),
            'min_price': entry_price if side.lower() == 'sell' else float('inf')
        }
        
        # Update total risk exposure
        self.total_risk_exposure += risk_amount
        
        logger.info(f"Registered {side} position for {symbol}: size={position_size}, " +
                  f"entry={entry_price:.8f}, stop={stop_loss:.8f}, tp={take_profit:.8f}")
        logger.info(f"Total risk exposure now: ${self.total_risk_exposure:.2f}")
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Close a position and update risk metrics.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position information or empty dict if not found
        """
        if symbol not in self.open_positions:
            logger.warning(f"Attempted to close non-existent position for {symbol}")
            return {}
            
        position = self.open_positions.pop(symbol)
        
        # Update total risk exposure
        self.total_risk_exposure -= position.get('risk_amount', 0)
        
        logger.info(f"Closed position for {symbol}: {position['side']}, " +
                  f"size={position['position_size']}, entry={position['entry_price']:.8f}")
        logger.info(f"Total risk exposure now: ${self.total_risk_exposure:.2f}")
        
        return position
    
    def update_position(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """
        Update a position's metrics including trailing stops.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            
        Returns:
            Updated position information or empty dict if not found
        """
        if symbol not in self.open_positions:
            return {}
            
        position = self.open_positions[symbol]
        
        # Update max/min price seen
        if position['side'].lower() == 'buy':
            position['max_price'] = max(position['max_price'], current_price)
        else:
            position['min_price'] = min(position['min_price'], current_price)
            
        # Update trailing stop if applicable
        position['stop_loss'] = self.update_trailing_stop(
            symbol, current_price, position['side'], position['stop_loss']
        )
        
        # Store updated position
        self.open_positions[symbol] = position
        
        return position
    
    def check_stop_hit(self, symbol: str, current_price: float) -> bool:
        """
        Check if current price has hit the stop loss level.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            
        Returns:
            True if stop loss is hit, False otherwise
        """
        if symbol not in self.open_positions:
            return False
            
        position = self.open_positions[symbol]
        
        if position['side'].lower() == 'buy':
            # For long positions, stop is hit if price falls below stop level
            if current_price <= position['stop_loss']:
                logger.info(f"Stop loss hit for {symbol} long position at {current_price:.8f}")
                return True
        else:
            # For short positions, stop is hit if price rises above stop level
            if current_price >= position['stop_loss']:
                logger.info(f"Stop loss hit for {symbol} short position at {current_price:.8f}")
                return True
                
        return False
    
    def check_take_profit_hit(self, symbol: str, current_price: float) -> bool:
        """
        Check if current price has hit the take profit level.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            
        Returns:
            True if take profit is hit, False otherwise
        """
        if symbol not in self.open_positions:
            return False
            
        position = self.open_positions[symbol]
        
        if position['side'].lower() == 'buy':
            # For long positions, TP is hit if price rises above TP level
            if current_price >= position['take_profit']:
                logger.info(f"Take profit hit for {symbol} long position at {current_price:.8f}")
                return True
        else:
            # For short positions, TP is hit if price falls below TP level
            if current_price <= position['take_profit']:
                logger.info(f"Take profit hit for {symbol} short position at {current_price:.8f}")
                return True
                
        return False
    
    def calculate_risk_metrics(self) -> Dict[str, float]:
        """
        Calculate overall risk metrics for the portfolio.
        
        Returns:
            Dict with risk metrics (total exposure, sharp ratio, etc.)
        """
        metrics = {
            'total_risk_exposure': self.total_risk_exposure,
            'open_positions_count': len(self.open_positions),
            'max_risk_allowed': self.max_risk_total,
            'risk_utilization': self.total_risk_exposure / self.max_risk_total if self.max_risk_total > 0 else 0.0,
        }
        
        logger.debug(f"Risk metrics: {metrics}")
        
        return metrics
    
    def can_open_position(self, symbol: str, risk_amount: float) -> bool:
        """
        Check if a new position can be opened within risk limits.
        
        Args:
            symbol: Trading symbol
            risk_amount: Amount at risk for the new position
            
        Returns:
            True if position can be opened, False otherwise
        """
        # Check if symbol already has an open position
        if symbol in self.open_positions:
            logger.warning(f"Position already exists for {symbol}")
            return False
            
        # Check if max open trades limit is reached
        if len(self.open_positions) >= self.max_open_trades:
            logger.warning(f"Max open trades limit reached ({self.max_open_trades})")
            return False
            
        # Check if adding this position would exceed total risk limit
        new_total_risk = self.total_risk_exposure + risk_amount
        if new_total_risk > self.max_risk_total:
            logger.warning(f"New position would exceed total risk limit: {new_total_risk:.2f} > {self.max_risk_total:.2f}")
            return False
            
        return True
    
    def get_position_status(self, symbol: str) -> Dict[str, Any]:
        """
        Get current status of a position.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position information or empty dict if not found
        """
        return self.open_positions.get(symbol, {}) 