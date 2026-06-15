#!/bin/bash
# =============================================================================
# echart-skill Release Packager
# =============================================================================
# Creates a release zip with optional offline wheel bundle.
#
# Before packaging for offline release:
#   bash scripts/download_wheels.sh              # download all wheels
#   bash scripts/download_wheels.sh --core-only  # or core-only (smaller)
#
# Usage:
#   bash package.sh              # package without wheels (smaller, needs network)
#   bash package.sh --offline    # package WITH wheels (larger, works offline)
# =============================================================================

# Get current timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_NAME="echart-skill_${TIMESTAMP}.zip"
DIST_DIR="dist"

# Ensure dist directory exists
mkdir -p "$DIST_DIR"

INCLUDE_WHEELS=false
if [[ "${1:-}" == "--offline" ]]; then
    INCLUDE_WHEELS=true
fi

echo "📦 Packaging Echart Skill …"

if $INCLUDE_WHEELS; then
    if [[ -d wheels ]] && ls wheels/*.whl &>/dev/null; then
        WHEEL_COUNT=$(ls -1 wheels/*.whl 2>/dev/null | wc -l | tr -d ' ')
        echo "   Including $WHEEL_COUNT offline wheels"
    else
        echo "⚠️  --offline requested but wheels/ dir is empty or missing."
        echo "   Run first: bash scripts/download_wheels.sh"
        echo "   Continuing WITHOUT wheels …"
        INCLUDE_WHEELS=false
    fi
fi

# Build exclude list
EXCLUDES=(
    ".git/*"
    ".gitignore"
    ".gitattributes"
    ".claude/*"
    ".planning/*"
    ".pytest_cache/*"
    "__pycache__/*"
    "*.pyc"
    "*.pyo"
    "*.DS_Store"
    "idea.md"
    "package.sh"
    "workspace.duckdb"
    "dist/*"
    "tmp/*"
    "outputs/*"
    "logs/*"
    "config.txt"
    "echart_config.txt"
    "*.skill"
    # generated chart outputs (not reference templates — see references/examples/*.md)
    "examples/agent_charts/*"
)

# Exclude wheels unless --offline
if ! $INCLUDE_WHEELS; then
    EXCLUDES+=("wheels/*")
fi

# Build the -x arguments
ZIP_ARGS=()
for pattern in "${EXCLUDES[@]}"; do
    ZIP_ARGS+=(-x "$pattern")
done

# Execute packaging
zip -r -q "$DIST_DIR/$PACKAGE_NAME" . "${ZIP_ARGS[@]}"

# Report
SIZE=$(du -sh "$DIST_DIR/$PACKAGE_NAME" | cut -f1)

echo ""
echo "✅ Packaging complete!"
echo "   📦 $DIST_DIR/$PACKAGE_NAME  ($SIZE)"
echo ""

if $INCLUDE_WHEELS; then
    echo "   🛡️  Offline-ready: users can install without PyPI access."
    echo "      They run:  bash scripts/install.sh --offline"
    echo "      (or on Windows:  scripts\\install.bat --offline)"
else
    echo "   🌐 Online install required (pip downloads from PyPI)."
    echo "      For offline release:  bash package.sh --offline"
fi
