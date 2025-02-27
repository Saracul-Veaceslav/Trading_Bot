"""Module for Binance Testnet exchange interactions."""

import logging
import time
from typing import Dict, Optional, Any

import ccxt
import pandas as pd

from bot.config.settings import SETTINGS


class BinanceTestnet:
    """Handles interactions with Binance Testnet exchange."""
    
    def __init__(self, trading_logger, error_logger):
        """Initialize exchange connection."""
        self.trading_logger = trading_logger
        self.error_logger = error_logger
        self.exchange = self._initialize_exchange()
        self.open_position = None
    
    def _initialize_exchange(self) -> ccxt.binance:
        """Initialize the ccxt exchange object."""
        try:
            exchange = ccxt.binance({
                'apiKey': SETTINGS['API_KEY'],
                'secret': SETTINGS['API_SECRET'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                    'test': SETTINGS['TESTNET'],
                    'adjustForTimeDifference': True,
                }
            })
            
            exchange.set_sandbox_mode(SETTINGS['TESTNET'])
            exchange.fetch_status()
            self.trading_logger.info("Successfully connected to Binance Testnet")
            
            return exchange
            
        except Exception as e:
            self.error_logger.exception(f"Failed to initialize exchange: {str(e)}")
            raise
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Fetch OHLCV data from the exchange."""
        for attempt in range(SETTINGS['MAX_RETRIES']):
            try:
                candles = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                self.trading_logger.debug(f"Fetched {len(df)} candles for {symbol}")
                return df
                
            except Exception as e:
                self.error_logger.error(f"Error fetching OHLCV (attempt {attempt+1}): {str(e)}")
                
                if attempt < SETTINGS['MAX_RETRIES'] - 1:
                    sleep_time = (2 ** attempt) * SETTINGS['ERROR_SLEEP_TIME']
                    self.trading_logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    self.error_logger.exception("Max retries exceeded for fetch_ohlcv")
                    raise
    
    def create_market_order(self, symbol: str, side: str, amount: float) -> Dict[str, Any]:
        """Create a paper market order on Binance Testnet."""
        for attempt in range(SETTINGS['MAX_RETRIES']):
            try:
                # Get current market price
                ticker = self.exchange.fetch_ticker(symbol)
                price = ticker['last']
                
                # Execute market order
                order = self.exchange.create_market_order(symbol, side, amount)
                
                # Log the trade
                self.trading_logger.info(
                    f"{side.upper()} order: {amount} {symbol.split('/')[0]} at ~{price}"
                )
                
                # Update position tracking
                if side == 'buy':
                    self.open_position = {
                        'symbol': symbol,
                        'entry_price': price,
                        'amount': amount,
                        'side': 'long',
                        'entry_time': pd.Timestamp.now(),
                        'order_id': order['id'],
                    }
                    self.trading_logger.info(f"Opened long position at {price}")
                else:  # sell
                    if self.open_position:
                        # Calculate profit/loss
                        entry_price = self.open_position['entry_price']
                        pnl_percent = ((price - entry_price) / entry_price) * 100
                        pnl_absolute = (price - entry_price) * amount
                        
                        self.trading_logger.info(
                            f"Closed position with P&L: {pnl_percent:.2f}% ({pnl_absolute:.6f})"
                        )
                        self.open_position = None
                
                return order
                
            except Exception as e:
                self.error_logger.error(f"Error creating order (attempt {attempt+1}): {str(e)}")
                
                if attempt < SETTINGS['MAX_RETRIES'] - 1:
                    sleep_time = (2 ** attempt) * SETTINGS['ERROR_SLEEP_TIME']
                    self.trading_logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    self.error_logger.exception("Max retries exceeded for create_market_order")
                    raise
    
    def check_stop_loss_take_profit(self, symbol: str) -> Optional[str]:
        """Check if stop-loss or take-profit conditions are met."""
        if not self.open_position:
            return None
            
        # Get current price
        ticker = self.exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Extract position details
        entry_price = self.open_position['entry_price']
        
        # Check stop loss (price below entry - stop loss %)
        stop_price = entry_price * (1 - SETTINGS['STOP_LOSS_PERCENT'])
        if current_price <= stop_price:
            self.trading_logger.info(f"Stop loss triggered at {current_price}")
            return 'stop_loss'
            
        # Check take profit (price above entry + take profit %)
        take_profit_price = entry_price * (1 + SETTINGS['TAKE_PROFIT_PERCENT'])
        if current_price >= take_profit_price:
            self.trading_logger.info(f"Take profit triggered at {current_price}")
            return 'take_profit'
        
        return None
    
    def get_current_price(self, symbol: str) -> float:
        """Get the current price for a symbol."""
        ticker = self.exchange.fetch_ticker(symbol)
        return ticker['last'] 