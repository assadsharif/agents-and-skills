"""
Stock Signal API - Technical Indicator Calculator

Calculates RSI, MACD, SMA, and EMA from historical price data using pandas-ta.
"""

import logging

import pandas as pd
import pandas_ta_classic as ta

from ..config import settings
from ..models.indicator import (
    EMAIndicator,
    Indicators,
    MACDIndicator,
    SMAIndicator,
)

logger = logging.getLogger("app.services.indicator_calculator")


class IndicatorCalculator:
    """Calculates technical indicators from OHLCV DataFrame using pandas-ta."""

    def __init__(self) -> None:
        self.rsi_period = settings.RSI_PERIOD
        self.macd_fast = settings.MACD_FAST
        self.macd_slow = settings.MACD_SLOW
        self.macd_signal = settings.MACD_SIGNAL
        self.sma_periods = settings.SMA_PERIODS
        self.ema_periods = settings.EMA_PERIODS

    def calculate(self, df: pd.DataFrame) -> Indicators:
        """
        Calculate all technical indicators from an OHLCV DataFrame.

        Args:
            df: DataFrame with columns: Open, High, Low, Close, Volume.
                Must have at least 1 row.

        Returns:
            Indicators model with calculated values (None where insufficient data).
        """
        close = df["Close"]
        current_price = float(close.iloc[-1])

        rsi = self._calc_rsi(close)
        macd = self._calc_macd(close)
        sma = self._calc_sma(close)
        ema = self._calc_ema(close)

        return Indicators(rsi=rsi, macd=macd, sma=sma, ema=ema)

    def get_current_price(self, df: pd.DataFrame) -> float:
        """Extract the most recent closing price from the DataFrame."""
        return round(float(df["Close"].iloc[-1]), 2)

    def get_data_freshness(self, df: pd.DataFrame) -> pd.Timestamp:
        """Return the timestamp of the most recent data point."""
        return df.index[-1]

    # ── Private calculation helpers ──────────────────────────────────

    def _calc_rsi(self, close: pd.Series) -> float | None:
        """Calculate RSI (14-period). Returns None if insufficient data."""
        if len(close) < self.rsi_period + 1:
            logger.info("Insufficient data for RSI (%d rows)", len(close))
            return None
        rsi_series = ta.rsi(close, length=self.rsi_period)
        if rsi_series is None or rsi_series.dropna().empty:
            return None
        return round(float(rsi_series.dropna().iloc[-1]), 2)

    def _calc_macd(self, close: pd.Series) -> MACDIndicator:
        """Calculate MACD (12, 26, 9). Returns nulls if insufficient data."""
        min_rows = self.macd_slow + self.macd_signal
        if len(close) < min_rows:
            logger.info("Insufficient data for MACD (%d rows)", len(close))
            return MACDIndicator()

        macd_df = ta.macd(
            close,
            fast=self.macd_fast,
            slow=self.macd_slow,
            signal=self.macd_signal,
        )
        if macd_df is None or macd_df.dropna().empty:
            return MACDIndicator()

        last = macd_df.dropna().iloc[-1]
        # pandas-ta MACD column names: MACD_12_26_9, MACDs_12_26_9, MACDh_12_26_9
        line_col = f"MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}"
        signal_col = f"MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}"
        hist_col = f"MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}"

        return MACDIndicator(
            line=round(float(last[line_col]), 2),
            signal=round(float(last[signal_col]), 2),
            histogram=round(float(last[hist_col]), 2),
        )

    def _calc_sma(self, close: pd.Series) -> SMAIndicator:
        """Calculate SMA for 20, 50, 200-day periods."""
        values: dict[str, float | None] = {}
        for period in self.sma_periods:
            if len(close) < period:
                logger.info(
                    "Insufficient data for SMA-%d (%d rows)", period, len(close)
                )
                values[f"{period}_day"] = None
            else:
                sma = ta.sma(close, length=period)
                if sma is None or sma.dropna().empty:
                    values[f"{period}_day"] = None
                else:
                    values[f"{period}_day"] = round(float(sma.dropna().iloc[-1]), 2)

        return SMAIndicator(**values)

    def _calc_ema(self, close: pd.Series) -> EMAIndicator:
        """Calculate EMA for 12, 26-day periods."""
        values: dict[str, float | None] = {}
        for period in self.ema_periods:
            if len(close) < period:
                logger.info(
                    "Insufficient data for EMA-%d (%d rows)", period, len(close)
                )
                values[f"{period}_day"] = None
            else:
                ema = ta.ema(close, length=period)
                if ema is None or ema.dropna().empty:
                    values[f"{period}_day"] = None
                else:
                    values[f"{period}_day"] = round(float(ema.dropna().iloc[-1]), 2)

        return EMAIndicator(**values)
