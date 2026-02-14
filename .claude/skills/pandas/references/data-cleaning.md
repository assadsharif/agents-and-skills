# Data Cleaning

Missing data handling, type conversion, string operations, and data quality patterns.

---

## Missing Data

### Detection

```python
df.isna()                     # Boolean mask of NaN values
df.notna()                    # Inverse
df.isna().sum()               # Count NaN per column
df.isna().sum().sum()         # Total NaN count
df.isna().any()               # Columns with any NaN
df[df["col"].isna()]          # Rows where col is NaN
```

### Dropping

```python
df.dropna()                   # Drop rows with any NaN
df.dropna(how="all")          # Drop rows where all values NaN
df.dropna(subset=["col1"])    # Drop rows where col1 is NaN
df.dropna(thresh=3)           # Keep rows with at least 3 non-NaN values
df.dropna(axis=1)             # Drop columns with any NaN
```

### Filling

```python
df.fillna(0)                              # Fill with constant
df["col"].fillna(df["col"].mean())        # Fill with mean
df["col"].fillna(df["col"].median())      # Fill with median
df["col"].fillna(method="ffill")          # Forward fill
df["col"].fillna(method="bfill")          # Backward fill
df.fillna({"col1": 0, "col2": "unknown"}) # Different fill per column
df.interpolate()                           # Linear interpolation
df.interpolate(method="time")             # Time-based interpolation
```

### Replace

```python
df.replace(0, np.nan)                       # Replace value
df.replace({"col": {0: np.nan, -1: np.nan}}) # Column-specific
df.replace([0, -1, -999], np.nan)           # Multiple values
df.replace(r"^\s*$", np.nan, regex=True)    # Empty strings → NaN
```

---

## Type Conversion

### Basic Conversion

```python
df["col"] = df["col"].astype("int64")
df["col"] = df["col"].astype("float64")
df["col"] = df["col"].astype("str")
df["col"] = df["col"].astype("category")
```

### Numeric Conversion

```python
df["col"] = pd.to_numeric(df["col"], errors="coerce")   # Invalid → NaN
df["col"] = pd.to_numeric(df["col"], errors="ignore")   # Keep invalid as-is
df["col"] = pd.to_numeric(df["col"], downcast="integer") # Smallest int type
```

### DateTime Conversion

```python
df["date"] = pd.to_datetime(df["date_str"])
df["date"] = pd.to_datetime(df["date_str"], format="%Y-%m-%d")
df["date"] = pd.to_datetime(df["date_str"], errors="coerce")  # Invalid → NaT
df["date"] = pd.to_datetime(df[["year", "month", "day"]])      # From components
```

### Nullable Types (Recommended for v2.0+)

```python
df["int_col"] = df["int_col"].astype("Int64")       # Nullable integer
df["float_col"] = df["float_col"].astype("Float64") # Nullable float
df["bool_col"] = df["bool_col"].astype("boolean")   # Nullable boolean
df["str_col"] = df["str_col"].astype("string")      # String type (not object)
```

---

## String Operations

Access via `.str` accessor on Series with string dtype.

### Case

```python
df["name"].str.lower()
df["name"].str.upper()
df["name"].str.title()
df["name"].str.capitalize()
```

### Whitespace

```python
df["col"].str.strip()          # Both sides
df["col"].str.lstrip()         # Left
df["col"].str.rstrip()         # Right
```

### Substring

```python
df["col"].str.contains("pattern")         # Boolean mask
df["col"].str.contains("pattern", case=False)  # Case-insensitive
df["col"].str.startswith("prefix")
df["col"].str.endswith("suffix")
df["col"].str.extract(r"(\d+)")           # Regex extract
df["col"].str.findall(r"\d+")             # All matches
df["col"].str.len()                       # String length
df["col"].str[0:5]                        # Slice
```

### Replace and Split

```python
df["col"].str.replace("old", "new")
df["col"].str.replace(r"\d+", "", regex=True)  # Regex replace
df["col"].str.split(",")                        # → list column
df["col"].str.split(",", expand=True)           # → multiple columns
df["col"].str.cat(sep=", ")                     # Concatenate all values
```

### Padding and Alignment

```python
df["col"].str.pad(10, side="left", fillchar="0")
df["col"].str.zfill(5)                 # Zero-pad to width 5
```

---

## Data Quality Checks

### Unique Values

```python
df["col"].unique()             # Array of unique values
df["col"].nunique()            # Count of unique values
df["col"].value_counts()       # Frequency distribution
df["col"].value_counts(normalize=True)  # As proportions
```

### Range Validation

```python
# Check if values in expected range
assert df["age"].between(0, 150).all(), "Age values out of range"
assert df["score"].ge(0).all(), "Negative scores found"
```

### Pattern Validation

```python
# Validate email format
valid_email = df["email"].str.match(r"^[\w\.-]+@[\w\.-]+\.\w+$")
invalid_rows = df[~valid_email]

# Validate phone format
valid_phone = df["phone"].str.match(r"^\+?\d{10,15}$")
```

### Consistency Checks

```python
# Check referential integrity
assert df["category"].isin(valid_categories).all()

# Check for unexpected values
unexpected = df[~df["status"].isin(["active", "inactive", "pending"])]
```

---

## Common Cleaning Pipeline

```python
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .rename(columns=str.lower)                    # Lowercase columns
        .rename(columns=lambda x: x.strip().replace(" ", "_"))  # Clean names
        .drop_duplicates()                              # Remove duplicates
        .assign(
            date=lambda x: pd.to_datetime(x["date"], errors="coerce"),
            amount=lambda x: pd.to_numeric(x["amount"], errors="coerce"),
            name=lambda x: x["name"].str.strip().str.title(),
        )
        .dropna(subset=["date", "amount"])              # Drop critical NaN
        .query("amount > 0")                            # Filter invalid
        .reset_index(drop=True)                         # Clean index
    )
```

---

## Clipboard Operations

```python
df = pd.read_clipboard()          # Paste from clipboard
df.to_clipboard(index=False)      # Copy to clipboard
```
