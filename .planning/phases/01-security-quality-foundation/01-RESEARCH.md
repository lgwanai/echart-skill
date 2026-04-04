# Phase 1: Security & Quality Foundation - Research

**Researched:** 2026-04-04
**Domain:** Python security hardening, testing infrastructure, structured logging
**Confidence:** HIGH (verified from source code analysis and project context)

## Summary

This phase addresses critical security vulnerabilities (SQL injection in table name handling) and establishes quality infrastructure (testing framework, structured logging). The codebase has clear injection points at `data_exporter.py:26` and `data_cleaner.py:43` where f-strings directly interpolate table names into SQL. The project lacks any test infrastructure, has no structured logging, and uses hardcoded API keys. All print statements need migration to structlog.

**Primary recommendation:** Implement table name whitelist validation using regex pattern `^[a-zA-Z][a-zA-Z0-9_]*$`, set up pytest with conftest.py fixtures, and migrate all logging to structlog with file output.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**测试优先级**
- 测试顺序：业务核心优先 — chart_generator.py + data_importer.py 最先测试
- 覆盖率目标：所有核心模块达到 80% 覆盖率
- 后续测试：data_exporter.py, data_cleaner.py（安全相关）, server.py, metrics_manager.py

**日志策略**
- 日志框架：structlog（结构化日志，便于 AI Agent 解析）
- 日志级别：标准级别 — INFO for 正常操作, WARNING for 节点问题, ERROR for 异常
- 输出位置：仅文件 — logs/echart-skill.log
- 结构化字段：基础字段（时间戳、级别、模块名）+ 操作上下文（文件路径、表名、SQL 摘要）+ 性能指标（执行耗时、数据量）+ 错误详情（堆栈、异常）

**校验严格度**
- 表名校验：严格白名单 — 仅允许字母、数字、下划线，且以字母开头
- 路径校验：严格路径限制 — 必须在项目目录内，拒绝 ../ 等路径穿越
- 错误语言：中文 — 符合现有代码风格

**向后兼容性**
- API Key 迁移：环境变量优先 + 回退 — 优先读环境变量，回退到 config.txt
- 弃用策略：立即移除 config.txt 支持 — 明确告知用户需要迁移

### Claude's Discretion

None specified — all decisions were locked.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SEC-01 | SQL injection vulnerabilities fixed in data_exporter.py and data_cleaner.py using table name whitelist validation | Table name whitelist pattern `^[a-zA-Z][a-zA-Z0-9_]*$`; SQLite parameterized queries for other values |
| SEC-02 | Input validation added for file paths, table names, and SQL queries using pydantic | pydantic 2.12.5 with FilePath validator; custom validators for table names |
| SEC-03 | Baidu API key removed from config.txt, replaced with environment variable | os.environ.get() pattern; immediate deprecation of config.txt |
| SEC-04 | Path traversal protection added to server.py file serving | os.path.realpath() + startswith() check against base directory |
| QUAL-01 | Logging framework (structlog) replaces all print() statements | structlog 25.5.0 with file handler; JSON output format |
| QUAL-02 | Silent exception handling eliminated - all exceptions logged | Replace bare `except:` with explicit types + structlog.error() |
| QUAL-03 | pytest test framework set up with conftest.py fixtures | pytest 9.0.2 + pytest-cov 7.1.0 + pytest-asyncio 1.3.0 |
| QUAL-04 | Unit tests for core modules (chart_generator, data_importer, server) | Test files: tests/test_chart_generator.py, tests/test_data_importer.py, tests/test_server.py |
| QUAL-05 | Integration tests for end-to-end workflows | Test file: tests/test_integration.py |
| QUAL-06 | Test coverage reaches 80%+ for core modules | pytest-cov with --cov-fail-under=80 |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.2 | Testing framework | Python ecosystem standard; native marker support for test categorization; extensive plugin ecosystem |
| structlog | 25.5.0 | Structured logging | JSON output for AI agent consumption; context binding; stdlib integration |
| pydantic | 2.12.5 | Input validation | Runtime validation with type hints; clear error messages; zero-trust boundary |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-cov | 7.1.0 | Coverage reporting | Required for 80% coverage enforcement |
| pytest-asyncio | 1.3.0 | Async test support | Testing async code (future Phase 2) |
| respx | 0.22.0 | HTTP mocking for httpx | Mocking Baidu API in tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| structlog | logging (stdlib) | Use stdlib only if external dependencies must be minimized; structlog's structured output is critical for AI agent integration |
| pydantic | manual validation | Manual validation is error-prone and verbose; pydantic provides declarative validation with clear errors |

