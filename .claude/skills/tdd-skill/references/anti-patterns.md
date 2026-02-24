# TDD Anti-Patterns

Common mistakes that undermine TDD. Recognise these and course-correct immediately.

---

## 1. Implementation Before Tests

**What it looks like:**
```python
# Writing all the code first...
class OrderProcessor:
    def process(self, order): ...
    def validate(self, order): ...
    def notify(self, order): ...

# ...then writing tests to match
def test_process():  # tests fit the code, not the other way around
    assert OrderProcessor().process(order) is not None
```

**Why it matters:** Tests written after code confirm the code works but don't drive better design. They become documentation, not discipline.

**Fix:** Stop. Delete the implementation. Write the test first.

---

## 2. Testing Private Methods / Implementation Details

**What it looks like:**
```python
def test_uses_quicksort_algorithm():
    sorter = Sorter()
    sorter._quicksort([3, 1, 2])  # private method
    ...

def test_internal_cache_populated():
    service = UserService()
    service.get_user(1)
    assert service._cache  # internal state
```

**Why it matters:** Tests break on refactoring even when behavior is unchanged, creating friction and discouraging cleanup.

**Fix:** Test public interfaces and observable behavior only.

---

## 3. Skipping the Refactor Step

**What it looks like:**
```python
# GREEN — tests pass, move on immediately to next feature
def calculate_discount(price, user_type, loyalty_years, promo_code, is_employee):
    # 50-line function, no clear logic, but tests pass...
    ...
```

**Why it matters:** Technical debt accumulates. Tests are green but the code is a mess that's hard to extend.

**Fix:** After GREEN, always ask: "Can this be cleaner?" Small refactors compound into good design.

---

## 4. One Giant Test Per Feature

**What it looks like:**
```python
def test_user_registration():
    # 60 lines
    # Tests signup, validation, email, DB save, and welcome message
    # All in one function
```

**Why it matters:** When it fails, you don't know why. It's hard to maintain and impossible to reuse setup.

**Fix:** One assertion focus per test. Split into `test_registration_validates_email`, `test_registration_saves_to_db`, etc.

---

## 5. Shared Mutable State Between Tests

**What it looks like:**
```python
cart = ShoppingCart()  # module-level — shared across all tests

def test_add_item():
    cart.add_item("Apple", 1.0, 2)
    assert len(cart.items) == 1

def test_add_second_item():
    cart.add_item("Banana", 0.5, 1)
    assert len(cart.items) == 1  # FAILS — items from test_add_item still there
```

**Why it matters:** Tests pass or fail depending on execution order. Impossible to run in isolation.

**Fix:** Create fresh instances in fixtures, never at module level.

---

## 6. Over-Mocking Business Logic

**What it looks like:**
```python
def test_calculate_discount(mocker):
    mocker.patch("myapp.pricing.apply_loyalty", return_value=10)
    mocker.patch("myapp.pricing.apply_promo", return_value=5)
    mocker.patch("myapp.pricing.apply_employee", return_value=2)
    # You've mocked the entire feature you're supposed to be testing
```

**Why it matters:** The test passes even if the logic is completely wrong. You're testing the mock, not the code.

**Fix:** Mock only external boundaries — HTTP calls, database I/O, file system, time, randomness. Never mock your own pure functions.

---

## 7. `sleep()` in Tests

**What it looks like:**
```python
def test_background_job_completes():
    start_job()
    time.sleep(5)  # hope it finishes
    assert job_result() == "done"
```

**Why it matters:** Slow, flaky, and wrong — if the job takes 6 seconds, the test lies.

**Fix:** Use explicit polling, event signaling, or mock `time.time` for determinism.

---

## 8. Commented-Out or Skipped Tests Without Context

**What it looks like:**
```python
@pytest.mark.skip  # broken
def test_payment_gateway():
    ...

# def test_refund_flow():
#     assert ...  # TODO fix later
```

**Why it matters:** Silently reduces coverage confidence. "Later" never comes.

**Fix:** Either fix the test immediately, or document with a ticket reference:
```python
@pytest.mark.skip(reason="Blocked by JIRA-1234 — payment gateway integration")
```

---

## 9. Tests That Depend on Execution Order

**What it looks like:**
```python
def test_create_user():
    global user_id
    user_id = db.create_user("alice")

def test_delete_user():
    db.delete_user(user_id)  # fails if test_create_user didn't run first
```

**Fix:** Each test must own its full setup via fixtures. Use `scope="function"` for anything that modifies state.

---

## 10. Writing Too Many Tests Before Running

**What it looks like:**
- Writing 10 failing tests before any implementation
- Bulk test generation from a spec before seeing any code run

**Why it matters:** You lose the feedback loop. TDD's power comes from the tight RED → GREEN cycle.

**Fix:** One test at a time. Run after every small change.
