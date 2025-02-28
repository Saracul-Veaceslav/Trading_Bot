"""
Binance Exchange Adapter

This module provides integration with the Binance cryptocurrency exchange.
"""
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import pandas as pd
import math

# Import the Exchange base class
from trading_bot.exchanges.base import Exchange

# Initialize logger
logger = logging.getLogger('trading_bot.exchanges.binance')

class BinanceExchange(Exchange):
    """
    Binance exchange adapter implementing the Exchange interface.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Binance exchange adapter.
        
        Args:
            config: Configuration dictionary with Binance API credentials and settings
        """
        super().__init__(config)
        self.name = "binance"
        self.rate_limit_per_minute = 1200  # Default rate limit for Binance
        
        # Define API credentials
        self.api_key = config.get('api_key', '')
        self.api_secret = config.get('api_secret', '')
        
        # Set test mode
        self.testnet = config.get('testnet', False)
        
        # Define endpoint URLs
        self.base_url = "https://api.binance.com" if not self.testnet else "https://testnet.binance.vision"
        
        logger.info(f"Initialized Binance exchange adapter (testnet: {self.testnet})")
    
    def initialize(self) -> None:
        """
        Initialize the Binance API connection and load market data.
        """
        try:
            # Try to import ccxt library dynamically
            try:
                import ccxt
            except ImportError:
                logger.error("CCXT library is required for Binance exchange. Install using 'pip install ccxt'")
                raise ImportError("CCXT library not found")
            
            # Initialize the CCXT Binance client
            binance_params = {
                'enableRateLimit': True
            }
            
            if self.testnet:
                binance_params['options'] = {'defaultType': 'future'}
                self.api = ccxt.binanceusdm({
                    'apiKey': self.api_key,
                    'secret': self.api_secret,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'future'},
                })
                self.api.set_sandbox_mode(True)
            else:
                if self.config.get('futures', False):
                    self.api = ccxt.binanceusdm({
                        'apiKey': self.api_key,
                        'secret': self.api_secret,
                        'enableRateLimit': True,
                    })
                else:
                    self.api = ccxt.binance({
                        'apiKey': self.api_key,
                        'secret': self.api_secret,
                        'enableRateLimit': True,
                    })
            
            # Load markets
            self.markets = self.api.load_markets()
            self.symbols = list(self.markets.keys())
            
            # Extract rate limits
            self.rate_limits = self.api.describe().get('rateLimit', 1000)
            
            logger.info(f"Binance exchange initialized successfully with {len(self.symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Failed to initialize Binance exchange: {str(e)}")
            raise
    
    def shutdown(self) -> None:
        """Close all connections and release resources."""
        self.api = None
        logger.info("Binance exchange connection closed")
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, 
                   start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None,
                   limit: int = 1000) -> List[List[Any]]:
        """
        Fetch OHLCV candle data from Binance.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe ('1m', '1h', '1d', etc.)
            start_time: Start time for candles
            end_time: End time for candles
            limit: Maximum number of candles to fetch
            
        Returns:
            List of OHLCV candles
        """
        self._throttle_api_call('fetch_ohlcv')
        
        try:
            params = {}
            if start_time:
                # Convert to milliseconds timestamp
                params['since'] = int(start_time.timestamp() * 1000)
            
            # Fetch the data
            ohlcv = self.api.fetch_ohlcv(symbol, timeframe, params=params, limit=limit)
            
            # Filter by end_time if specified
            if end_time:
                end_ms = int(end_time.timestamp() * 1000)
                ohlcv = [candle for candle in ohlcv if candle[0] <= end_ms]
            
            logger.debug(f"Fetched {len(ohlcv)} {timeframe} candles for {symbol}")
            return ohlcv
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV data for {symbol}: {str(e)}")
            return []
    
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current ticker information for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict with ticker information
        """
        self._throttle_api_call('fetch_ticker')
        
        try:
            ticker = self.api.fetch_ticker(symbol)
            logger.debug(f"Fetched ticker for {symbol}: {ticker['last']}")
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {str(e)}")
            return {}
    
    def fetch_balance(self) -> Dict[str, Any]:
        """
        Fetch account balance from Binance.
        
        Returns:
            Dict with balance information
        """
        self._throttle_api_call('fetch_balance')
        
        try:
            balance = self.api.fetch_balance()
            logger.debug(f"Fetched account balance: {len(balance)} currencies")
            return balance
        except Exception as e:
            logger.error(f"Error fetching account balance: {str(e)}")
            return {}
    
    def create_order(self, symbol: str, order_type: str, side: str, 
                    amount: float, price: Optional[float] = None,
                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a trading order on Binance.
        
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
        if not self.validate_order(symbol, order_type, side, amount, price):
            raise ValueError(f"Invalid order parameters for {symbol}")
        
        # Skip actual order creation in test mode
        if self.is_test_mode:
            logger.info(f"TEST MODE: Would create {order_type} {side} order for {amount} {symbol} at price {price}")
            
            # Return a mock order structure
            import time
            order_id = f"test_{int(time.time() * 1000)}"
            return {
                'id': order_id,
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'amount': amount,
                'price': price if price else 0.0,
                'status': 'open',
                'timestamp': int(time.time() * 1000),
                'datetime': datetime.now().isoformat(),
                'fee': None,
                'cost': amount * (price if price else 0.0),
                'filled': 0.0,
                'remaining': amount,
                'info': {'test': True},
            }
        
        self._throttle_api_call('create_order')
        
        try:
            if params is None:
                params = {}
            
            order = self.api.create_order(symbol, order_type, side, amount, price, params)
            logger.info(f"Created {order_type} {side} order for {amount} {symbol}" + 
                         (f" at price {price}" if price else ""))
            return order
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise
    
    def fetch_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch information about an order from Binance.
        
        Args:
            order_id: Order ID
            symbol: Trading symbol (required by Binance)
            
        Returns:
            Dict with order information
        """
        if self.is_test_mode and order_id.startswith('test_'):
            logger.info(f"TEST MODE: Would fetch test order {order_id}")
            return {
                'id': order_id,
                'symbol': symbol,
                'status': 'closed',
                'filled': 1.0,
                'remaining': 0.0,
                'info': {'test': True},
            }
        
        if symbol is None:
            raise ValueError("Symbol is required for Binance fetch_order")
        
        self._throttle_api_call('fetch_order')
        
        try:
            order = self.api.fetch_order(order_id, symbol)
            logger.debug(f"Fetched order {order_id} for {symbol}: {order['status']}")
            return order
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            raise
    
    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an order on Binance.
        
        Args:
            order_id: Order ID
            symbol: Trading symbol (required by Binance)
            
        Returns:
            Dict with cancellation information
        """
        if self.is_test_mode and order_id.startswith('test_'):
            logger.info(f"TEST MODE: Would cancel test order {order_id}")
            return {
                'id': order_id,
                'symbol': symbol,
                'status': 'canceled',
                'info': {'test': True},
            }
        
        if symbol is None:
            raise ValueError("Symbol is required for Binance cancel_order")
        
        self._throttle_api_call('cancel_order')
        
        try:
            result = self.api.cancel_order(order_id, symbol)
            logger.info(f"Cancelled order {order_id} for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {str(e)}")
            raise
    
    def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch open orders from Binance.
        
        Args:
            symbol: Trading symbol or None for all symbols
            
        Returns:
            List of open orders
        """
        if self.is_test_mode:
            logger.info(f"TEST MODE: Would fetch open orders for {symbol if symbol else 'all symbols'}")
            return []
        
        self._throttle_api_call('fetch_open_orders')
        
        try:
            orders = self.api.fetch_open_orders(symbol)
            logger.debug(f"Fetched {len(orders)} open orders" + 
                         (f" for {symbol}" if symbol else ""))
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {str(e)}")
            raise
    
    def fetch_closed_orders(self, symbol: Optional[str] = None, 
                           since: Optional[int] = None, 
                           limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch closed orders from Binance.
        
        Args:
            symbol: Trading symbol (required by Binance)
            since: Timestamp in ms to fetch orders from
            limit: Maximum number of orders to fetch
            
        Returns:
            List of closed orders
        """
        if symbol is None:
            raise ValueError("Symbol is required for Binance fetch_closed_orders")
        
        if self.is_test_mode:
            logger.info(f"TEST MODE: Would fetch closed orders for {symbol}")
            return []
        
        self._throttle_api_call('fetch_closed_orders')
        
        try:
            params = {}
            if since:
                params['since'] = since
            if limit:
                params['limit'] = limit
                
            orders = self.api.fetch_closed_orders(symbol, params=params)
            logger.debug(f"Fetched {len(orders)} closed orders for {symbol}")
            return orders
        except Exception as e:
            logger.error(f"Error fetching closed orders: {str(e)}")
            raise
            
    def get_server_time(self) -> int:
        """
        Get the server time from Binance.
        
        Returns:
            Server time in milliseconds
        """
        try:
            time_info = self.api.public_get_time()
            return time_info['serverTime']
        except Exception as e:
            logger.error(f"Error getting server time: {str(e)}")
            return int(time.time() * 1000)
            
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get exchange information from Binance.
        
        Returns:
            Dict with exchange information
        """
        try:
            return self.api.public_get_exchangeinfo()
        except Exception as e:
            logger.error(f"Error getting exchange info: {str(e)}")
            return {} 