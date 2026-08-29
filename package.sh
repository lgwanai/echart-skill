#!/bin/bash
# =============================================================================
# echart-skill Release Packager
# =============================================================================
set -euo pipefail

DATE=$(date +"%Y%m%d")
PACKAGE_NAME="${PACKAGE_NAME:-echart-skill_${DATE}.zip}"
DIST_DIR="${DIST_DIR:-dist}"
mkdir -p "$DIST_DIR"

echo "📦 Packaging Echart Skill …"

INCLUDES=(
    "SKILL.md"
    "README.md"
    "README_EN.md"
    "pyproject.toml"
    "requirements-core.txt"
    "requirements-optional.txt"
    "requirements.txt"
    "database.py"
    "logging_config.py"
    "validators.py"
    "assets"
    "commands"
    "references"
    "scripts"
    "workflow_specs"
)

EXCLUDES=(
    "*/.DS_Store" "*.pyc" "*.pyo" "*/__pycache__/*"
    "references/db_connections.txt"
    "references/project_*_index.json"
    "scripts/install.bat" "scripts/install.sh"
)

ZIP_ARGS=()
for pattern in "${EXCLUDES[@]}"; do
    ZIP_ARGS+=(-x "$pattern")
done

zip -r -q "$DIST_DIR/$PACKAGE_NAME" "${INCLUDES[@]}" "${ZIP_ARGS[@]}"

SIZE=$(du -sh "$DIST_DIR/$PACKAGE_NAME" | cut -f1)
echo "✅ $DIST_DIR/$PACKAGE_NAME  ($SIZE)"
