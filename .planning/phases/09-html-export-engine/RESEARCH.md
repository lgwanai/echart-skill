# RESEARCH.md: Phase 9 HTML Export Engine

**Researched:** 2026-04-11
**Status:** Complete

## Current Architecture Analysis

### HTML Generation Pattern

All generators use the same pattern:
1. `generate_echarts_html(df, config, output_path)` in `chart_generator.py`
2. Dashboard uses `generate_dashboard_html()` which embeds data as JSON
3. Gantt chart calls `generate_echarts_html()` internally

### Current Dependencies

**Current HTML depends on local HTTP server:**
- `ensure_server_running()` returns `http://localhost:8100-8200`
- Scripts loaded from `{base_url}/assets/echarts/`
- This means HTML files require the server to be running

### Data Embedding (Already Implemented!)

```python
# In chart_generator.py
raw_data_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False)
dataset_source_json = json.dumps([df.columns.tolist()] + df.values.tolist(), ensure_ascii=False)
custom_js = f"var rawData = {raw_data_json};\nvar datasetSource = {dataset_source_json};\n" + custom_js
```

Data is already embedded! Only the ECharts library needs to be made standalone.

## Asset Sizes

| File | Size | Notes |
|------|------|-------|
| echarts.min.js | 1.1MB | Core library - must include |
| china.js | 64KB | China map - optional |
| world.js | ~500KB | World map - optional |
| Province maps | 32-80KB each | Optional per province |

## Standalone Export Strategy

### Option Selected: Inline Scripts

**Rationale:** Single HTML file that works anywhere, no external dependencies.

**Implementation:**
1. Read ECharts library file content
2. Embed as inline `<script>` tag in HTML
3. Conditionally embed map scripts (china.js, world.js, provinces)
4. Remove dependency on `ensure_server_running()`

### File Size Estimate

- Base HTML with ECharts: ~1.2MB
- With China map: ~1.3MB
- With world map: ~1.7MB

Acceptable for offline sharing use case.

## Key Functions to Modify

### New Module: `scripts/html_exporter.py`

```python
class HTMLExporter:
    """Export charts/dashboards as standalone HTML with embedded scripts."""
    
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self._echarts_content = None
        self._map_cache = {}
    
    def export_chart(self, config: dict, output_path: str, theme: str = "default") -> str:
        """Export chart as standalone HTML."""
        pass
    
    def export_dashboard(self, config_path: str, output_path: str, theme: str = "default") -> str:
        """Export dashboard as standalone HTML."""
        pass
    
    def export_gantt(self, config: dict, output_path: str, theme: str = "default") -> str:
        """Export Gantt chart as standalone HTML."""
        pass
```

### Template Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body { margin: 0; padding: 0; }
        #main { width: 100%; height: 100vh; }
    </style>
</head>
<body>
    <div id="main"></div>
    <script>
    // Inline ECharts library (1.1MB)
    {echarts_content}
    </script>
    <script>
    // Inline map scripts (if needed)
    {map_scripts}
    </script>
    <script>
    // Chart initialization
    var myChart = echarts.init(document.getElementById('main'));
    var option = {option_json};
    var rawData = {data_json};  // Already embedded!
    {custom_js}
    myChart.setOption(option);
    </script>
</body>
</html>
```

## Technical Considerations

### Chinese Character Support
- Use `ensure_ascii=False` in `json.dumps()` ✓ (already implemented)

### Theme Support
- ECharts supports themes via `echarts.registerTheme()`
- Can embed theme JS alongside echarts.min.js
- Default theme is built-in

### Data Size Warning
- Log embedded data size for user awareness
- Consider warning threshold (e.g., >10MB embedded data)

## Dependencies

No new Python dependencies needed.

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `scripts/html_exporter.py` | Create | New exporter module |
| `scripts/chart_generator.py` | Modify | Add export flag |
| `scripts/dashboard_generator.py` | Modify | Add export flag |
| `scripts/gantt_chart.py` | Modify | Add export flag |

---
*Research completed: 2026-04-11*
