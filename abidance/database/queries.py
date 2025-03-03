"""
Optimized database queries for the Abidance trading bot.

This module provides optimized query implementations for common database operations.
"""
from typing import Dict, Union
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session



class QueryOptimizer:
    """
    Optimized query implementations for database operations.

    This class provides methods for efficient data retrieval and aggregation
    from the database, using optimized SQL queries and window functions.
    """

    def __init__(self, session: Session):
        """
        Initialize the QueryOptimizer.

        Args:
            session: SQLAlchemy session object
        """
        self._session = session

    def get_trade_statistics(self, symbol: str) -> Dict[str, float]:
        """
        Get aggregated trade statistics for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')

        Returns:
            Dictionary containing trade statistics
        """
        # Using raw SQL with text() to avoid SQLAlchemy func.count() issue
        query = text("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(amount) as total_volume,
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price
            FROM trades
            WHERE symbol = :symbol
        """)

        result = self._session.execute(query, {"symbol": symbol}).first()

        return {
            'total_trades': result.total_trades if result.total_trades else 0,
            'total_volume': result.total_volume if result.total_volume else 0.0,
            'avg_price': result.avg_price if result.avg_price else 0.0,
            'min_price': result.min_price if result.min_price else 0.0,
            'max_price': result.max_price if result.max_price else 0.0
        }

    def get_ohlcv_with_indicators(self, symbol: str,
                                window: int = 14) -> pd.DataFrame:
        """
        Get OHLCV data with pre-calculated technical indicators.

        Uses window functions for efficient indicator calculation directly in SQL.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            window: Lookback window for indicators (default: 14)

        Returns:
            DataFrame containing OHLCV data with indicators
        """
        # Use window functions for efficient indicator calculation
        query = """
        WITH price_changes AS (
            SELECT
                timestamp,
                open,
                high,
                low,
                close,
                volume,
                close - LAG(close) OVER (ORDER BY timestamp) as price_change
            FROM ohlcv
            WHERE symbol = :symbol
        ),
        gains_losses AS (
            SELECT
                timestamp,
                open,
                high,
                low,
                close,
                volume,
                CASE WHEN price_change > 0 THEN price_change ELSE 0 END as gain,
                CASE WHEN price_change < 0 THEN -price_change ELSE 0 END as loss
            FROM price_changes
        )
        SELECT
            o.*,
            AVG(close) OVER (
                ORDER BY timestamp
                ROWS BETWEEN :window-1 PRECEDING AND CURRENT ROW
            ) as sma,
            AVG(gain) OVER (
                ORDER BY timestamp
                ROWS BETWEEN :window-1 PRECEDING AND CURRENT ROW
            ) / NULLIF(
                AVG(loss) OVER (
                    ORDER BY timestamp
                    ROWS BETWEEN :window-1 PRECEDING AND CURRENT ROW
                ), 0
            ) as rsi_ratio
        FROM ohlcv o
        WHERE symbol = :symbol
        ORDER BY timestamp
        """

        result = self._session.execute(text(query), {
            'symbol': symbol,
            'window': window
        })

        return pd.DataFrame(result.fetchall())

    def get_strategy_performance(self, strategy_id: int) -> Dict[str, Union[int, float]]:
        """
        Get performance metrics for a specific strategy.

        Args:
            strategy_id: ID of the strategy

        Returns:
            Dictionary containing performance metrics
        """
        query = """
        WITH trade_results AS (
            SELECT
                id,
                CASE
                    WHEN side = 'BUY' THEN -price * amount
                    WHEN side = 'SELL' THEN price * amount
                END as pnl
            FROM trades
            WHERE strategy_id = :strategy_id
        ),
        trade_stats AS (
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) as total_profit,
                ABS(SUM(CASE WHEN pnl <= 0 THEN pnl ELSE 0 END)) as total_loss
            FROM trade_results
        )
        SELECT
            total_trades,
            winning_trades,
            losing_trades,
            total_profit,
            total_loss,
            CAST(winning_trades AS FLOAT) / NULLIF(total_trades, 0) as win_rate,
            total_profit / NULLIF(total_loss, 0) as profit_factor
        FROM trade_stats
        """

        result = self._session.execute(text(query), {
            'strategy_id': strategy_id
        }).first()

        if not result or not result.total_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_profit': 0.0,
                'total_loss': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0
            }

        return {
            'total_trades': result.total_trades,
            'winning_trades': result.winning_trades,
            'losing_trades': result.losing_trades,
            'total_profit': result.total_profit,
            'total_loss': result.total_loss,
            'win_rate': result.win_rate,
            'profit_factor': result.profit_factor
        }

    def get_aggregated_ohlcv(self, symbol: str, interval: str) -> pd.DataFrame:
        """
        Get OHLCV data aggregated to a specific time interval.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            interval: Time interval for aggregation ('1h', '4h', '1d', etc.)

        Returns:
            DataFrame containing aggregated OHLCV data
        """
        # Map interval to SQLite time format
        interval_format = {
            '1m': '%Y-%m-%d %H:%M',
            '5m': '%Y-%m-%d %H:%M',  # Will need additional filtering
            '15m': '%Y-%m-%d %H:%M',  # Will need additional filtering
            '30m': '%Y-%m-%d %H:%M',  # Will need additional filtering
            '1h': '%Y-%m-%d %H:00',
            '4h': '%Y-%m-%d %H:00',  # Will need additional filtering
            '1d': '%Y-%m-%d',
            '1w': '%Y-%W',
            '1M': '%Y-%m'
        }

        time_format = interval_format.get(interval, '%Y-%m-%d %H:00')

        # For intervals that need additional filtering
        mod_clause = ""
        if interval == '5m':
            mod_clause = "AND CAST(strftime('%M', timestamp) AS INTEGER) % 5 = 0"
        elif interval == '15m':
            mod_clause = "AND CAST(strftime('%M', timestamp) AS INTEGER) % 15 = 0"
        elif interval == '30m':
            mod_clause = "AND CAST(strftime('%M', timestamp) AS INTEGER) % 30 = 0"
        elif interval == '4h':
            mod_clause = "AND CAST(strftime('%H', timestamp) AS INTEGER) % 4 = 0"

        query = f"""
        WITH time_groups AS (
            SELECT
                strftime('{time_format}', timestamp) as interval_timestamp,
                MIN(timestamp) as first_timestamp,
                open,
                high,
                low,
                close,
                volume
            FROM ohlcv
            WHERE symbol = :symbol {mod_clause}
            GROUP BY interval_timestamp
        ),
        aggregated AS (
            SELECT
                interval_timestamp,
                first_timestamp as timestamp,
                FIRST_VALUE(open) OVER (PARTITION BY interval_timestamp ORDER BY first_timestamp) as open,
                MAX(high) OVER (PARTITION BY interval_timestamp) as high,
                MIN(low) OVER (PARTITION BY interval_timestamp) as low,
                LAST_VALUE(close) OVER (
                    PARTITION BY interval_timestamp
                    ORDER BY first_timestamp
                    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) as close,
                SUM(volume) OVER (PARTITION BY interval_timestamp) as volume
            FROM time_groups
        )
        SELECT DISTINCT
            timestamp,
            open,
            high,
            low,
            close,
            volume
        FROM aggregated
        ORDER BY timestamp
        """

        result = self._session.execute(text(query), {
            'symbol': symbol
        })

        return pd.DataFrame(result.fetchall())
