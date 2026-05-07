# Phase 3: Dashboard Layouts - Research

**Researched:** 2026-04-04
**Domain:** Multi-chart dashboard generation with CSS Grid layout and ECharts
**Confidence:** MEDIUM

## Summary

This phase implements a dashboard generator that creates multi-chart layouts in a single HTML file. The solution combines CSS Grid Layout for flexible positioning with ECharts' standard multi-instance pattern (one DOM container per chart). The existing `chart_generator.py` provides the foundation for chart generation; the dashboard generator will orchestrate multiple chart configurations into a unified HTML output.

The key insight is that ECharts dashboard layouts are primarily an HTML/CSS concern rather than an ECharts API concern. Each chart is an independent `echarts.init(dom)` call, and CSS Grid handles the positioning. The dashboard generator's role is to:
1. Validate dashboard configuration against a JSON schema
2. Generate HTML with CSS Grid layout
3. Iterate through chart configurations, generating ECharts options and embedding them

**Primary recommendation:** Use CSS Grid Layout with explicit row/column positioning, combined with pydantic for configuration validation. Build on existing `generate_echarts_html()` pattern.

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DASH-01 | Grid layout engine for multi-chart dashboard composition | CSS Grid Layout with `grid-template-columns`, `grid-template-rows`, and `grid-area` for explicit positioning |
| DASH-02 | Dashboard configuration JSON schema for chart placement | pydantic v2 `BaseModel` with validation, JSON schema generation via `model_json_schema()` |
| DASH-03 | Single HTML export for complete dashboards | Combine all chart options in one HTML template with multiple ECharts instances |
| DASH-04 | Dashboard generator script (scripts/dashboard_generator.py) | Extend existing `chart_generator.py` patterns, use same database repository and logging infrastructure |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| CSS Grid Layout | CSS3 | Dashboard layout | Native browser support, no dependencies, flexible grid positioning |
| pydantic | v2.x | Configuration validation | Already used in project for input validation, JSON schema generation built-in |
| ECharts | 6.0 | Chart rendering | Already integrated, multi-instance support is standard pattern |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| jsonschema | 4.x | Optional schema validation | If external schema validation needed beyond pydantic |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CSS Grid | Flexbox | Flexbox is one-dimensional; Grid handles 2D layouts better |
| CSS Grid | Bootstrap Grid | External dependency; CSS Grid is native |
| pydantic | jsonschema library | jsonschema requires manual schema definition; pydantic derives schema from model |
| Single HTML | iframe-based | iframe approach separates charts but adds complexity and breaks interactions |

**Installation:**
No new dependencies required. Project already has pydantic for validation and ECharts for rendering.

## Architecture Patterns

### Recommended Project Structure
```
scripts/
├── chart_generator.py      # Existing - single chart generation
├── dashboard_generator.py  # NEW - multi-chart dashboard generation
├── dashboard_schema.py     # NEW - pydantic models for configuration
└── server.py               # Existing - local HTTP serving

outputs/
├── html/
│   ├── chart.html          # Single charts (existing)
│   └── dashboards/         # NEW - dashboard HTML outputs
└── configs/
    └── dashboard/          # NEW - dashboard configuration files

tests/
├── test_dashboard_generator.py  # NEW
└── test_dashboard_schema.py     # NEW
```

### Pattern 1: CSS Grid Layout for Dashboard

**What:** Use CSS Grid Layout to position multiple chart containers in a flexible grid.

**When to use:** All multi-chart dashboards requiring flexible positioning.

**Example:**
```html
<!-- Source: CSS Grid standard pattern -->
<!DOCTYPE html>
<html>
<head>
    <style>
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);  /* 2 equal columns */
            grid-template-rows: auto;               /* Rows sized by content */
            gap: 16px;
            padding: 16px;
        }
        .chart-container {
            min-height: 400px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        /* Explicit positioning for specific charts */
        .chart-wide {
            grid-column: span 2;  /* Spans 2 columns */
        }
        .chart-tall {
            grid-row: span 2;     /* Spans 2 rows */
        }
    </style>
</head>
<body>
    <div class="dashboard-grid">
        <div id="chart1" class="chart-container chart-wide"></div>
        <div id="chart2" class="chart-container"></div>
        <div id="chart3" class="chart-container"></div>
    </div>
</body>
</html>
```

