"""Unit tests for ticker validation (app/utils/validators.py)."""

import pytest

from app.utils.validators import TickerValidationError, is_valid_ticker, validate_ticker


class TestValidateTicker:
    """Tests for validate_ticker()."""

    def test_valid_uppercase(self):
        assert validate_ticker("AAPL") == "AAPL"

    def test_valid_single_char(self):
        assert validate_ticker("A") == "A"

    def test_valid_five_chars(self):
        assert validate_ticker("ABCDE") == "ABCDE"

    def test_valid_alphanumeric(self):
        assert validate_ticker("BRK3") == "BRK3"

    def test_lowercase_converted(self):
        assert validate_ticker("aapl") == "AAPL"

    def test_mixed_case_converted(self):
        assert validate_ticker("aApL") == "AAPL"

    def test_whitespace_stripped(self):
        assert validate_ticker("  AAPL  ") == "AAPL"

    def test_empty_raises(self):
        with pytest.raises(TickerValidationError, match="cannot be empty"):
            validate_ticker("")

    def test_too_long_raises(self):
        with pytest.raises(TickerValidationError, match="too long"):
            validate_ticker("ABCDEF")

    def test_special_chars_raises(self):
        with pytest.raises(TickerValidationError, match="Invalid ticker"):
            validate_ticker("AB-C")

    def test_spaces_in_middle_raises(self):
        with pytest.raises(TickerValidationError, match="Invalid ticker"):
            validate_ticker("A B")

    def test_unicode_raises(self):
        with pytest.raises(TickerValidationError):
            validate_ticker("AB\u00e9")

    def test_sql_injection_raises(self):
        with pytest.raises(TickerValidationError):
            validate_ticker("'; DROP")

    def test_path_traversal_raises(self):
        with pytest.raises(TickerValidationError):
            validate_ticker("../etc")


class TestIsValidTicker:
    """Tests for is_valid_ticker() boolean wrapper."""

    def test_valid_returns_true(self):
        assert is_valid_ticker("AAPL") is True

    def test_invalid_returns_false(self):
        assert is_valid_ticker("") is False

    def test_too_long_returns_false(self):
        assert is_valid_ticker("TOOLONG") is False
