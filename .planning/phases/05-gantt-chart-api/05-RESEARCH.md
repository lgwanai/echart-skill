# Phase 5: Gantt Chart API - Research

**Researched:** 2026-04-04
**Domain:** ECharts custom series for Gantt chart visualization
**Confidence:** HIGH

## Summary

This phase requires implementing a simplified Gantt chart API wrapper over ECharts. ECharts does not have a native "gantt" chart type; instead, Gantt charts are implemented using the `custom` series type with a `renderItem` function. The existing codebase already has a powerful template-based chart generation system (`scripts/chart_generator.py`) that can be extended with a Gantt-specific wrapper.

**Primary recommendation:** Create a `scripts/gantt_chart.py` module with a simplified API that accepts a task array (name, start, end) and generates the required ECharts custom series configuration internally. Add a corresponding prompt template to `references/prompts/gantt/` following existing patterns.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CHART-01 | Gantt chart simplified API wrapper over existing template | ECharts custom series with renderItem function; simplified API design documented below |
| CHART-02 | Gantt chart documentation and examples added to SKILL.md | Follow existing SKILL.md patterns; add new Scenario 9 for Gantt charts |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ECharts | 6.0 | Chart rendering | Already in use, supports custom series |
| pydantic | 2.x | Input validation | Already used in dashboard_schema.py for similar patterns |
| Python | 3.x | Core language | Existing codebase |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| datetime | stdlib | Date/time parsing | User input date strings |
| json | stdlib | Configuration serialization | Chart config generation |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ECharts custom series | External Gantt library (dhtmlxGantt) | External libraries break offline-first promise; ECharts custom is more flexible |
| renderItem from scratch | Copy from support_original.md | Existing airport Gantt example is complex; simplify for basic use case |

**Installation:**
No new dependencies required. All functionality uses existing ECharts 6.0 custom series.

## Architecture Patterns

### Recommended Project Structure
```
scripts/
├── gantt_chart.py        # New: Simplified Gantt API wrapper
├── chart_generator.py    # Existing: Core chart generation
└── dashboard_generator.py # Existing: Dashboard composition

references/prompts/
├── gantt/                # New: Gantt chart templates
│   ├── basic_gantt.md    # Simple task timeline
│   └── index.md          # Gantt prompt index
└── ... (existing prompt directories)

tests/
├── test_gantt_chart.py   # New: Gantt API tests
└── conftest.py           # Existing: Shared fixtures
```

### Pattern 1: Simplified Gantt API Design

**What:** A `generate_gantt_chart()` function that accepts simple task data and internally generates the complex ECharts custom series configuration.

**When to use:** When users need Gantt charts without learning ECharts configuration details.

**Input Schema (pydantic):**
```python
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class GanttTask(BaseModel):
    """Single task in a Gantt chart."""
    name: str
    start: datetime | str  # Accept datetime or ISO string
    end: datetime | str
    category: Optional[str] = None  # For grouping/row assignment
    color: Optional[str] = None     # Custom bar color

    @field_validator('start', 'end', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v

    @field_validator('end')
    @classmethod
    def end_after_start(cls, v, info):
        if 'start' in info.data and v <= info.data['start']:
            raise ValueError("End time must be after start time")
        return v

class GanttChartConfig(BaseModel):
    """Gantt chart configuration."""
    title: str = "Gantt Chart"
    tasks: list[GanttTask]
    output_path: Optional[str] = None
    db_path: str = "workspace.db"  # For consistency with other generators
```

**Example usage:**
```python
from scripts.gantt_chart import generate_gantt_chart

# Simple task array input
config = {
    "title": "Project Timeline",
    "tasks": [
        {"name": "Design", "start": "2024-01-01", "end": "2024-01-15"},
        {"name": "Development", "start": "2024-01-10", "end": "2024-02-01"},
        {"name": "Testing", "start": "2024-01-25", "end": "2024-02-10"}
    ]
}
generate_gantt_chart(config)
```

### Pattern 2: ECharts Custom Series for Gantt

