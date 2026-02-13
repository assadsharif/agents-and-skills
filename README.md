# Stock Signal API

REST API for stock trading signals based on technical analysis.

Provides buy/sell/hold recommendations with confidence levels and reasoning based on technical indicators (RSI, MACD, SMA, EMA) calculated from historical price data.

## Features

- **Trading Signals**: Get buy/sell/hold signals for US stocks (NYSE, NASDAQ)
- **Technical Indicators**: View RSI, MACD, SMA, and EMA calculations
- **Signal Reasoning**: Understand why each signal was generated
- **Fast Response**: <2s for cached data, 15-minute cache TTL
- **Graceful Degradation**: Handles data source failures and partial data

## Quick Start

### Prerequisites

- Python 3.11+
- pip package manager
- Internet connection (for fetching stock data)

### Installation

```bash
# Clone repository
cd /path/to/stock-signal-api

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the API

```bash
# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server running at: http://localhost:8000
```

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Get trading signal for Apple (AAPL)
curl http://localhost:8000/signal/AAPL

# View technical indicators
curl http://localhost:8000/indicators/AAPL
```

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### `/signal/{ticker}` - Get Trading Signal

Returns buy/sell/hold signal with confidence level and reasoning.

```bash
curl http://localhost:8000/signal/AAPL
```

Response:
```json
{
  "ticker": "AAPL",
  "signal": "BUY",
  "confidence": 80,
  "reasoning": "Strong BUY signal: RSI at 28.5 (oversold), MACD bullish crossover detected, price above 50-day SMA ($175.20 > $172.50)",
  "timestamp": "2026-02-13T14:30:00Z",
  "data_freshness": "2026-02-13T14:15:00Z",
  "current_price": 175.20,
  "indicators": {
    "rsi": 28.5,
    "macd": { "line": 1.25, "signal": 0.95, "histogram": 0.30 },
    "sma": { "20_day": 170.50, "50_day": 172.50, "200_day": 165.00 },
    "ema": { "12_day": 173.80, "26_day": 171.20 }
  }
}
```

### `/indicators/{ticker}` - Get Technical Indicators

Returns calculated technical indicators without generating a signal.

```bash
curl http://localhost:8000/indicators/AAPL
```

Response:
```json
{
  "ticker": "AAPL",
  "calculated_at": "2026-02-13T14:30:00Z",
  "current_price": 175.20,
  "indicators": {
    "rsi": 28.5,
    "macd": { "line": 1.25, "signal": 0.95, "histogram": 0.30 },
    "sma": { "20_day": 170.50, "50_day": 172.50, "200_day": 165.00 },
    "ema": { "12_day": 173.80, "26_day": 171.20 }
  }
}
```

### `/health` - Health Check

Returns service health status and data source availability.

```bash
curl http://localhost:8000/health
```

## Technical Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.100+
- **Data Source**: Yahoo Finance (via yfinance)
- **Indicators**: pandas-ta
- **Caching**: cachetools (in-memory, 15-minute TTL)
- **Testing**: pytest

## Project Structure

```
app/
├── main.py              # FastAPI app, CORS, response-time middleware
├── config.py            # Pydantic settings (cache, indicators, thresholds)
├── models/
│   ├── stock.py         # Stock, PriceData, Exchange
│   ├── indicator.py     # Indicators, MACD, SMA, EMA, IndicatorResponse
│   └── signal.py        # Signal, SignalAction
├── services/
│   ├── cache_service.py         # TTLCache with hit/miss stats
│   ├── data_fetcher.py          # yfinance async wrapper with retry
│   ├── indicator_calculator.py  # pandas-ta RSI/MACD/SMA/EMA
│   └── signal_generator.py      # Rule-based scoring + reasoning
├── api/
│   ├── routes/
│   │   ├── health.py      # GET /health
│   │   ├── signals.py     # GET /signal/{ticker}
│   │   └── indicators.py  # GET /indicators/{ticker}
│   ├── dependencies.py    # DI singletons
│   └── errors.py          # Custom exceptions + handlers
└── utils/
    ├── validators.py      # Ticker validation
    └── logging.py         # JSON structured logging

tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
└── fixtures/            # Test fixtures
```

## Development

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

## Performance

- **Cached requests**: <100ms typical (target: <2s)
- **Uncached requests**: <1s typical
- **Cache hit rate**: >80% for repeated queries
- **Throughput**: 100+ requests/hour

## Error Handling

- **400**: Invalid ticker symbol
- **404**: Ticker not found
- **503**: Data source unavailable (with retry-after)

## Limitations (MVP)

- US stocks only (NYSE, NASDAQ)
- Daily data only (no intraday)
- 15-minute data freshness
- Single-instance deployment (in-memory cache)

## Documentation

- **Feature Spec**: `specs/001-stock-signal-api/spec.md`
- **Implementation Plan**: `specs/001-stock-signal-api/plan.md`
- **API Contract**: `specs/001-stock-signal-api/contracts/openapi.yaml`
- **Quick Start Guide**: `specs/001-stock-signal-api/quickstart.md`

## License

MIT

## Support

For issues and questions, see documentation in `specs/001-stock-signal-api/`
