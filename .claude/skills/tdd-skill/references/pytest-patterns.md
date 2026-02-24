# pytest Patterns Reference

## Fixture Scopes

| Scope | Runs | Use For |
|-------|------|---------|
| `function` (default) | Each test | Fresh state per test |
| `module` | Once per file | Shared read-only state |
| `session` | Once per run | Expensive setup (DB, server) |

```python
@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def session(db_engine):
    with Session(db_engine) as s:
        yield s
        s.rollback()   # reset state after each test
```

---

## Parametrized Fixtures

Run the same test against multiple configurations:

```python
@pytest.fixture(params=["sqlite", "postgresql"])
def db_url(request):
    if request.param == "sqlite":
        return "sqlite:///:memory:"
    return os.environ["TEST_POSTGRES_URL"]

def test_user_saved(db_url):
    # runs twice — once per db backend
    db = Database(db_url)
    ...
```

---

## Factory Fixtures

Use factory functions to build test objects with sensible defaults:

```python
@pytest.fixture
def make_user():
    def _make(name="Alice", role="user", active=True):
        return User(name=name, role=role, active=active)
    return _make

def test_admin_can_delete(make_user):
    admin = make_user(role="admin")
    assert admin.can_delete()

def test_inactive_user_cannot_login(make_user):
    user = make_user(active=False)
    assert not user.can_login()
```

---

## Async Tests (pytest-asyncio)

```bash
uv add --dev pytest-asyncio
```

```python
# pytest.ini or pyproject.toml
# asyncio_mode = auto   ← sets all tests to async by default

import pytest

@pytest.mark.asyncio
async def test_fetch_data():
    result = await fetch_data("https://api.example.com/users")
    assert result["status"] == "ok"
```

### Async FastAPI with TestClient

```python
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_root_async():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
```

---

## Mocking Patterns

### Patch a module-level function

```python
def test_send_email(mocker):
    mock_send = mocker.patch("myapp.email.send_email")
    trigger_welcome_email("alice@example.com")
    mock_send.assert_called_once_with("alice@example.com", subject="Welcome!")
```

### Patch time (for deterministic tests)

```python
def test_token_expiry(mocker):
    mocker.patch("time.time", return_value=1_000_000)
    token = generate_token(ttl=3600)
    assert token.expires_at == 1_003_600
```

### AsyncMock

```python
async def test_async_service(mocker):
    mocker.patch("myapp.service.fetch", new_callable=mocker.AsyncMock,
                 return_value={"data": "ok"})
    result = await process()
    assert result == "ok"
```

### Context manager mock

```python
def test_file_processing(mocker):
    mock_open = mocker.mock_open(read_data="line1\nline2")
    mocker.patch("builtins.open", mock_open)
    result = count_lines("any_file.txt")
    assert result == 2
```

---

## Exception Testing

```python
def test_divide_by_zero_raises():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)

def test_invalid_input_raises_type_error():
    with pytest.raises(TypeError):
        add("a", 1)
```

---

## Markers

```python
# pytest.ini
# markers =
#     unit: Unit tests (no I/O)
#     integration: Integration tests (I/O allowed)
#     slow: Slow-running tests (>1s)
#     wip: Work in progress

@pytest.mark.slow
def test_full_pipeline():
    ...

@pytest.mark.integration
def test_database_round_trip():
    ...
```

Run selectively:
```bash
pytest -m "unit"           # only unit tests
pytest -m "not slow"       # exclude slow tests
pytest -m "integration"    # only integration
```

---

## conftest.py: Shared Fixtures

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

Fixtures in `conftest.py` are available to all tests in the same directory and below — no imports needed.

---

## Coverage Configuration

```ini
# pytest.ini
[pytest]
addopts =
    --cov=.
    --cov-report=term-missing
    --cov-report=html
    --cov-branch
    --cov-fail-under=80
```

```ini
# .coveragerc
[run]
source = .
branch = True
omit =
    */tests/*
    */.venv/*
    */.claude/*

[html]
directory = htmlcov
```

View HTML report: `open htmlcov/index.html`
