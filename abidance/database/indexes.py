"""
Database index definitions for query optimization.

This module defines indexes for the database tables to optimize query performance.
"""
from sqlalchemy import Index, text

from abidance.database.models import Trade, OHLCV, Strategy


def create_indexes(engine):
    """
    Create all indexes for optimized query performance.

    Args:
        engine: SQLAlchemy engine instance
    """
    # Trade indexes
    trade_timestamp_idx = Index('idx_trade_timestamp', Trade.timestamp)
    trade_symbol_timestamp_idx = Index('idx_trade_symbol_timestamp',
                                      Trade.symbol, Trade.timestamp)
    trade_strategy_timestamp_idx = Index('idx_trade_strategy_timestamp',
                                        Trade.strategy_id, Trade.timestamp)

    # OHLCV indexes
    ohlcv_timestamp_idx = Index('idx_ohlcv_timestamp', OHLCV.timestamp)
    ohlcv_symbol_timestamp_idx = Index('idx_ohlcv_symbol_timestamp',
                                      OHLCV.symbol, OHLCV.timestamp)

    # Strategy indexes
    strategy_name_idx = Index('idx_strategy_name', Strategy.name)

    # Create all indexes
    indexes = [
        trade_timestamp_idx,
        trade_symbol_timestamp_idx,
        trade_strategy_timestamp_idx,
        ohlcv_timestamp_idx,
        ohlcv_symbol_timestamp_idx,
        strategy_name_idx
    ]

    # Create indexes that don't already exist
    with engine.connect() as conn:
        for idx in indexes:
            # Check if index already exists
            idx_name = idx.name
            result = conn.execute(text(
                f"SELECT 1 FROM sqlite_master WHERE type='index' AND name='{idx_name}'"
            ))
            if not result.scalar():
                idx.create(engine)


def drop_indexes(engine):
    """
    Drop all custom indexes.

    Args:
        engine: SQLAlchemy engine instance
    """
    index_names = [
        'idx_trade_timestamp',
        'idx_trade_symbol_timestamp',
        'idx_trade_strategy_timestamp',
        'idx_ohlcv_timestamp',
        'idx_ohlcv_symbol_timestamp',
        'idx_strategy_name'
    ]

    with engine.connect() as conn:
        for idx_name in index_names:
            result = conn.execute(text(
                f"SELECT 1 FROM sqlite_master WHERE type='index' AND name='{idx_name}'"
            ))
            if result.scalar():
                conn.execute(text(f"DROP INDEX IF EXISTS {idx_name}"))


def create_function_based_indexes(engine):
    """
    Create function-based indexes for advanced query optimization.

    Args:
        engine: SQLAlchemy engine instance
    """
    # These are more advanced indexes that might be database-specific
    # For SQLite, we can create indexes on expressions
    with engine.connect() as conn:
        # Index for date extraction (for time-based grouping)
        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_ohlcv_date
        ON ohlcv(strftime('%Y-%m-%d', timestamp))
        """))

        # Index for hour extraction (for hourly aggregation)
        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_ohlcv_hour
        ON ohlcv(strftime('%Y-%m-%d %H', timestamp))
        """))
