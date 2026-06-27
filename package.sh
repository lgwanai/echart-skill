#!/bin/bash
# =============================================================================
# echart-skill Release Packager
# =============================================================================
set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_NAME="echart-skill_${TIMESTAMP}.zip"
DIST_DIR="dist"
mkdir -p "$DIST_DIR"

echo "📦 Packaging Echart Skill …"

EXCLUDES=(
    ".git/*"
    ".gitignore"
    ".gitattributes"
    ".claude/*"
    ".planning/*"
    ".pytest_cache/*"
    "__pycache__/*"
    "*.pyc" "*.pyo" "*.DS_Store"
    "idea.md" "package.sh"
    "workspace.duckdb"
    "dist/*" "tmp/*" "outputs/*" "logs/*" "tests/*"
    "examples/*" "wheels/*"
    "config.txt" "echart_config.txt"
    "*.skill"
)

ZIP_ARGS=()
for pattern in "${EXCLUDES[@]}"; do
    ZIP_ARGS+=(-x "$pattern")
done

zip -r -q "$DIST_DIR/$PACKAGE_NAME" . "${ZIP_ARGS[@]}"

SIZE=$(du -sh "$DIST_DIR/$PACKAGE_NAME" | cut -f1)
echo "✅ $DIST_DIR/$PACKAGE_NAME  ($SIZE)"
