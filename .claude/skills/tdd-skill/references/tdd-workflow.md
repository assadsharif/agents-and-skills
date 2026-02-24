# TDD Workflow: Full Examples

## RED → GREEN → REFACTOR: ShoppingCart

### Step 1 — RED: Write the Failing Test

Write the smallest test that fails because the code doesn't exist yet.

```python
# tests/unit/test_cart.py
def test_calculate_total_with_tax_returns_correct_amount():
    cart = ShoppingCart()
    cart.add_item("Apple", price=1.00, quantity=3)

    assert cart.calculate_total(tax_rate=0.1) == 3.30  # FAILS — class doesn't exist
```

Run and confirm failure:
```bash
pytest tests/unit/test_cart.py -v
# Expected: FAILED (ImportError or AttributeError)
```

Write error-path test first, before the happy path:
```python
def test_calculate_total_empty_cart_returns_zero():
    assert ShoppingCart().calculate_total() == 0.0
```

### Step 2 — GREEN: Minimum Code to Pass

Write just enough to make both tests pass. Hard-coding is fine at this stage.

```python
# cart.py
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, name: str, price: float, quantity: int):
        self.items.append({"name": name, "price": price, "quantity": quantity})

    def calculate_total(self, tax_rate: float = 0.0) -> float:
        subtotal = sum(item["price"] * item["quantity"] for item in self.items)
        return round(subtotal * (1 + tax_rate), 2)
```

Run and confirm green:
```bash
pytest tests/unit/test_cart.py -v
# Expected: 2 passed
```

### Step 3 — REFACTOR: Improve Design

The tests are green — now improve the design. Run tests after every change.

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
        return round(sum(i.subtotal for i in self.items) * (1 + tax_rate), 2)
```

Confirm still green:
```bash
pytest tests/unit/test_cart.py -v
# Expected: 2 passed (same tests, better code)
```

---

## TDD Patterns

### Triangulation: Force a General Solution

Write multiple tests with different inputs to avoid hard-coding:

```python
def test_add_positive():   assert add(2, 3) == 5
def test_add_negative():   assert add(-2, -3) == -5
def test_add_mixed():      assert add(-2, 5) == 3
```

Each test forces the implementation toward a more general solution.

### Fake It Till You Make It

Start with the simplest possible return value, then generalize:

```python
# RED
def test_fib_zero(): assert fibonacci(0) == 0

# GREEN (fake it)
def fibonacci(n): return 0

# RED (add a test that breaks the fake)
def test_fib_one(): assert fibonacci(1) == 1

# GREEN (still faking)
def fibonacci(n): return n if n <= 1 else ...

# Continue adding tests until hard-coding is impossible
```

### Test List

Keep a running checklist of tests to write. One at a time.

```python
# TODO Tests:
# [x] test_empty_cart_total_is_zero
# [x] test_calculate_total_with_tax
# [ ] test_remove_item_from_cart
# [ ] test_apply_discount_code
# [ ] test_cart_total_with_multiple_items
```

---

## FastAPI TDD Example

```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

# RED: write first, before the endpoint exists
def test_create_item_returns_201(client):
    response = client.post("/items", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    assert response.json()["name"] == "Widget"

# GREEN: add the endpoint to main.py
# REFACTOR: extract business logic to service layer
```

---

## Watch Mode: Continuous Feedback

Keep tests running automatically as you type:

```bash
# Install
uv add --dev pytest-watch

# Start watch mode
ptw

# Watch specific directory
ptw tests/unit/

# Watch with coverage
ptw -- --cov=. --cov-report=term-missing
```

Target: tests re-run within 1 second of saving a file.
