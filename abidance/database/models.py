"""
Database models for the Abidance trading bot.

This module defines the SQLAlchemy ORM models used to persist trading data,
including trades, strategies, and market data.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Index, JSON
from sqlalchemy.orm import declarative_base, relationship

from abidance.trading.order import OrderSide

# Use the new SQLAlchemy 2.0 API
Base = declarative_base()


# pylint: disable=too-few-public-methods
class Trade(Base):
    """Model for storing trade information."""
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'))

    strategy = relationship("Strategy", back_populates="trades")

    def __repr__(self):
        return f"<Trade(symbol={self.symbol}, side={self.side}, amount={self.amount})>"


# pylint: disable=too-few-public-methods
class Strategy(Base):
    """Model for storing strategy configurations."""
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trades = relationship("Trade", back_populates="strategy")

    def __repr__(self):
        return f"<Strategy(name={self.name})>"


# pylint: disable=too-few-public-methods
class OHLCV(Base):
    """Model for storing OHLCV data."""
    __tablename__ = 'ohlcv'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp', unique=True),
    )

    def __repr__(self):
        return f"<OHLCV(symbol={self.symbol}, timestamp={self.timestamp})>"
