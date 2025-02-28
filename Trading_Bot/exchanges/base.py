"""
Exchange Base Class

This module provides the base class for exchange integrations.
All exchange adapters should inherit from this class.
"""
import logging
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
import time
from datetime import datetime
import pandas as pd

logger = logging.getLogger('trading_bot.exchanges.base')

class Exchange(ABC):
    """
    Base class for all exchange adapters.
    Defines common functionality and interface for exchange operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the exchange with configuration.
        
        Args:
            config: Exchange configuration including API keys, settings
        """
        self.name = "base"
        self.config = config
        self.api = None
        self.markets = {}
        self.symbols = []
        self.rate_limits = {}
        self.last_api_call = {}
        self.is_test_mode = config.get('test_mode', False)
        
        # Logging setup
        self.logger = logging.getLogger(f'trading_bot.exchanges.{self.name}')
        
        logger.info(f"Initialized base exchange class")
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize exchange connection and load market data.
        Should be called after instantiation.
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Close all connections and release resources."""
        pass
    
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, 
                   start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None,
                   limit: int = 1000) -> List[List[Any]]:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) candle data.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe ('1m', '1h', '1d', etc.)
            start_time: Start time for candles
            end_time: End time for candles
            limit: Maximum number of candles to fetch
            
        Returns:
            List of OHLCV candles
        """
        pass
    
    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current ticker information for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict with ticker information
        """
        pass
    
    @abstractmethod
    def fetch_balance(self) -> Dict[str, Any]:
        """
        Fetch account balance.
        
        Returns:
            Dict with balance information
        """
        pass
    
    @abstractmethod
    def create_order(self, symbol: str, order_type: str, side: str, 
                    amount: float, price: Optional[float] = None,
                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a trading order.
        
        Args:
            symbol: Trading symbol
            order_type: Type of order ('limit', 'market')
            side: Order side ('buy' or 'sell')
            amount: Amount to buy/sell
            price: Price for limit orders
            params: Additional parameters
            
        Returns:
            Dict with order information
        """
        pass
    
    @abstractmethod
    def fetch_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch information about an order.
        
        Args:
            order_id: Order ID
            symbol: Trading symbol
            
        Returns:
            Dict with order information
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID
            symbol: Trading symbol
            
        Returns:
            Dict with cancellation information
        """
        pass
    
    @abstractmethod
    def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch open orders.
        
        Args:
            symbol: Trading symbol or None for all symbols
            
        Returns:
            List of open orders
        """
        pass
    
    def has_symbol(self, symbol: str) -> bool:
        """
        Check if a symbol is supported by the exchange.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if supported, False otherwise
        """
        return symbol in self.symbols
    
    def format_symbol(self, base: str, quote: str) -> str:
        """
        Format a symbol according to exchange requirements.
        
        Args:
            base: Base currency
            quote: Quote currency
            
        Returns:
            Formatted symbol
        """
        return f"{base}/{quote}"
    
    def get_min_order_amount(self, symbol: str) -> float:
        """
        Get the minimum order amount for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Minimum order amount
        """
        if symbol in self.markets:
            return self.markets[symbol].get('limits', {}).get('amount', {}).get('min', 0.0)
        return 0.0
    
    def get_min_price(self, symbol: str) -> float:
        """
        Get the minimum price for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Minimum price
        """
        if symbol in self.markets:
            return self.markets[symbol].get('limits', {}).get('price', {}).get('min', 0.0)
        return 0.0
    
    def _throttle_api_call(self, endpoint: str, limit_ms: int = 1000) -> None:
        """
        Throttle API calls to avoid hitting rate limits.
        
        Args:
            endpoint: API endpoint name
            limit_ms: Minimum time between calls in milliseconds
        """
        current_time = time.time() * 1000  # Convert to milliseconds
        if endpoint in self.last_api_call:
            elapsed = current_time - self.last_api_call[endpoint]
            if elapsed < limit_ms:
                sleep_time = (limit_ms - elapsed) / 1000.0
                logger.debug(f"Rate limiting {endpoint}, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.last_api_call[endpoint] = time.time() * 1000
    
    def convert_to_dataframe(self, ohlcv_data: List[List[Any]]) -> pd.DataFrame:
        """
        Convert OHLCV data to pandas DataFrame.
        
        Args:
            ohlcv_data: List of OHLCV data from exchange
            
        Returns:
            DataFrame with OHLCV data
        """
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    
    def get_precision(self, symbol: str, price_or_amount: str = 'price') -> int:
        """
        Get the precision for a symbol's price or amount.
        
        Args:
            symbol: Trading symbol
            price_or_amount: 'price' or 'amount'
            
        Returns:
            Decimal precision
        """
        if symbol not in self.markets:
            return 8  # Default to 8 decimal places
        
        if price_or_amount == 'price':
            return self.markets[symbol].get('precision', {}).get('price', 8)
        else:
            return self.markets[symbol].get('precision', {}).get('amount', 8)
    
    def calculate_fee(self, symbol: str, order_type: str, 
                     side: str, amount: float, price: float) -> float:
        """
        Calculate the fee for an order.
        
        Args:
            symbol: Trading symbol
            order_type: Type of order
            side: Order side ('buy' or 'sell')
            amount: Amount to buy/sell
            price: Price for order
            
        Returns:
            Fee amount
        """
        # Default implementation using standard fee rate
        # Specific exchanges should override with their fee structure
        standard_fee_rate = 0.001  # 0.1% default fee
        
        if symbol in self.markets:
            fee_structure = self.markets[symbol].get('fees', {})
            if order_type == 'limit':
                fee_rate = fee_structure.get('maker', standard_fee_rate)
            else:
                fee_rate = fee_structure.get('taker', standard_fee_rate)
        else:
            fee_rate = standard_fee_rate
        
        return amount * price * fee_rate
    
    def validate_order(self, symbol: str, order_type: str, 
                      side: str, amount: float, price: Optional[float] = None) -> bool:
        """
        Validate an order before submitting.
        
        Args:
            symbol: Trading symbol
            order_type: Type of order
            side: Order side
            amount: Amount to buy/sell
            price: Price for limit orders
            
        Returns:
            True if valid, False otherwise
        """
        if not self.has_symbol(symbol):
            logger.error(f"Symbol {symbol} not supported")
            return False
        
        min_amount = self.get_min_order_amount(symbol)
        if amount < min_amount:
            logger.error(f"Order amount {amount} below minimum {min_amount}")
            return False
        
        if order_type == 'limit' and price is not None:
            min_price = self.get_min_price(symbol)
            if price < min_price:
                logger.error(f"Order price {price} below minimum {min_price}")
                return False
        
        return True 