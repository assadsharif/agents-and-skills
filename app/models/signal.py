"""
Stock Signal API - Signal Model

Pydantic models for trading signals matching openapi.yaml Signal schema.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from .indicator import Indicators


class SignalAction(str, Enum):
    """Trading signal recommendation."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Signal(BaseModel):
    """Trading signal response per openapi.yaml Signal schema."""

    ticker: str = Field(
        ..., pattern=r"^[A-Z0-9]{1,5}$", description="Stock ticker symbol"
    )
    signal: SignalAction = Field(
        ..., description="Trading recommendation (BUY/SELL/HOLD)"
    )
    confidence: int = Field(
        ..., ge=0, le=100, description="Confidence level (0-100%)"
    )
    reasoning: str = Field(
        ...,
        min_length=20,
        max_length=500,
        description="Human-readable explanation of signal generation",
    )
    timestamp: datetime = Field(
        ..., description="When signal was generated (UTC)"
    )
    data_freshness: datetime = Field(
        ..., description="Timestamp of underlying price data (UTC)"
    )
    current_price: float = Field(
        ..., ge=0, description="Current stock price"
    )
    indicators: Indicators = Field(
        ..., description="Technical indicators used for signal generation"
    )