**What:** ECharts Gantt charts use `type: 'custom'` with a `renderItem` function that draws horizontal bars.

**Key configuration elements:**
```javascript
option = {
    xAxis: {
        type: 'time',  // Time axis for dates
        position: 'top'
    },
    yAxis: {
        type: 'category',  // Task names on Y-axis
        data: ['Task 1', 'Task 2', 'Task 3']
    },
    series: [{
        type: 'custom',
        renderItem: function(params, api) {
            var categoryIndex = api.value(0);  // Y-axis index
            var start = api.coord([api.value(1), categoryIndex]);
            var end = api.coord([api.value(2), categoryIndex]);
            var height = 20;

            return {
                type: 'rect',
                shape: {
                    x: start[0],
                    y: start[1] - height / 2,
                    width: end[0] - start[0],
                    height: height
                },
                style: api.style()
            };
        },
        encode: {
            x: [1, 2],  // Start and end times
            y: 0        // Category index
        },
        data: [
            [0, '2024-01-01', '2024-01-15', 'Design'],
            [1, '2024-01-10', '2024-02-01', 'Development']
        ]
    }]
};
```

Source: ECharts official example (Gantt Chart of Airport Flights) from `references/support_original.md`

### Pattern 3: Prompt Template Structure

**What:** Follow existing prompt template structure for consistency.

**Example** (`references/prompts/gantt/basic_gantt.md`):
```markdown
## 图表类型：基础甘特图 (Basic Gantt Chart)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### 数据结构要求
用户数据应包含以下字段：
- name: 任务名称
- start: 开始时间 (datetime 或 ISO 字符串)
- end: 结束时间 (datetime 或 ISO 字符串)
- category: 可选，任务分类/行

### ECharts Option 骨架参考
请基于此结构生成配置：

```javascript
option = {
    xAxis: {
        type: 'time',
        position: 'top'
    },
    yAxis: {
        type: 'category',
        data: [ /* 任务名称数组 */ ]
    },
    series: [{
        type: 'custom',
        renderItem: renderGanttItem,
        encode: {
            x: [1, 2],
            y: 0
        },
        data: [ /* [categoryIndex, startTime, endTime, taskName] */ ]
    }]
};

function renderGanttItem(params, api) {
    // renderItem implementation
}
```
```

### Anti-Patterns to Avoid

- **Don't use bar series for Gantt:** Bar series cannot handle time ranges on X-axis properly. Use `custom` series with `renderItem`.
- **Don't put pie on maps:** SKILL.md already documents this - pie series does not support `coordinateSystem: 'geo'`.
- **Don't create complex renderItem from scratch:** Start with simplified version from existing examples; complexity (drag, zoom) can be added later.
- **Don't use external CDN scripts:** All JS dependencies must use local paths injected by Python generator (per SKILL.md rules).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Date parsing | Custom date parser | `datetime.fromisoformat()` | Handles ISO format, edge cases |
| Input validation | Manual type checking | pydantic `BaseModel` | Used throughout project, automatic validation |
| ECharts config generation | Full option from scratch | Template + `replace_placeholders()` | Existing pattern in chart_generator.py |
| HTML output | Custom HTML template | `generate_echarts_html()` | Existing function handles all boilerplate |

**Key insight:** The heavy lifting (HTML generation, server integration, map scripts) is already done in `chart_generator.py`. The Gantt wrapper only needs to transform simple task input into ECharts custom series configuration.

## Common Pitfalls

### Pitfall 1: Time Zone Handling

**What goes wrong:** Users provide dates without timezone info, leading to inconsistent rendering or errors.

**Why it happens:** ECharts `type: 'time'` axis expects valid dates, but user input may be ambiguous.

**How to avoid:**
- Accept both datetime objects and ISO strings in API
- Default to local timezone if not specified
- Document timezone behavior in SKILL.md

**Warning signs:** "Invalid date" appearing in chart, bars rendered at wrong positions.

### Pitfall 2: Category Index Mismatch

