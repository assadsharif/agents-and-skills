---
name: pandas
description: |
  Expert pandas data manipulation and analysis guidance. Generate DataFrame operations,
  data cleaning pipelines, I/O code, groupby aggregations, merge/join patterns, reshaping,
  time series analysis, and performance optimization. This skill should be used when users
  ask to work with DataFrames, clean data, merge datasets, aggregate data, read/write CSV/
  Excel/Parquet/SQL, or optimize pandas code. Triggers on: "pandas", "dataframe", "csv",
  "data cleaning", "groupby", "merge dataframes", "pivot table", "read csv", "data analysis".
---

# Pandas Data Manipulation Expert

Expert guidance for pandas (v2.0+) data manipulation, analysis, and I/O operations.

## Scope

**Does**: Generate DataFrame/Series operations, data cleaning pipelines, I/O code (CSV/Excel/JSON/Parquet/SQL), merge/join/concat patterns, groupby aggregations, reshaping (pivot/melt/stack), time series operations, string operations, performance optimization, anti-pattern detection.

**Does NOT**: Build full applications, manage database infrastructure, create ML pipelines (use scikit-learn), handle distributed computing (use Dask/Spark), generate visualization code beyond basic `.plot()`.

## Before Writing Code

| Source | Gather |
|--------|--------|
| **Conversation** | Data shape, column names, dtypes, desired output |
| **Skill References** | Best practices from `references/` |
| **Codebase** | Existing pandas usage patterns, data files |
| **User Data** | Sample data to understand structure |

## Workflow

```
Understand Data → Choose Operation → Generate Code → Validate → Optimize
```

### Step 1: Understand the Data

Clarify before writing code:

| Ask | Purpose |
|-----|---------|
| What does the data look like? (columns, dtypes) | Choose correct operations |
| What's the desired output? | Define success criteria |
| How large is the dataset? | Performance considerations |

### Step 2: Choose the Right Operation

| Goal | Primary Operations |
|------|-------------------|
| **Read/Write data** | `read_csv`, `read_excel`, `read_parquet`, `read_sql`, `to_csv`, `to_parquet` |
| **Select/Filter** | `.loc`, `.iloc`, `.query()`, boolean indexing, `.isin()` |
| **Transform** | `.apply()`, `.map()`, `.transform()`, `.assign()`, vectorized ops |
| **Aggregate** | `.groupby().agg()`, `.pivot_table()`, `.value_counts()`, `.describe()` |
| **Combine** | `pd.merge()`, `pd.concat()`, `.join()`, `merge_asof()` |
| **Reshape** | `.pivot()`, `.melt()`, `.stack()`, `.unstack()`, `.explode()` |
| **Clean** | `.dropna()`, `.fillna()`, `.drop_duplicates()`, `.astype()`, `.str.*` |
| **Time series** | `.resample()`, `.rolling()`, `.shift()`, `pd.to_datetime()` |

### Step 3: Generate Code

**Key Principles:**
- Prefer vectorized operations over `.apply()` with lambdas
- Use method chaining for readability
- Specify dtypes explicitly when reading data
- Use `.loc`/`.iloc` for assignment (avoid chained indexing)
- Handle missing data explicitly

### Step 4: Validate

- Check output shape and dtypes match expectations
- Verify no silent data loss from merges or filters
- Confirm missing data handled correctly
- Test edge cases (empty DataFrames, all-NaN columns)

### Step 5: Optimize (if needed)

- Use categorical dtypes for low-cardinality string columns
- Read only needed columns with `usecols`
- Use chunked reading for large files
- Prefer Parquet over CSV for large datasets
- Avoid iterating rows — use vectorized operations

## Quick Reference: Common Patterns

| Pattern | Code |
|---------|------|
| Read CSV | `pd.read_csv('file.csv', dtype={'col': 'int64'}, parse_dates=['date'])` |
| Filter rows | `df[df['col'] > value]` or `df.query('col > @value')` |
| Select columns | `df[['col1', 'col2']]` or `df.loc[:, 'col1':'col3']` |
| GroupBy agg | `df.groupby('key').agg(total=('val', 'sum'), avg=('val', 'mean'))` |
| Merge | `pd.merge(left, right, on='key', how='left')` |
| Pivot table | `df.pivot_table(values='val', index='row', columns='col', aggfunc='mean')` |
| Fill NaN | `df['col'].fillna(df['col'].median())` |
| String ops | `df['col'].str.lower().str.strip().str.replace('old', 'new')` |
| DateTime | `df['date'] = pd.to_datetime(df['date_str'], format='%Y-%m-%d')` |
| Method chain | `df.pipe(clean).query('val > 0').groupby('key').agg('sum')` |

## Must Avoid

- **Chained indexing**: `df['col'][0] = val` — use `df.loc[0, 'col'] = val`
- **Iterating rows**: `for i, row in df.iterrows()` — use vectorized ops
- **Growing DataFrames**: `df = pd.concat([df, new_row])` in a loop — collect then concat
- **Ignoring dtypes**: Reading everything as object — specify dtypes upfront
- **Using `inplace=True`**: Deprecated pattern — use `df = df.method()` instead
- **Silent merge issues**: Not checking merge result shape — use `validate` parameter
- **Python `and`/`or` in boolean**: Use `&`/`|` with parentheses instead

## Performance Tips

| Tip | Impact |
|-----|--------|
| Use `pd.Categorical` for repeated strings | 10-100x memory reduction |
| Read with `usecols` parameter | Faster I/O, less memory |
| Use Parquet instead of CSV | 2-10x faster I/O |
| Vectorized string ops over `.apply()` | 10-100x faster |
| Use `.at`/`.iat` for scalar access | Fastest single-value access |
| Avoid `object` dtype for numerics | Enable vectorized math |
| Use `dtype_backend='pyarrow'` | Better nullable type support |

## Reference Files

| File | When to Read |
|------|--------------|
| `references/core-operations.md` | DataFrame/Series creation, indexing, selection, filtering |
| `references/data-cleaning.md` | Missing data, duplicates, type conversion, string ops |
| `references/aggregation.md` | GroupBy, pivot tables, reshaping, window functions |
| `references/io-guide.md` | Reading/writing CSV, Excel, JSON, Parquet, SQL |
| `references/performance.md` | Optimization patterns, memory reduction, vectorization |
