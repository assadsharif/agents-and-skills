"""
Stock Signal API - Stock Model

Pydantic models for stock and price data entities.
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Exchange(str, Enum):
    """Supported stock exchanges."""

    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    UNKNOWN = "UNKNOWN"


class Stock(BaseModel):
    """Represents a publicly traded equity."""

    ticker: str = Field(
        ...,
        pattern=r"^[A-Z0-9]{1,5}$",
        description="Stock ticker symbol",
        examples=["AAPL"],
    )
    company_name: str = Field(
        ..., description="Company name", examples=["Apple Inc."]
    )
    exchange: str = Field(
        default="UNKNOWN",
        description="Stock exchange",
        examples=["NASDAQ"],
    )
    current_price: float = Field(
        ..., ge=0, description="Current stock price", examples=[175.20]
    )


class PriceData(BaseModel):
    """Historical price data for a single trading day."""

    ticker: str = Field(..., pattern=r"^[A-Z0-9]{1,5}$")
    date: date
    open: float = Field(..., ge=0)
    high: float = Field(..., ge=0)
    low: float = Field(..., ge=0)
    close: float = Field(..., ge=0)
    volume: int = Field(..., ge=0)
