---
name: pytest-tdd
description: "Comprehensive pytest and Test-Driven Development (TDD) toolkit. Use when: (1) Setting up pytest in a Python project, (2) Following TDD Red-Green-Refactor workflow, (3) Writing tests with fixtures, parametrization, or mocking, (4) Organizing test suites, (5) Running tests in watch mode, or (6) Any pytest-related testing task requiring TDD best practices. Triggers include TDD, pytest, test first, Red Green Refactor, write tests, test driven, property based testing."
version: "1.0"
last_verified: "2025-01"
---

# Pytest TDD

**Senior Python Engineer executing strict Test-Driven Development.**

Generate production-grade code via TDD — no tutorials, no theory dumps. This skill enforces the Red-Green-Refactor discipline while providing comprehensive pytest patterns and tooling.

## What This Skill Does

- Execute Red-Green-Refactor TDD cycles with strict discipline
- Generate failing tests BEFORE implementation
- Initialize pytest in any Python project with TDD-optimized configuration
- Write pytest suites (fixtures, parametrize, mocking, property-based)
- Apply TDD to APIs (FastAPI/Flask), databases (SQLModel/SQLAlchemy), and architecture
- Organize test suites (unit, integration, e2e)
- Run tests in watch mode for continuous feedback
- Refactor legacy code safely via characterization tests

## What This Skill Does NOT Do

- Teach TDD theory or philosophy
- Generate implementation without tests first
- Write unittest-style tests (unless legacy/interview context requires it)
- Create UI/browser tests (use Playwright/Selenium skills instead)
- Perform load testing or benchmarking
- Production deployment or CI/CD pipeline setup
- Security auditing or penetration testing

## Required Clarifications

Before generating, ask:

1. **Project context**: "What framework/stack? (FastAPI, Flask, Django, plain Python)"
2. **Test scope**: "Unit tests, integration tests, or both?"
3. **Existing code?**: "Is this greenfield or adding tests to existing code?"

### Optional Clarifications

4. **CI requirements**: "Any CI constraints (timeout, coverage threshold)?" (ask if mentioned)
5. **Mocking boundaries**: "Which external services need mocking?" (ask if integration-heavy)

### Before Asking

Check existing context first:
- Review conversation for framework/stack mentions
- Infer from file names (e.g., `main.py` with FastAPI imports)
- Check pyproject.toml/requirements.txt if available
- Only ask what cannot be determined from context

---

## Core TDD Rules

**These are NON-NEGOTIABLE:**

1. **ALWAYS write tests BEFORE implementation** (RED → GREEN → REFACTOR)
2. **Start with error paths, NOT happy path**
3. **Tests must be:** Fast (ms), Deterministic (no flakiness), Isolated (no shared state)
4. **Use pytest as primary framework**
5. **Follow AAA** (Arrange-Act-Assert) or Given-When-Then structure
6. **Use parametrized tests instead of loops**
7. **Prefer fewer high-signal tests over many weak tests**
8. **If a test is slow, flaky, or unclear — refactor the TEST first**

## Output Format

**Every TDD response follows this structure:**

1. **RED:** Start with FAILING TESTS only
2. **GREEN:** Write MINIMAL implementation to pass
3. **REFACTOR:** Improve code AND tests if needed
4. **NOTES:** Brief decision notes ONLY if non-obvious
5. **Never dump theory or long explanations**

---

## Quick Start

### Initialize pytest in a project

```bash
python scripts/init_pytest.py /path/to/project
```

Creates: test directory structure, `pytest.ini`, `.coveragerc`, `conftest.py`, example tests.

### Run TDD watch mode

```bash
./scripts/run_tdd_cycle.sh              # Watch all tests
./scripts/run_tdd_cycle.sh tests/unit   # Watch specific tests
./scripts/run_tdd_cycle.sh --lf         # Watch last failed
```

## TDD Workflow: Red-Green-Refactor

### 1. RED: Write a Failing Test

Write the smallest possible test that fails because the functionality doesn't exist.

```python
def test_calculate_total_price():
    cart = ShoppingCart()
    cart.add_item("Apple", price=1.00, quantity=3)
    assert cart.calculate_total(tax_rate=0.1) == 3.30  # Fails - doesn't exist yet
```

### 2. GREEN: Write Minimum Code to Pass

Write just enough code to make the test pass. Don't worry about perfect design.

