# Codebase Structure

**Analysis Date:** 2026-04-04

## Directory Layout

```
/Users/wuliang/workspace/echart-skill/
├── scripts/                    # Core Python scripts for data operations
│   ├── data_importer.py        # File import (CSV/Excel/Numbers)
│   ├── data_exporter.py        # Data export (CSV/Excel)
│   ├── chart_generator.py      # ECharts HTML generation
│   ├── data_cleaner.py         # Old data cleanup
│   ├── metrics_manager.py      # Business metric definitions
│   ├── server.py               # Local HTTP server for charts
│   └── utils/                  # Utility scripts
│       └── generate_all_templates.py
├── references/                 # Reference materials and templates
│   ├── prompts/                # 350+ ECharts chart templates
│   │   ├── line/               # Line chart templates
│   │   ├── bar/                # Bar chart templates
│   │   ├── pie/                # Pie chart templates
│   │   ├── scatter/            # Scatter chart templates
│   │   ├── map/                # Map chart templates
│   │   ├── 3D/                 # 3D chart templates
│   │   └── ... (40+ chart types)
│   ├── metrics.md              # Business metric definitions
│   ├── support_original.md     # ECharts official examples reference
│   └── geo_cache.json          # Geocoding cache (runtime)
├── assets/                     # Static assets
│   └── echarts/                # ECharts library files
│       ├── echarts.min.js      # Core ECharts library
│       ├── china.js            # China map
│       ├── world.js            # World map
│       ├── bmap.min.js         # Baidu Map extension
│       └── [province].js       # 34 province map files
├── outputs/                    # Generated outputs (gitignored)
│   ├── html/                   # Generated chart HTML files
│   ├── configs/                # Chart configuration JSON files
│   └── scripts/                # Generated Python scripts
├── tmp/                        # Temporary files (gitignored)
├── dist/                       # Release packages (gitignored)
├── .planning/                  # Planning documents
│   └── codebase/               # Codebase analysis documents
├── README.md                   # Project documentation (Chinese)
├── SKILL.md                    # Agent skill definition
├── requirements.txt            # Python dependencies
├── config.example.txt          # Configuration template
├── config.txt                  # User configuration (gitignored)
├── package.sh                  # Release packaging script
└── workspace.db                # SQLite database (gitignored, runtime)
```

## Directory Purposes

**scripts/:**
- Purpose: Core operational scripts for the skill
- Contains: 6 main Python modules + utils subdirectory
- Key files:
  - `scripts/data_importer.py` (326 lines) - Complex file import with header detection
  - `scripts/chart_generator.py` (243 lines) - HTML generation with ECharts
  - `scripts/server.py` (119 lines) - HTTP server management

**references/prompts/:**
- Purpose: ECharts configuration templates for all chart types
- Contains: 350+ markdown files organized by chart type
- Key subdirectories:
  - `line/` - Line, area, stacked charts
  - `bar/` - Bar, column, stacked bar charts
  - `pie/` - Pie, donut, nested pie charts
  - `scatter/` - Scatter, bubble charts
  - `map/` - Geographic map charts
  - `3D/` - 3D bar, surface, scatter charts
  - `tree/`, `graph/`, `sankey/`, `funnel/` - Specialized charts

**assets/echarts/:**
- Purpose: Offline ECharts dependencies
- Contains: 40+ JavaScript files
- Key files:
  - `echarts.min.js` - Core library (offline)
  - `china.js` - China map geoJSON
  - `world.js` - World map geoJSON
  - `bmap.min.js` - Baidu Map integration
  - 34 provincial map files (e.g., `beijing.js`, `shanghai.js`)

**outputs/:**
- Purpose: Generated artifacts (gitignored)
- Contains: HTML charts, config JSONs, export files
- Structure mirrors runtime generation needs

## Key File Locations

**Entry Points:**
- `scripts/data_importer.py` - Primary data ingestion CLI
- `scripts/chart_generator.py` - Primary visualization CLI
- `scripts/data_exporter.py` - Primary export CLI

**Configuration:**
- `config.txt` - Runtime configuration (BAIDU_AK)
- `config.example.txt` - Configuration template
- `requirements.txt` - Python dependencies

**Documentation:**
- `README.md` - User-facing project documentation (Chinese)
- `SKILL.md` - Agent operational procedures (Chinese)
- `RELEASE_NOTE.md` - Version release notes

**Core Logic:**
- `scripts/data_importer.py` - File parsing, MD5 deduplication, SQLite writing
- `scripts/chart_generator.py` - SQL execution, HTML template generation
- `scripts/server.py` - HTTP server lifecycle management

**Templates:**
- `references/prompts/index.md` - Chart type index
- `references/prompts/{type}/{example}.md` - Individual chart templates

## Naming Conventions

**Files:**
- Python scripts: `snake_case.py` (e.g., `data_importer.py`)
- Markdown templates: `descriptive_name.md` (e.g., `stacked_area_chart.md`)
- JavaScript assets: `lowercase.js` (e.g., `echarts.min.js`)
- Output configs: `descriptive_name.json`

**Directories:**
- Source code: `snake_case/` (e.g., `scripts/`, `references/`)
- Chart types: `camelCase/` matching ECharts naming (e.g., `bar3D/`, `scatterGL/`)

**SQLite Tables:**
- User tables: `original_filename` (cleaned, alphanumeric + underscore)
- Metadata table: `_data_skill_meta` (underscore prefix for system tables)
- Versioned tables: `tablename_v1`, `tablename_v2` (suffix versioning)

## Where to Add New Code

**New Chart Type Support:**
- Add templates to: `references/prompts/{chart_type}/`
- Follow naming: `{description}_{chart_type}.md`
- Include: ECharts option skeleton, data structure requirements

**New Data Import Format:**
- Extend: `scripts/data_importer.py`
- Add parser function, update `import_to_sqlite()` dispatcher
- Add dependency to `requirements.txt`

**New Export Format:**
- Extend: `scripts/data_exporter.py`
- Add format detection in `export_data()` function

**New Utility Scripts:**
- Location: `scripts/utils/` or `scripts/` root
- Follow pattern: argparse CLI, main function, `if __name__ == "__main__"` guard

**Business Metric Definitions:**
- Storage: `references/metrics.md` (auto-managed via `scripts/metrics_manager.py`)
- Manual edits: Follow existing markdown structure

## Special Directories

**references/prompts/:**
- Purpose: ECharts template library
- Generated: No (manually curated)
- Committed: Yes
- Count: 350+ markdown files

**assets/echarts/:**
- Purpose: Offline ECharts dependencies
- Generated: No (downloaded from ECharts official)
- Committed: Yes
- Size: ~2MB+ of JavaScript files

**outputs/:**
- Purpose: Runtime generated artifacts
- Generated: Yes (by chart_generator.py, data_exporter.py)
- Committed: No (in .gitignore)
- Cleanup: Managed by user or `scripts/data_cleaner.py`

**tmp/:**
- Purpose: Temporary development files
- Generated: Yes (development utilities)
- Committed: No (in .gitignore)

**dist/:**
- Purpose: Release packages
- Generated: Yes (by `package.sh`)
- Committed: No (in .gitignore)
- Contents: `echart-skill_YYYYMMDD_HHMMSS.zip`

---

*Structure analysis: 2026-04-04*
