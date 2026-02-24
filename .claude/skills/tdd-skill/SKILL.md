---
name: tdd-skill
description: >
  Test-Driven Development (TDD) skill for Python projects using pytest.
  Apply this skill whenever the user asks to: implement a feature, fix a bug,
  add tests, write unit/integration tests, set up pytest, or any task involving
  Python code that should be verified. Enforce the Red-Green-Refactor cycle —
  always write failing tests BEFORE implementation code. Use for FastAPI,
  plain Python, SQLModel, and async code. Triggers on: "add tests", "write TDD",
  "implement with tests", "set up pytest", "test-driven", or any feature request
  in a Python codebase.
---

# TDD Skill — Test-Driven Development with pytest

Senior Python engineer executing strict TDD. Tests come first. Always.

## What This Skill Does

- Enforce Red-Green-Refactor discipline on every feature or bug fix
- Initialize pytest in Python projects with TDD-optimized configuration
- Write failing tests first, then minimum implementation to pass
- Generate pytest fixtures, parametrize, mocking, and async test patterns
- Apply TDD to FastAPI routes, plain Python, databases, and CLI tools

## What This Skill Does NOT Do

- Generate implementation code without tests first
- Teach TDD theory at length — it acts on it
- Write browser/UI tests (use Playwright skill instead)
- Perform load testing, benchmarking, or security auditing
- Generate `unittest`-style tests (unless explicitly asked)

---

## Required Clarifications

Before generating, check the conversation for context. Only ask what cannot be inferred.

1. **Framework/stack** — FastAPI, Flask, Django, or plain Python?
2. **Test scope** — Unit tests, integration tests, or both?
3. **Greenfield or existing code?** — New feature or adding tests to existing code?

## Optional Clarifications

4. **Coverage threshold** — Is there a minimum % requirement? (ask if CI is mentioned)
5. **External services** — Which need mocking? (ask only if integration-heavy)

If the user doesn't answer, proceed with sensible defaults: unit + integration scope, no coverage threshold enforced, mock all HTTP and DB calls in unit tests.

---

## Core TDD Rules (Non-Negotiable)

1. **Tests BEFORE implementation** — RED → GREEN → REFACTOR, no exceptions
2. **Error paths first** — Test failure modes before the happy path
3. **One test at a time** — Make it pass, then write the next
4. **AAA structure** — Arrange → Act → Assert in every test
5. **Name tests descriptively** — `test_<action>_<condition>_<result>`

---

## Quick Start: Initialize pytest

```bash
python3 .claude/skills/pytest-tdd/scripts/init_pytest.py .
uv add --dev pytest pytest-cov pytest-mock httpx   # or: pip install ...
```

---

## TDD Workflow: Red-Green-Refactor

```
RED    → write the smallest test that fails for the right reason
GREEN  → write minimum code to make it pass (hard-code if needed)
REFACTOR → improve design while keeping all tests green
COMMIT → save progress, start next cycle (target: 2-10 min per cycle)
```

See `references/tdd-workflow.md` for full annotated code examples of each step.

---

## Core pytest Patterns

### Fixtures

```python
@pytest.fixture
def db():
    conn = Database(":memory:")
    conn.connect()
    yield conn          # teardown runs after yield
    conn.disconnect()

def test_user_saved(db):
    db.save(User("alice"))
    assert db.find("alice") is not None
```

### Parametrize

```python
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5), (-5, 5, 0), (0, 0, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Mocking (boundaries only)

```python
def test_fetch_user_calls_api(mocker):
    mock = mocker.patch("requests.get")
    mock.return_value.json.return_value = {"id": 1, "name": "Alice"}
    assert fetch_user(1)["name"] == "Alice"