```python
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, name: str, price: float, quantity: int):
        self.items.append({"name": name, "price": price, "quantity": quantity})

    def calculate_total(self, tax_rate: float = 0.0) -> float:
        subtotal = sum(item["price"] * item["quantity"] for item in self.items)
        return round(subtotal * (1 + tax_rate), 2)
```

### 3. REFACTOR: Improve Code Quality

Improve the design while keeping tests green.

```python
from dataclasses import dataclass

@dataclass
class CartItem:
    name: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

class ShoppingCart:
    def __init__(self):
        self.items: list[CartItem] = []

    def add_item(self, name: str, price: float, quantity: int):
        self.items.append(CartItem(name, price, quantity))

    def calculate_total(self, tax_rate: float = 0.0) -> float:
        return round(sum(item.subtotal for item in self.items) * (1 + tax_rate), 2)
```

**See:** `references/tdd-workflow.md` for detailed patterns.

---

## Must Follow

- [ ] Tests written before implementation
- [ ] Error paths tested before happy path
- [ ] Clear test naming (`test_<unit>_<scenario>_<expected>`)
- [ ] Dependency injection for testable design
- [ ] No hidden side effects in modules
- [ ] Property-based testing (hypothesis) for non-trivial logic
- [ ] Mocking only at boundaries (external APIs, time, randomness)
- [ ] Each test runs in isolation (no shared mutable state)

## Must Avoid

- Writing implementation before tests
- Testing implementation details instead of behavior
- Over-mocking (mocking your own code)
- Shared state between tests
- Flaky tests (time-dependent, order-dependent, network-dependent)
- God-objects and tight coupling
- `sleep()` in tests
- Ignoring test smells (duplicate setup, assertion-free tests, commented tests)

---

## Essential Patterns

### Fixtures: Reusable Test Setup

```python
@pytest.fixture
def database():
    db = Database("test.db")
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def user(database):
    user = User("alice", "password123")
    database.save(user)
    return user

def test_user_login(user):
    result = login("alice", "password123")
    assert result.success
```

**See:** `references/fixtures-guide.md`

### Parametrization: Test Multiple Inputs

```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (10, 20, 30),
    (-5, 5, 0),
])
def test_addition(a, b, expected):
    assert add(a, b) == expected
```

**See:** `references/parametrization-guide.md`

### Mocking: Isolate Code Under Test

```python
def test_fetch_user(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mocker.patch("requests.get", return_value=mock_response)

    result = fetch_user(1)
    assert result == {"id": 1, "name": "Alice"}
```

**See:** `references/mocking-guide.md`

---

## Output Checklist

Before delivering, verify ALL items:

### Functional
- [ ] All tests fail before implementation (RED confirmed)
- [ ] All tests pass after implementation (GREEN confirmed)
- [ ] Refactoring preserves passing tests
- [ ] Edge cases covered (empty inputs, None, boundaries)

### Quality
- [ ] Test names describe behavior, not implementation
- [ ] No hardcoded test data (use factories/fixtures)
- [ ] Parametrized tests for similar scenarios
- [ ] Coverage of error paths matches or exceeds happy paths

### Standards
- [ ] pytest conventions followed (conftest.py, fixtures, markers)
- [ ] No print() debugging left in tests
- [ ] Tests run in <5 seconds total (unit tests)
- [ ] No external dependencies in unit tests

---

## Quality Gate Checklist

Before marking tests as complete, verify:

- [ ] All tests pass (`pytest` exits with code 0)
- [ ] No `@pytest.mark.skip` without ticket/issue reference
- [ ] Each test has one clear assertion focus
- [ ] Tests run independently (any order works)
- [ ] Mocks only cover external dependencies
- [ ] No hardcoded secrets or credentials
- [ ] Coverage meets project threshold (if defined)
- [ ] `tests/` directory with `unit/` and `integration/` subdirectories
- [ ] `pytest.ini` with markers and coverage configuration
- [ ] `.coveragerc` with source and exclusion patterns
- [ ] `conftest.py` with shared fixtures
- [ ] Tests following AAA pattern (Arrange-Act-Assert)
- [ ] Descriptive test names: `test_<action>_<condition>_<result>`
- [ ] Coverage report accessible via `htmlcov/index.html`

---

## Error Handling Guidance

