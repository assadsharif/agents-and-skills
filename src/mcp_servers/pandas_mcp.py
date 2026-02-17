"""
Pandas MCP Server — toolkit for generating pandas DataFrame operations,
data cleaning pipelines, I/O code, aggregations, merge patterns, and
performance-optimized code.

TOOLS:
    pandas_generate_read        Generate code to read data from various formats
    pandas_generate_transform   Generate data transformation/cleaning code
    pandas_generate_aggregate   Generate groupby/pivot/window aggregation code
    pandas_generate_merge       Generate merge/join/concat code
    pandas_generate_io          Generate I/O code for any supported format
    pandas_detect_antipatterns  Detect performance anti-patterns in pandas code
    pandas_optimize_code        Suggest optimizations for pandas code
    pandas_generate_pipeline    Generate a complete data processing pipeline
"""

import json
import re
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP("pandas_mcp")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Supported file formats
IO_FORMATS = {
    "csv": {
        "read": "pd.read_csv",
        "write": "df.to_csv",
        "key_params": ["sep", "header", "index_col", "usecols", "dtype", "parse_dates", "na_values", "encoding", "chunksize"],
    },
    "excel": {
        "read": "pd.read_excel",
        "write": "df.to_excel",
        "key_params": ["sheet_name", "header", "usecols", "dtype", "engine"],
    },
    "json": {
        "read": "pd.read_json",
        "write": "df.to_json",
        "key_params": ["orient", "lines", "dtype", "convert_dates"],
    },
    "parquet": {
        "read": "pd.read_parquet",
        "write": "df.to_parquet",
        "key_params": ["columns", "engine", "compression"],
    },
    "sql": {
        "read": "pd.read_sql",
        "write": "df.to_sql",
        "key_params": ["sql/table_name", "con", "index_col", "parse_dates", "chunksize", "if_exists"],
    },
    "feather": {
        "read": "pd.read_feather",
        "write": "df.to_feather",
        "key_params": ["columns"],
    },
    "html": {
        "read": "pd.read_html",
        "write": "df.to_html",
        "key_params": ["match", "header", "index_col"],
    },
    "pickle": {
        "read": "pd.read_pickle",
        "write": "df.to_pickle",
        "key_params": ["compression"],
    },
    "clipboard": {
        "read": "pd.read_clipboard",
        "write": "df.to_clipboard",
        "key_params": ["sep"],
    },
}

# Anti-patterns
ANTI_PATTERNS = [
    {
        "id": "iterrows",
        "pattern": r"\.iterrows\(\)",
        "name": "Using iterrows()",
        "severity": "high",
        "fix": "Use vectorized operations instead. Example: df['result'] = df['a'] + df['b']",
    },
    {
        "id": "itertuples_mutation",
        "pattern": r"for.*itertuples.*:.*\.loc\[",
        "name": "Mutating during itertuples",
        "severity": "high",
        "fix": "Use vectorized operations or .apply() instead of loop mutation",
    },
    {
        "id": "chained_indexing",
        "pattern": r"df\[.*\]\[.*\]\s*=",
        "name": "Chained indexing assignment",
        "severity": "high",
        "fix": "Use df.loc[condition, column] = value instead",
    },
    {
        "id": "concat_in_loop",
        "pattern": r"(for|while).*\n.*pd\.concat\(",
        "name": "pd.concat() in a loop",
        "severity": "high",
        "fix": "Collect DataFrames in a list, then concat once: pd.concat(frames)",
    },
    {
        "id": "append_deprecated",
        "pattern": r"\.append\(",
        "name": "Using deprecated .append()",
        "severity": "medium",
        "fix": "Use pd.concat([df1, df2]) instead of df1.append(df2)",
    },
    {
        "id": "inplace_true",
        "pattern": r"inplace\s*=\s*True",
        "name": "Using inplace=True",
        "severity": "low",
        "fix": "Use df = df.method() instead of df.method(inplace=True)",
    },
    {
        "id": "apply_simple_ops",
        "pattern": r"\.apply\(lambda\s+\w+\s*:\s*\w+\s*[\+\-\*\/]",
        "name": "apply() for simple arithmetic",
        "severity": "medium",
        "fix": "Use vectorized operation: df['col'] * 2 instead of df['col'].apply(lambda x: x * 2)",
    },
    {
        "id": "python_and_or",
        "pattern": r"df\[.*\band\b.*\]|df\[.*\bor\b.*\]",
        "name": "Python and/or in boolean indexing",
        "severity": "high",
        "fix": "Use & (and), | (or), ~ (not) with parentheses: df[(cond1) & (cond2)]",
    },
    {
        "id": "no_usecols",
        "pattern": r"read_csv\([^)]*\)(?!.*usecols)",
        "name": "read_csv without usecols",
        "severity": "low",
        "fix": "Specify usecols to read only needed columns for better performance",
    },
    {
        "id": "object_dtype",
        "pattern": r"dtype.*object",
        "name": "Using object dtype explicitly",
        "severity": "low",
        "fix": "Use 'string' dtype instead of 'object' for text columns (pandas 2.0+)",
    },
]

