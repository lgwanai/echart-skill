# Technology Stack

**Analysis Date:** 2026-04-04

## Languages

**Primary:**
- Python 3.13+ - All backend data processing, chart generation, and server logic

**Secondary:**
- JavaScript - ECharts visualization library (bundled assets)
- HTML - Generated chart output files
- Markdown - Documentation and skill definitions

## Runtime

**Environment:**
- Python 3.13.3 (standard CPython interpreter)
- No virtual environment configuration detected

**Package Manager:**
- pip (standard Python package manager)
- Lockfile: Not present (requirements.txt only)

## Frameworks

**Core:**
- ECharts 6.0 (Apache ECharts) - Interactive charting library
  - Location: `assets/echarts/echarts.min.js`
  - Size: ~1MB minified
  - Supports 100% of ECharts 6.0 chart types

**Data Processing:**
- pandas - Data manipulation and analysis
- openpyxl - Excel file reading/writing
- matplotlib/seaborn - Static chart generation (optional/fallback)

**Text Processing:**
- thefuzz - Fuzzy string matching for semantic joins

**Optional:**
- numbers-parser - Mac Numbers file support (`.numbers` files)

## Key Dependencies

**Critical (from requirements.txt):**
- `pandas` - Core data frame operations, SQL integration
- `openpyxl` - Excel file parsing, merged cell handling
- `matplotlib` - Static visualization fallback
- `seaborn` - Statistical visualization
- `thefuzz` - Fuzzy matching for data joins

**Infrastructure:**
- `sqlite3` - Built-in Python module for local database
- `http.server` / `socketserver` - Built-in HTTP server for chart serving
- `hashlib` - MD5 hashing for duplicate file detection
- `urllib` - Baidu Map API geocoding requests

## Configuration

**Environment:**
- Config file: `config.txt` (user-specific, gitignored)
- Example config: `config.example.txt`
- Required variable: `BAIDU_AK` - Baidu Maps API Key for geocoding

**Build:**
- No build system (pure Python + static assets)
- Packaging: `package.sh` - Bash script creating distributable ZIP

**Database:**
- SQLite database: `workspace.db` (default, created at runtime)
- Metadata table: `_data_skill_meta` - Tracks file imports and usage

## Platform Requirements

**Development:**
- Python 3.13+
- pip package manager
- Bash shell (for packaging)

**Production:**
- Same as development (local execution model)
- No server deployment required
- Optional: Baidu Maps AK for geocoding features

**Supported File Formats:**
- Import: `.csv`, `.xlsx`, `.xls`, `.et` (WPS), `.numbers` (Mac)
- Export: `.csv`, `.xlsx`
- Output: `.html` (interactive charts)

## Asset Structure

**ECharts Library:**
- `assets/echarts/echarts.min.js` - Core library
- `assets/echarts/bmap.min.js` - Baidu Map extension
- `assets/echarts/china.js` - China map geoJSON
- `assets/echarts/world.js` - World map geoJSON
- `assets/echarts/{province}.js` - 34 Chinese provinces/regions

**Chart Templates:**
- `references/prompts/` - 40+ chart type prompt templates
- `references/support_original.md` - ECharts examples reference
- `references/metrics.md` - User-defined business metrics

---

*Stack analysis: 2026-04-04*
