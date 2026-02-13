"""Unit tests for SignalGenerator (app/services/signal_generator.py)."""

import pytest

from app.models.indicator import (
    EMAIndicator,
    Indicators,
    MACDIndicator,
    SMAIndicator,
)
from app.models.signal import SignalAction
from app.services.signal_generator import SignalGenerator


@pytest.fixture
def generator():
    return SignalGenerator()


def _indicators(
    rsi=50.0, histogram=0.0, sma_50=None, sma_200=None, sma_20=None,
):
    """Helper to build Indicators with sensible defaults."""
    return Indicators(
        rsi=rsi,
        macd=MACDIndicator(line=0.5, signal=0.5, histogram=histogram),
        sma=SMAIndicator(**{
            "20_day": sma_20 or 100.0,
            "50_day": sma_50,
            "200_day": sma_200,
        }),
        ema=EMAIndicator(**{"12_day": 100.0, "26_day": 100.0}),
    )


class TestScoring:
    """Verify the rule-based scoring algorithm."""

    def test_strong_oversold_rsi_adds_2(self, generator):
        ind = _indicators(rsi=25.0)
        result = generator.generate(ind, 100.0)
        # RSI < 30 = +2
        assert result.score >= 2

    def test_mild_oversold_rsi_adds_1(self, generator):
        ind = _indicators(rsi=35.0)
        result = generator.generate(ind, 100.0)
        # RSI < 40 = +1, histogram=0 no score
        assert any("mildly oversold" in r for r in result.reasons)

    def test_strong_overbought_rsi_subtracts_2(self, generator):
        ind = _indicators(rsi=75.0)
        result = generator.generate(ind, 100.0)
        assert result.score <= -2

    def test_mild_overbought_rsi_subtracts_1(self, generator):
        ind = _indicators(rsi=65.0)
        result = generator.generate(ind, 100.0)
        assert any("mildly overbought" in r for r in result.reasons)

    def test_bullish_macd_adds_2(self, generator):
        ind = _indicators(rsi=50.0, histogram=0.5)
        result = generator.generate(ind, 100.0)
        assert any("bullish" in r for r in result.reasons)

    def test_bearish_macd_subtracts_2(self, generator):
        ind = _indicators(rsi=50.0, histogram=-0.5)
        result = generator.generate(ind, 100.0)
        assert any("bearish" in r for r in result.reasons)

    def test_price_above_sma50_adds_1(self, generator):
        ind = _indicators(sma_50=95.0)
        result = generator.generate(ind, 100.0)
        assert any("above 50-day" in r for r in result.reasons)

    def test_price_below_sma200_subtracts_1(self, generator):
        ind = _indicators(sma_200=110.0)
        result = generator.generate(ind, 100.0)
        assert any("below 200-day" in r for r in result.reasons)


class TestSignalAction:
    """Verify BUY/SELL/HOLD thresholds."""

    def test_strong_buy_signal(self, generator):
        # RSI < 30 (+2) + bullish MACD (+2) + above SMA50 (+1) = +5
        ind = _indicators(rsi=25.0, histogram=0.5, sma_50=90.0)
        result = generator.generate(ind, 100.0)
        assert result.action == SignalAction.BUY
        assert result.score >= 2

    def test_strong_sell_signal(self, generator):
        # RSI > 70 (-2) + bearish MACD (-2) + below SMA50 (-1) = -5
        ind = _indicators(rsi=75.0, histogram=-0.5, sma_50=110.0)
        result = generator.generate(ind, 100.0)
        assert result.action == SignalAction.SELL
        assert result.score <= -2

    def test_hold_signal_neutral(self, generator):
        # RSI neutral (0) + no MACD (0) + no SMAs = 0
        ind = _indicators(rsi=50.0, histogram=0.0)
        result = generator.generate(ind, 100.0)
        assert result.action == SignalAction.HOLD
        assert -1 <= result.score <= 1

    def test_hold_signal_mixed(self, generator):
        # RSI oversold (+2) + bearish MACD (-2) = 0
        ind = _indicators(rsi=25.0, histogram=-0.5)
        result = generator.generate(ind, 100.0)
        assert result.action == SignalAction.HOLD


