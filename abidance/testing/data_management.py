from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json

class HistoricalDataManager:
    """Manager for historical market data."""

    def __init__(self, data_dir: str = 'data/historical'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_ohlcv(self, symbol: str, timeframe: str,
                   data: pd.DataFrame) -> None:
        """Save OHLCV data to disk."""
        file_path = self._get_ohlcv_path(symbol, timeframe)
        data.to_parquet(file_path)

    def load_ohlcv(self, symbol: str, timeframe: str,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Load OHLCV data from disk with optional date filtering."""
        file_path = self._get_ohlcv_path(symbol, timeframe)
        if not file_path.exists():
            raise FileNotFoundError(f"No data found for {symbol} {timeframe}")

        data = pd.read_parquet(file_path)

        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]

        return data

    def _get_ohlcv_path(self, symbol: str, timeframe: str) -> Path:
        """
        Get file path for OHLCV data.

        Replaces forward slashes in symbol with underscores to avoid directory issues.
        """
        # Replace forward slashes with underscores to avoid directory issues
        safe_symbol = symbol.replace('/', '_')
        return self.data_dir / f"{safe_symbol}_{timeframe}.parquet"