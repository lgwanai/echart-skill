---
phase: 01-security-quality-foundation
plan: 03
subsystem: security
tags: [api-key, environment-variables, path-traversal, security, pytest]

# Dependency graph
requires:
  - phase: 01-security-quality-foundation
    plan: 01
    provides: pytest framework, validators module
  - phase: 01-security-quality-foundation
    plan: 02
    provides: structlog logging infrastructure
provides:
  - Environment-based API key configuration with deprecation warning
  - Path traversal protection in HTTP server
affects: [server, chart_generator, security]

# Tech tracking
tech-stack:
  added: []
  patterns: [env-first configuration, path validation, deprecation warnings]

key-files:
  created:
    - tests/test_config.py
    - tests/test_server_security.py
  modified:
    - scripts/chart_generator.py
    - scripts/server.py

key-decisions:
  - "Environment variable BAIDU_AK takes priority over config.txt"
  - "config.txt fallback shows DeprecationWarning"
  - "Path traversal protection uses existing validate_file_path from validators.py"

patterns-established:
  - "Environment variables for secrets: primary source, file fallback with warning"
  - "Path validation: validate_file_path before serving any file"

requirements-completed:
  - SEC-03
  - SEC-04

# Metrics
duration: 4min
completed: 2026-04-04
---

# Phase 1 Plan 3: API Key Migration + Path Traversal Protection Summary

**Migrated Baidu API key from hardcoded config.txt to environment variable with deprecation warning fallback, and added path traversal protection to the HTTP server.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-04T00:53:37Z
- **Completed:** 2026-04-04T00:57:42Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- API key now read from BAIDU_AK environment variable as primary source
- config.txt fallback shows DeprecationWarning to encourage migration
- HTTP server validates all file paths against project directory
- Path traversal attempts (including URL-encoded) return 403 Forbidden

## Task Commits

Each task was committed atomically:

1. **Task 1: Migrate API key to environment variable** - `6abeefc` (feat)
2. **Task 2: Add path traversal protection to server** - `c0fc853` (feat)

## Files Created/Modified

- `scripts/chart_generator.py` - Added environment variable priority, deprecation warning for config.txt fallback
- `scripts/server.py` - Added path traversal protection using validate_file_path
- `tests/test_config.py` - Tests for environment variable, fallback, and missing key scenarios
- `tests/test_server_security.py` - Tests for path validation (valid, traversal, absolute, nested, symlink)

## Decisions Made

- **Environment variable priority:** BAIDU_AK env var is checked first, config.txt is deprecated fallback
- **Deprecation messaging:** Chinese warning message for consistency with project
- **Path validation reuse:** Used existing validate_file_path from validators.py rather than duplicating logic

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed test import paths for module resolution**
- **Found during:** Task 1 (test execution)
- **Issue:** Tests failed with "ModuleNotFoundError: No module named 'server'" due to incorrect sys.path setup
- **Fix:** Added both project root and scripts directory to sys.path in test files
- **Files modified:** tests/test_config.py
- **Verification:** Tests executed successfully
- **Committed in:** 6abeefc (part of Task 1 commit)

**2. [Rule 3 - Blocking] Fixed macOS temp directory symlink resolution in tests**
- **Found during:** Task 2 (test execution)
- **Issue:** Tests failed because macOS symlinks /var to /private/var, causing path comparison mismatches
- **Fix:** Used Path.resolve() to get the real path before comparison in tests
- **Files modified:** tests/test_server_security.py
- **Verification:** All path validation tests pass
- **Committed in:** c0fc853 (part of Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both blocking)
**Impact on plan:** Both fixes necessary for tests to run correctly on macOS. No scope creep.

## Issues Encountered

None - all issues were handled via deviation rules.

## User Setup Required

None - no external service configuration required. Users may optionally set BAIDU_AK environment variable instead of using config.txt.

## Next Phase Readiness

- Security hardening complete for secrets management and file access
- All security tests passing
- Ready for next phase of quality improvements

---
*Phase: 01-security-quality-foundation*
*Completed: 2026-04-04*

## Self-Check: PASSED

- All files verified to exist
- All commits verified in git history
