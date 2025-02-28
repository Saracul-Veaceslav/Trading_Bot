"""
Module for managing trading bot data (OHLCV and trade data).
"""
import os
import json
import pandas as pd
import logging
from datetime import datetime
from Trading_Bot.config.settings import SETTINGS

class DataManager:
    """
    Manages data for the trading bot, including historical price data and trade records.
    """
    
    def __init__(self, trading_logger=None, error_logger=None):
        """
        Initialize the DataManager.
        
        Args:
            trading_logger: Logger for trading activity
            error_logger: Logger for errors
        """
        self.logger = trading_logger if trading_logger else logging.getLogger(__name__)
        self.error_logger = error_logger if error_logger else self.logger
        self.historical_data_path = SETTINGS.get('HISTORICAL_DATA_PATH', 'data/historical')
        self.trades_data_path = SETTINGS.get('TRADES_DATA_PATH', 'data/trades')
        self.historical_trades_path = SETTINGS.get('HISTORICAL_TRADES_PATH', 'data/trades')
        self.initialize_files()
        
    def initialize_files(self):
        """
        Initialize directory structure for data storage.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Create historical data directory if it doesn't exist
            os.makedirs(self.historical_data_path, exist_ok=True)
            self.logger.info(f"Initialized historical data directory: {self.historical_data_path}")
                
            # Create trades data directory if it doesn't exist
            os.makedirs(self.trades_data_path, exist_ok=True)
            self.logger.info(f"Initialized trades data directory: {self.trades_data_path}")
            
            # Create historical trades directory if it doesn't exist
            os.makedirs(self.historical_trades_path, exist_ok=True)
            self.logger.info(f"Initialized historical trades directory: {self.historical_trades_path}")
                
            return True
            
        except Exception as e:
            self.error_logger.error(f"Error initializing data files: {e}")
            return False
    
    def load_latest_ohlcv(self, symbol, interval='1h', limit=500):
        """
        Load the latest OHLCV data for a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT')
            interval (str): Candlestick interval (e.g., '1h', '4h', '1d')
            limit (int): Number of candlesticks to retrieve
            
        Returns:
            pandas.DataFrame: DataFrame with historical data
        """
        try:
            # Format the symbol for filename (replace '/' with '_')
            formatted_symbol = symbol.replace('/', '_')
            file_path = os.path.join(self.historical_data_path, f"{formatted_symbol}_{interval}.csv")
            
            if not os.path.exists(file_path):
                self.logger.warning(f"Historical data file not found: {file_path}")
                return pd.DataFrame()
                
            df = pd.read_csv(file_path)
            
            # Ensure datetime is parsed correctly
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
            # Sort by timestamp and get the most recent data
            df = df.sort_values(by='timestamp', ascending=True)
            
            if limit and len(df) > limit:
                df = df.tail(limit)
                
            return df
            
        except Exception as e:
            self.error_logger.error(f"Error retrieving historical data: {e}")
            return pd.DataFrame()
    
    def get_historical_data(self, symbol, interval, limit=500):
        """
        Get historical OHLCV data from local storage.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            interval (str): Candlestick interval (e.g., '1h', '4h', '1d')
            limit (int): Number of candlesticks to retrieve
            
        Returns:
            pandas.DataFrame: DataFrame with historical data
        """
        # This is an alias for load_latest_ohlcv to maintain backwards compatibility
        return self.load_latest_ohlcv(symbol, interval, limit)
    
    def store_ohlcv_data(self, symbol, interval, data, append=True):
        """
        Store OHLCV data to local storage.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT')
            interval (str): Candlestick interval (e.g., '1h', '4h', '1d')
            data (pandas.DataFrame): DataFrame with OHLCV data
            append (bool): If True, append to existing file; otherwise, overwrite
            
        Returns:
            bool: True if data stored successfully, False otherwise
        """
        try:
            if data is None or data.empty:
                self.logger.warning("No data provided to store")
                return False
            
            # Format the symbol for filename (replace '/' with '_')
            formatted_symbol = symbol.replace('/', '_')
            file_path = os.path.join(self.historical_data_path, f"{formatted_symbol}_{interval}.csv")
            
            # If appending and file exists, load existing data
            if append and os.path.exists(file_path):
                existing_data = pd.read_csv(file_path)
                
                # Ensure timestamp is in datetime format for both DataFrames
                if 'timestamp' in existing_data.columns and 'timestamp' in data.columns:
                    existing_data['timestamp'] = pd.to_datetime(existing_data['timestamp'])
                    data['timestamp'] = pd.to_datetime(data['timestamp'])
                    
                # Merge and remove duplicates
                combined_data = pd.concat([existing_data, data])
                combined_data = combined_data.drop_duplicates(subset=['timestamp'], keep='last')
                
                # Sort by timestamp
                combined_data = combined_data.sort_values(by='timestamp', ascending=True)
                
                # Save combined data
                combined_data.to_csv(file_path, index=False)
            else:
                # Save new data
                data.to_csv(file_path, index=False)
                
            self.logger.info(f"Stored OHLCV data for {symbol} {interval} in {file_path}")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Error storing OHLCV data: {e}")
            return False
    
    def prepare_data_for_strategy(self, df):
        """
        Prepare data for strategy consumption.
        
        Args:
            df (pandas.DataFrame): Raw OHLCV data
            
        Returns:
            pandas.DataFrame: Processed data ready for strategy
        """
        try:
            if df is None or df.empty:
                self.logger.warning("No data provided for preparation")
                return None
                
            # Make a copy to avoid modifying the original
            prepared_df = df.copy()
            
            # Ensure column names are lowercase
            prepared_df.columns = [col.lower() for col in prepared_df.columns]
            
            # Ensure we have required columns
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            # If we have numeric columns without names, try to map them
            if len(prepared_df.columns) >= 6 and not all(col in prepared_df.columns for col in required_columns):
                prepared_df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'] + list(prepared_df.columns[6:])
                
            return prepared_df
            
        except Exception as e:
            self.error_logger.error(f"Error preparing data for strategy: {e}")
            return None
    
    def store_trade(self, trade_data):
        """
        Store trade information.
        
        Args:
            trade_data (dict): Trade details
            
        Returns:
            bool: True if trade stored successfully, False otherwise
        """
        try:
            # Generate a unique trade ID if not provided
            if 'id' not in trade_data:
                trade_data['id'] = datetime.now().strftime("%Y%m%d%H%M%S%f")
                
            # Add timestamp if not provided
            if 'timestamp' not in trade_data:
                trade_data['timestamp'] = datetime.now().isoformat()
            
            # Format the symbol for filename (replace '/' with '_')
            if 'symbol' in trade_data:
                formatted_symbol = trade_data['symbol'].replace('/', '_')
            else:
                formatted_symbol = "unknown_symbol"
                
            # Store in both historical trades (CSV) and detailed trades (JSON)
            # JSON storage for detailed trade information
            json_file_path = os.path.join(self.trades_data_path, f"trades_{formatted_symbol}.json")
            
            # Load existing trades if file exists
            existing_trades = []
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    existing_trades = json.load(f)
                    
            # Add the new trade
            existing_trades.append(trade_data)
            
            # Save the updated trades
            with open(json_file_path, 'w') as f:
                json.dump(existing_trades, f, indent=2)
                
            # CSV storage for historical analysis
            csv_file_path = os.path.join(self.historical_trades_path, "historical_trades.csv")
            
            # Convert the trade to a DataFrame for CSV storage
            trade_df = pd.DataFrame([trade_data])
            
            # Append to existing CSV if it exists
            if os.path.exists(csv_file_path):
                existing_df = pd.read_csv(csv_file_path)
                combined_df = pd.concat([existing_df, trade_df])
                combined_df.to_csv(csv_file_path, index=False)
            else:
                trade_df.to_csv(csv_file_path, index=False)
                
            self.logger.info(f"Stored trade: {trade_data['id']} for {trade_data.get('symbol', 'unknown')}")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Error storing trade: {e}")
            return False
    
    def update_trade_exit(self, trade_id, exit_data):
        """
        Update a trade with exit information.
        
        Args:
            trade_id (str): Unique ID of the trade to update
            exit_data (dict): Exit details (price, time, etc.)
            
        Returns:
            bool: True if trade updated successfully, False otherwise
        """
        try:
            # Find the trade file that might contain this trade
            trade_found = False
            
            for file_name in os.listdir(self.trades_data_path):
                if file_name.startswith("trades_") and file_name.endswith(".json"):
                    file_path = os.path.join(self.trades_data_path, file_name)
                    
                    # Load existing trades
                    with open(file_path, 'r') as f:
                        trades = json.load(f)
                        
                    # Find the trade by ID
                    for i, trade in enumerate(trades):
                        if trade.get('id') == trade_id:
                            # Update the trade with exit data
                            trades[i].update(exit_data)
                            trade_found = True
                            
                            # Save the updated trades
                            with open(file_path, 'w') as f:
                                json.dump(trades, f, indent=2)
                                
                            # Also update the historical trades CSV
                            csv_file_path = os.path.join(self.historical_trades_path, "historical_trades.csv")
                            if os.path.exists(csv_file_path):
                                trades_df = pd.read_csv(csv_file_path)
                                if trade_id in trades_df['id'].values:
                                    for key, value in exit_data.items():
                                        trades_df.loc[trades_df['id'] == trade_id, key] = value
                                    trades_df.to_csv(csv_file_path, index=False)
                            
                            self.logger.info(f"Updated trade exit: {trade_id}")
                            return True
                    
            if not trade_found:
                self.error_logger.error(f"Trade not found for exit update: {trade_id}")
                return False
                
        except Exception as e:
            self.error_logger.error(f"Error updating trade exit: {e}")
            return False
            
        return False
