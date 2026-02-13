"""
Stock Signal API - Technical Indicator Models

Pydantic models for technical indicators matching openapi.yaml schema.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class MACDIndicator(BaseModel):
    """MACD indicator values (12-EMA, 26-EMA, 9-signal)."""

    line: float | None = Field(
        None, description="MACD line (12-EMA minus 26-EMA)"
    )
    signal: float | None = Field(
        None, description="MACD signal line (9-EMA of MACD line)"
    )
    histogram: float | None = Field(
        None, description="MACD histogram (MACD line minus signal line)"
    )


class SMAIndicator(BaseModel):
    """Simple Moving Average values for standard periods."""

    day_20: float | None = Field(
        None, alias="20_day", description="20-day SMA"
    )
    day_50: float | None = Field(
        None, alias="50_day", description="50-day SMA"
    )
    day_200: float | None = Field(
        None, alias="200_day", description="200-day SMA"
    )

    model_config = {"populate_by_name": True}


class EMAIndicator(BaseModel):
    """Exponential Moving Average values for standard periods."""

    day_12: float | None = Field(
        None, alias="12_day", description="12-day EMA"
    )
    day_26: float | None = Field(
        None, alias="26_day", description="26-day EMA"
    )

    model_config = {"populate_by_name": True}


class Indicators(BaseModel):
    """Complete set of technical indicators per openapi.yaml Indicators schema."""

    rsi: float | None = Field(
        None, ge=0, le=100, description="RSI (14-period, 0-100)"
    )
    macd: MACDIndicator = Field(default_factory=MACDIndicator)
    sma: SMAIndicator = Field(default_factory=SMAIndicator)
    ema: EMAIndicator = Field(default_factory=EMAIndicator)


class IndicatorResponse(BaseModel):
    """GET /indicators/{ticker} response per openapi.yaml IndicatorResponse schema."""

    ticker: str = Field(
        ..., pattern=r"^[A-Z0-9]{1,5}$", description="Stock ticker symbol"
    )
    calculated_at: datetime = Field(
        ..., description="When indicators were calculated (UTC)"
    )
    current_price: float = Field(
        ..., ge=0, description="Current stock price"
    )
    indicators: Indicators = Field(
        ..., description="Calculated technical indicators"
    )