### Pattern 2: ECharts Multi-Instance Initialization

**What:** Initialize separate ECharts instances for each chart container.

**When to use:** All dashboards with multiple independent charts.

**Example:**
```javascript
// Source: ECharts standard multi-instance pattern
// Each chart gets its own DOM element and option object
var charts = [];

// Chart 1 - Bar chart
charts.push(echarts.init(document.getElementById('chart1')));
charts[0].setOption({
    title: { text: 'Sales by Category' },
    xAxis: { type: 'category', data: ['A', 'B', 'C'] },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: [10, 20, 30] }]
});

// Chart 2 - Pie chart
charts.push(echarts.init(document.getElementById('chart2')));
charts[1].setOption({
    title: { text: 'Distribution' },
    series: [{ type: 'pie', data: [{value: 10, name: 'A'}, {value: 20, name: 'B'}] }]
});

// Resize all charts on window resize
window.addEventListener('resize', function() {
    charts.forEach(chart => chart.resize());
});
```

### Pattern 3: Dashboard Configuration Schema

**What:** Use pydantic models to define and validate dashboard configuration.

**When to use:** All dashboard configuration files.

**Example:**
```python
# Source: pydantic v2 standard patterns
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class ChartPosition(BaseModel):
    """Position of a chart in the grid."""
    row: int = Field(ge=0, description="Row position (0-indexed)")
    col: int = Field(ge=0, description="Column position (0-indexed)")
    row_span: int = Field(default=1, ge=1, description="Number of rows to span")
    col_span: int = Field(default=1, ge=1, description="Number of columns to span")

class ChartConfig(BaseModel):
    """Configuration for a single chart in the dashboard."""
    id: str = Field(..., description="Unique chart identifier")
    position: ChartPosition
    title: str = Field(default="", description="Chart title")
    query: str = Field(..., description="SQL query for chart data")
    echarts_option: dict = Field(default_factory=dict, description="ECharts option object")
    custom_js: str = Field(default="", description="Custom JavaScript code")

class DashboardConfig(BaseModel):
    """Complete dashboard configuration."""
    title: str = Field(default="Dashboard", description="Dashboard title")
    columns: int = Field(default=2, ge=1, le=12, description="Number of grid columns")
    row_height: int = Field(default=400, ge=100, description="Height of each row in pixels")
    gap: int = Field(default=16, ge=0, description="Gap between charts in pixels")
    charts: list[ChartConfig] = Field(..., min_length=1, description="List of chart configurations")
    db_path: str = Field(default="workspace.db", description="Database path")

    @field_validator('charts')
    @classmethod
    def validate_no_overlapping_positions(cls, v: list[ChartConfig]) -> list[ChartConfig]:
        """Ensure chart positions do not overlap."""
        occupied = set()
        for chart in v:
            for row in range(chart.position.row, chart.position.row + chart.position.row_span):
                for col in range(chart.position.col, chart.position.col + chart.position.col_span):
                    cell = (row, col)
                    if cell in occupied:
                        raise ValueError(f"Chart {chart.id} overlaps with another chart at position {cell}")
                    occupied.add(cell)
        return v
```

### Anti-Patterns to Avoid
- **Single ECharts instance with multiple grids:** ECharts supports multiple grids in one instance, but this complicates interactions and resizing. Use separate instances per chart.
- **Inline styles for each chart:** Hard to maintain. Use CSS classes with grid properties.
- **Fixed pixel widths:** Breaks responsive design. Use `1fr` units for flexible columns.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Configuration validation | Custom validation functions | pydantic BaseModel | Automatic schema generation, type coercion, clear error messages |
| JSON schema generation | Manual schema definition | `model.model_json_schema()` | Derived from code, stays in sync |
| Grid positioning | Custom JavaScript positioning | CSS Grid Layout | Native browser support, declarative, responsive |
| Chart resizing | Manual resize logic | `window.addEventListener('resize')` with chart.resize() | Standard ECharts pattern |

**Key insight:** Dashboard layout is primarily a CSS concern, not a JavaScript/ECharts concern. Keep layout logic in CSS and ECharts logic in JavaScript.