# Transform operations
TRANSFORM_OPS = {
    "filter_rows": "df[condition] or df.query('condition')",
    "select_columns": "df[['col1', 'col2']] or df.loc[:, 'col1':'col3']",
    "rename_columns": "df.rename(columns={'old': 'new'})",
    "drop_columns": "df.drop(columns=['col1', 'col2'])",
    "sort": "df.sort_values('col', ascending=False)",
    "add_column": "df['new'] = expression or df.assign(new=expression)",
    "conditional": "np.where(condition, true_val, false_val)",
    "type_convert": "df['col'].astype('type') or pd.to_numeric/to_datetime",
    "string_ops": "df['col'].str.method()",
    "fill_na": "df.fillna(value) or df['col'].fillna(df['col'].median())",
    "drop_na": "df.dropna(subset=['col'])",
    "drop_duplicates": "df.drop_duplicates(subset=['col'])",
    "reset_index": "df.reset_index(drop=True)",
    "clip": "df['col'].clip(lower=0, upper=100)",
    "replace": "df.replace({'col': {old: new}})",
    "map": "df['col'].map(mapping_dict)",
}

# Aggregation operations
AGG_OPS = {
    "groupby": "df.groupby('key').agg(result=('col', 'func'))",
    "pivot_table": "df.pivot_table(values='val', index='row', columns='col', aggfunc='mean')",
    "crosstab": "pd.crosstab(df['row'], df['col'])",
    "value_counts": "df['col'].value_counts()",
    "describe": "df.describe()",
    "rolling": "df['col'].rolling(window=7).mean()",
    "expanding": "df['col'].expanding().mean()",
    "ewm": "df['col'].ewm(span=7).mean()",
    "resample": "df.resample('D').mean() (requires datetime index)",
    "rank": "df['col'].rank(ascending=False)",
    "cumsum": "df.groupby('key')['col'].cumsum()",
    "pct_change": "df['col'].pct_change()",
    "shift": "df['col'].shift(1)",
}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

_CFG = ConfigDict(str_strip_whitespace=True, extra="forbid")


