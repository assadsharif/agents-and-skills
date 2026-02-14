"""
Test Fixtures - Mock Price Data

Provides realistic OHLCV DataFrames for testing indicator calculations
and signal generation without hitting Yahoo Finance.
"""

import numpy as np
import pandas as pd


def make_ohlcv(
    days: int = 200,
    start_price: float = 150.0,
    trend: str = "neutral",
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic OHLCV DataFrame.

    Args:
        days: Number of trading days.
        start_price: Starting close price.
        trend: "bullish", "bearish", or "neutral".
        seed: Random seed for reproducibility.

    Returns:
        DataFrame indexed by DatetimeIndex with Open, High, Low, Close, Volume.
    """
    rng = np.random.default_rng(seed)
    drift = {"bullish": 0.002, "bearish": -0.002, "neutral": 0.0}[trend]

    returns = rng.normal(loc=drift, scale=0.015, size=days)
    close = start_price * np.cumprod(1 + returns)
    open_ = close * (1 + rng.normal(0, 0.003, days))
    high = np.maximum(open_, close) * (1 + rng.uniform(0.001, 0.015, days))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.001, 0.015, days))
    volume = rng.integers(1_000_000, 50_000_000, size=days)

    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="B")

    # Ensure array length matches index length (business days may differ)
    n = len(dates)

    return pd.DataFrame(
        {
            "Open": np.round(open_[:n], 2),
            "High": np.round(high[:n], 2),
            "Low": np.round(low[:n], 2),
            "Close": np.round(close[:n], 2),
            "Volume": volume[:n],
        },
        index=dates,
    )


# Pre-built fixtures for common test scenarios
# Use extra days to compensate for business-day truncation in date_range(freq='B')
BULLISH_200D = make_ohlcv(210, 150.0, "bullish", seed=1)
BEARISH_200D = make_ohlcv(210, 150.0, "bearish", seed=2)
NEUTRAL_200D = make_ohlcv(210, 150.0, "neutral", seed=3)
SHORT_50D = make_ohlcv(55, 100.0, "neutral", seed=4)
MINIMAL_15D = make_ohlcv(15, 100.0, "neutral", seed=5)