## Common Pitfalls

### Pitfall 1: Chart Not Rendering Due to Hidden Container

**What goes wrong:** Charts don't render because the container has zero height when `echarts.init()` is called.

**Why it happens:** ECharts requires the container to have explicit dimensions at initialization time.

**How to avoid:**
- Set explicit `min-height` on all chart containers
- Use CSS Grid with `grid-template-rows` that specifies minimum heights
- Call `chart.resize()` if containers are revealed after initialization

**Warning signs:** Empty dashboard cells, console errors about container size

### Pitfall 2: Missing Map Scripts in Dashboard

**What goes wrong:** Map charts in dashboards fail because china.js/world.js are not loaded.

**Why it happens:** The dashboard generator must scan all chart options for map usage, not just one chart.

**How to avoid:**
- Aggregate all required map scripts before generating HTML
- Check each chart's `echarts_option` and `custom_js` for map references
- Use the existing pattern from `chart_generator.py` but iterate over all charts

**Warning signs:** "Map china is not defined" console errors

### Pitfall 3: Overlapping Chart Positions

**What goes wrong:** Charts overlap or cover each other unexpectedly.

**Why it happens:** Grid positions are specified incorrectly or row/column spans exceed grid dimensions.

**How to avoid:**
- Validate positions in pydantic model (see Pattern 3 above)
- Check that `col + col_span <= total_columns`
- Warn if charts extend beyond defined rows

**Warning signs:** Charts rendering on top of each other

### Pitfall 4: Memory Issues with Many Charts

**What goes wrong:** Dashboard with 10+ charts causes browser slowdown.

**Why it happens:** Each ECharts instance consumes memory for canvas, data, and event handlers.

**How to avoid:**
- Document recommended maximum of 8-12 charts per dashboard
- Use `chart.clear()` and `chart.dispose()` if dynamically removing charts
- Consider lazy loading for very large dashboards

**Warning signs:** Slow rendering, browser tab using excessive memory

## Code Examples

Verified patterns from existing codebase:

### Generating ECharts HTML (from chart_generator.py)
```python
# Source: /scripts/chart_generator.py lines 279-383
def generate_echarts_html(df, config, output_path):
    """Generate an interactive HTML file using ECharts configuration directly."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    baidu_ak = get_baidu_ak()
    bmap_script = ""

    title = config.get("title", "Chart")
    custom_js = config.get("custom_js", "")
    option = config.get("echarts_option", {})

    # Automatic Dataset Injection
    if not option.get('dataset') and not df.empty:
        dataset_source = [df.columns.tolist()] + df.values.tolist()
        option['dataset'] = {'source': dataset_source}

    raw_data_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False)
    dataset_source_json = json.dumps([df.columns.tolist()] + df.values.tolist(), ensure_ascii=False)
    custom_js = f"var rawData = {raw_data_json};\nvar datasetSource = {dataset_source_json};\n" + custom_js

    base_url = ensure_server_running()

    # Map script detection pattern
    if ("bmap" in json.dumps(option) or "bmap" in custom_js) and baidu_ak:
        bmap_script = f"""
        <script type="text/javascript" src="https://api.map.baidu.com/api?v=3.0&ak={baidu_ak}"></script>
        <script src="{base_url}/assets/echarts/bmap.min.js"></script>
        """
    # ... additional map script detection for china, world, provinces
```