class GenerateReadInput(BaseModel):
    model_config = _CFG
    format: str = Field(
        ..., description="File format: csv, excel, json, parquet, sql, feather, html, pickle, clipboard"
    )
    file_path: str = Field(
        default="data.csv", max_length=500, description="Path or URL to data source"
    )
    columns: list[str] = Field(
        default_factory=list, description="Specific columns to read (empty = all)"
    )
    dtypes: dict[str, str] = Field(
        default_factory=dict, description="Column dtype mapping, e.g. {'age': 'int32', 'name': 'string'}"
    )
    parse_dates: list[str] = Field(
        default_factory=list, description="Columns to parse as datetime"
    )
    large_file: bool = Field(
        default=False, description="Whether file is large (enables chunked reading)"
    )

    @field_validator("format")
    @classmethod
    def _validate_format(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in IO_FORMATS:
            raise ValueError(f"format must be one of: {', '.join(IO_FORMATS.keys())}")
        return v


class GenerateTransformInput(BaseModel):
    model_config = _CFG
    operations: list[str] = Field(
        ..., min_length=1, description="List of operations to perform: filter_rows, select_columns, rename_columns, drop_columns, sort, add_column, type_convert, string_ops, fill_na, drop_na, drop_duplicates, etc."
    )
    columns: list[str] = Field(
        default_factory=list, description="Columns involved in operations"
    )
    conditions: list[str] = Field(
        default_factory=list, description="Filter conditions, e.g. ['age > 25', 'city == NYC']"
    )
    description: str = Field(
        default="", max_length=1000, description="Natural language description of desired transformation"
    )


class GenerateAggregateInput(BaseModel):
    model_config = _CFG
    operation: str = Field(
        ..., description="Aggregation type: groupby, pivot_table, crosstab, value_counts, rolling, resample"
    )
    group_by: list[str] = Field(
        default_factory=list, description="Columns to group by"
    )
    value_columns: list[str] = Field(
        default_factory=list, description="Columns to aggregate"
    )
    agg_functions: list[str] = Field(
        default_factory=lambda: ["sum"], description="Aggregation functions: sum, mean, count, min, max, std, median, nunique"
    )
    window_size: int = Field(
        default=7, ge=1, description="Window size for rolling/ewm operations"
    )


class GenerateMergeInput(BaseModel):
    model_config = _CFG
    operation: str = Field(
        ..., description="Operation: merge, concat, join, merge_asof"
    )
    how: str = Field(
        default="inner", description="Join type: inner, outer, left, right, cross"
    )
    on: list[str] = Field(
        default_factory=list, description="Key columns for merge"
    )
    left_on: list[str] = Field(
        default_factory=list, description="Left key columns (if different from right)"
    )
    right_on: list[str] = Field(
        default_factory=list, description="Right key columns (if different from left)"
    )
    merge_validate: str = Field(
        default="", description="Merge validation: one_to_one, one_to_many, many_to_one, many_to_many"
    )


class DetectAntipatternsInput(BaseModel):
    model_config = _CFG
    code: str = Field(
        ..., min_length=1, max_length=20000, description="Pandas code to analyze"
    )


class OptimizeCodeInput(BaseModel):
    model_config = _CFG
    code: str = Field(
        ..., min_length=1, max_length=20000, description="Pandas code to optimize"
    )
    priorities: list[str] = Field(
        default_factory=lambda: ["speed"], description="Optimization priorities: speed, memory, readability"
    )


class GeneratePipelineInput(BaseModel):
    model_config = _CFG
    input_format: str = Field(
        default="csv", description="Input data format"
    )
    input_path: str = Field(
        default="data.csv", max_length=500, description="Input file path"
    )
    steps: list[str] = Field(
        ..., min_length=1, description="Pipeline steps: read, clean, filter, transform, aggregate, merge, write"
    )
    output_format: str = Field(
        default="csv", description="Output data format"
    )
    output_path: str = Field(
        default="output.csv", max_length=500, description="Output file path"
    )
    description: str = Field(
        default="", max_length=2000, description="Natural language description of the pipeline"
    )


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------


def _detect_patterns(code: str) -> list[dict]:
    """Detect anti-patterns in pandas code."""
    findings = []
    for ap in ANTI_PATTERNS:
        try:
            if re.search(ap["pattern"], code, re.MULTILINE):
                findings.append({
                    "id": ap["id"],
                    "name": ap["name"],
                    "severity": ap["severity"],
                    "fix": ap["fix"],
                })
        except re.error:
            # Skip patterns with regex issues
            pass

    # Check for common indicators without regex
    if "iterrows" in code:
        if not any(f["id"] == "iterrows" for f in findings):
            findings.append({
                "id": "iterrows",
                "name": "Using iterrows()",
                "severity": "high",
                "fix": "Use vectorized operations instead",
            })

    return findings


def _generate_read_code(fmt: str, path: str, columns: list, dtypes: dict, parse_dates: list, large: bool) -> str:
    """Generate read code for a given format."""
    func = IO_FORMATS[fmt]["read"]
    lines = ["import pandas as pd", ""]

    params = [f'"{path}"']

    if columns and fmt in ("csv", "parquet", "feather"):
        param_name = "usecols" if fmt == "csv" else "columns"
        params.append(f'{param_name}={columns}')

    if dtypes and fmt in ("csv", "excel", "json"):
        params.append(f"dtype={dtypes}")

    if parse_dates and fmt in ("csv", "excel"):
        params.append(f"parse_dates={parse_dates}")

    if fmt == "csv":
        params.append('encoding="utf-8"')

    if fmt == "excel":
        params.append('engine="openpyxl"')

    if large and fmt == "csv":
        # Chunked reading
        lines.append(f"chunks = {func}(")
        for p in params:
            lines.append(f"    {p},")
        lines.append("    chunksize=10000,")
        lines.append(")")
        lines.append("df = pd.concat(chunk for chunk in chunks)")
    else:
        if len(params) == 1:
            lines.append(f"df = {func}({params[0]})")
        else:
            lines.append(f"df = {func}(")
            for p in params:
                lines.append(f"    {p},")
            lines.append(")")

    lines.append("")
    lines.append("print(df.shape)")
    lines.append("print(df.dtypes)")

    return "\n".join(lines)


def _generate_merge_code(operation: str, how: str, on: list, left_on: list, right_on: list, validate: str) -> str:
    """Generate merge/join/concat code."""
    lines = ["import pandas as pd", ""]

    if operation == "concat":
        lines.append("# Concatenate DataFrames")
        lines.append("result = pd.concat([df1, df2], ignore_index=True)")
        lines.append("")
        lines.append("# Verify shape")
        lines.append("print(f'Combined: {result.shape}')")
    elif operation == "merge":
        lines.append("# Merge DataFrames")
        params = [f'how="{how}"']
        if on:
            params.append(f"on={on}")
        elif left_on and right_on:
            params.append(f"left_on={left_on}")
            params.append(f"right_on={right_on}")
        if validate:
            params.append(f'validate="{validate}"')
        params.append('indicator=True')

        lines.append("result = pd.merge(")
        lines.append("    left,")
        lines.append("    right,")
        for p in params:
            lines.append(f"    {p},")
        lines.append(")")
        lines.append("")
        lines.append("# Check merge quality")
        lines.append("print(result['_merge'].value_counts())")
        lines.append("result = result.drop(columns=['_merge'])")
    elif operation == "join":
        lines.append("# Join on index")
        lines.append(f'result = left.join(right, how="{how}")')
    elif operation == "merge_asof":
        lines.append("# Nearest-match join (both must be sorted)")
        lines.append("result = pd.merge_asof(")
        lines.append("    left.sort_values('time'),")
        lines.append("    right.sort_values('time'),")
        lines.append("    on='time',")
        if on:
            lines.append(f"    by={on},")
        lines.append(")")

    lines.append("")
    lines.append("print(f'Result shape: {result.shape}')")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def pandas_generate_read(
    format: str,
    file_path: str = "data.csv",
    columns: list[str] | None = None,
    dtypes: dict[str, str] | None = None,
    parse_dates: list[str] | None = None,
    large_file: bool = False,
) -> str:
    """Generate pandas code to read data from CSV, Excel, JSON, Parquet, SQL, or other formats."""
    try:
        inp = GenerateReadInput(
            format=format,
            file_path=file_path,
            columns=columns or [],
            dtypes=dtypes or {},
            parse_dates=parse_dates or [],
            large_file=large_file,
        )

        code = _generate_read_code(
            inp.format, inp.file_path, inp.columns,
            inp.dtypes, inp.parse_dates, inp.large_file,
        )

        format_info = IO_FORMATS[inp.format]

        return json.dumps({
            "code": code,
            "format": inp.format,
            "read_function": format_info["read"],
            "write_function": format_info["write"],
            "available_params": format_info["key_params"],
            "tips": [
                "Always specify dtypes for CSV to avoid inference overhead",
                "Use usecols/columns to read only needed columns",
                "Use chunked reading for files larger than available RAM",
            ] if inp.format == "csv" else [
                f"Use {format_info['read']} with appropriate parameters",
            ],
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def pandas_generate_transform(
    operations: list[str],
    columns: list[str] | None = None,
    conditions: list[str] | None = None,
    description: str = "",
) -> str:
    """Generate pandas data transformation and cleaning code."""
    try:
        inp = GenerateTransformInput(
            operations=operations,
            columns=columns or [],
            conditions=conditions or [],
            description=description,
        )

        code_blocks = ["import pandas as pd", "import numpy as np", ""]

        for op in inp.operations:
            op_lower = op.lower().replace(" ", "_")
            if op_lower in TRANSFORM_OPS:
                code_blocks.append(f"# {op}")
                code_blocks.append(f"# Pattern: {TRANSFORM_OPS[op_lower]}")
                code_blocks.append("")
            else:
                code_blocks.append(f"# {op} — custom operation")
                code_blocks.append("")

        # Generate method chain if multiple operations
        if len(inp.operations) > 2:
            code_blocks.append("# Combined as method chain:")
            code_blocks.append("result = (")
            code_blocks.append("    df")
            for op in inp.operations:
                code_blocks.append(f"    .pipe(lambda x: x)  # {op}")
            code_blocks.append(")")

        return json.dumps({
            "code": "\n".join(code_blocks),
            "operations_requested": inp.operations,
            "available_operations": list(TRANSFORM_OPS.keys()),
            "patterns": {op: TRANSFORM_OPS.get(op.lower().replace(" ", "_"), "custom")
                        for op in inp.operations},
            "best_practices": [
                "Use vectorized ops over .apply() for speed",
                "Use .loc for assignment (avoid chained indexing)",
                "Chain methods with .pipe() for readability",
                "Handle missing data explicitly before transformations",
            ],
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def pandas_generate_aggregate(
    operation: str,
    group_by: list[str] | None = None,
    value_columns: list[str] | None = None,
    agg_functions: list[str] | None = None,
    window_size: int = 7,
) -> str:
    """Generate pandas aggregation code (groupby, pivot, rolling, resample)."""
    try:
        inp = GenerateAggregateInput(
            operation=operation,
            group_by=group_by or [],
            value_columns=value_columns or [],
            agg_functions=agg_functions or ["sum"],
            window_size=window_size,
        )

        lines = ["import pandas as pd", ""]
        op = inp.operation.lower()

        if op == "groupby":
            gb_cols = inp.group_by if inp.group_by else ["key"]
            gb_str = f"'{gb_cols[0]}'" if len(gb_cols) == 1 else str(gb_cols)

            lines.append("# GroupBy with named aggregation (recommended)")
            lines.append(f"result = df.groupby({gb_str}).agg(")
            for vc in (inp.value_columns or ["value"]):
                for af in inp.agg_functions:
                    lines.append(f'    {vc}_{af}=("{vc}", "{af}"),')
            lines.append(")")

        elif op == "pivot_table":
            val = inp.value_columns[0] if inp.value_columns else "value"
            idx = inp.group_by[0] if inp.group_by else "row"
            lines.append("result = df.pivot_table(")
            lines.append(f'    values="{val}",')
            lines.append(f'    index="{idx}",')
            lines.append(f'    columns="category",')
            lines.append(f'    aggfunc="{inp.agg_functions[0]}",')
            lines.append("    fill_value=0,")
            lines.append("    margins=True,")
            lines.append(")")

        elif op == "rolling":
            col = inp.value_columns[0] if inp.value_columns else "value"
            lines.append(f'df["{col}_rolling_{inp.agg_functions[0]}"] = (')
            lines.append(f'    df["{col}"].rolling(window={inp.window_size}, min_periods=1).{inp.agg_functions[0]}()')
            lines.append(")")

        elif op == "resample":
            col = inp.value_columns[0] if inp.value_columns else "value"
            lines.append("# Requires DatetimeIndex")
            lines.append(f'result = df.resample("D")["{col}"].{inp.agg_functions[0]}()')

        elif op == "value_counts":
            col = inp.value_columns[0] if inp.value_columns else "column"
            lines.append(f'result = df["{col}"].value_counts()')
            lines.append(f'result_pct = df["{col}"].value_counts(normalize=True)')

        elif op == "crosstab":
            lines.append("result = pd.crosstab(")
            lines.append(f'    df["{inp.group_by[0] if inp.group_by else "row"}"],')
            lines.append(f'    df["{inp.value_columns[0] if inp.value_columns else "col"}"],')
            lines.append(")")

        lines.append("")
        lines.append("print(result)")

        return json.dumps({
            "code": "\n".join(lines),
            "operation": inp.operation,
            "available_operations": list(AGG_OPS.keys()),
            "pattern": AGG_OPS.get(op, "custom"),
            "tips": [
                "Use named aggregation for clarity: agg(name=('col', 'func'))",
                "Filter columns before groupby for performance",
                "Use sort=False if group order doesn't matter",
            ],
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def pandas_generate_merge(
    operation: str,
    how: str = "inner",
    on: list[str] | None = None,
    left_on: list[str] | None = None,
    right_on: list[str] | None = None,
    merge_validate: str = "",
) -> str:
    """Generate pandas merge/join/concat code for combining DataFrames."""
    try:
        inp = GenerateMergeInput(
            operation=operation,
            how=how,
            on=on or [],
            left_on=left_on or [],
            right_on=right_on or [],
            merge_validate=merge_validate,
        )

        code = _generate_merge_code(
            inp.operation, inp.how, inp.on,
            inp.left_on, inp.right_on, inp.merge_validate,
        )

        return json.dumps({
            "code": code,
            "operation": inp.operation,
            "join_type": inp.how,
            "tips": [
                "Always use validate parameter to catch unexpected duplicates",
                "Use indicator=True to check merge quality",
                "For concat: collect frames in a list, then concat once",
                "merge_asof requires both DataFrames to be sorted",
            ],
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def pandas_generate_io(
    format: str,
    direction: str = "read",
    file_path: str = "data.csv",
) -> str:
    """Generate I/O code for any pandas-supported format."""
    try:
        fmt = format.lower().strip()
        if fmt not in IO_FORMATS:
            return json.dumps({"error": f"Unsupported format: {fmt}. Use one of: {', '.join(IO_FORMATS.keys())}"})

        fmt_info = IO_FORMATS[fmt]
        func = fmt_info["read"] if direction == "read" else fmt_info["write"]

        if direction == "read":
            code = f'import pandas as pd\n\ndf = {func}("{file_path}")\nprint(df.shape)\nprint(df.head())'
        else:
            code = f'df.{func.split(".")[-1]}("{file_path}", index=False)'

        return json.dumps({
            "code": code,
            "format": fmt,
            "function": func,
            "direction": direction,
            "key_params": fmt_info["key_params"],
            "all_formats": list(IO_FORMATS.keys()),
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def pandas_detect_antipatterns(
    code: str,
) -> str:
    """Detect performance anti-patterns in pandas code."""
    try:
        inp = DetectAntipatternsInput(code=code)
        findings = _detect_patterns(inp.code)

        severity_order = {"high": 0, "medium": 1, "low": 2}
        findings.sort(key=lambda f: severity_order.get(f["severity"], 3))

        return json.dumps({
            "findings": findings,
            "count": len(findings),
            "severity_summary": {
                "high": sum(1 for f in findings if f["severity"] == "high"),
                "medium": sum(1 for f in findings if f["severity"] == "medium"),
                "low": sum(1 for f in findings if f["severity"] == "low"),
            },
            "verdict": (
                "CLEAN — no anti-patterns detected"
                if not findings
                else f"ISSUES FOUND — {len(findings)} anti-pattern(s) detected"
            ),
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def pandas_optimize_code(
    code: str,
    priorities: list[str] | None = None,
) -> str:
    """Suggest optimizations for pandas code based on priorities (speed, memory, readability)."""
    try:
        inp = OptimizeCodeInput(code=code, priorities=priorities or ["speed"])

        # Detect anti-patterns first
        findings = _detect_patterns(inp.code)

        suggestions = []

        # Anti-pattern fixes
        for f in findings:
            suggestions.append({
                "priority": "high",
                "category": "fix_antipattern",
                "issue": f["name"],
                "fix": f["fix"],
            })

        # Speed optimizations
        if "speed" in inp.priorities:
            if "apply" in inp.code:
                suggestions.append({
                    "priority": "medium",
                    "category": "speed",
                    "issue": "Consider replacing .apply() with vectorized operations",
                    "fix": "Use built-in pandas/numpy operations instead of apply with lambda",
                })
            if "read_csv" in inp.code and "dtype" not in inp.code:
                suggestions.append({
                    "priority": "medium",
                    "category": "speed",
                    "issue": "Specify dtypes when reading CSV",
                    "fix": "Add dtype parameter to avoid type inference overhead",
                })
            if "csv" in inp.code.lower() and "parquet" not in inp.code.lower():
                suggestions.append({
                    "priority": "low",
                    "category": "speed",
                    "issue": "Consider Parquet format",
                    "fix": "Parquet is 2-10x faster than CSV for read/write",
                })

        # Memory optimizations
        if "memory" in inp.priorities:
            suggestions.append({
                "priority": "medium",
                "category": "memory",
                "issue": "Consider categorical dtypes",
                "fix": "Use .astype('category') for low-cardinality string columns",
            })
            suggestions.append({
                "priority": "medium",
                "category": "memory",
                "issue": "Consider downcasting numeric types",
                "fix": "Use pd.to_numeric(col, downcast='integer') for smaller int types",
            })

        # Readability
        if "readability" in inp.priorities:
            if inp.code.count("[") > 5:
                suggestions.append({
                    "priority": "low",
                    "category": "readability",
                    "issue": "Consider method chaining",
                    "fix": "Use .pipe() and method chaining for cleaner code",
                })
            if "query" not in inp.code and "&" in inp.code:
                suggestions.append({
                    "priority": "low",
                    "category": "readability",
                    "issue": "Consider .query() for boolean indexing",
                    "fix": "df.query('a > 0 and b < 10') is more readable than df[(df['a'] > 0) & (df['b'] < 10)]",
                })

        return json.dumps({
            "suggestions": suggestions,
            "count": len(suggestions),
            "priorities": inp.priorities,
            "anti_patterns_found": len(findings),
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def pandas_generate_pipeline(
    input_format: str = "csv",
    input_path: str = "data.csv",
    steps: list[str] | None = None,
    output_format: str = "csv",
    output_path: str = "output.csv",
    description: str = "",
) -> str:
    """Generate a complete pandas data processing pipeline."""
    try:
        inp = GeneratePipelineInput(
            input_format=input_format,
            input_path=input_path,
            steps=steps or ["read", "clean", "write"],
            output_format=output_format,
            output_path=output_path,
            description=description,
        )

        lines = [
            '"""',
            f"Data Processing Pipeline",
            f"Input: {inp.input_path} ({inp.input_format})",
            f"Output: {inp.output_path} ({inp.output_format})",
            f"Steps: {', '.join(inp.steps)}",
            '"""',
            "",
            "import pandas as pd",
            "import numpy as np",
            "",
        ]

        # Generate step functions
        for step in inp.steps:
            step_lower = step.lower()

            if step_lower == "read":
                read_func = IO_FORMATS.get(inp.input_format, IO_FORMATS["csv"])["read"]
                lines.append(f"# Step: Read data")
                lines.append(f'df = {read_func}("{inp.input_path}")')
                lines.append(f'print(f"Read: {{df.shape[0]}} rows, {{df.shape[1]}} columns")')
                lines.append("")

            elif step_lower == "clean":
                lines.append("# Step: Clean data")
                lines.append("df = (")
                lines.append("    df")
                lines.append("    .rename(columns=str.lower)")
                lines.append("    .rename(columns=lambda x: x.strip().replace(' ', '_'))")
                lines.append("    .drop_duplicates()")
                lines.append("    .dropna(how='all')")
                lines.append("    .reset_index(drop=True)")
                lines.append(")")
                lines.append(f'print(f"After cleaning: {{df.shape[0]}} rows")')
                lines.append("")

            elif step_lower == "filter":
                lines.append("# Step: Filter data")
                lines.append("# df = df.query('column > value')")
                lines.append("# df = df[df['column'].notna()]")
                lines.append("")

            elif step_lower == "transform":
                lines.append("# Step: Transform data")
                lines.append("# df['new_col'] = df['col1'] + df['col2']")
                lines.append("# df['category'] = np.where(df['val'] > 0, 'positive', 'negative')")
                lines.append("")

            elif step_lower == "aggregate":
                lines.append("# Step: Aggregate data")
                lines.append("# result = df.groupby('key').agg(")
                lines.append("#     total=('value', 'sum'),")
                lines.append("#     average=('value', 'mean'),")
                lines.append("#     count=('value', 'count'),")
                lines.append("# )")
                lines.append("")

            elif step_lower == "merge":
                lines.append("# Step: Merge with other data")
                lines.append("# other = pd.read_csv('other.csv')")
                lines.append("# df = pd.merge(df, other, on='key', how='left', validate='many_to_one')")
                lines.append("")

            elif step_lower == "write":
                write_func = IO_FORMATS.get(inp.output_format, IO_FORMATS["csv"])["write"]
                lines.append("# Step: Write output")
                lines.append(f'df.{write_func.split(".")[-1]}("{inp.output_path}", index=False)')
                lines.append(f'print(f"Written: {{df.shape[0]}} rows to {inp.output_path}")')
                lines.append("")

        return json.dumps({
            "code": "\n".join(lines),
            "steps": inp.steps,
            "input": f"{inp.input_path} ({inp.input_format})",
            "output": f"{inp.output_path} ({inp.output_format})",
            "customization_notes": [
                "Uncomment and modify the filter/transform/aggregate/merge steps",
                "Add dtype specifications to read step for better performance",
                "Add error handling with try/except for production use",
            ],
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