**What goes wrong:** Tasks appear on wrong rows or overlap unexpectedly.

**Why it happens:** Y-axis categories and data array indices don't match.

**How to avoid:**
- Generate Y-axis category data from unique task names/categories
- Use consistent indexing (0-based) in both Y-axis data and series data
- Add validation for category uniqueness

**Warning signs:** Tasks showing on wrong rows, empty rows in chart.

### Pitfall 3: Overlapping Task Names

**What goes wrong:** Long task names overlap on Y-axis, becoming unreadable.

**Why it happens:** Default Y-axis doesn't handle long labels well.

**How to avoid:**
- Set appropriate `grid.left` to accommodate label width
- Consider `axisLabel.width` with overflow handling
- Document recommended max task name length

**Warning signs:** Labels cut off, overlapping text.

### Pitfall 4: Date Range Mismatch

**What goes wrong:** Chart shows wrong time range, or bars appear off-screen.

**Why it happens:** xAxis min/max not set appropriately for task dates.

**How to avoid:**
- Auto-calculate min/max from task start/end dates
- Add padding before first start and after last end
- Include dataZoom for large date ranges

**Warning signs:** Bars not visible, empty chart area.

## Code Examples

### Basic Gantt Chart Generator Function

```python
# scripts/gantt_chart.py
import json
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from pydantic import BaseModel, field_validator

from scripts.chart_generator import generate_echarts_html
from logging_config import get_logger

logger = get_logger(__name__)


class GanttTask(BaseModel):
    """Single task in a Gantt chart."""
    name: str
    start: datetime
    end: datetime
    category: Optional[str] = None
    color: Optional[str] = None

    @field_validator('start', 'end', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v

    @field_validator('end')
    @classmethod
    def end_after_start(cls, v, info):
        if 'start' in info.data and v <= info.data['start']:
            raise ValueError(f"Task '{info.data.get('name', 'unknown')}': end time must be after start time")
        return v


class GanttChartConfig(BaseModel):
    """Gantt chart configuration."""
    title: str = "Gantt Chart"
    tasks: list[GanttTask]
    output_path: Optional[str] = None


# JavaScript for renderItem function
GANTT_RENDER_ITEM_JS = """
function renderGanttItem(params, api) {
    var categoryIndex = api.value(0);
    var start = api.coord([api.value(1), categoryIndex]);
    var end = api.coord([api.value(2), categoryIndex]);
    var height = api.size([0, 1])[1] * 0.6;

    return {
        type: 'rect',
        shape: {
            x: start[0],
            y: start[1] - height / 2,
            width: end[0] - start[0],
            height: height
        },
        style: api.style({
            fill: api.value(3) || '#5470c6'
        })
    };
}
"""


def generate_gantt_chart(config: dict) -> str:
    """
    Generate a Gantt chart from simplified task configuration.

    Args:
        config: Dict with 'title', 'tasks' list, optional 'output_path'

    Returns:
        Path to generated HTML file
    """
    # Validate config
    gantt_config = GanttChartConfig(**config)

    # Extract unique categories (task names for Y-axis)
    task_names = list(dict.fromkeys(task.name for task in gantt_config.tasks))

    # Calculate date range with padding
    all_dates = []
    for task in gantt_config.tasks:
        all_dates.extend([task.start, task.end])

    min_date = min(all_dates) - timedelta(days=1)
    max_date = max(all_dates) + timedelta(days=1)

    # Build series data: [categoryIndex, startTime, endTime, color]
    series_data = []
    for task in gantt_config.tasks:
        category_index = task_names.index(task.name)
        series_data.append([
            category_index,
            task.start.isoformat(),
            task.end.isoformat(),
            task.color
        ])

    # Build ECharts option
    echarts_option = {
        "title": {
            "text": gantt_config.title,
            "left": "center"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": function_format_tooltip()  # Simplified for example
        },
        "xAxis": {
            "type": "time",
            "position": "top",
            "min": min_date.isoformat(),
            "max": max_date.isoformat()
        },
        "yAxis": {
            "type": "category",
            "data": task_names,
            "inverse": True
        },
        "series": [{
            "type": "custom",
            "renderItem": "__renderGanttItem__",  # Placeholder
            "encode": {
                "x": [1, 2],
                "y": 0
            },
            "data": series_data
        }]
    }

    # Prepare custom JS with renderItem function
    custom_js = GANTT_RENDER_ITEM_JS

    # Generate HTML using existing infrastructure
    output_path = gantt_config.output_path
    if not output_path:
        base_dir = Path(__file__).parent.parent
        output_path = base_dir / "outputs" / "html" / "gantt_chart.html"

    # Empty DataFrame since data is in echarts_option
    import pandas as pd
    df = pd.DataFrame()

    generate_echarts_html(df, {
        "title": gantt_config.title,
        "echarts_option": echarts_option,
        "custom_js": custom_js
    }, str(output_path))

    return str(output_path)
```

