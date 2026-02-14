# Performance Optimization

Vectorization, memory reduction, efficient patterns, and anti-patterns.

---

## Vectorization (Most Important)

Always prefer vectorized operations over loops.

### Instead of `.apply()` with Lambda

```python
# Slow
df["result"] = df["col"].apply(lambda x: x * 2 + 1)

# Fast (vectorized)
df["result"] = df["col"] * 2 + 1
```

### Instead of `iterrows()`

```python
# Very slow
for i, row in df.iterrows():
    df.loc[i, "result"] = row["a"] + row["b"]

# Fast (vectorized)
df["result"] = df["a"] + df["b"]
```

### Conditional Operations

```python
# Slow
df["label"] = df["score"].apply(lambda x: "pass" if x > 70 else "fail")

# Fast
df["label"] = np.where(df["score"] > 70, "pass", "fail")

# Multiple conditions
df["grade"] = np.select(
    [df["score"] >= 90, df["score"] >= 70, df["score"] >= 50],
    ["A", "B", "C"],
    default="F",
)
```

### String Operations

```python
# Slow
df["clean"] = df["name"].apply(lambda x: x.lower().strip())

# Fast (vectorized string ops)
df["clean"] = df["name"].str.lower().str.strip()
```

---

## Memory Optimization

### Check Memory Usage

```python
df.info(memory_usage="deep")
df.memory_usage(deep=True)
df.memory_usage(deep=True).sum() / 1024**2  # MB
```

### Downcast Numeric Types

```python
# Integers
df["int_col"] = pd.to_numeric(df["int_col"], downcast="integer")
# Automatically picks int8/int16/int32 based on range

# Floats
df["float_col"] = pd.to_numeric(df["float_col"], downcast="float")
```

### Use Categorical for Low-Cardinality Strings

```python
# Before: object dtype — stores each string separately
df["status"].dtype  # object, ~800 bytes for 100 rows

# After: category dtype — stores unique values once
df["status"] = df["status"].astype("category")
# ~200 bytes for 100 rows (10-100x reduction)

# Best when: nunique / len < 0.5 (less than 50% unique)
```

### Nullable Types (Avoid Object for Numeric with NaN)

```python
# Bad: int column with NaN becomes float64
df["id"] = pd.array([1, 2, None, 4], dtype="Int64")  # Nullable integer

# Good: explicit nullable types
df = df.astype({
    "int_col": "Int64",
    "float_col": "Float64",
    "bool_col": "boolean",
    "str_col": "string",
})
```

### Read Only What You Need

```python
# Read subset of columns
df = pd.read_csv("data.csv", usecols=["col1", "col2", "col3"])

# Read subset of rows
df = pd.read_csv("data.csv", nrows=10000)

# Specify dtypes upfront (avoid inference)
df = pd.read_csv("data.csv", dtype={
    "id": "int32",
    "name": "string",
    "category": "category",
    "amount": "float32",
})
```

---

## Efficient Patterns

### Build Then Concat (Not Iterative Append)

```python
# Slow — copies entire DataFrame each iteration
df = pd.DataFrame()
for item in items:
    df = pd.concat([df, process(item)])

# Fast — collect, then concat once
frames = [process(item) for item in items]
df = pd.concat(frames, ignore_index=True)
```

### Use `.pipe()` for Method Chaining

```python
result = (
    df
    .pipe(clean_names)
    .pipe(filter_valid)
    .pipe(add_features)
    .pipe(aggregate_results)
)
```

### Use `.query()` Over Boolean Indexing for Readability

```python
# Verbose
df[(df["age"] > 25) & (df["city"] == "NYC") & (df["score"] > 80)]

# Clean
df.query("age > 25 and city == 'NYC' and score > 80")
```

### Use `.eval()` for Complex Expressions

```python
# Standard (creates intermediate arrays)
df["result"] = (df["a"] + df["b"]) / (df["c"] - df["d"])

# Efficient for large DataFrames (less memory)
df.eval("result = (a + b) / (c - d)", inplace=True)
```

### Merge Validation

```python
# Always validate merges to catch unexpected duplicates
result = pd.merge(left, right, on="key", validate="one_to_one")
assert len(result) == len(left), f"Merge changed row count: {len(left)} → {len(result)}"
```

---

## Anti-Patterns

### 1. Chained Indexing (SettingWithCopyWarning)

```python
# Bad — may not work, raises warning
df[df["A"] > 0]["B"] = 1

# Good — single indexing operation
df.loc[df["A"] > 0, "B"] = 1
```

### 2. Growing DataFrame in a Loop

```python
# Bad — O(n²) complexity
for row in data:
    df = pd.concat([df, pd.DataFrame([row])])

# Good — O(n) complexity
df = pd.DataFrame(data)
```

### 3. Using `inplace=True`

```python
# Deprecated pattern — avoid
df.drop(columns=["col"], inplace=True)

# Preferred
df = df.drop(columns=["col"])
```

### 4. Using `object` dtype for Everything

```python
# Bad — slow, uses more memory
df = pd.read_csv("data.csv")  # All strings become object

# Good — specify types
df = pd.read_csv("data.csv", dtype={
    "id": "int32",
    "name": "string",
    "active": "boolean",
})
```

### 5. Unnecessary `.apply()`

```python
# Bad — Python-level loop
df["year"] = df["date"].apply(lambda x: x.year)

# Good — vectorized accessor
df["year"] = df["date"].dt.year
```

### 6. Not Using PyArrow Backend

```python
# For better performance with nullable types (pandas 2.0+)
df = pd.read_csv("data.csv", dtype_backend="pyarrow")
```

---

## Benchmarking

```python
import timeit

# Time a pandas operation
%timeit df.groupby("key")["val"].sum()

# Compare approaches
%timeit df["col"].apply(lambda x: x * 2)      # Slow
%timeit df["col"] * 2                           # Fast
```

---

## When to Use Alternatives

| Scenario | Alternative |
|----------|-------------|
| Data > RAM | Dask, Polars, or chunked reading |
| Heavy numeric computation | NumPy directly |
| SQL-like queries on large data | DuckDB with pandas integration |
| Distributed processing | PySpark, Dask |
| Speed-critical operations | Polars (Rust-based) |