```

See `references/pytest-patterns.md` for FastAPI TestClient, async tests, factories, and scope guide.

---

## Must Follow

- [ ] Write tests before implementation (confirm RED before GREEN)
- [ ] Start with error paths, not happy path
- [ ] Use `test_<action>_<condition>_<result>` naming
- [ ] Each test has one clear assertion focus
- [ ] Use fixtures for all shared setup — no copy-paste setup code
- [ ] Use `parametrize` instead of loops in tests
- [ ] Mock only at external boundaries (APIs, time, randomness)
- [ ] Tests run independently in any order (no shared mutable state)
- [ ] Unit tests complete in <5 seconds total

## Must Avoid

- Writing implementation before tests
- Testing private methods or internal implementation details
- Using `sleep()` in tests
- Shared global state between tests
- Over-mocking your own business logic
- Commenting out or skipping tests without a ticket reference
- Using `assert` outside test functions for validation
- Hardcoding credentials, API keys, or secrets in test fixtures (use env vars)

---

## Output Checklist (Before Delivering)

### Functional
- [ ] All tests fail before implementation (RED confirmed)
- [ ] All tests pass after implementation (GREEN confirmed)
- [ ] Refactoring did not break any tests
- [ ] Edge cases covered (empty inputs, None, boundary values)

### Quality
- [ ] Test names describe behavior, not implementation
- [ ] No hardcoded test data — use fixtures or factories
- [ ] Parametrized tests for equivalent scenarios
- [ ] Error paths covered as deeply as happy paths

### Structure
- [ ] `tests/unit/` and `tests/integration/` directories exist
- [ ] `conftest.py` in `tests/` with shared fixtures
- [ ] `pytest.ini` or `pyproject.toml` has markers and coverage config
- [ ] No `print()` debugging left in tests

---

## Error Handling Guide

| Scenario | Action |
|----------|--------|
| Existing code has no tests | Write characterization tests first, then refactor |
| Test is flaky (order/time/network) | Identify root cause, fix or mark `@pytest.mark.flaky` |
| CI timeout on slow tests | Mark with `@pytest.mark.slow`, run separately |
| Coverage gaps | Prioritize untested error paths over more happy-path tests |
| Legacy `unittest` code | Keep as-is; add new tests in pytest style |

---

## Essential Commands

```bash
pytest                  # Run all tests
pytest -v               # Verbose output
pytest --cov=.          # With coverage report
pytest --lf             # Last failed only
pytest -k "keyword"     # Filter by name
pytest -m "unit"        # Filter by marker
pytest -x               # Stop on first failure
uv run pytest           # Run via uv (recommended)
```

---

## Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| `pytest` | Test runner | Required |
| `pytest-cov` | Coverage reporting | Recommended |
| `pytest-mock` | `mocker` fixture | Recommended |
| `httpx` | FastAPI TestClient | FastAPI projects |
| `pytest-asyncio` | Async test support | Async code |
| `hypothesis` | Property-based testing | Non-trivial logic |
| `pytest-watch` | Watch mode (TDD flow) | Optional |

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Pytest Docs | https://docs.pytest.org/ | Core API, fixtures, plugins |
| pytest-cov | https://pytest-cov.readthedocs.io/ | Coverage configuration |
| pytest-mock | https://pytest-mock.readthedocs.io/ | Mocker fixture patterns |
| pytest-asyncio | https://pytest-asyncio.readthedocs.io/ | Async test patterns |
| hypothesis | https://hypothesis.readthedocs.io/ | Property-based testing |
| FastAPI testing | https://fastapi.tiangolo.com/tutorial/testing/ | TestClient patterns |

When a pattern is not covered here, fetch from https://docs.pytest.org/ before guessing.

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/tdd-workflow.md` | Full RED/GREEN/REFACTOR examples with annotated code |
| `references/pytest-patterns.md` | Async tests, FastAPI TestClient, factories, fixture scopes |
| `references/anti-patterns.md` | 10 common TDD mistakes with bad/good code examples |

---

## Keeping Current

- **Last verified**: 2026-02
- **pytest changelog**: https://docs.pytest.org/en/stable/changelog.html
- pytest follows semantic versioning — minor updates rarely break tests.
  When upgrading, run `pytest --collect-only` first to catch collection issues.
- When upgrading pytest-asyncio, check `asyncio_mode` setting — it changed in v0.21.
- For patterns not listed here, fetch from https://docs.pytest.org/ before guessing.
