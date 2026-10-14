#!/bin/bash
set -euo pipefail
DATE=$(date +"%Y%m%d")
PACKAGE_NAME="${PACKAGE_NAME:-echart-skill_${DATE}.zip}"
DIST_DIR="${DIST_DIR:-dist}"
python scripts/build_skill_package.py --mode "${PACKAGE_MODE:-full}" --output "$DIST_DIR/$PACKAGE_NAME"