### Database Query Pattern (from chart_generator.py)
```python
# Source: /scripts/chart_generator.py lines 407-417
def generate_chart(config):
    db_path = config.get("db_path", "workspace.db")
    query = config.get("query")

    if not query:
        raise ValueError("Missing SQL query in config")

    # Use DatabaseRepository for connection pooling and WAL mode
    repo = get_repository(db_path)
    with repo.connection() as conn:
        df = pd.read_sql_query(query, conn)

    if df.empty:
        logger.warning("查询返回空数据", query=query)
        return None
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Table-based layouts | CSS Grid Layout | 2017+ | Responsive, flexible, no frameworks needed |
| Manual schema JSON | pydantic BaseModel | v2 (2023) | Schema derived from Python code, type-safe |
| Single chart per page | Multi-instance ECharts | ECharts 3.0+ | Dashboards are standard use case |

**Deprecated/outdated:**
- Float-based layouts: Use CSS Grid instead
- Fixed pixel layouts: Use `fr` units and minmax() for responsive design
- jQuery-dependent layouts: Modern CSS handles layout natively

## Open Questions

1. **Should dashboards support linked interactions (filter coordination)?**
   - What we know: Listed as ADV-04 in requirements, deferred to v2
   - What's unclear: Whether v1 should include hooks for future linked interactions
   - Recommendation: Keep v1 simple (no linked interactions), but use consistent data structures that could support linking in future

2. **What is the maximum recommended number of charts per dashboard?**
   - What we know: Each ECharts instance consumes memory
   - What's unclear: Exact performance threshold
   - Recommendation: Document 8-12 charts as recommended maximum, test with 15+ to establish hard limit

3. **Should dashboard configuration support responsive breakpoints?**
   - What we know: CSS Grid supports responsive design natively
   - What's unclear: Whether configuration should specify different layouts for different screen sizes
   - Recommendation: Use CSS Grid's auto-fit/auto-fill for basic responsiveness; defer explicit breakpoint configuration to v2

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | pyproject.toml (existing) |
| Quick run command | `pytest tests/test_dashboard_generator.py tests/test_dashboard_schema.py -x -v` |
| Full suite command | `pytest --cov=scripts --cov-report=term-missing` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DASH-01 | Grid layout generates correct CSS | unit | `pytest tests/test_dashboard_generator.py::TestGridLayout -x` | Wave 0 |
| DASH-01 | Charts positioned correctly in grid | unit | `pytest tests/test_dashboard_generator.py::TestChartPositioning -x` | Wave 0 |
| DASH-02 | Valid configuration passes validation | unit | `pytest tests/test_dashboard_schema.py::TestValidConfig -x` | Wave 0 |
| DASH-02 | Invalid positions caught by validator | unit | `pytest tests/test_dashboard_schema.py::TestInvalidPositions -x` | Wave 0 |
| DASH-02 | JSON schema generated correctly | unit | `pytest tests/test_dashboard_schema.py::TestSchemaGeneration -x` | Wave 0 |
| DASH-03 | Single HTML contains all charts | unit | `pytest tests/test_dashboard_generator.py::TestHTMLGeneration -x` | Wave 0 |
| DASH-03 | HTML opens in browser | integration | `pytest tests/test_dashboard_generator.py::TestHTMLRendering -x` | Wave 0 |
| DASH-04 | Generator script runs from CLI | integration | `pytest tests/test_dashboard_generator.py::TestCLI -x` | Wave 0 |
| DASH-04 | Generator produces valid output | integration | `pytest tests/test_dashboard_generator.py::TestEndToEnd -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_dashboard_generator.py tests/test_dashboard_schema.py -x -v`
- **Per wave merge:** `pytest --cov=scripts --cov-report=term-missing`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_dashboard_generator.py` - unit and integration tests for dashboard generation
- [ ] `tests/test_dashboard_schema.py` - pydantic model validation tests
- [ ] No framework install needed - pytest already configured

## Sources

### Primary (HIGH confidence)
- Existing codebase: `/scripts/chart_generator.py` - chart generation patterns, database access, map script detection
- Existing codebase: `/database.py` - DatabaseRepository with connection pooling
- Existing codebase: `/validators.py` - validation patterns already established
- Existing codebase: `/tests/conftest.py` - test fixtures for database and output paths

### Secondary (MEDIUM confidence)
- CSS Grid Layout: Standard CSS3 specification, widely documented and supported
- pydantic v2: Official documentation for BaseModel, field_validator, JSON schema generation
- ECharts multi-instance: Standard pattern documented in ECharts handbook

### Tertiary (LOW confidence)
- Performance thresholds for number of charts: Based on general ECharts knowledge, not project-specific testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing patterns (CSS Grid, pydantic, ECharts) with no new dependencies
- Architecture: HIGH - Building on established `chart_generator.py` patterns
- Pitfalls: MEDIUM - Based on common ECharts issues and existing codebase analysis

**Research date:** 2026-04-04
**Valid until:** 30 days (stable technologies with no expected breaking changes)
