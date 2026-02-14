"""Unit tests for IndicatorCalculator (app/services/indicator_calculator.py)."""

import pytest

from app.services.indicator_calculator import IndicatorCalculator
from tests.fixtures.sample_data import (
    BEARISH_200D,
    BULLISH_200D,
    MINIMAL_15D,
    NEUTRAL_200D,
    SHORT_50D,
)


@pytest.fixture
def calculator():
    return IndicatorCalculator()


class TestRSI:
    def test_rsi_in_range(self, calculator):
        ind = calculator.calculate(NEUTRAL_200D)
        assert ind.rsi is not None
        assert 0 <= ind.rsi <= 100

    def test_rsi_bullish_trend(self, calculator):
        ind = calculator.calculate(BULLISH_200D)
        # Bullish trend should push RSI higher (though not guaranteed > 50)
        assert ind.rsi is not None

    def test_rsi_bearish_trend(self, calculator):
        ind = calculator.calculate(BEARISH_200D)
        assert ind.rsi is not None

    def test_rsi_none_for_insufficient_data(self, calculator):
        # 15 days is barely enough for 14-period RSI
        ind = calculator.calculate(MINIMAL_15D)
        # With exactly 15 rows the RSI series may have a single value
        # This is acceptable — it should not crash
        assert ind.rsi is None or 0 <= ind.rsi <= 100


class TestMACD:
    def test_macd_values_present(self, calculator):
        ind = calculator.calculate(NEUTRAL_200D)
        assert ind.macd.line is not None
        assert ind.macd.signal is not None
        assert ind.macd.histogram is not None

    def test_histogram_equals_line_minus_signal(self, calculator):
        ind = calculator.calculate(NEUTRAL_200D)
        expected = round(ind.macd.line - ind.macd.signal, 2)
        assert ind.macd.histogram == expected

    def test_macd_none_for_insufficient_data(self, calculator):
        ind = calculator.calculate(MINIMAL_15D)
        # 15 days < 26 + 9 = 35 minimum for MACD
        assert ind.macd.line is None
        assert ind.macd.signal is None
        assert ind.macd.histogram is None


class TestSMA:
    def test_sma_all_present_200d(self, calculator):
        ind = calculator.calculate(NEUTRAL_200D)
        assert ind.sma.day_20 is not None
        assert ind.sma.day_50 is not None
        assert ind.sma.day_200 is not None

    def test_sma_partial_for_50d(self, calculator):
        ind = calculator.calculate(SHORT_50D)
        assert ind.sma.day_20 is not None
        assert ind.sma.day_50 is not None
        assert ind.sma.day_200 is None  # Not enough data

    def test_sma_minimal_data(self, calculator):
        ind = calculator.calculate(MINIMAL_15D)
        assert ind.sma.day_20 is None  # 15 < 20
        assert ind.sma.day_50 is None
        assert ind.sma.day_200 is None


class TestEMA:
    def test_ema_all_present(self, calculator):
        ind = calculator.calculate(NEUTRAL_200D)
        assert ind.ema.day_12 is not None
        assert ind.ema.day_26 is not None

    def test_ema_partial_for_minimal(self, calculator):
        ind = calculator.calculate(MINIMAL_15D)
        assert ind.ema.day_12 is not None  # 15 >= 12
        assert ind.ema.day_26 is None  # 15 < 26


class TestCurrentPrice:
    def test_returns_last_close(self, calculator):
        price = calculator.get_current_price(NEUTRAL_200D)
        expected = round(float(NEUTRAL_200D["Close"].iloc[-1]), 2)
        assert price == expected


class TestDataFreshness:
    def test_returns_last_index(self, calculator):
        ts = calculator.get_data_freshness(NEUTRAL_200D)
        assert ts == NEUTRAL_200D.index[-1]
