"""Module for managing data storage and retrieval."""

import os
from pathlib import Path
from typing import Dict, Optional, Any

import pandas as pd

from bot.config.settings import SETTINGS


class DataManager:
    """Manages data storage and retrieval for the trading bot."""
    
    def __init__(self, trading_logger, error_logger):
        """Initialize data manager."""
        self.trading_logger = trading_logger
        self.error_logger = error_logger
        
        # Create data directory and initialize files
        Path('data').mkdir(exist_ok=True)
        self._init_files()
    
    def _init_files(self):
        """Initialize data files if they don't exist."""
        # Historical OHLCV data file
        if not os.path.exists(SETTINGS['HISTORICAL_DATA_PATH']):
            cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'strategy_signal']
            pd.DataFrame(columns=cols).to_csv(SETTINGS['HISTORICAL_DATA_PATH'], index=False)
            self.trading_logger.info(f"Created historical data file")
        
        # Historical trades file
        if not os.path.exists(SETTINGS['HISTORICAL_TRADES_PATH']):
            cols = ['timestamp', 'order_id', 'symbol', 'side', 'entry_price', 'exit_price', 
                    'quantity', 'pnl', 'stop_loss_triggered', 'take_profit_triggered']
            pd.DataFrame(columns=cols).to_csv(SETTINGS['HISTORICAL_TRADES_PATH'], index=False)
            self.trading_logger.info(f"Created trades file")
    
    def store_ohlcv_data(self, df: pd.DataFrame, symbol: str, strategy_signal: Optional[int] = None):
        """Store OHLCV data to CSV file, avoiding duplicates."""
        try:
            # Add symbol and signal if needed
            if 'symbol' not in df.columns:
                df['symbol'] = symbol
            if strategy_signal is not None:
                df['strategy_signal'] = strategy_signal
            
            file_path = SETTINGS['HISTORICAL_DATA_PATH']
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                # Read existing data and find new records
                existing_df = pd.read_csv(file_path)
                
                if not pd.api.types.is_datetime64_any_dtype(existing_df['timestamp']):
                    existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
                
                # Find new data
                merged = pd.merge(df, existing_df, on=['timestamp', 'symbol'], how='left', indicator=True)
                new_data = df[merged['_merge'] == 'left_only']
                
                if len(new_data) > 0:
                    new_data.to_csv(file_path, mode='a', header=False, index=False)
                    self.trading_logger.info(f"Stored {len(new_data)} new OHLCV records")
            else:
                df.to_csv(file_path, index=False)
                self.trading_logger.info(f"Stored {len(df)} OHLCV records")
        
        except Exception as e:
            self.error_logger.exception(f"Error storing OHLCV data: {str(e)}")
    
    def load_latest_ohlcv(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Load the latest OHLCV data from the CSV file."""
        try:
            file_path = SETTINGS['HISTORICAL_DATA_PATH']
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                df = pd.read_csv(file_path)
                
                # Filter and sort
                df = df[df['symbol'] == symbol]
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp', ascending=False)
                
                # Return most recent records
                return df.head(limit).sort_values('timestamp')
            
            return pd.DataFrame()
        
        except Exception as e:
            self.error_logger.exception(f"Error loading OHLCV data: {str(e)}")
            return pd.DataFrame()
    
    def store_trade(self, trade_data: Dict[str, Any]):
        """Store trade information to the trades CSV file."""
        try:
            trade_df = pd.DataFrame([trade_data])
            file_path = SETTINGS['HISTORICAL_TRADES_PATH']
            
            trade_df.to_csv(file_path, mode='a', header=False, index=False)
            self.trading_logger.info(f"Trade recorded: {trade_data['side']} {trade_data['quantity']} at {trade_data['entry_price']}")
            
        except Exception as e:
            self.error_logger.exception(f"Error storing trade data: {str(e)}")
    
    def update_trade_exit(self, order_id: str, exit_data: Dict[str, Any]):
        """Update an existing trade record with exit information."""
        try:
            file_path = SETTINGS['HISTORICAL_TRADES_PATH']
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                trades_df = pd.read_csv(file_path)
                trade_idx = trades_df[trades_df['order_id'] == order_id].index
                
                if len(trade_idx) > 0:
                    # Update the trade with exit information
                    for key, value in exit_data.items():
                        trades_df.loc[trade_idx[0], key] = value
                    
                    trades_df.to_csv(file_path, index=False)
                    self.trading_logger.info(f"Updated trade exit for order {order_id} with PnL: {exit_data.get('pnl', 'N/A')}")
                else:
                    self.error_logger.error(f"Trade with order_id {order_id} not found")
            else:
                self.error_logger.error("Trades file not found or empty")
                
        except Exception as e:
            self.error_logger.exception(f"Error updating trade exit: {str(e)}") 