Source: Derived from ECharts official Gantt example in `references/support_original.md` and existing `chart_generator.py` patterns.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded chart configs | Template-based generation | Phase 1-3 | Reusable, maintainable |
| Direct ECharts option exposure | Simplified API wrappers | This phase | User-friendly, less error-prone |

**Deprecated/outdated:**
- External Gantt libraries (dhtmlxGantt, Frappe Gantt): Violates offline-first principle

## Open Questions

1. **Should Gantt support task dependencies (arrows between tasks)?**
   - What we know: ECharts can render this with `series.lines` type
   - What's unclear: User demand for this feature
   - Recommendation: Start with basic bars; dependencies can be Phase 6 enhancement

2. **Should tasks support progress percentage (partial fill)?**
   - What we know: renderItem can draw partial bars
   - What's unclear: Data structure for progress input
   - Recommendation: Defer to future enhancement; keep initial API simple

3. **Should there be a SQL-to-Gantt shortcut?**
   - What we know: Other charts use `query` + `db_path` pattern
   - What's unclear: How to map arbitrary SQL results to tasks
   - Recommendation: Accept raw task array first; SQL shortcut can be added via query transformation

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | None - fixtures in conftest.py |
| Quick run command | `pytest tests/test_gantt_chart.py -x` |
| Full suite command | `pytest tests/ --cov=scripts --cov-report=term-missing` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CHART-01 | Generate Gantt from task array | unit | `pytest tests/test_gantt_chart.py::TestGenerateGanttChart -x` | Wave 0 |
| CHART-01 | Validate task dates (end > start) | unit | `pytest tests/test_gantt_chart.py::TestGanttTaskValidation -x` | Wave 0 |
| CHART-01 | Generate correct ECharts option | unit | `pytest tests/test_gantt_chart.py::TestEChartsOptionGeneration -x` | Wave 0 |
| CHART-02 | SKILL.md updated with Gantt scenario | manual | Review SKILL.md section | N/A |

### Sampling Rate
- **Per task commit:** `pytest tests/test_gantt_chart.py -x`
- **Per wave merge:** `pytest tests/ --cov=scripts --cov-report=term-missing`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_gantt_chart.py` - new test file for Gantt functionality
- [ ] `references/prompts/gantt/basic_gantt.md` - prompt template for Gantt
- [ ] `references/prompts/gantt/index.md` - index file for Gantt prompts

## Sources

### Primary (HIGH confidence)
- `references/support_original.md` - ECharts Gantt example code (airport flights)
- `scripts/chart_generator.py` - Existing chart generation patterns
- `scripts/dashboard_schema.py` - Pydantic validation patterns

### Secondary (MEDIUM confidence)
- `SKILL.md` - Existing documentation patterns
- `tests/conftest.py` - Test fixture patterns

### Tertiary (LOW confidence)
- None required - all information available from primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All dependencies already in use
- Architecture: HIGH - Clear patterns from existing code
- Pitfalls: MEDIUM - Based on ECharts patterns, need validation with real usage

**Research date:** 2026-04-04
**Valid until:** 30 days - stable patterns
