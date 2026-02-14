# Core Operations

DataFrame and Series creation, indexing, selection, and filtering patterns.

---

## Creating DataFrames

### From Dictionary

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "score": [85.5, 90.2, 78.8],
})
```

### From NumPy Array

```python
dates = pd.date_range("2024-01-01", periods=6)
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))
```

### From List of Dicts

```python
records = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
df = pd.DataFrame.from_records(records)
```

### Series

```python
s = pd.Series([1, 3, 5, np.nan, 6], name="values")
s = pd.Series({"a": 1, "b": 2, "c": 3})
```

---

## Viewing Data

```python
df.head(5)              # First 5 rows
df.tail(3)              # Last 3 rows
df.shape                # (rows, cols) tuple
df.dtypes               # Column data types
df.info()               # Summary (dtypes, non-null counts, memory)
df.describe()           # Statistical summary for numeric columns
df.columns.tolist()     # Column names as list
df.index                # Row index
df.to_numpy()           # Underlying NumPy array
df.T                    # Transpose
```

---

## Selection by Label: `.loc`

Label-based — slices are **inclusive on both ends**.

```python
df.loc["row_label"]                    # Single row → Series
df.loc[["row1", "row2"]]              # Multiple rows
df.loc[:, "col1"]                      # Single column
df.loc[:, ["col1", "col2"]]           # Multiple columns
df.loc["row1":"row3", "A":"C"]        # Slice rows and columns (inclusive)
df.loc[df["A"] > 0]                   # Boolean mask
df.loc[df["A"] > 0, ["B", "C"]]      # Boolean + column selection
```

---

## Selection by Position: `.iloc`

Integer position-based — slices follow **Python convention** (exclusive end).

```python
df.iloc[0]                # First row → Series
df.iloc[0:3]              # First 3 rows
df.iloc[:, 0]             # First column
df.iloc[0:3, 0:2]         # Rows 0-2, columns 0-1
df.iloc[[0, 2, 4]]        # Specific rows by position
df.iloc[1, 1]             # Single value
```

---

## Fast Scalar Access

```python
df.at["row_label", "col_name"]    # By label (fastest)
df.iat[0, 1]                      # By position (fastest)
```

---

## Boolean Indexing

```python
# Single condition
df[df["age"] > 25]

# Multiple conditions (use & | ~ with parentheses)
df[(df["age"] > 25) & (df["score"] > 80)]
df[(df["city"] == "NYC") | (df["city"] == "LA")]
df[~df["name"].str.startswith("A")]

# isin for membership testing
df[df["city"].isin(["NYC", "LA", "Chicago"])]

# between for range
df[df["age"].between(25, 35)]
```

---

## Query Method

```python
df.query("age > 25 and score > 80")
df.query("city in ['NYC', 'LA']")
df.query("name.str.startswith('A')", engine="python")

# With variables
min_age = 25
df.query("age > @min_age")
```

---

## Where and Mask

```python
df.where(df > 0)                # Keep where True, NaN where False
df.where(df > 0, other=0)      # Replace False values with 0
df.mask(df < 0)                 # Keep where False, NaN where True
```

---

## Setting Values

```python
# By label
df.loc[0, "age"] = 26
df.loc[df["age"] > 30, "category"] = "senior"

# By position
df.iloc[0, 1] = 26

# New column
df["new_col"] = df["a"] + df["b"]
df = df.assign(ratio=lambda x: x["a"] / x["b"])

# Conditional
df["grade"] = np.where(df["score"] > 80, "pass", "fail")
```

---

## Sorting

```python
df.sort_values("age")                          # Ascending
df.sort_values("age", ascending=False)         # Descending
df.sort_values(["age", "score"], ascending=[True, False])  # Multi-column
df.sort_index()                                # Sort by index
df.nsmallest(5, "score")                       # Bottom 5
df.nlargest(5, "score")                        # Top 5
```

---

## Column Operations

```python
df.rename(columns={"old": "new"})              # Rename columns
df.drop(columns=["col1", "col2"])              # Drop columns
df.reindex(columns=["col2", "col1", "col3"])   # Reorder columns
df.select_dtypes(include=["number"])           # Select by dtype
df.select_dtypes(exclude=["object"])           # Exclude by dtype
```

---

## Sampling

```python
df.sample(n=5)                    # 5 random rows
df.sample(frac=0.1)               # 10% of rows
df.sample(n=5, random_state=42)   # Reproducible
df.sample(n=10, replace=True)     # With replacement
```

---

## Duplicates

```python
df.duplicated()                       # Boolean mask
df.duplicated(subset=["col1"])        # Check specific columns
df.drop_duplicates()                   # Keep first occurrence
df.drop_duplicates(subset=["col1"], keep="last")  # Keep last
df.drop_duplicates(keep=False)         # Remove all duplicates
```

---

## Key Gotchas

1. **`.loc` slicing is inclusive**: `df.loc["a":"c"]` includes row "c"
2. **`.iloc` slicing is exclusive**: `df.iloc[0:3]` excludes position 3
3. **Chained indexing warning**: `df["col"][0]` may not set values — use `df.loc[0, "col"]`
4. **Boolean operators**: Use `&`, `|`, `~` (not Python `and`, `or`, `not`)
5. **Axis alignment**: `.loc` aligns axes on assignment; `.iloc` does not
6. **`.at`/`.iat`**: Fastest for scalar access but no slicing
