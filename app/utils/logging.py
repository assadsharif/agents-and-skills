"""
Stock Signal API - Structured JSON Logging

Configures structured logging with JSON format for production observability.
Logs include: timestamp, level, logger name, message, and extra context fields.
"""

import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON for structured log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include extra context fields if present
        for key in ("ticker", "cache_key", "cache_hit", "response_time_ms",
                     "status_code", "data_source", "attempt", "error"):
            value = getattr(record, key, None)
            if value is not None:
                log_entry[key] = value

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with JSON formatter for all app loggers."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger("app")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False