**Installation:**
```bash
pip install pytest==9.0.2 pytest-cov==7.1.0 pytest-asyncio==1.3.0 structlog==25.5.0 pydantic==2.12.5 respx==0.22.0
```

## Architecture Patterns

### Recommended Project Structure
```
.
├── scripts/              # Existing CLI scripts (modified)
│   ├── chart_generator.py
│   ├── data_cleaner.py
│   ├── data_exporter.py
│   ├── data_importer.py
│   ├── metrics_manager.py
│   └── server.py
├── tests/                # NEW: Test infrastructure
│   ├── __init__.py
│   ├── conftest.py       # Shared fixtures
│   ├── test_chart_generator.py
│   ├── test_data_importer.py
│   ├── test_data_exporter.py
│   ├── test_data_cleaner.py
│   ├── test_server.py
│   └── test_integration.py
├── logging_config.py     # NEW: Structlog configuration
├── validators.py         # NEW: Input validation utilities
└── logs/                 # NEW: Log output directory
    └── echart-skill.log
```

### Pattern 1: Table Name Whitelist Validation

**What:** Validate table names against strict whitelist pattern before SQL interpolation
**When to use:** Anywhere user input is used as SQL identifier (table name, column name)
**Example:**
```python
import re

# Compile once at module level for performance
TABLE_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')

def validate_table_name(table_name: str) -> str:
    """
    Validate table name against whitelist pattern.
    Only allows letters, numbers, underscores; must start with letter.
    """
    if not table_name:
        raise ValueError("表名不能为空")

    if not TABLE_NAME_PATTERN.match(table_name):
        raise ValueError(f"无效的表名 '{table_name}': 表名只能包含字母、数字和下划线，且必须以字母开头")

    # Check for SQL reserved words (optional additional protection)
    reserved_words = {'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter', 'table'}
    if table_name.lower() in reserved_words:
        raise ValueError(f"'{table_name}' 是 SQL 保留字，不能作为表名")

    return table_name

# Usage in data_exporter.py:
def export_data(db_path, output_path, table_name=None, query=None):
    # ... existing code ...
    if table_name:
        table_name = validate_table_name(table_name)  # Validate before use
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
```

### Pattern 2: Path Traversal Prevention

**What:** Ensure file paths stay within allowed directories
**When to use:** Any file operation with user-provided paths
**Example:**
```python
import os
from pathlib import Path

def validate_path_in_directory(file_path: str, base_dir: str) -> str:
    """
    Validate that file_path is within base_dir.
    Prevents path traversal attacks using ../ or symlinks.
    """
    # Resolve to absolute path (follows symlinks)
    real_path = os.path.realpath(file_path)
    real_base = os.path.realpath(base_dir)

    # Ensure path starts with base directory
    if not real_path.startswith(real_base + os.sep) and real_path != real_base:
        raise ValueError(f"路径 '{file_path}' 不在允许的目录内")

    return real_path

# Usage in server.py:
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Validate path before serving
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        requested_path = os.path.join(base_dir, self.path.lstrip('/'))
        try:
            validated_path = validate_path_in_directory(requested_path, base_dir)
        except ValueError as e:
            self.send_error(403, str(e))
            return
        super().do_GET()
```

### Pattern 3: Structlog Configuration

**What:** Centralized structured logging with file output
**When to use:** All logging throughout the application
**Example:**
```python
# logging_config.py
import logging
import sys
from pathlib import Path
import structlog

def configure_logging(log_file: str = "logs/echart-skill.log"):
    """Configure structlog with file output."""
    # Ensure log directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
        ],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger for a module."""
    return structlog.get_logger(name)

# Usage in any module:
from logging_config import get_logger

logger = get_logger(__name__)

def export_data(db_path, output_path, table_name=None, query=None):
    logger.info("开始导出数据", db_path=db_path, output_path=output_path,
                table_name=table_name, query_summary=query[:50] if query else None)
    try:
        # ... do work ...
        logger.info("导出完成", rows_exported=len(df), output_path=output_path)
    except Exception as e:
        logger.error("导出失败", error=str(e), exc_info=True)
        raise
```

### Pattern 4: API Key Environment Variable Migration

