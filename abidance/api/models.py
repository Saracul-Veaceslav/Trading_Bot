"""
API response models for the Abidance trading bot.

This module defines Pydantic models used for API responses, ensuring proper
data validation and serialization.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from abidance.trading.order import OrderSide


class TradeResponse(BaseModel):
    """
    Response model for trade data.
    
    This model is used to serialize trade data for API responses.
    """
    id: int
    symbol: str
    side: OrderSide
    amount: float
    price: float
    timestamp: datetime
    strategy_id: Optional[int] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "symbol": "BTC/USD",
                "side": "BUY",
                "amount": 0.1,
                "price": 50000.0,
                "timestamp": "2023-01-01T12:00:00",
                "strategy_id": 1
            }
        }
    )


class StrategyResponse(BaseModel):
    """
    Response model for strategy data.
    
    This model is used to serialize strategy data for API responses.
    """
    id: int
    name: str
    parameters: Dict[str, Any]
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "SMA Crossover",
                "parameters": {
                    "fast_period": 10,
                    "slow_period": 20
                },
                "created_at": "2023-01-01T12:00:00"
            }
        }
    )


class ErrorResponse(BaseModel):
    """
    Response model for error messages.
    
    This model is used to serialize error details for API responses.
    """
    detail: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "An error occurred while processing the request."
            }
        }
    ) 