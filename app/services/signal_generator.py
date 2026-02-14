"""
Stock Signal API - Signal Generator

Generates BUY/SELL/HOLD trading signals using a rule-based scoring algorithm.
Scoring logic per research.md and data-model.md:

  BUY signals (+):
    RSI < 30:  +2  (strong oversold)
    RSI < 40:  +1  (mild oversold)
    MACD bullish crossover (histogram > 0):  +2
    Price > 50-day SMA:  +1
    Price > 200-day SMA:  +1

  SELL signals (-):
    RSI > 70:  -2  (strong overbought)
    RSI > 60:  -1  (mild overbought)
    MACD bearish crossover (histogram < 0):  -2
    Price < 50-day SMA:  -1
    Price < 200-day SMA:  -1

  Final:
    Score >= +2:  BUY
    Score <= -2:  SELL
    -1 to +1:    HOLD
    Confidence = min(abs(score) * 20, 100)
"""

import logging

from ..config import settings
from ..models.indicator import Indicators
from ..models.signal import SignalAction

logger = logging.getLogger("app.services.signal_generator")


class SignalResult:
    """Intermediate result from signal generation (before full Signal model)."""

    __slots__ = ("action", "confidence", "score", "reasons")

    def __init__(
        self,
        action: SignalAction,
        confidence: int,
        score: int,
        reasons: list[str],
    ) -> None:
        self.action = action
        self.confidence = confidence
        self.score = score
        self.reasons = reasons


