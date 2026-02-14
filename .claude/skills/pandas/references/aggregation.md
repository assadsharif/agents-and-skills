# Aggregation & Reshaping

GroupBy, pivot tables, reshaping, merge/join, and window functions.

---

## GroupBy (Split-Apply-Combine)

### Basic GroupBy

```python
df.groupby("col")["val"].sum()                  # Single column, single agg
df.groupby("col")[["val1", "val2"]].mean()      # Multiple columns
df.groupby(["col1", "col2"]).sum()              # Multi-level groupby
```

### Named Aggregation (Recommended)

```python
df.groupby("department").agg(
    total_salary=("salary", "sum"),
    avg_salary=("salary", "mean"),
    headcount=("employee_id", "count"),
    max_tenure=("years", "max"),
)
```

### Multiple Aggregations

```python
df.groupby("col").agg(["mean", "std", "count"])        # Same agg, all columns
df.groupby("col").agg({"val1": "sum", "val2": "mean"}) # Different per column
```

### Built-in Aggregation Methods

```python
grouped = df.groupby("key")
grouped.sum()         grouped.mean()        grouped.median()
grouped.std()         grouped.var()          grouped.min()
grouped.max()         grouped.count()        grouped.size()
grouped.first()       grouped.last()         grouped.nunique()
grouped.any()         grouped.all()          grouped.quantile(0.95)
```

### Transform (Same-Indexed Output)

```python
# Normalize within groups
df["normalized"] = df.groupby("group")["val"].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Fill NaN with group mean
df["val_filled"] = df.groupby("group")["val"].transform("mean")

# Cumulative within groups
df["cumsum"] = df.groupby("group")["val"].transform("cumsum")

# Rank within groups
df["rank"] = df.groupby("group")["score"].transform("rank", ascending=False)
```

### Filter (Keep/Remove Entire Groups)

```python
# Keep groups with more than 5 members
df.groupby("group").filter(lambda x: len(x) > 5)

# Keep groups where mean > threshold
df.groupby("group").filter(lambda x: x["val"].mean() > 50)
```

### GroupBy Selection

```python
grouped.head(3)                # Top 3 per group
grouped.tail(3)                # Bottom 3 per group
grouped.nth(0)                 # First row per group
grouped.nth([0, -1])           # First and last per group
grouped.nlargest(3, "val")     # Top 3 values per group
grouped.nsmallest(3, "val")    # Bottom 3 values per group
```

### GroupBy Tips

```python
grouped = df.groupby("key", sort=False)        # Preserve order (faster)
grouped = df.groupby("key", as_index=False)     # Keys as columns, not index
grouped = df.groupby("key", dropna=False)       # Include NaN groups
grouped = df.groupby("key", observed=True)      # Only observed categories
```

---

## Merge / Join

### pd.merge (SQL-Style)

```python
# Inner join (default)
pd.merge(left, right, on="key")

# Left join
pd.merge(left, right, on="key", how="left")

# Different key names
pd.merge(left, right, left_on="lkey", right_on="rkey")

# Join on index
pd.merge(left, right, left_index=True, right_index=True)

# Multiple keys
pd.merge(left, right, on=["key1", "key2"])

# With validation
pd.merge(left, right, on="key", validate="one_to_many")

# With indicator
result = pd.merge(left, right, on="key", how="outer", indicator=True)
# _merge column: 'left_only', 'right_only', 'both'
```

### Join Types

| `how` | SQL | Behavior |
|-------|-----|----------|
| `inner` | INNER JOIN | Only matching keys |
| `left` | LEFT JOIN | All left keys + matching right |
| `right` | RIGHT JOIN | All right keys + matching left |
| `outer` | FULL OUTER JOIN | All keys from both |
| `cross` | CROSS JOIN | Cartesian product |

### pd.concat

```python
# Stack vertically (default)
pd.concat([df1, df2, df3])

# Stack horizontally
pd.concat([df1, df2], axis=1)

# Reset index
pd.concat([df1, df2], ignore_index=True)

# Add keys for MultiIndex
pd.concat([df1, df2], keys=["source1", "source2"])

# Inner join (intersection of columns)
pd.concat([df1, df2], join="inner")
```

### merge_asof (Nearest Match)

```python
# Join on nearest timestamp (must be sorted)
pd.merge_asof(trades, quotes, on="timestamp", by="ticker")

# With tolerance
pd.merge_asof(trades, quotes, on="time", tolerance=pd.Timedelta("10ms"))
```

---

## Pivot Tables

```python
# Basic pivot table
df.pivot_table(
    values="revenue",
    index="region",
    columns="quarter",
    aggfunc="sum",
)

# Multiple aggregations
df.pivot_table(
    values="revenue",
    index="region",
    columns="quarter",
    aggfunc=["sum", "mean", "count"],
    margins=True,               # Add totals
    fill_value=0,               # Replace NaN
)

# Multiple values
df.pivot_table(
    values=["revenue", "units"],
    index="region",
    aggfunc={"revenue": "sum", "units": "mean"},
)
```

### pivot vs pivot_table

```python
# pivot: reshape without aggregation (values must be unique)
df.pivot(index="date", columns="ticker", values="price")

# pivot_table: reshape with aggregation (handles duplicates)
df.pivot_table(index="date", columns="ticker", values="price", aggfunc="mean")
```

---

## Reshaping

### Melt (Wide → Long)

```python
pd.melt(
    df,
    id_vars=["name"],          # Keep these columns
    value_vars=["Q1", "Q2"],   # Unpivot these columns
    var_name="quarter",        # Name for variable column
    value_name="revenue",      # Name for value column
)
```

### Stack / Unstack

```python
df.stack()           # Columns → rows (add level to index)
df.unstack()         # Rows → columns (remove level from index)
df.unstack(level=0)  # Specify which level to unstack
```

### Explode (List → Rows)

```python
df.explode("tags")   # Each list item becomes a row
```

### Cross-Tabulation

```python
pd.crosstab(df["row"], df["col"])                        # Counts
pd.crosstab(df["row"], df["col"], values=df["val"], aggfunc="mean")
pd.crosstab(df["row"], df["col"], normalize="index")     # Row proportions
```

---

## Window Functions

### Rolling

```python
df["rolling_mean"] = df["val"].rolling(window=7).mean()
df["rolling_std"] = df["val"].rolling(window=7).std()
df["rolling_sum"] = df["val"].rolling(window=30, min_periods=1).sum()
```

### Expanding

```python
df["cumulative_mean"] = df["val"].expanding().mean()
df["cumulative_max"] = df["val"].expanding().max()
```

### EWM (Exponentially Weighted)

```python
df["ewm_mean"] = df["val"].ewm(span=7).mean()
df["ewm_mean"] = df["val"].ewm(halflife=7).mean()
```

### Shift

```python
df["prev_val"] = df["val"].shift(1)        # Previous row
df["next_val"] = df["val"].shift(-1)       # Next row
df["pct_change"] = df["val"].pct_change()  # Percentage change
df["diff"] = df["val"].diff()              # Difference
```