class TestConfidence:
    """Verify confidence = min(abs(score) * 20, 100)."""

    def test_zero_score_zero_confidence(self, generator):
        ind = _indicators(rsi=50.0, histogram=0.0)
        result = generator.generate(ind, 100.0)
        assert result.confidence == 0

    def test_score_2_confidence_40(self, generator):
        # RSI < 30 (+2) alone, histogram=0
        ind = _indicators(rsi=25.0, histogram=0.0)
        result = generator.generate(ind, 100.0)
        assert result.confidence == abs(result.score) * 20

    def test_confidence_capped_at_100(self, generator):
        # RSI < 30 (+2) + bullish (+2) + above SMA50 (+1) + above SMA200 (+1) = 6
        ind = _indicators(rsi=25.0, histogram=0.5, sma_50=90.0, sma_200=85.0)
        result = generator.generate(ind, 100.0)
        assert result.confidence == 100


class TestReasoning:
    """Verify reasoning generation."""

    def test_reasoning_length_constraint(self, generator):
        ind = _indicators(rsi=50.0)
        result = generator.generate(ind, 100.0)
        reasoning = generator.build_reasoning(result, ind, 100.0)
        assert 20 <= len(reasoning) <= 500

    def test_strong_prefix_at_high_confidence(self, generator):
        ind = _indicators(rsi=25.0, histogram=0.5, sma_50=90.0, sma_200=85.0)
        result = generator.generate(ind, 100.0)
        reasoning = generator.build_reasoning(result, ind, 100.0)
        assert reasoning.startswith("Strong BUY")

    def test_no_strong_prefix_at_low_confidence(self, generator):
        ind = _indicators(rsi=50.0, histogram=0.0)
        result = generator.generate(ind, 100.0)
        reasoning = generator.build_reasoning(result, ind, 100.0)
        assert not reasoning.startswith("Strong")

    def test_two_plus_indicator_refs(self, generator):
        ind = _indicators(rsi=50.0, histogram=0.0)
        result = generator.generate(ind, 100.0)
        reasoning = generator.build_reasoning(result, ind, 100.0).lower()
        refs = sum(1 for i in ["rsi", "macd", "sma", "ema"] if i in reasoning)
        assert refs >= 2

    def test_limited_data_mentioned(self, generator):
        ind = _indicators(rsi=45.0)
        result = generator.generate(ind, 100.0)
        reasoning = generator.build_reasoning(result, ind, 100.0, data_days=50)
        assert "Limited data" in reasoning
        assert "50 days" in reasoning

    def test_unavailable_sma_mentioned(self, generator):
        ind = Indicators(
            rsi=45.0,
            macd=MACDIndicator(line=0.1, signal=0.1, histogram=0.0),
            sma=SMAIndicator(**{"20_day": 100.0, "50_day": None, "200_day": None}),
            ema=EMAIndicator(**{"12_day": 100.0, "26_day": 100.0}),
        )
        result = generator.generate(ind, 100.0)
        reasoning = generator.build_reasoning(result, ind, 100.0, data_days=30)
        assert "unavailable" in reasoning.lower()

    def test_hold_uses_mixed_indicators_prefix(self, generator):
        ind = _indicators(rsi=50.0, histogram=0.0)
        result = generator.generate(ind, 100.0)
        reasoning = generator.build_reasoning(result, ind, 100.0)
        assert "Mixed indicators" in reasoning


class TestNullIndicators:
    """Verify graceful handling of null/missing indicators."""

    def test_all_null_produces_hold(self, generator):
        ind = Indicators()
        result = generator.generate(ind, 100.0)
        assert result.action == SignalAction.HOLD
        assert result.score == 0

    def test_only_rsi_available(self, generator):
        ind = Indicators(rsi=25.0)
        result = generator.generate(ind, 100.0)
        assert result.action in [SignalAction.BUY, SignalAction.HOLD]
        assert result.score == 2  # RSI < 30 = +2
