# Testing Patterns

**Analysis Date:** 2026-04-04

## Test Framework Status

**Current State:** NO TESTS DETECTED

- No test files found (no `*.test.py`, `*.spec.py`, or `test_*.py` files)
- No test configuration files (no `pytest.ini`, `setup.cfg`, `pyproject.toml` with test config)
- No testing framework in `requirements.txt`

## Test Framework Recommendation

**Recommended Framework:** pytest

**Why pytest:**
- Standard for Python testing
- Compatible with pandas/numpy testing patterns
- Good fixture support for database testing
- Simple assertion syntax

**Suggested Dependencies:**
```
pytest>=7.0.0
pytest-cov>=4.0.0
```

## Test Organization (Recommended)

**Directory Structure:**
```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_data_importer.py
│   ├── test_data_exporter.py
│   ├── test_chart_generator.py
│   └── test_data_cleaner.py
├── integration/
│   ├── __init__.py
│   ├── test_import_export_flow.py
│   └── test_chart_generation_flow.py
├── fixtures/
│   ├── sample.csv
│   ├── sample.xlsx
│   └── sample_config.json
└── conftest.py
```

**Test File Naming:**
- `test_<module_name>.py` for unit tests
- `test_<feature>_flow.py` for integration tests

## Test Structure (Recommended Pattern)

**Unit Test Example:**
```python
import pytest
from scripts.data_importer import clean_column_names, calculate_md5

class TestCleanColumnNames:
    def test_removes_special_characters(self):
        columns = ["Name", "Age (years)", "Salary $"]
        result = clean_column_names(columns)
        assert result == ["Name", "Age_years", "Salary_"]
    
    def test_handles_duplicates(self):
        columns = ["Name", "Name", "Name"]
        result = clean_column_names(columns)
        assert result == ["Name", "Name_1", "Name_2"]
    
    def test_handles_na_values(self):
        columns = [None, "Valid", ""]
        result = clean_column_names(columns)
        assert result[0] == "Unnamed"
```

**Integration Test Example:**
```python
import pytest
import sqlite3
import os
from scripts.data_importer import import_to_sqlite
from scripts.data_exporter import export_data

class TestImportExportFlow:
    def test_csv_import_export_roundtrip(self, tmp_path):
        # Setup
        csv_path = tmp_path / "input.csv"
        csv_path.write_text("name,age\nAlice,30\nBob,25")
        db_path = tmp_path / "test.db"
        output_path = tmp_path / "output.csv"
        
        # Execute
        import_to_sqlite(str(csv_path), str(db_path), "test_table")
        export_data(str(db_path), str(output_path), table_name="test_table")
        
        # Verify
        assert output_path.exists()
        content = output_path.read_text()
        assert "Alice" in content
        assert "Bob" in content
```

## Mocking (Recommended)

**Framework:** pytest-mock (mocker fixture)

**Patterns:**
```python
def test_geocoding_with_cache(mocker):
    # Mock file operations
    mock_open = mocker.patch('builtins.open')
    mock_json = mocker.patch('json.load')
    mock_json.return_value = {"Beijing": [116.4, 39.9]}
    
    from scripts.chart_generator import get_geo_coord
    result = get_geo_coord("Beijing", "fake_ak")
    
    assert result == [116.4, 39.9]
```

**What to Mock:**
- External API calls (Baidu geocoding)
- File system operations (use tmp_path fixture instead)
- Database connections (use in-memory SQLite)
- HTTP requests

## Fixtures and Factories (Recommended)

**conftest.py:**
```python
import pytest
import sqlite3
import pandas as pd
import tempfile
import os

@pytest.fixture
def temp_db():
    """Create a temporary SQLite database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    conn = sqlite3.connect(db_path)
    yield db_path, conn
    conn.close()
    os.unlink(db_path)

@pytest.fixture
def sample_dataframe():
    """Return a sample DataFrame for testing."""
    return pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [30, 25, 35],
        'salary': [50000, 60000, 70000]
    })

@pytest.fixture
def sample_chart_config():
    """Return a sample chart configuration."""
    return {
        "db_path": "test.db",
        "query": "SELECT * FROM test",
        "title": "Test Chart",
        "output_path": "test_output.html",
        "echarts_option": {}
    }
```

## Coverage

**Current State:** No coverage measurement configured

**Recommended Target:** 80% minimum (per project standards)

**Commands:**
```bash
# Run tests with coverage
pytest --cov=scripts --cov-report=term-missing

# Generate HTML report
pytest --cov=scripts --cov-report=html

# Check coverage threshold
pytest --cov=scripts --cov-fail-under=80
```

## Test Types Needed

**Unit Tests (Priority: High):**
- `data_importer.py`: `clean_column_names()`, `calculate_md5()`, `find_header_row()`
- `data_exporter.py`: Format detection, export validation
- `chart_generator.py`: Placeholder replacement, HTML template generation
- `data_cleaner.py`: Date filtering, table cleanup logic

**Integration Tests (Priority: High):**
- CSV import -> SQLite -> Export flow
- Excel with merged cells import
- Chart generation with sample data
- Server startup and health check

**E2E Tests (Priority: Medium):**
- Full workflow: Import data -> Query -> Generate chart -> View in browser

## Critical Test Coverage Gaps

**High Risk - No Tests:**
1. **Data Import Logic** (`scripts/data_importer.py` - 325 lines)
   - File format detection
   - Header row detection
   - Column name sanitization
   - Duplicate import detection (MD5 hashing)
   - Excel merged cell handling

2. **Chart Generation** (`scripts/chart_generator.py` - 242 lines)
   - ECharts option generation
   - HTML template rendering
   - Placeholder replacement logic
   - Baidu map integration

3. **Data Export** (`scripts/data_exporter.py` - 59 lines)
   - Format detection (CSV vs Excel)
   - Query execution
   - File writing

4. **Data Cleanup** (`scripts/data_cleaner.py` - 66 lines)
   - Date-based filtering
   - Table dropping logic

## Testing Commands (To Implement)

**Run Tests:**
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_data_importer.py

# Run specific test
pytest tests/unit/test_data_importer.py::TestCleanColumnNames

# Run with watch mode
pytest-watch
```

**Coverage:**
```bash
# View coverage report
pytest --cov=scripts --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=scripts --cov-report=html
```

## Testing Challenges

**File System Dependencies:**
- Many functions read/write files
- Solution: Use `tmp_path` fixture and monkeypatch

**Database Dependencies:**
- SQLite operations throughout
- Solution: Use in-memory database or temp files

**External API Calls:**
- Baidu geocoding API
- Solution: Mock `urllib.request` calls

**HTTP Server:**
- Server startup in background
- Solution: Use subprocess or mock server class

## Recommended First Tests

**Priority 1 - Critical Functions:**
1. `clean_column_names()` - Input validation, edge cases
2. `calculate_md5()` - File hashing consistency
3. `replace_placeholders()` - Template rendering
4. `find_header_row()` - Header detection logic

**Priority 2 - Integration:**
1. CSV import roundtrip
2. Excel import with merged cells
3. Chart HTML generation

---

*Testing analysis: 2026-04-04*
