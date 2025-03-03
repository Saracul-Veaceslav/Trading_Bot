"""
Mock exchange implementation for testing.

This module provides a mock exchange implementation that can be used for testing
trading strategies without relying on external services. It simulates the behavior
of a real exchange with deterministic responses.
"""
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime
from abidance.trading.order import OrderType, OrderSide
from abidance.core.domain import Position
from abidance.exchange.protocols import Exchange


class MockExchange(Exchange):
    """Mock exchange implementation for testing."""
    
    def __init__(self, initial_balance: float = 10000.0):
        """
        Initialize the mock exchange.
        
        Args:
            initial_balance: Initial balance for the account
        """
        self.positions: Dict[str, Position] = {}
        self.orders: List[Dict[str, Any]] = []
        self.balance = initial_balance
        self._ohlcv_data: Dict[str, pd.DataFrame] = {}
        self._current_price: Dict[str, float] = {}
        
        # Required by Exchange protocol
        self.exchange_id = "mock"
        self.testnet = True
        self.api_key = None
        self.api_secret = None
    
    def set_ohlcv_data(self, symbol: str, data: pd.DataFrame) -> None:
        """
        Set OHLCV data for a symbol.
        
        Args:
            symbol: The market symbol
            data: DataFrame with OHLCV data
        """
        self._ohlcv_data[symbol] = data.copy()
        
        # Set current price to the last close price
        if not data.empty:
            self._current_price[symbol] = data['close'].iloc[-1]
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, 
                   since: Optional[datetime] = None, 
                   limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetch OHLCV candle data from exchange.
        
        Args:
            symbol: The market symbol
            timeframe: Timeframe interval (e.g., '1m', '1h', '1d')
            since: Starting time
            limit: Maximum number of candles to retrieve
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            ValueError: If no data is available for the symbol
        """
        if symbol not in self._ohlcv_data:
            raise ValueError(f"No data available for symbol {symbol}")
            
        data = self._ohlcv_data[symbol]
        
        # Filter by timestamp if since is provided
        if since is not None:
            data = data[data['timestamp'] >= since]
            
        # Limit the number of records if limit is provided
        if limit is not None:
            data = data.tail(limit)
            
        return data
    
    def create_market_order(self, symbol: str, side: OrderSide, 
                           amount: float) -> Dict[str, Any]:
        """
        Create a market order on the exchange.
        
        Args:
            symbol: The market symbol
            side: Order side (BUY or SELL)
            amount: Order amount
            
        Returns:
            Dictionary with order information
            
        Raises:
            ValueError: If no price data is available for the symbol
        """
        if symbol not in self._current_price:
            raise ValueError(f"No price data available for symbol {symbol}")
            
        price = self._current_price[symbol]
        order_id = f"order_{len(self.orders) + 1}"
        
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'type': OrderType.MARKET,
            'amount': amount,
            'price': price,
            'timestamp': datetime.now(),
            'status': 'closed'
        }
        
        self.orders.append(order)
        
        # Update position and balance
        self._update_position(symbol, side, amount, price)
        
        return order
    
    def _update_position(self, symbol: str, side: OrderSide,
                        amount: float, price: float) -> None:
        """
        Update position and balance after order execution.
        
        Args:
            symbol: The market symbol
            side: Order side (BUY or SELL)
            amount: Order amount
            price: Execution price
        
        Raises:
            ValueError: If trying to sell without an existing position
        """
        if side == OrderSide.BUY:
            # Create or update long position
            if symbol in self.positions:
                existing_pos = self.positions[symbol]
                total_amount = existing_pos.size + amount
                avg_price = (
                    (existing_pos.entry_price * existing_pos.size) +
                    (price * amount)
                ) / total_amount
                
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side=side,
                    entry_price=avg_price,
                    size=total_amount,
                    timestamp=datetime.now()
                )
            else:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side=side,
                    entry_price=price,
                    size=amount,
                    timestamp=datetime.now()
                )
            
            # Update balance
            self.balance -= price * amount
            
        elif side == OrderSide.SELL:
            # Close or reduce position
            if symbol in self.positions:
                existing_pos = self.positions[symbol]
                if existing_pos.size <= amount:
                    # Close position
                    del self.positions[symbol]
                else:
                    # Reduce position
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        side=existing_pos.side,
                        entry_price=existing_pos.entry_price,
                        size=existing_pos.size - amount,
                        timestamp=datetime.now()
                    )
                
                # Update balance
                self.balance += price * amount
            else:
                raise ValueError("Cannot sell without an existing position")
    
    # Implement required Exchange protocol methods
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """Get all available markets/symbols on the exchange."""
        return [{'symbol': symbol} for symbol in self._ohlcv_data.keys()]
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker data for a symbol."""
        if symbol not in self._current_price:
            raise ValueError(f"No price data available for symbol {symbol}")
        
        return {
            'symbol': symbol,
            'last': self._current_price[symbol],
            'timestamp': datetime.now().timestamp()
        }
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
                 since: Optional[datetime] = None, 
                 limit: Optional[int] = None) -> List[List[float]]:
        """Get OHLCV (Open, High, Low, Close, Volume) data."""
        df = self.fetch_ohlcv(symbol, timeframe, since, limit)
        
        # Convert DataFrame to list of lists format
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].values.tolist()
    
    def get_balance(self) -> Dict[str, Dict[str, float]]:
        """Get account balances."""
        return {'total': {'USD': self.balance}}
    
    def place_order(self, order) -> Dict[str, Any]:
        """Place an order on the exchange."""
        return self.create_market_order(order.symbol, order.side, order.quantity)
    
    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an existing order."""
        for i, order in enumerate(self.orders):
            if order['id'] == order_id:
                if order['status'] == 'closed':
                    return {'error': 'Order already executed'}
                
                self.orders[i]['status'] = 'canceled'
                return self.orders[i]
        
        return {'error': 'Order not found'}
    
    def get_order_status(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get the status of an order."""
        for order in self.orders:
            if order['id'] == order_id:
                return order
        
        return {'error': 'Order not found'}
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open orders."""
        open_orders = [order for order in self.orders if order['status'] == 'open']
        
        if symbol:
            open_orders = [order for order in open_orders if order['symbol'] == symbol]
        
        return open_orders 