| Scenario | Action |
|----------|--------|
| Existing code has no tests | Write characterization tests first, then refactor |
| Test is flaky | Identify source (time, ordering, network), fix or mark `@pytest.mark.flaky` |
| Legacy unittest code | Keep as-is unless migration requested; add new tests in pytest |
| CI timeout | Split slow tests with `@pytest.mark.slow`, run separately |
| Coverage gaps | Prioritize untested error paths over more happy-path tests |

---

## Essential Commands

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=src         # With coverage
pytest --lf              # Last failed
pytest -k "keyword"      # Filter by keyword
pytest -m "unit"         # Filter by marker
pytest -x                # Stop on first failure
```

**See:** `references/running-tests.md` for full command reference.

## Dependencies

### Required
- Python 3.10+
- pytest >= 7.0

### Recommended
- pytest-cov (coverage reporting)
- pytest-mock (mocker fixture)
- pytest-watch (watch mode)
- hypothesis (property-based testing)
- factory-boy (test data factories)
- faker (realistic test data)

### Framework-Specific
- httpx / fastapi.testclient (FastAPI testing)
- pytest-django (Django testing)
- pytest-asyncio (async code testing)

### Installation

```bash
# Using pip
pip install pytest pytest-cov pytest-mock pytest-watch

# Using uv
uv add --dev pytest pytest-cov pytest-mock pytest-watch
```

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Pytest Docs | https://docs.pytest.org/ | Core API, fixtures, plugins |
| pytest-cov | https://pytest-cov.readthedocs.io/ | Coverage configuration |
| pytest-mock | https://pytest-mock.readthedocs.io/ | Mocker fixture patterns |
| hypothesis | https://hypothesis.readthedocs.io/ | Property-based testing |
| factory-boy | https://factoryboy.readthedocs.io/ | Test data factories |
| Coverage.py | https://coverage.readthedocs.io/ | .coveragerc options |
| FastAPI testing | https://fastapi.tiangolo.com/tutorial/testing/ | TestClient patterns |
| SQLModel testing | https://sqlmodel.tiangolo.com/tutorial/ | DB test patterns |

For patterns not covered here, fetch from the official pytest docs.

---

## Reference Guides

| File | When to Read |
|------|--------------|
| `references/tdd-workflow.md` | Detailed Red-Green-Refactor patterns |
| `references/backend-api-tdd.md` | Testing FastAPI/Flask endpoints |
| `references/database-tdd.md` | SQLModel/SQLAlchemy test patterns |
| `references/fixtures-guide.md` | Fixture scopes, factories, advanced usage |
| `references/parametrization-guide.md` | Data-driven testing, dynamic generation |
| `references/mocking-guide.md` | pytest-mock, spies, AsyncMock, isolation |
| `references/architecture-via-tdd.md` | Using TDD to drive clean architecture |
| `references/running-tests.md` | Command-line options, filtering, debugging |
| `references/configuration.md` | pytest.ini, pyproject.toml, .coveragerc |
| `references/test-organization.md` | Directory structure, naming, markers |
| `references/anti-patterns.md` | Common mistakes and how to avoid them |
| `references/troubleshooting.md` | Common pytest issues and solutions |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_pytest.py` | Initialize pytest in a project with best practices |
| `scripts/run_tdd_cycle.sh` | Run tests in watch mode for TDD workflow |

---

## Best Practices Summary

### Do

- Write one test at a time, make it pass, then write the next
- Test behavior, not implementation details
- Use fixtures for setup/teardown
- Run tests every 30-60 seconds during development
- Keep tests fast (mock external dependencies)
- Make tests independent (run in any order)

### Don't

- Write tests after all code is complete
- Test private methods or implementation details
- Skip the refactor step when tests are green
- Ignore failing tests or comment them out
- Over-mock your own business logic
- Create tests that depend on execution order

**See:** `references/anti-patterns.md` for comprehensive anti-pattern guide.

---

## Quick TDD Cycle Reference

```
┌─────────────────────────────────────────┐
│  1. RED    → Write failing test         │
│  2. GREEN  → Write minimum code to pass │
│  3. REFACTOR → Improve design           │
│  4. COMMIT → Save progress              │
│  5. REPEAT                              │
└─────────────────────────────────────────┘
```

**Target rhythm:** 2-10 minutes per cycle.

---

## Keeping Current

- **Last verified:** 2025-01
- **Check for updates:** https://docs.pytest.org/en/stable/changelog.html
- Pytest follows semantic versioning; minor updates rarely break tests
- When upgrading pytest, run `pytest --collect-only` first to check for issues
