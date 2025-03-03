#!/usr/bin/env python3
"""
Script to fetch historical trading data from Binance.

This script uses the BinanceDataFetcher class to fetch historical OHLCV data
for specified symbols and timeframes, and stores it using the PylonStorage system.
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
import os

from abidance.testing.binance_data_fetcher import BinanceDataFetcher
from abidance.testing.pylon_storage import PylonStorage

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/data_fetcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_fetcher")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Fetch historical trading data from Binance')
    
    parser.add_argument('--symbols', type=str, nargs='+', 
                        default=['XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT', 'DOTUSDT'],
                        help='Trading symbols to fetch data for')
    
    parser.add_argument('--timeframes', type=str, nargs='+', 
                        default=['1h'],
                        help='Timeframes to fetch (e.g., 15m, 1h, 4h, 1d)')
    
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days of historical data to fetch')
    
    parser.add_argument('--start-date', type=str,
                        help='Start date for data fetching (format: YYYY-MM-DD)')
    
    parser.add_argument('--end-date', type=str,
                        help='End date for data fetching (format: YYYY-MM-DD)')
    
    parser.add_argument('--use-pagination', action='store_true',
                        help='Use pagination for fetching large date ranges')
    
    parser.add_argument('--parallel', action='store_true',
                        help='Fetch data for multiple symbols in parallel')
    
    parser.add_argument('--max-workers', type=int, default=5,
                        help='Maximum number of parallel workers when using --parallel')
    
    parser.add_argument('--data-dir', type=str, default='data/pylon',
                        help='Directory to store the fetched data')
    
    return parser.parse_args()

def main():
    """Main function to fetch historical data."""
    args = parse_args()
    
    # Create data directory if it doesn't exist
    Path(args.data_dir).mkdir(parents=True, exist_ok=True)
    
    # Parse dates
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    elif args.days > 0:
        start_date = datetime.now() - timedelta(days=args.days)
    
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    logger.info(f"Fetching data for symbols: {args.symbols}")
    logger.info(f"Timeframes: {args.timeframes}")
    logger.info(f"Date range: {start_date} to {end_date}")
    
    # Initialize the data fetcher
    pylon_storage = PylonStorage(base_path=args.data_dir)
    fetcher = BinanceDataFetcher()
    
    # Fetch data for each symbol and timeframe
    for timeframe in args.timeframes:
        logger.info(f"Fetching {timeframe} data...")
        
        if args.parallel:
            logger.info(f"Using parallel fetching with {args.max_workers} workers")
            results = fetcher.fetch_multiple_symbols_parallel(
                symbols=args.symbols,
                timeframe=timeframe,
                max_workers=args.max_workers,
                start_date=start_date,
                end_date=end_date,
                use_pagination=args.use_pagination,
                use_pylon=True
            )
            
            # Log results
            for symbol, df in results.items():
                if df.empty:
                    logger.warning(f"No data fetched for {symbol} {timeframe}")
                else:
                    logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
        else:
            for symbol in args.symbols:
                logger.info(f"Fetching data for {symbol} {timeframe}...")
                try:
                    df = fetcher.fetch_historical_data(
                        symbol=symbol,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date,
                        use_pagination=args.use_pagination,
                        use_pylon=True
                    )
                    
                    if df.empty:
                        logger.warning(f"No data fetched for {symbol} {timeframe}")
                    else:
                        logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
                        
                        # Store the data using PylonStorage
                        pylon_storage.store_dataframe(df, symbol, timeframe)
                        
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol} {timeframe}: {e}")
    
    # Print summary of available data
    logger.info("\nData fetching complete. Available datasets:")
    for symbol in args.symbols:
        for timeframe in args.timeframes:
            try:
                info = pylon_storage.get_dataset_info(symbol, timeframe)
                logger.info(f"{symbol} {timeframe}: {info['row_count']} candles from {info['min_date']} to {info['max_date']}")
            except FileNotFoundError:
                logger.warning(f"No dataset found for {symbol} {timeframe}")

if __name__ == "__main__":
    main() 