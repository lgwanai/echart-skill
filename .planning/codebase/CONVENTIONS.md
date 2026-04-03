# Coding Conventions

**Analysis Date:** 2026-04-04

## Language & Standards

**Primary Language:** Python 3

**Standards:**
- Follow PEP 8 conventions
- Use type annotations on function signatures (observed in `metrics_manager.py`)
- No explicit linting configuration detected (no `.pylintrc`, `setup.cfg`, or `pyproject.toml` with linting rules)

## Naming Patterns

**Files:**
- Module names use `snake_case`: `chart_generator.py`, `data_importer.py`, `data_exporter.py`
- Utility scripts in subdirectory: `scripts/utils/generate_all_templates.py`

**Functions:**
- Use `snake_case` for all function names
- Examples:
  - `generate_echarts_html()` in `scripts/chart_generator.py`
  - `import_to_sqlite()` in `scripts/data_importer.py`
  - `clean_old_data()` in `scripts/data_cleaner.py`

**Variables:**
- Use `snake_case` for local variables
- Examples: `db_path`, `table_name`, `output_path`, `chunk_size`

**Classes:**
- Use `PascalCase` for class names
- Example: `CustomHTTPRequestHandler` in `scripts/server.py`

**Constants:**
- No strict constant naming convention observed
- Module-level variables use regular naming (e.g., `base_dir`, `support_file`)

## Code Style

**Formatting:**
- No auto-formatter configuration detected (no `black`, `isort`, or `ruff` config)
- 4-space indentation consistently used
- Line length appears to follow ~100-120 characters (not strictly enforced)

**Import Organization:**
Standard library imports first, then third-party, then local:
```python
# Standard library
import argparse
import sqlite3
import os
import json

# Third-party
import pandas as pd

# Local imports
from server import ensure_server_running
```

## Function Design

**Size:**
- Functions are generally focused (<50 lines for simple functions)
- Larger functions exist for complex operations (e.g., `import_to_sqlite()` at ~160 lines in `scripts/data_importer.py`)
- Nested functions used for helpers (e.g., `get_unique_table_name()` inside `import_to_sqlite()`)

**Parameters:**
- Use type annotations where appropriate:
  ```python
  def add_metric(metric_name: str, metric_description: str, file_path: str = "references/metrics.md"):
  ```
- Default parameters for optional configuration
- Config dictionaries used for complex chart generation

**Return Values:**
- Return specific types (paths, DataFrames, None)
- For CLI scripts, often return None and rely on side effects (file creation)

## Error Handling

**Patterns:**
1. **Explicit exception raising for validation:**
   ```python
   if not table_name and not query:
       raise ValueError("Either table_name or query must be provided.")
   ```

2. **Try-except with specific error messages:**
   ```python
   try:
       # operation
   except Exception as e:
       print(f"ERROR: {e}")
   ```

3. **Graceful degradation:**
   ```python
   try:
       with open(cache_file, 'r', encoding='utf-8') as f:
           cache = json.load(f)
   except Exception:
       pass  # Continue with empty cache
   ```

4. **Finally blocks for resource cleanup:**
   ```python
   try:
       conn = sqlite3.connect(db_path)
       # operations
   finally:
       conn.close()
   ```

**Error Messages:**
- Use descriptive error messages
- Include context (file paths, values) when helpful
- Chinese messages used for user-facing output

## Logging

**Framework:** `print()` statements (no formal logging module used)

**Patterns:**
- Success indicators with emojis: `print(f"✅ 交互式 ECharts 图表已生成！")`
- Error prefix: `print(f"ERROR: {e}")`
- Progress messages for long operations
- Warnings for configuration issues

**Suppression:**
- Server logging suppressed: `def log_message(self, format, *args): pass`
- Warnings filtered for known issues (openpyxl): `warnings.filterwarnings('ignore', ...)`

## Comments

**When to Comment:**
- Docstrings for module-level functions describing purpose and parameters
- Section comments for logical blocks within large functions
- Inline comments for complex logic or workarounds

**Docstring Style:**
```python
def export_data(db_path, output_path, table_name=None, query=None):
    """
    Export data from SQLite to a CSV or Excel file.
    Either table_name or query must be provided.
    """
```

**Chinese Comments:**
- Extensive use of Chinese comments for business logic
- Example: `# 提取数据`, `# 自动检测是否使用了 'china' 地图`

## Module Design

**Structure:**
- Each script is self-contained with `if __name__ == "__main__":` block
- CLI argument parsing using `argparse` in main blocks
- Reusable functions defined at module level

**Exports:**
- No `__all__` declarations found
- Functions intended for import are defined at top level
- Scripts can be imported as modules (e.g., `from server import ensure_server_running`)

**Side Effects:**
- Most scripts perform I/O operations (file read/write, database operations)
- Database connections opened and closed within functions

## Configuration

**External Config:**
- `config.txt` for simple key-value pairs (BAIDU_AK)
- JSON files for complex chart configurations
- No formal config management library used

**Environment:**
- Hardcoded paths relative to script location using `os.path.dirname(__file__)`
- Database path defaults to `workspace.db` in project root

## File Organization

**Project Structure:**
```
scripts/
├── chart_generator.py    # HTML/chart generation (242 lines)
├── data_importer.py      # Data import from CSV/Excel (325 lines)
├── data_exporter.py      # Data export to CSV/Excel (59 lines)
├── data_cleaner.py       # Cleanup old data (66 lines)
├── server.py             # HTTP server for viewing charts (118 lines)
├── metrics_manager.py    # Metrics documentation (43 lines)
└── utils/
    └── generate_all_templates.py  # Template generation
```

**Size Guidelines:**
- Files range from 43 to 325 lines
- Largest file (`data_importer.py`) handles complex Excel/CSV import logic
- No strict file size limit enforced

## Special Patterns

**Path Resolution:**
```python
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```
Used consistently to reference project root from any script location.

**Database Operations:**
- SQLite used as primary data store
- Context managers not used (explicit connect/close)
- Parameterized queries used throughout

**Template Generation:**
- JSON templates for ECharts configurations
- Placeholder replacement using recursive function
- Custom JavaScript injection for complex interactions

---

*Convention analysis: 2026-04-04*