**What:** Read API keys from environment with fallback to config file (deprecated)
**When to use:** All secret/key management
**Example:**
```python
import os
import warnings

def get_baidu_ak() -> str | None:
    """
    Retrieve Baidu AK from environment variable.
    config.txt support is DEPRECATED and will be removed.
    """
    # Primary: environment variable
    ak = os.environ.get('BAIDU_AK')
    if ak:
        return ak

    # Fallback: config.txt (DEPRECATED)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.txt')

    if os.path.exists(config_path):
        warnings.warn(
            "从 config.txt 读取 BAIDU_AK 已弃用，请设置环境变量 BAIDU_AK",
            DeprecationWarning,
            stacklevel=2
        )
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('BAIDU_AK='):
                    ak = line.strip().split('=', 1)[1]
                    if ak:
                        return ak

    return None
```

### Pattern 5: Pytest Fixtures for Common Test Data

**What:** Shared test fixtures in conftest.py
**When to use:** All test files that need common setup
**Example:**
```python
# tests/conftest.py
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE test_data (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value REAL
        )
    ''')
    conn.execute("INSERT INTO test_data (name, value) VALUES ('test1', 100)")
    conn.execute("INSERT INTO test_data (name, value) VALUES ('test2', 200)")
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    os.unlink(db_path)

@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_config():
    """Sample chart configuration for testing."""
    return {
        "db_path": "workspace.db",
        "query": "SELECT name, value FROM test_data",
        "title": "Test Chart",
        "output_path": "tmp/test_chart.html"
    }
```

### Anti-Patterns to Avoid

- **Bare except clauses:** `except Exception: pass` silently swallows errors. Use explicit exception types and log with structlog.error().
- **f-string SQL interpolation:** `f"SELECT * FROM {table_name}"` allows SQL injection. Always validate identifiers against whitelist.
- **print() for output:** Use structlog for all output; print statements cannot be filtered by level or parsed by AI agents.
- **Hardcoded secrets in source:** API keys must come from environment variables.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Logging | print() statements | structlog | No level filtering, no structured context, can't parse programmatically |
| Validation | Manual regex checks scattered in code | pydantic validators | Centralized, reusable, clear error messages |
| Test fixtures | Duplicate setup code in each test | pytest fixtures | DRY principle, shared state, easy cleanup |
| Coverage | Manual test tracking | pytest-cov | Automated measurement, fail thresholds, HTML reports |

**Key insight:** Security vulnerabilities arise from ad-hoc solutions. Use proven libraries and patterns.

## Common Pitfalls

### Pitfall 1: Incomplete SQL Injection Fix

**What goes wrong:** Fixing only the obvious f-string cases but missing indirect injection points
**Why it happens:** Developer focuses on `f"SELECT * FROM {table_name}"` but misses that `query` parameter in data_exporter.py is also vulnerable
**How to avoid:** Audit all SQL execution paths; any user input going into SQL must be validated
**Warning signs:** Any string formatting with variables that go into SQL execution

### Pitfall 2: Log File Permission Issues

**What goes wrong:** Application fails silently when logs/ directory doesn't exist or isn't writable
**Why it happens:** Logging configuration doesn't create parent directories
**How to avoid:** `Path(log_file).parent.mkdir(parents=True, exist_ok=True)` before configuring logging
**Warning signs:** Logs not appearing after deployment

### Pitfall 3: Environment Variable Not Set

**What goes wrong:** API calls fail because BAIDU_AK environment variable wasn't set
**Why it happens:** User didn't read migration documentation or set variable in wrong shell
**How to avoid:** Clear error message with setup instructions; check at startup, not just when needed
**Warning signs:** Geocoding returning None without clear error

### Pitfall 4: Test Coverage Gaps

**What goes wrong:** Coverage reports 80%+ but critical paths aren't tested
**Why it happens:** Tests cover happy paths but not edge cases and error handling
**How to avoid:** Use pytest-cov's branch coverage; write tests for error paths
**Warning signs:** Tests pass but bugs still occur in production

## Code Examples

### Table Name Validation (SEC-01)

```python
# validators.py
import re
from typing import Final

TABLE_NAME_PATTERN: Final = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
MAX_TABLE_NAME_LENGTH: Final = 128

SQL_RESERVED_WORDS: Final = frozenset({
    'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter',
    'table', 'index', 'view', 'trigger', 'schema', 'database',
    'from', 'where', 'join', 'inner', 'outer', 'left', 'right',
    'on', 'group', 'order', 'having', 'limit', 'offset', 'union',
    'all', 'distinct', 'as', 'and', 'or', 'not', 'null', 'true', 'false',
})

def validate_table_name(table_name: str) -> str:
    """
    Validate table name for SQL safety.

    Rules:
    - Must start with a letter
    - Can only contain letters, numbers, underscores
    - Cannot be a SQL reserved word
    - Max length 128 characters

    Raises:
        ValueError: If table name is invalid
    """
    if not table_name:
        raise ValueError("表名不能为空")

    if len(table_name) > MAX_TABLE_NAME_LENGTH:
        raise ValueError(f"表名过长，最大允许 {MAX_TABLE_NAME_LENGTH} 个字符")

    if not TABLE_NAME_PATTERN.match(table_name):
        raise ValueError(
            f"无效的表名 '{table_name}': "
            "表名只能包含字母、数字和下划线，且必须以字母开头"
        )

    if table_name.lower() in SQL_RESERVED_WORDS:
        raise ValueError(f"'{table_name}' 是 SQL 保留字，不能作为表名")

    return table_name
```

