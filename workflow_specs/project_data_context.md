# Project Data Context Workflow

Use this workflow before locating data for an analysis. Its purpose is to make
previously configured databases and previously used project files discoverable
without searching arbitrary directories or guessing the source again.

## Project-owned state

The canonical project file is:

```text
<project>/.echart-skill/data_sources.json
```

It belongs to the project, not to the reusable Skill. The file contains only:

- database profile name, database/schema name, table/collection names;
- column names, types, nullability, inferred time/measure/dimension roles;
- approximate row counts where available;
- local file path, size, modification time, SHA-256 and sheet/table structure;
- preferred access path, last-use time and use count.

It must never contain hosts, usernames, passwords, connection strings, tokens,
raw rows, sampled values or PII examples.

## Required source-resolution sequence

Before scanning directories, assuming `workspace.duckdb`, or asking the user to
repeat a connection name, run:

```bash
python scripts/project_data_context.py resolve --query "<the user's analysis request>"
```

Interpret the result as follows:

- `resolved`: use the selected profile/file and the stated preferred access path.
- `needs_refresh`: refresh that source before querying it.
- `ambiguous`: present the top plausible candidates and ask the user to choose;
  do not silently select a database or file.
- `not_found`: inspect effective connection profiles and user-provided/project
  files, then register the selected source. Do not recursively search unrelated
  parent, output, cache or backup directories.

After successful use, record the choice:

```bash
python scripts/project_data_context.py touch '<source-id>' --query "<request>"
```

Prior usage is only a weak ranking signal; table/column/name matches take
precedence. A stale or missing file is never selected as active.

## Database lifecycle

Testing a connection refreshes its project index by default:

```bash
python scripts/db_manager.py test <profile> --cwd <project>
```

The refresh connects with the maintained profile, lists tables/collections,
describes their structure, infers analytical roles and stores approximate row
counts when available. It samples MongoDB documents only to infer field types;
sampled values are never persisted.

Manual refresh:

```bash
python scripts/project_data_context.py --project-root <project> refresh-db <profile>
```

Use `--no-index` on connection tests only for a deliberate connectivity-only
diagnostic. Such a test does not make the source analysis-ready.

## File lifecycle

The maintained file-import CLI automatically records the original file and its
materialized DuckDB tables. When a file is used without importing it, register
it immediately after selection:

```bash
python scripts/project_data_context.py --project-root <project> register-file <path>
```

For an already materialized file:

```bash
python scripts/project_data_context.py --project-root <project> register-file <path> \
  --duckdb <db-path> --table <table-name>
```

Registration persists structure, not data values. Modification time and size
are checked during resolution; changed files must be registered again.

## Validation

```bash
python scripts/project_data_context.py --project-root <project> validate
```

Validation blocks duplicate source IDs, unsupported kinds, sensitive keys at
any nesting level, and missing or changed files. Project context, connection profiles and
local data files are forbidden release-package content.
