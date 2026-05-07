# Phase 10 Research: Export CLI & UX

**Phase:** 10-export-cli-ux
**Researched:** 2026-04-12
**Researcher Model:** sonnet

---

## Executive Summary

Phase 10 builds CLI commands wrapping the export functionality from Phase 9. This is a thin wrapper layer focused on user experience and CLI ergonomics, not new export capabilities.

---

## Phase 9 Context (Prerequisites)

Phase 9 created three export functions in `scripts/chart_exporter.py`:

### Available Export Functions

1. **`export_chart_html()`**
   - Exports single chart as standalone HTML
   - Parameters: `config_path`, `output_path`, `theme`
   - Returns: path to generated HTML file

2. **`export_dashboard_html()`**
   - Exports dashboard as standalone HTML
   - Parameters: `config_path`, `output_path`, `theme`
   - Returns: path to generated HTML file

3. **`export_gantt_html()`**
   - Exports Gantt chart as standalone HTML
   - Parameters: `tasks`, `output_path`, `title`, `theme`
   - Returns: path to generated HTML file

### Key Implementation Details

- All exports embed data as JSON in HTML
- ECharts library loaded from CDN (echarts.min.js)
- Chinese characters preserved (ensure_ascii=False)
- Data size logged for awareness

---

## CLI Design Patterns (Python)

### 1. argparse Best Practices

**Standard structure:**
```python
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Export charts as standalone HTML files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Positional arguments (required)
    parser.add_argument('config', help='Path to chart config JSON')
    
    # Optional arguments with flags
    parser.add_argument('--output', '-o', help='Output HTML file path')
    parser.add_argument('--theme', choices=['default', 'dark'], default='default')
    parser.add_argument('--config-file', help='YAML config file path')
    
    args = parser.parse_args()
```

**Key patterns:**
- Subcommands for multiple operations (like git): `chart export-chart`, `chart export-dashboard`
- Mutually exclusive groups for parameters vs config file
- Exit codes: 0 (success), 1 (error), 2 (usage error)
- Clear error messages with actionable guidance

### 2. Error Handling

**User-friendly errors:**
```python
try:
    result = export_chart_html(...)
except FileNotFoundError:
    print(f"Error: Config file not found: {args.config}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

### 3. Filename Generation (UX-03)

**Default naming pattern:**
```python
from datetime import datetime
import re

def generate_filename(title, chart_type):
    """Generate filename from title and timestamp."""
    # Sanitize title
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    
    # Add timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{safe_title}_{timestamp}.html"

# Example: "销售数据概览" → "销售数据概览_20260412_143022.html"
```

---

## Local ECharts Embedding (UX-02)

### Current Implementation (Phase 9)

```html
<!-- CDN approach -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
```

### Local Embedding Strategy

**Option A: Inline Script (Recommended for small files)**
```python
def embed_echarts_local(html_content):
    """Embed ECharts library inline in HTML."""
    echarts_path = "references/echarts.min.js"  # ~1MB minified
    
    with open(echarts_path, 'r', encoding='utf-8') as f:
        echarts_code = f.read()
    
    # Replace CDN link with inline script
    html_content = html_content.replace(
        '<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>',
        f'<script>\n{echarts_code}\n</script>'
    )
    
    return html_content