### Path Validation (SEC-02, SEC-04)

```python
# validators.py
import os
from pathlib import Path

def validate_file_path(
    file_path: str | Path,
    base_dir: str | Path,
    must_exist: bool = False
) -> Path:
    """
    Validate that file path is within base directory.

    Args:
        file_path: Path to validate
        base_dir: Base directory that paths must be within
        must_exist: If True, raise error if file doesn't exist

    Returns:
        Validated absolute Path

    Raises:
        ValueError: If path is outside base directory
        FileNotFoundError: If must_exist=True and file not found
    """
    file_path = Path(file_path)
    base_dir = Path(base_dir).resolve()

    # Resolve to absolute path (follows symlinks, handles ..)
    try:
        resolved_path = file_path.resolve()
    except OSError as e:
        raise ValueError(f"无效的文件路径: {e}")

    # Check for path traversal
    if not str(resolved_path).startswith(str(base_dir) + os.sep):
        if resolved_path != base_dir:
            raise ValueError(
                f"路径 '{file_path}' 不在允许的目录 '{base_dir}' 内"
            )

    if must_exist and not resolved_path.exists():
        raise FileNotFoundError(f"文件不存在: {resolved_path}")

    return resolved_path
```

### Structlog Configuration (QUAL-01)

```python
# logging_config.py
import logging
import sys
from pathlib import Path
from typing import Any

import structlog


def configure_logging(
    log_file: str = "logs/echart-skill.log",
    level: int = logging.INFO,
) -> None:
    """
    Configure structlog for the application.

    Args:
        log_file: Path to log file
        level: Minimum log level
    """
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure standard library logging to file
    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
        ],
    )

    # Configure structlog processors
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured structlog logger.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Context manager for operation logging
class LogOperation:
    """Context manager for logging operation start/end."""

    def __init__(self, logger: structlog.stdlib.BoundLogger, operation: str, **context: Any):
        self.logger = logger
        self.operation = operation
        self.context = context

    def __enter__(self) -> "LogOperation":
        self.logger.info(f"开始{self.operation}", **self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self.logger.info(f"完成{self.operation}", **self.context)
        else:
            self.logger.error(
                f"{self.operation}失败",
                error=str(exc_val),
                error_type=exc_type.__name__,
                **self.context
            )
```

### Pydantic Validation Model (SEC-02)

