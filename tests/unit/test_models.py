"""Unit tests for Pydantic models (app/models/)."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.indicator import (
    EMAIndicator,
    IndicatorResponse,
    Indicators,
    MACDIndicator,
    SMAIndicator,
)
from app.models.signal import Signal, SignalAction
from app.models.stock import PriceData, Stock


class TestStockModel:
    def test_valid_stock(self):
        s = Stock(ticker="AAPL", company_name="Apple Inc.", exchange="NASDAQ", current_price=175.20)
        assert s.ticker == "AAPL"
        assert s.current_price == 175.20

    def test_invalid_ticker_pattern(self):
        with pytest.raises(ValidationError):
            Stock(ticker="invalid!", company_name="X", exchange="NYSE", current_price=10.0)

    def test_negative_price_rejected(self):
        with pytest.raises(ValidationError):
            Stock(ticker="AAPL", company_name="Apple", exchange="NYSE", current_price=-1.0)


class TestPriceDataModel:
    def test_valid_price_data(self):
        p = PriceData(
            ticker="AAPL",
            date="2026-02-13",
            open=170.0, high=176.0, low=169.0, close=175.0, volume=50000000,
        )
        assert p.close == 175.0

    def test_negative_volume_rejected(self):
        with pytest.raises(ValidationError):
            PriceData(
                ticker="AAPL", date="2026-02-13",
                open=170.0, high=176.0, low=169.0, close=175.0, volume=-1,
            )


class TestIndicatorsModel:
    def test_all_null_defaults(self):
        ind = Indicators()
        assert ind.rsi is None
        assert ind.macd.line is None
        assert ind.sma.day_20 is None
        assert ind.ema.day_12 is None

    def test_full_indicators(self):
        ind = Indicators(
            rsi=45.0,
            macd=MACDIndicator(line=1.0, signal=0.8, histogram=0.2),
            sma=SMAIndicator(**{"20_day": 170.0, "50_day": 172.0, "200_day": 165.0}),
            ema=EMAIndicator(**{"12_day": 173.0, "26_day": 171.0}),
        )
        assert ind.rsi == 45.0
        assert ind.macd.histogram == 0.2
        assert ind.sma.day_50 == 172.0
        assert ind.ema.day_26 == 171.0

    def test_rsi_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            Indicators(rsi=101.0)

    def test_rsi_negative_rejected(self):
        with pytest.raises(ValidationError):
            Indicators(rsi=-1.0)

    def test_json_aliases(self):
        ind = Indicators(
            sma=SMAIndicator(**{"20_day": 100.0, "50_day": 105.0, "200_day": 110.0}),
            ema=EMAIndicator(**{"12_day": 102.0, "26_day": 104.0}),
        )
        d = ind.model_dump(by_alias=True)
        assert "20_day" in d["sma"]
        assert "12_day" in d["ema"]


class TestSignalModel:
    def _make_signal(self, **overrides):
        defaults = dict(
            ticker="AAPL",
            signal=SignalAction.BUY,
            confidence=80,
            reasoning="Strong BUY signal: RSI at 28 (oversold), MACD bullish crossover detected",
            timestamp=datetime.now(timezone.utc),
            data_freshness=datetime.now(timezone.utc),
            current_price=175.20,
            indicators=Indicators(),
        )
        defaults.update(overrides)
        return Signal(**defaults)

    def test_valid_signal(self):
        s = self._make_signal()
        assert s.signal == SignalAction.BUY
        assert s.confidence == 80

    def test_signal_enum_values(self):
        for action in [SignalAction.BUY, SignalAction.SELL, SignalAction.HOLD]:
            s = self._make_signal(signal=action)
            assert s.signal == action

    def test_confidence_out_of_range(self):
        with pytest.raises(ValidationError):
            self._make_signal(confidence=101)

    def test_reasoning_too_short(self):
        with pytest.raises(ValidationError):
            self._make_signal(reasoning="short")

    def test_reasoning_too_long(self):
        with pytest.raises(ValidationError):
            self._make_signal(reasoning="x" * 501)

    def test_negative_price_rejected(self):
        with pytest.raises(ValidationError):
            self._make_signal(current_price=-5.0)


class TestIndicatorResponseModel:
    def test_valid_response(self):
        r = IndicatorResponse(
            ticker="AAPL",
            calculated_at=datetime.now(timezone.utc),
            current_price=175.20,
            indicators=Indicators(rsi=45.0),
        )
        assert r.ticker == "AAPL"
        assert r.indicators.rsi == 45.0