```

**Pros:** Truly offline, single file
**Cons:** Increases file size by ~1MB

**Option B: Relative Path (For local deployments)**
```html
<script src="./lib/echarts.min.js"></script>
```

**Pros:** Smaller HTML files
**Cons:** Requires shipping lib folder

**Recommendation:** Option A for Phase 10 (aligns with "standalone HTML" requirement from Phase 9).

---

## CLI Command Structure

Based on user decisions from CONTEXT.md:

### Proposed Commands

**1. export-chart**
```bash
chart export-chart <config_path> [--output PATH] [--theme THEME]
```
- Exports single chart from config JSON
- Default output: `{chart_title}_{timestamp}.html`
- Theme: default | dark

**2. export-dashboard**
```bash
chart export-dashboard <config_path> [--output PATH] [--theme THEME]
```
- Exports dashboard from config JSON
- Default output: `{dashboard_title}_{timestamp}.html`

**3. export-gantt**
```bash
chart export-gantt <tasks_json> [--output PATH] [--title TITLE] [--theme THEME]
```
- Exports Gantt chart from tasks JSON
- Tasks JSON: Array of {name, start, end, category?}
- Default output: `{title}_{timestamp}.html`

### Common Parameters

- `--output`, `-o`: Output file path (overrides default naming)
- `--theme`: ECharts theme (default | dark)
- `--config-file`: Alternative to inline parameters (YAML/JSON)
- `--help`, `-h`: Show help

---

## SKILL.md Documentation Update

Phase 10 should update SKILL.md to document:

1. **New CLI Commands Section**
   - Command syntax and examples
   - Parameter descriptions
   - Common use cases

2. **Export Workflow**
   - How to use CLI for exports
   - Integration with existing chart generation

3. **Offline Usage**
   - Local ECharts embedding
   - Benefits of standalone HTML

**Location:** Update existing SKILL.md (no separate doc needed)

---

## Testing Strategy

### Unit Tests

1. **CLI Argument Parsing**
   - Test all parameter combinations
   - Test error handling for invalid inputs

2. **Filename Generation**
   - Test title sanitization
   - Test timestamp format
   - Test Chinese character handling

3. **Local Embedding**
   - Verify ECharts library is embedded
   - Verify HTML works offline

### Integration Tests

1. **End-to-End CLI**
   - Export chart from config
   - Export dashboard from config
   - Export Gantt from tasks JSON

2. **Error Scenarios**
   - Missing config file
   - Invalid JSON
   - Permission denied on output path

---

## Key Decisions for Planning

### Confirmed (from CONTEXT.md)

✅ Multiple separate commands (not unified)
✅ Commands: `export-chart`, `export-dashboard`, `export-gantt`
✅ Positional args for required, flags for optional
✅ Common params: `--output`, `--theme`, `--config`

### For Planner to Decide

1. **Entry Point:** Single `chart` command with subcommands vs three separate scripts
   - Recommendation: Single `chart` command (cleaner UX)

2. **Exit Codes:** Specific codes for different errors
   - Recommendation: 0 (success), 1 (error), 2 (usage)

3. **Help Text:** Level of detail in command help
   - Recommendation: Include examples in help text

4. **Local ECharts Location:** Where to store echarts.min.js
   - Recommendation: `references/echarts.min.js` (already in project)

---

## Dependencies

### Python Libraries (Already Available)

- `argparse` (stdlib) - CLI argument parsing
- `json` (stdlib) - JSON handling
- `pathlib` (stdlib) - Path operations
- `datetime` (stdlib) - Timestamp generation
- `re` (stdlib) - String sanitization

### Project Files

- `scripts/chart_exporter.py` - Export functions (Phase 9)
- `references/echarts.min.js` - Local ECharts library
- `references/prompts/` - Chart templates

---

## Common Pitfalls

1. **Over-engineering CLI** - Keep simple, focus on wrapping existing functions
2. **Complex error hierarchies** - User wants actionable errors, not stack traces
3. **Ignoring Chinese paths** - Test with non-ASCII characters
4. **Forgetting --help** - Good help text reduces support burden
5. **Hardcoding paths** - Use pathlib for cross-platform compatibility

---

## Implementation Approach

### Plan 01: CLI Export Commands

**Scope:**
- Create `scripts/chart_cli.py` with argparse
- Implement three subcommands: export-chart, export-dashboard, export-gantt
- Add filename generation logic
- Integrate with chart_exporter.py

**Verification:**
- Commands work from terminal
- Help text displays correctly
- Errors are user-friendly

### Plan 02: Local ECharts + Documentation

**Scope:**
- Implement local ECharts embedding in chart_exporter.py
- Update SKILL.md with CLI usage docs
- Add CLI examples to SKILL.md

**Verification:**
- Exported HTML works offline
- SKILL.md accurately documents commands
- Examples are copy-pasteable

---

## Questions for Planner

None - requirements and user decisions are clear.

---

## Success Criteria

Phase 10 succeeds when:

1. ✅ User can run `chart export-chart config.json` and get HTML
2. ✅ User can specify custom output path with `--output`
3. ✅ Default filenames use title + timestamp
4. ✅ Exported HTML works without internet
5. ✅ Help text guides users effectively
6. ✅ SKILL.md documents the new commands

---

**Research Complete**
Ready for planning.