```python
# validators.py
from pathlib import Path
from typing import Self

from pydantic import BaseModel, field_validator, model_validator


class ExportConfig(BaseModel):
    """Validated configuration for data export."""

    db_path: Path
    output_path: Path
    table_name: str | None = None
    query: str | None = None

    @field_validator('table_name')
    @classmethod
    def validate_table_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return validate_table_name(v)

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Basic validation: must start with SELECT
        if not v.strip().upper().startswith('SELECT'):
            raise ValueError("查询语句必须以 SELECT 开头")
        # Check for dangerous patterns
        dangerous_patterns = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
        query_upper = v.upper()
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                raise ValueError(f"查询语句不能包含 {pattern}")
        return v

    @model_validator(mode='after')
    def check_table_or_query(self) -> Self:
        if self.table_name is None and self.query is None:
            raise ValueError("必须提供 table_name 或 query")
        return self
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| print() statements | structlog with JSON | Phase 1 | Structured logs parseable by AI agents |
| f-string SQL | Whitelist validation | Phase 1 | Prevents SQL injection attacks |
| Hardcoded API keys | Environment variables | Phase 1 | Secrets no longer in source control |
| No test infrastructure | pytest + pytest-cov | Phase 1 | Automated quality gates |

**Deprecated/outdated:**
- config.txt for API keys: Security risk, replaced by environment variables
- Bare except clauses: Silent failures, replaced by explicit exception handling with logging

## Open Questions

1. **Query validation depth**
   - What we know: Basic SELECT-only validation is easy
   - What's unclear: How sophisticated should SQL query validation be?
   - Recommendation: Start with SELECT-only + dangerous keyword blacklist; expand if needed

2. **Log rotation**
   - What we know: structlog can integrate with logging.handlers.RotatingFileHandler
   - What's unclear: What size/count limits for log rotation?
   - Recommendation: Start with 10MB max size, 5 backup files; adjust based on usage

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | pyproject.toml (to be created) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ --cov=scripts --cov-fail-under=80 -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SEC-01 | Table name validation blocks injection | unit | `pytest tests/test_validators.py::test_table_name_validation -x` | Wave 0 |
| SEC-01 | SQL injection blocked in data_exporter | unit | `pytest tests/test_data_exporter.py::test_sql_injection_blocked -x` | Wave 0 |
| SEC-01 | SQL injection blocked in data_cleaner | unit | `pytest tests/test_data_cleaner.py::test_sql_injection_blocked -x` | Wave 0 |
| SEC-02 | Path traversal blocked | unit | `pytest tests/test_validators.py::test_path_traversal_blocked -x` | Wave 0 |
| SEC-02 | Invalid table names rejected | unit | `pytest tests/test_validators.py::test_invalid_table_names -x` | Wave 0 |
| SEC-03 | API key from environment | unit | `pytest tests/test_chart_generator.py::test_api_key_from_env -x` | Wave 0 |
| SEC-04 | Path traversal in server blocked | unit | `pytest tests/test_server.py::test_path_traversal_blocked -x` | Wave 0 |
| QUAL-01 | Logging configured correctly | unit | `pytest tests/test_logging_config.py::test_logging_setup -x` | Wave 0 |
| QUAL-01 | All print statements removed | unit | `pytest tests/test_no_print.py -x` | Wave 0 |
| QUAL-02 | Exceptions logged not silenced | unit | `pytest tests/test_exception_handling.py -x` | Wave 0 |
| QUAL-03 | pytest fixtures work | unit | `pytest tests/test_conftest.py -x` | Wave 0 |
| QUAL-04 | chart_generator unit tests | unit | `pytest tests/test_chart_generator.py -x` | Wave 0 |
| QUAL-04 | data_importer unit tests | unit | `pytest tests/test_data_importer.py -x` | Wave 0 |
| QUAL-04 | server unit tests | unit | `pytest tests/test_server.py -x` | Wave 0 |
| QUAL-05 | End-to-end import-export flow | integration | `pytest tests/test_integration.py::test_import_export_flow -x` | Wave 0 |
| QUAL-06 | Coverage threshold | quality | `pytest --cov-fail-under=80` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ --cov=scripts -v`
- **Phase gate:** `pytest tests/ --cov=scripts --cov-fail-under=80 -v`

### Wave 0 Gaps
- [ ] `tests/conftest.py` - shared fixtures (temp_db, temp_output_dir, sample_config)
- [ ] `tests/test_validators.py` - input validation tests
- [ ] `tests/test_data_exporter.py` - SQL injection + export functionality tests
- [ ] `tests/test_data_cleaner.py` - SQL injection + cleanup functionality tests
- [ ] `tests/test_chart_generator.py` - chart generation + API key tests
- [ ] `tests/test_data_importer.py` - import functionality tests
- [ ] `tests/test_server.py` - server + path traversal tests
- [ ] `tests/test_logging_config.py` - logging setup tests
- [ ] `tests/test_no_print.py` - verify no print statements
- [ ] `tests/test_exception_handling.py` - exception logging tests
- [ ] `tests/test_integration.py` - end-to-end workflow tests
- [ ] `pyproject.toml` - pytest and coverage configuration
- [ ] Framework install: `pip install pytest pytest-cov pytest-asyncio structlog pydantic respx`

## Sources

### Primary (HIGH confidence)
- Project source code analysis - data_exporter.py, data_cleaner.py, chart_generator.py, server.py, data_importer.py
- .planning/research/STACK.md - Technology recommendations with version verification
- .planning/codebase/CONCERNS.md - Security vulnerabilities and quality issues catalog

### Secondary (MEDIUM confidence)
- Python typing and pathlib documentation patterns
- structlog configuration patterns from training knowledge
- pytest fixture patterns from training knowledge

### Tertiary (LOW confidence)
- WebSearch for specific library configurations returned empty; relied on training knowledge for structlog and pydantic patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - versions verified from STACK.md research, compatible with Python 3.13
- Architecture: HIGH - patterns derived from existing codebase analysis
- Pitfalls: HIGH - identified from actual CONCERNS.md audit

**Research date:** 2026-04-04
**Valid until:** 30 days (stable libraries, security patterns are long-term stable)
