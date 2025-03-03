#!/usr/bin/env python3
"""
Script to demonstrate how to load and analyze the fetched historical data.

This script shows how to use the PylonStorage system to load the data
and perform basic analysis and visualization.
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from abidance.testing.pylon_storage import PylonStorage

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/data_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_analysis")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Analyze historical trading data')
    
    parser.add_argument('--symbol', type=str, default='XRPUSDT',
                        help='Trading symbol to analyze')
    
    parser.add_argument('--timeframe', type=str, default='1h',
                        help='Timeframe to analyze (e.g., 15m, 1h, 4h, 1d)')
    
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days of historical data to analyze')
    
    parser.add_argument('--start-date', type=str,
                        help='Start date for analysis (format: YYYY-MM-DD)')
    
    parser.add_argument('--end-date', type=str,
                        help='End date for analysis (format: YYYY-MM-DD)')
    
    parser.add_argument('--output-dir', type=str, default='reports',
                        help='Directory to save analysis reports and charts')
    
    return parser.parse_args()

def calculate_indicators(df):
    """Calculate technical indicators for the data."""
    # Calculate SMA
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # Calculate RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Calculate MACD
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['signal']
    
    # Calculate Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * df['bb_std']
    df['bb_lower'] = df['bb_middle'] - 2 * df['bb_std']
    
    return df

def plot_price_and_indicators(df, symbol, timeframe, output_dir):
    """Plot price chart with technical indicators."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Create figure and subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # Plot price and moving averages
    ax1.plot(df.index, df['close'], label='Close Price')
    ax1.plot(df.index, df['sma_20'], label='SMA 20')
    ax1.plot(df.index, df['sma_50'], label='SMA 50')
    ax1.plot(df.index, df['bb_upper'], 'k--', alpha=0.3)
    ax1.plot(df.index, df['bb_lower'], 'k--', alpha=0.3)
    ax1.fill_between(df.index, df['bb_upper'], df['bb_lower'], alpha=0.1, color='gray')
    
    ax1.set_title(f'{symbol} - {timeframe} Chart')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot RSI
    ax2.plot(df.index, df['rsi'], label='RSI')
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.3)
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.3)
    ax2.fill_between(df.index, df['rsi'], 70, where=(df['rsi'] >= 70), color='r', alpha=0.3)
    ax2.fill_between(df.index, df['rsi'], 30, where=(df['rsi'] <= 30), color='g', alpha=0.3)
    
    ax2.set_ylabel('RSI')
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot MACD
    ax3.plot(df.index, df['macd'], label='MACD')
    ax3.plot(df.index, df['signal'], label='Signal')
    ax3.bar(df.index, df['macd_hist'], label='Histogram', alpha=0.5, width=0.01)
    
    ax3.set_xlabel('Date')
    ax3.set_ylabel('MACD')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{symbol}_{timeframe}_analysis.png')
    logger.info(f"Chart saved to {output_dir}/{symbol}_{timeframe}_analysis.png")
    
    return fig

def generate_summary_stats(df, symbol, timeframe):
    """Generate summary statistics for the data."""
    # Calculate daily returns
    df['daily_return'] = df['close'].pct_change()
    
    # Calculate summary statistics
    summary = {
        'symbol': symbol,
        'timeframe': timeframe,
        'start_date': df.index.min(),
        'end_date': df.index.max(),
        'days': (df.index.max() - df.index.min()).days,
        'data_points': len(df),
        'first_price': df['close'].iloc[0],
        'last_price': df['close'].iloc[-1],
        'min_price': df['close'].min(),
        'max_price': df['close'].max(),
        'price_change': df['close'].iloc[-1] - df['close'].iloc[0],
        'price_change_pct': (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100,
        'avg_daily_return': df['daily_return'].mean() * 100,
        'std_daily_return': df['daily_return'].std() * 100,
        'sharpe_ratio': (df['daily_return'].mean() / df['daily_return'].std()) * np.sqrt(365),
        'positive_days': (df['daily_return'] > 0).sum(),
        'negative_days': (df['daily_return'] < 0).sum(),
        'avg_volume': df['volume'].mean(),
    }
    
    return summary

def main():
    """Main function to analyze historical data."""
    args = parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Parse dates
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    elif args.days > 0:
        start_date = datetime.now() - timedelta(days=args.days)
    
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    logger.info(f"Analyzing data for {args.symbol} ({args.timeframe})")
    
    # Initialize the PylonStorage
    pylon = PylonStorage()
    
    try:
        # Load data
        df = pylon.load_dataframe(args.symbol, args.timeframe, start_date, end_date)
        
        if df.empty:
            logger.error(f"No data found for {args.symbol} {args.timeframe}")
            return
        
        logger.info(f"Loaded {len(df)} data points from {df.index.min()} to {df.index.max()}")
        
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Generate summary statistics
        summary = generate_summary_stats(df, args.symbol, args.timeframe)
        
        # Print summary
        logger.info("\nSummary Statistics:")
        for key, value in summary.items():
            logger.info(f"{key}: {value}")
        
        # Plot chart
        fig = plot_price_and_indicators(df, args.symbol, args.timeframe, args.output_dir)
        
        # Save data to CSV
        csv_path = f"{args.output_dir}/{args.symbol}_{args.timeframe}_data.csv"
        df.to_csv(csv_path)
        logger.info(f"Data saved to {csv_path}")
        
        # Save summary to text file
        summary_path = f"{args.output_dir}/{args.symbol}_{args.timeframe}_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(f"Summary Statistics for {args.symbol} ({args.timeframe})\n")
            f.write(f"Generated on {datetime.now()}\n\n")
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
        logger.info(f"Summary saved to {summary_path}")
        
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")
        raise

if __name__ == "__main__":
    main() 