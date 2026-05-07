# Phase 10: Export CLI & UX - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

CLI commands for export operations with user-friendly defaults. Provides command-line interface for the export functions created in Phase 9. Does not include new export functionality—only CLI wrapper and UX improvements.

**明确范围：**
- CLI commands for chart, dashboard, and Gantt export
- Command-line argument parsing
- Output path handling
- Theme selection
- Error messages and feedback

**排除范围：**
- New export functionality (Phase 9)
- GUI or interactive mode
- Export scheduling

</domain>

<decisions>
## Implementation Decisions

### Command Structure

**命令组织：**
- Multiple separate commands (not unified)
- Each export type has its own command
- Clear and explicit naming

**命令命名约定：**
- `export-chart` - Export single chart as standalone HTML
- `export-dashboard` - Export dashboard as standalone HTML
- `export-gantt` - Export Gantt chart as standalone HTML

**参数设计：**
- Positional arguments for required parameters
- Flags for optional parameters
- Mix of explicit values and config file support

**共同参数：**
- `--output` - Output file path (required)
- `--theme` - ECharts theme (default, dark)
- `--config` - Configuration file path (alternative to inline parameters)

### Claude's Discretion

- Exact argparse implementation
- Error message wording
- Help text formatting
- Exit codes for different failure modes

</decisions>

<specifics>
## Specific Ideas

- "Positional arguments + flags" — User wants explicit required parameters with optional flags
- Commands should feel like standard CLI tools (git, docker, etc.)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 10-export-cli-ux*
*Context gathered: 2026-04-11*