class SignalGenerator:
    """Generates trading signals from technical indicators using rule-based scoring."""

    def __init__(self) -> None:
        self.buy_threshold = settings.BUY_THRESHOLD
        self.sell_threshold = settings.SELL_THRESHOLD
        self.confidence_multiplier = settings.CONFIDENCE_MULTIPLIER
        self.max_confidence = settings.MAX_CONFIDENCE

    def generate(
        self, indicators: Indicators, current_price: float
    ) -> SignalResult:
        """
        Generate a trading signal from indicators and current price.

        Args:
            indicators: Calculated technical indicators.
            current_price: Most recent closing price.

        Returns:
            SignalResult with action, confidence, score, and reasoning parts.
        """
        score = 0
        reasons: list[str] = []

        score, reasons = self._score_rsi(indicators, score, reasons)
        score, reasons = self._score_macd(indicators, score, reasons)
        score, reasons = self._score_sma(indicators, current_price, score, reasons)

        action = self._determine_action(score)
        confidence = self._calculate_confidence(score)

        return SignalResult(
            action=action,
            confidence=confidence,
            score=score,
            reasons=reasons,
        )

    def build_reasoning(
        self,
        result: SignalResult,
        indicators: Indicators,
        current_price: float,
        data_days: int | None = None,
    ) -> str:
        """
        Build a human-readable reasoning string from the signal result.

        Implements T033-T039:
        - Strength prefix based on confidence (Strong/moderate)
        - BUY/SELL/HOLD templates matching openapi.yaml examples
        - Specific numerical values from indicators
        - At least 2 indicator references per SC-006
        - Insufficient data edge case reasoning

        Returns a string between 20-500 chars per openapi.yaml constraint.
        """
        action = result.action.value
        confidence = result.confidence
        parts: list[str] = []

        # T039: Limited data prefix
        is_limited = data_days is not None and data_days < 200
        if is_limited:
            parts.append(f"Limited data (only {data_days} days available)")

        # Collect indicator-specific reasons from scoring
        if result.reasons:
            parts.extend(result.reasons)

        # T039: Note unavailable long-term indicators for partial data
        if is_limited:
            unavailable: list[str] = []
            if indicators.sma.day_200 is None:
                unavailable.append("200-day SMA")
            if indicators.sma.day_50 is None:
                unavailable.append("50-day SMA")
            if unavailable:
                parts.append(
                    f"Unable to assess long-term trend ({', '.join(unavailable)} unavailable)"
                )

        # T038: Ensure at least 2 indicator references (SC-006)
        indicator_count = self._count_indicator_refs(parts)
        if indicator_count < 2:
            parts = self._add_supplementary_refs(
                parts, indicators, current_price
            )

        # T034-T036: Build with action-specific template
        prefix = self._action_prefix(action, confidence)

        if action == "HOLD" and not is_limited:
            # T036: HOLD template — emphasise mixed/neutral nature
            detail = ", ".join(parts)
            reasoning = f"{prefix}Mixed indicators - {detail}."
        else:
            detail = ", ".join(parts)
            reasoning = f"{prefix}{detail}."

        # Enforce openapi.yaml 20-500 char constraint
        if len(reasoning) < 20:
            reasoning = (
                reasoning.rstrip(".")
                + " - indicators are within neutral ranges."
            )
        if len(reasoning) > 500:
            reasoning = reasoning[:497] + "..."

        return reasoning

    # ── Reasoning helpers ────────────────────────────────────────────

    @staticmethod
    def _action_prefix(action: str, confidence: int) -> str:
        """Return a strength-qualified prefix matching openapi.yaml examples."""
        if confidence >= 80:
            return f"Strong {action} signal: "
        return f"{action} signal: "

    @staticmethod
    def _count_indicator_refs(parts: list[str]) -> int:
        """Count how many distinct indicator families are referenced."""
        text = " ".join(parts).lower()
        count = 0
        if "rsi" in text:
            count += 1
        if "macd" in text:
            count += 1
        if "sma" in text:
            count += 1
        if "ema" in text:
            count += 1
        return count

    def _add_supplementary_refs(
        self,
        parts: list[str],
        indicators: Indicators,
        current_price: float,
    ) -> list[str]:
        """Add supplementary indicator mentions to meet the 2-ref minimum."""
        text = " ".join(parts).lower()

        # Add RSI context if not already mentioned
        if "rsi" not in text and indicators.rsi is not None:
            rsi = indicators.rsi
            if rsi < settings.RSI_OVERSOLD_STRONG:
                parts.append(f"RSI at {rsi} (oversold)")
            elif rsi > settings.RSI_OVERBOUGHT_STRONG:
                parts.append(f"RSI at {rsi} (overbought)")
            else:
                parts.append(f"RSI at {rsi}")

        text = " ".join(parts).lower()

        # Add MACD context if not already mentioned
        if "macd" not in text and indicators.macd.histogram is not None:
            h = indicators.macd.histogram
            if h > 0:
                parts.append("MACD positive")
            elif h < 0:
                parts.append("MACD negative")
            else:
                parts.append("MACD neutral")

        text = " ".join(parts).lower()

        # Add SMA-20 context if still under 2 refs
        if self._count_indicator_refs(parts) < 2:
            sma_20 = indicators.sma.day_20
            if sma_20 is not None:
                if current_price > sma_20:
                    parts.append(f"price above 20-day SMA (${current_price:.2f} > ${sma_20:.2f})")
                else:
                    parts.append(f"price near 20-day SMA (${sma_20:.2f})")

        return parts

    # ── Private scoring helpers ──────────────────────────────────────

    def _score_rsi(
        self, indicators: Indicators, score: int, reasons: list[str]
    ) -> tuple[int, list[str]]:
        rsi = indicators.rsi
        if rsi is None:
            return score, reasons

        if rsi < settings.RSI_OVERSOLD_STRONG:
            score += 2
            reasons.append(f"RSI at {rsi} (oversold)")
        elif rsi < settings.RSI_OVERSOLD_MILD:
            score += 1
            reasons.append(f"RSI at {rsi} (mildly oversold)")
        elif rsi > settings.RSI_OVERBOUGHT_STRONG:
            score -= 2
            reasons.append(f"RSI at {rsi} (overbought)")
        elif rsi > settings.RSI_OVERBOUGHT_MILD:
            score -= 1
            reasons.append(f"RSI at {rsi} (mildly overbought)")
        else:
            reasons.append(f"RSI neutral at {rsi}")

        return score, reasons

    def _score_macd(
        self, indicators: Indicators, score: int, reasons: list[str]
    ) -> tuple[int, list[str]]:
        macd = indicators.macd
        if macd.histogram is None:
            return score, reasons

        if macd.histogram > 0:
            score += 2
            reasons.append("MACD bullish crossover detected")
        elif macd.histogram < 0:
            score -= 2
            reasons.append("MACD bearish crossover detected")
        else:
            reasons.append("MACD shows no clear trend")

        return score, reasons

    def _score_sma(
        self,
        indicators: Indicators,
        current_price: float,
        score: int,
        reasons: list[str],
    ) -> tuple[int, list[str]]:
        sma = indicators.sma

        sma_50 = sma.day_50
        if sma_50 is not None:
            if current_price > sma_50:
                score += 1
                reasons.append(
                    f"price above 50-day SMA (${current_price:.2f} > ${sma_50:.2f})"
                )
            elif current_price < sma_50:
                score -= 1
                reasons.append(
                    f"price below 50-day SMA (${current_price:.2f} < ${sma_50:.2f})"
                )

        sma_200 = sma.day_200
        if sma_200 is not None:
            if current_price > sma_200:
                score += 1
                reasons.append(
                    f"price above 200-day SMA (${current_price:.2f} > ${sma_200:.2f})"
                )
            elif current_price < sma_200:
                score -= 1
                reasons.append(
                    f"price below 200-day SMA (${current_price:.2f} < ${sma_200:.2f})"
                )

        return score, reasons

    def _determine_action(self, score: int) -> SignalAction:
        if score >= self.buy_threshold:
            return SignalAction.BUY
        elif score <= self.sell_threshold:
            return SignalAction.SELL
        return SignalAction.HOLD

    def _calculate_confidence(self, score: int) -> int:
        raw = abs(score) * self.confidence_multiplier
        return min(raw, self.max_confidence)
