"""
FastAPI application for the Abidance trading bot.

This module defines the FastAPI application and routes for the Abidance trading bot API.
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from abidance.database.models import Trade, Strategy
from abidance.api.database import get_db
from abidance.api.models import TradeResponse, StrategyResponse

# Create FastAPI application
app = FastAPI(
    title="Abidance Trading Bot API",
    description="API for the Abidance trading bot",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/api/v1/strategies", response_model=List[StrategyResponse], tags=["strategies"])
async def list_strategies(db: Session = Depends(get_db)):
    """
    List all available trading strategies.
    
    This endpoint returns a list of all trading strategies in the database.
    
    Args:
        db: Database session dependency.
        
    Returns:
        List[StrategyResponse]: List of strategy response models.
        
    Raises:
        HTTPException: If an error occurs while retrieving strategies.
    """
    try:
        strategies = db.query(Strategy).all()
        return [StrategyResponse.model_validate(s) for s in strategies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/trades", response_model=List[TradeResponse], tags=["trades"])
async def list_trades(
    symbol: Optional[str] = Query(None, description="Filter trades by symbol"),
    start_date: Optional[datetime] = Query(None, description="Filter trades after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter trades before this date"),
    db: Session = Depends(get_db)
):
    """
    List trades with optional filtering.
    
    This endpoint returns a list of trades, optionally filtered by symbol and date range.
    
    Args:
        symbol: Optional symbol to filter trades by.
        start_date: Optional start date to filter trades by.
        end_date: Optional end date to filter trades by.
        db: Database session dependency.
        
    Returns:
        List[TradeResponse]: List of trade response models.
        
    Raises:
        HTTPException: If an error occurs while retrieving trades.
    """
    try:
        query = db.query(Trade)
        
        if symbol:
            query = query.filter(Trade.symbol == symbol)
        if start_date:
            query = query.filter(Trade.timestamp >= start_date)
        if end_date:
            query = query.filter(Trade.timestamp <= end_date)
        
        trades = query.all()
        return [TradeResponse.model_validate(t) for t in trades]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 