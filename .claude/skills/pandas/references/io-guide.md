# I/O Guide

Reading and writing data in CSV, Excel, JSON, Parquet, SQL, and other formats.

---

## Format Overview

| Format | Read | Write | Best For |
|--------|------|-------|----------|
| CSV | `read_csv()` | `to_csv()` | Universal text exchange |
| Excel | `read_excel()` | `to_excel()` | Business users, formatted reports |
| JSON | `read_json()` | `to_json()` | APIs, web data |
| Parquet | `read_parquet()` | `to_parquet()` | Large datasets, analytics |
| SQL | `read_sql()` | `to_sql()` | Database integration |
| Feather | `read_feather()` | `to_feather()` | Fast DataFrame serialization |
| Pickle | `read_pickle()` | `to_pickle()` | Python-only persistence |
| HTML | `read_html()` | `to_html()` | Web scraping, reports |
| Clipboard | `read_clipboard()` | `to_clipboard()` | Quick data transfer |

---

## CSV

### Reading

```python
# Basic
df = pd.read_csv("data.csv")

# Common parameters
df = pd.read_csv(
    "data.csv",
    sep=",",                    # Delimiter (default comma)
    header=0,                   # Row for column names (0-indexed)
    names=["a", "b", "c"],      # Custom column names
    index_col="id",             # Column to use as index
    usecols=["col1", "col2"],   # Read only these columns
    dtype={"age": "int32", "name": "string"},  # Explicit dtypes
    parse_dates=["date"],       # Parse as datetime
    na_values=["NA", "N/A", ""],  # Custom NaN markers
    skiprows=2,                 # Skip first 2 rows
    nrows=1000,                 # Read only 1000 rows
    encoding="utf-8",           # Character encoding
    compression="gzip",         # For compressed files
)

# Chunked reading for large files
chunks = pd.read_csv("large.csv", chunksize=10000)
df = pd.concat(chunk for chunk in chunks)

# From URL
df = pd.read_csv("https://example.com/data.csv")
```

### Writing

```python
df.to_csv("output.csv", index=False)

df.to_csv(
    "output.csv",
    sep=",",
    index=False,               # Don't write index
    columns=["col1", "col2"],  # Select columns
    header=True,               # Write column names
    encoding="utf-8",
    date_format="%Y-%m-%d",
    float_format="%.2f",       # 2 decimal places
    compression="gzip",        # Compress output
    mode="a",                  # Append mode
)
```

---

## Excel

### Reading

```python
df = pd.read_excel("data.xlsx")

df = pd.read_excel(
    "data.xlsx",
    sheet_name="Sheet1",        # Sheet name or index
    header=0,
    usecols="A:D",              # Excel column range
    dtype={"id": "int64"},
    parse_dates=["date"],
    engine="openpyxl",          # For .xlsx files
)

# Read all sheets
sheets = pd.read_excel("data.xlsx", sheet_name=None)  # Dict of DataFrames
```

### Writing

```python
df.to_excel("output.xlsx", sheet_name="Results", index=False)

# Multiple sheets
with pd.ExcelWriter("output.xlsx", engine="openpyxl") as writer:
    df1.to_excel(writer, sheet_name="Data", index=False)
    df2.to_excel(writer, sheet_name="Summary", index=False)
```

---

## JSON

### Reading

```python
df = pd.read_json("data.json")

df = pd.read_json(
    "data.json",
    orient="records",           # Format: records, columns, index, split, table
    lines=True,                 # One JSON object per line (JSONL)
    dtype={"col": "int64"},
    convert_dates=True,
)

# From JSON string
df = pd.read_json('{"col1":[1,2],"col2":[3,4]}')
```

### Writing

```python
df.to_json("output.json", orient="records", indent=2)

# Orient options
df.to_json(orient="records")    # [{"col1":1,"col2":3}, ...]
df.to_json(orient="columns")    # {"col1":{"0":1},"col2":{"0":3}}
df.to_json(orient="split")      # {"columns":[],"index":[],"data":[]}
df.to_json(orient="table")      # {"schema":{},"data":[]}
df.to_json(orient="records", lines=True)  # JSONL format
```

---

## Parquet

Best format for large analytical datasets — columnar, compressed, typed.

### Reading

```python
df = pd.read_parquet("data.parquet")

df = pd.read_parquet(
    "data.parquet",
    columns=["col1", "col2"],    # Read subset of columns
    engine="pyarrow",            # pyarrow or fastparquet
)

# From S3 (requires s3fs)
df = pd.read_parquet("s3://bucket/data.parquet")
```

### Writing

```python
df.to_parquet("output.parquet")

df.to_parquet(
    "output.parquet",
    compression="snappy",        # snappy (default), gzip, brotli, zstd
    index=False,
    engine="pyarrow",
)
```

---

## SQL

### Reading

```python
import sqlite3

conn = sqlite3.connect("database.db")

# Read table
df = pd.read_sql("SELECT * FROM users", conn)

# Read with query
df = pd.read_sql(
    "SELECT name, age FROM users WHERE age > 25",
    conn,
    index_col="id",
    parse_dates=["created_at"],
)

# SQLAlchemy (recommended for production)
from sqlalchemy import create_engine
engine = create_engine("sqlite:///database.db")
df = pd.read_sql("users", engine)  # Table name
df = pd.read_sql_query("SELECT * FROM users", engine)  # Query

# Chunked reading
for chunk in pd.read_sql("SELECT * FROM big_table", engine, chunksize=10000):
    process(chunk)
```

### Writing

```python
df.to_sql("users", conn, if_exists="replace", index=False)

df.to_sql(
    "users",
    engine,
    if_exists="append",          # fail, replace, append
    index=False,
    chunksize=1000,              # Write in chunks
    dtype={"name": "VARCHAR(100)"},  # SQL type hints
)
```

---

## Remote & Compressed Files

```python
# HTTP/HTTPS
df = pd.read_csv("https://example.com/data.csv")

# Compressed (auto-detected)
df = pd.read_csv("data.csv.gz")
df = pd.read_csv("data.csv.bz2")
df = pd.read_csv("data.csv.zip")
df = pd.read_csv("data.csv.xz")

# S3 (requires s3fs)
df = pd.read_parquet("s3://bucket/data.parquet")

# GCS (requires gcsfs)
df = pd.read_parquet("gs://bucket/data.parquet")
```

---

## Best Practices

1. **Always specify dtypes** when reading CSV — prevents silent type inference errors
2. **Use Parquet** for large datasets — 2-10x faster than CSV, preserves types
3. **Use `usecols`** to read only needed columns — saves memory and I/O time
4. **Use chunked reading** for files that don't fit in memory
5. **Write `index=False`** unless the index contains meaningful data
6. **Use SQLAlchemy** engine for SQL connections (not raw connection objects)
7. **Specify `encoding`** for international data (default is system-dependent)
