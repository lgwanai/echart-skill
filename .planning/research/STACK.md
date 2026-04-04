# Stack Research

**Domain:** Python data analysis tool with visualization (ECharts integration)
**Researched:** 2026-04-04
**Confidence:** HIGH (versions verified from PyPI)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.13+ | Runtime environment | Project already uses 3.13; latest stable with performance improvements |
| pytest | 9.0.2 | Testing framework | Python ecosystem standard; extensive plugin system; native marker support for unit/integration test categorization |
| structlog | 25.5.0 | Structured logging | Structured output for AI agent consumption; context binding; seamless stdlib logging integration |
| httpx | 0.28.1 | Async HTTP client | Modern async/await syntax; HTTP/2 support; better API than aiohttp; unified sync/async interface |
| pydantic | 2.12.5 | Input validation | Runtime validation with type hints; clear error messages for user input; zero-trust boundary enforcement |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-asyncio | 1.3.0 | Async test support | Required for testing httpx async code |
| pytest-cov | 7.1.0 | Coverage reporting | Required for 80% coverage enforcement |
| respx | 0.22.0 | HTTP mocking for httpx | Mocking external API calls in tests (better than aioresponses which is aiohttp-specific) |
| tenacity | 9.1.4 | Retry logic | Async-compatible retry for geocoding API calls with exponential backoff |
| pandas | 2.3.3+ | Data manipulation | Already in use; upgrade to latest stable for performance improvements |
| openpyxl | 3.1.5 | Excel handling | Already in use; latest stable |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| ruff | 0.15.9 | Linting and formatting | Replaces flake8 + isort + black; 100x faster; single config |
| mypy | 1.20.0 | Static type checking | Catch type errors before runtime; strict mode recommended |

## Installation

```bash
# Core testing and logging
pip install pytest==9.0.2 pytest-asyncio==1.3.0 pytest-cov==7.1.0 structlog==25.5.0

# Async HTTP and validation
pip install httpx==0.28.1 pydantic==2.12.5 tenacity==9.1.4

# Test mocking
pip install respx==0.22.0

# Development tools
pip install ruff==0.15.9 mypy==1.20.0
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| pytest | unittest | Only for stdlib-only constraints; pytest is universally preferred |
| structlog | logging (stdlib) | Use stdlib logging only if external dependencies must be minimized; structlog's structured output is critical for AI agent integration |
| httpx | aiohttp | Use aiohttp only for existing codebases already using it; httpx has better async API and HTTP/2 |
| httpx | requests | requests is sync-only; httpx provides both sync and async with identical API |
| pydantic | marshmallow | marshmallow for complex serialization; pydantic for validation-first with better type inference |
| respx | aioresponses | aioresponses is aiohttp-specific; respx is designed for httpx |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| print() statements | Silent failures; no severity levels; unstructured output | structlog with appropriate log levels |
| unittest | Verbose boilerplate; no fixtures; poor async support | pytest with pytest-asyncio |
| requests | Sync-only; blocks event loop in async code | httpx (supports both sync and async) |
| bare except clauses | Swallowing exceptions silently | Explicit exception types with proper logging |
| string concatenation for SQL | SQL injection vulnerability | Parameterized queries with `?` placeholders |

## Stack Patterns by Variant

**For URL/API Data Source Feature:**
- Use httpx.AsyncClient for fetching external data
- Use pydantic for validating API responses before processing
- Use tenacity for retry logic with exponential backoff
- Pattern: `async with httpx.AsyncClient() as client: response = await client.get(url)`

**For Large File Streaming:**
- Use pandas chunksize parameter (already partially implemented)
- Pattern: `pd.read_csv(file_path, chunksize=50000)` for memory-safe processing
- Combine with generator pattern for lazy evaluation

**For Dashboard Layout:**
- Pure ECharts grid option (no additional Python dependency needed)
- Use ECharts `grid` option array for multi-chart layout
- Each chart gets its own grid definition with x/y position

**For Gantt Chart:**
- ECharts custom series (already supported in ECharts 6.0)
- No additional Python library required
- Use `series.type: 'custom'` with renderItem function

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| pytest@9.0.2 | pytest-asyncio@1.3.0 | Full compatibility confirmed |
| httpx@0.28.1 | respx@0.22.0 | Designed together; full mock support |
| pydantic@2.12.5 | Python 3.13+ | Full support for Python 3.13 type hints |
| structlog@25.5.0 | Python 3.13+ | Native asyncio support |

## Sources

- PyPI package index — Version verification (HIGH confidence)
- Project codebase analysis — Current implementation patterns (HIGH confidence)
- WebSearch for ECharts dashboard patterns — Grid layout best practices (MEDIUM confidence)

---
*Stack research for: echart-skill quality improvement*
*Researched: 2026-04-04*
