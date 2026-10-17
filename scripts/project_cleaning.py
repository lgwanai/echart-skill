"""Project-owned cleaning registry and automatic, isolated DuckDB query preparation.

No user Python/SQL is loaded as executable configuration. Rules are approved by
content hash, not by filename. Every query starts from a fresh raw snapshot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.project_data_context import discover_project_root
from scripts.data_cleaner import clean_dataframe, _quote_column

MANIFEST = "config/data_cleaning/manifest.json"
ENGINE_VERSION = 1


class CleaningError(ValueError):
    pass


def project_root(explicit=None):
    chosen = explicit or os.environ.get("ECHART_PROJECT_ROOT")
    root = Path(chosen).expanduser().resolve() if chosen else discover_project_root()
    if not root.is_dir():
        raise CleaningError("Project root must be an existing directory")
    return root


def _inside(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise CleaningError("Cleaning paths must be non-empty project-relative paths")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise CleaningError("Cleaning path escapes the project (including symlinks)")
    return path


def _read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise CleaningError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(CleaningError(f"Non-finite JSON: {value}")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CleaningError(f"Cannot load cleaning configuration: {path.name}") from exc


def _keys(obj, allowed, required=()):
    if not isinstance(obj, dict) or set(obj) - set(allowed) or set(required) - set(obj):
        raise CleaningError(f"Invalid configuration keys; allowed={sorted(allowed)}, required={sorted(required)}")


def _choice(value, choices, label):
    if value not in choices:
        raise CleaningError(f"Unsupported {label}: {value!r}")


def validate_rules(config):
    """Reject unsupported/typoed options before the permissive legacy engine runs."""
    groups = {
        "type_conversions": ({"column", "type", "format", "decimals", "true_values", "false_values"}, {"column", "type"}),
        "text_cleaning": ({"column", "strip", "case", "remove_special", "replace"}, {"column"}),
        "outliers": ({"column", "method", "min", "max", "threshold", "action", "flag_column"}, {"column"}),
        "normalization": ({"column", "method", "target_column"}, {"column"}),
        "derived_features": ({"name", "method", "source", "part", "numerator", "denominator", "decimals", "columns", "sep"}, {"name", "method"}),
        "masking": ({"column", "method", "keep_start", "keep_end", "mask", "salt"}, {"column"}),
        "rules": ({"name", "left", "right", "right_value", "op", "action", "flag_column"}, {"name", "left", "op"}),
        "cross_table_rules": ({"name", "table", "left", "right", "op", "key", "left_key", "right_key", "left_keys", "right_keys"}, {"name", "table", "left", "right", "op"}),
    }
    _keys(config, set(groups) | {"missing_values", "boolean_mappings", "deduplicate", "unique_key", "unique_keys",
                               "duplicate_keep", "duplicate_order_by", "duplicate_order_ascending"})
    for group, (allowed, required) in groups.items():
        rules = config.get(group, [])
        if not isinstance(rules, list):
            raise CleaningError(f"{group} must be an array")
        for rule in rules:
            _keys(rule, allowed, required)
            if "column" in required and (not isinstance(rule["column"], str) or not rule["column"]):
                raise CleaningError("Rule column must be a non-empty string")
            if group == "type_conversions":
                _choice(rule["type"], {"date", "datetime", "money", "decimal", "float", "number", "numeric", "int", "integer", "string", "text", "bool", "boolean"}, "type")
            elif group == "text_cleaning":
                if "case" in rule:
                    _choice(rule["case"], {"lower", "upper"}, "text case")
                if "replace" in rule and (not isinstance(rule["replace"], dict) or not all(isinstance(v, str) for v in rule["replace"].values())):
                    raise CleaningError("Text replacements must map literal strings to strings")
            elif group == "outliers":
                _choice(rule.get("method", "bounds"), {"bounds", "iqr", "zscore"}, "outlier method")
                _choice(rule.get("action", "flag"), {"flag", "null", "drop", "clip"}, "outlier action")
                if (rule.get("method", "bounds") == "bounds" or rule.get("action") == "clip") and not {"min", "max"} & rule.keys():
                    raise CleaningError("Bounds/clip requires explicit min or max")
                if "min" in rule and "max" in rule and rule["min"] > rule["max"]:
                    raise CleaningError("min cannot exceed max")
            elif group == "normalization":
                _choice(rule.get("method", "minmax"), {"minmax", "zscore"}, "normalization")
            elif group == "derived_features":
                _choice(rule["method"], {"date_part", "ratio", "concat"}, "derived feature")
                if rule["method"] == "date_part":
                    _choice(rule.get("part", "year"), {"year", "month", "day", "weekday", "is_weekend"}, "date part")
            elif group == "masking":
                _choice(rule.get("method", "middle"), {"middle", "hash"}, "masking")
            elif group in {"rules", "cross_table_rules"}:
                _choice(rule["op"], {"<", "<=", ">", ">=", "==", "!="}, "comparison")
                if group == "rules":
                    _choice(rule.get("action", "flag"), {"flag", "drop"}, "rule action")
    missing = config.get("missing_values", {})
    if not isinstance(missing, dict):
        raise CleaningError("missing_values must be an object")
    for spec in missing.values():
        spec = {"strategy": spec} if isinstance(spec, str) else spec
        _keys(spec, {"strategy", "value"}, {"strategy"})
        _choice(spec["strategy"], {"drop", "mean", "median", "mode", "constant", "none"}, "missing strategy")
        if spec["strategy"] == "constant" and ("value" not in spec or spec["value"] is None):
            raise CleaningError("Constant fill requires a non-null value")
    mappings = config.get("boolean_mappings", {})
    if not isinstance(mappings, dict):
        raise CleaningError("boolean_mappings must be an object")
    for spec in mappings.values():
        _keys(spec, {"true_values", "false_values"}, {"true_values", "false_values"})
    for spec in [*mappings.values(), *config.get("type_conversions", [])]:
        if "true_values" in spec or "false_values" in spec:
            if not all(isinstance(spec.get(k, []), list) for k in ("true_values", "false_values")):
                raise CleaningError("Boolean values must be arrays")
            if set(map(str, spec.get("true_values", []))) & set(map(str, spec.get("false_values", []))):
                raise CleaningError("True and false mappings overlap")
    for key in ("deduplicate", "duplicate_order_ascending"):
        if key in config and type(config[key]) is not bool:
            raise CleaningError(f"{key} must be boolean")
    if "unique_key" in config and "unique_keys" in config:
        raise CleaningError("Specify unique_key once")
    key = config.get("unique_key", config.get("unique_keys"))
    if key is not None and not (isinstance(key, str) and key.strip() or isinstance(key, list) and key and all(isinstance(k, str) and k for k in key)):
        raise CleaningError("unique_key must name one or more columns")
    keep = config.get("duplicate_keep", "first")
    _choice(keep, {"first", "last", "latest", False}, "duplicate_keep")
    if keep == "latest" and not config.get("duplicate_order_by"):
        raise CleaningError("latest requires duplicate_order_by")
    if keep == "latest" and config.get("duplicate_order_ascending", True) is not True:
        raise CleaningError("latest requires ascending order; use first/last for other orders")


def load_registry(root=None):
    root = project_root(root)
    path = _inside(root, MANIFEST)
    if not path.exists():
        folder = _inside(root, "config/data_cleaning")
        if folder.exists() and any(folder.glob("*.json")):
            raise CleaningError("Cleaning JSON exists but manifest.json is missing; register it before analysis")
        return root, None, []
    if root == ROOT:
        raise CleaningError("Business cleaning rules belong in a user project, not the Skill source tree")
    manifest = _read_json(path)
    _keys(manifest, {"version", "datasets"}, {"version", "datasets"})
    if manifest["version"] != 1 or not isinstance(manifest["datasets"], list):
        raise CleaningError("Unsupported cleaning manifest version/structure")
    entries, ids, targets = [], set(), set()
    for item in manifest["datasets"]:
        _keys(item, {"id", "db", "table", "rules", "checks", "approved_sha256", "origin"}, {"id", "db", "table", "rules"})
        if not isinstance(item["id"], str) or not item["id"] or item["id"] in ids:
            raise CleaningError("Dataset IDs must be non-empty and unique")
        ids.add(item["id"])
        db = _inside(root, item["db"])
        table = item["table"]
        if not isinstance(table, str) or not table or "." in table:
            raise CleaningError("Only main-schema table names (without catalog/schema prefix) are supported")
        target = (str(db), table.casefold())
        if target in targets:
            raise CleaningError("Conflicting rules for the same database/table")
        targets.add(target)
        rules_path = _inside(root, item["rules"])
        config = _read_json(rules_path)
        validate_rules(config)
        checks = item.get("checks", {})
        _keys(checks, {"max_new_nulls", "max_removed_rows", "max_rule_violations", "min_output_rows"})
        if any(type(v) is not int or v < 0 for v in checks.values()):
            raise CleaningError("Check thresholds must be non-negative integers")
        if "origin" in item:
            _keys(item["origin"], {"profile", "table"}, {"profile", "table"})
            if not all(isinstance(v, str) and v for v in item["origin"].values()):
                raise CleaningError("origin must name a profile and table, never credentials")
        # Bind approval to the engine implementation, source binding, checks and rules.
        engine_hash = hashlib.sha256((ROOT / "scripts/data_cleaner.py").read_bytes() + Path(__file__).read_bytes()).hexdigest()
        digest = hashlib.sha256(json.dumps({"engine": engine_hash, "binding": {k: v for k, v in item.items() if k != "approved_sha256"},
                                           "rules": config}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        entries.append({"binding": item, "db": db, "config": config, "sha256": digest,
                        "approved": item.get("approved_sha256") == digest})
    return root, manifest, entries


def _atomic_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".cleaning-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def registry_summary(root=None):
    root, manifest, entries = load_registry(root)
    return {"status": "configured" if manifest else "not_configured", "manifest": str(root / MANIFEST),
            "datasets": [{"id": e["binding"]["id"], "db": e["binding"]["db"], "table": e["binding"]["table"],
                          "approved": e["approved"]} for e in entries],
            "instruction": "Use sql_runner/analysis_runner local queries for automatic cleaning. Read workflow_specs/data_cleaning_workflow.md for new/changed rules."}


def _apply(conn, entry):
    import pandas as pd
    table = entry["binding"]["table"]
    original = conn.execute(f"SELECT * FROM main.{_quote_column(table)}").fetchdf()
    source_hash = hashlib.sha256(pd.util.hash_pandas_object(original, index=False).values.tobytes()
                                 + str(list(zip(original.columns, map(str, original.dtypes)))).encode()).hexdigest()
    cleaned, report = clean_dataframe(original, entry["config"], conn)
    if report["warnings"]:
        raise CleaningError("Cleaning warnings block analysis: " + "; ".join(report["warnings"]))
    import numpy as np
    for column in cleaned.select_dtypes(include="number"):
        if (cleaned[column].notna() & ~np.isfinite(cleaned[column])).any():
            raise CleaningError(f"{table}: non-finite numeric output in {column}")
    before_nulls = original.isna().sum()
    # Compare retained source rows as well as conversion counters (before fills/drops).
    recorded_nulls = sum(r.get("new_nulls", 0) for r in report["type_conversions"] + report["boolean_mappings"])
    retained_nulls = sum(int((cleaned[col].isna() & original.loc[cleaned.index, col].notna()).sum())
                         for col in set(original.columns) & set(cleaned.columns))
    new_nulls = max(recorded_nulls, retained_nulls)
    checks = entry["binding"].get("checks", {})
    violations = sum(r["violations"] for r in report["rules"] + report["cross_table_rules"])
    if new_nulls > checks.get("max_new_nulls", 0):
        raise CleaningError(f"{table}: new nulls {new_nulls} exceed the approved limit")
    if violations > checks.get("max_rule_violations", 0):
        raise CleaningError(f"{table}: rule violations {violations} exceed the approved limit")
    if report["removed_rows"] > checks.get("max_removed_rows", len(original)):
        raise CleaningError(f"{table}: removed rows exceed the approved limit")
    if len(cleaned) < checks.get("min_output_rows", 1):
        raise CleaningError(f"{table}: output has too few rows")
    # Do not store mapping replacements, salts or raw/sample values in receipts.
    report["text_cleaning"] = [{"column": r["column"]} for r in report["text_cleaning"]]
    report.update(dataset=entry["binding"]["id"], source_table=table, rule_sha256=entry["sha256"],
                  source_sha256=source_hash, new_nulls=new_nulls,
                  missing_before={str(k): int(v) for k, v in before_nulls.items()},
                  missing_after={str(k): int(v) for k, v in cleaned.isna().sum().items()})
    return cleaned, report


def _snapshot(db):
    from database import get_repository
    if not db.is_file():
        raise CleaningError("Registered source database does not exist")
    # A child cursor has isolated temp relations; never leak them into the pool.
    with get_repository(str(db)).connection() as base:
        conn = base.cursor()
    conn.execute("BEGIN TRANSACTION")
    return conn


def execute_project_query(sql, db_path, root=None):
    """Return (rows, receipt), or None when this DB has no project cleaning rules.

    All registered tables in the selected DB are refreshed and checked together.
    Only a single SELECT is allowed. Raw tables are never updated or renamed.
    """
    root, _, entries = load_registry(root)
    db = Path(db_path).expanduser().resolve()
    entries = [entry for entry in entries if entry["db"] == db]
    if not entries:
        return None
    if any(not e["approved"] for e in entries):
        raise CleaningError("Project cleaning rules are new/changed; preview and approve before analysis")
    conn = _snapshot(db)
    try:
        statements = conn.extract_statements(sql)
        if len(statements) != 1 or str(statements[0].type) != "StatementType.SELECT":
            raise CleaningError("Automatic cleaning accepts one SELECT only; use schema tools for inspection")
        frames, reports = [], []
        for entry in entries:
            frame, report = _apply(conn, entry)
            frames.append(frame)
            reports.append(report)
        # No cached cleaned table: run against the current transaction snapshot.
        for entry, frame in zip(entries, frames):
            conn.register(entry["binding"]["table"], frame)
        # Catalog-qualified references and existing views must not bypass the
        # clean temp relation. Disable optimizations so metadata-only COUNT and
        # predicate elimination cannot hide a physical scan during this check.
        conn.execute("PRAGMA disable_optimizer")
        plan = json.loads(conn.execute("EXPLAIN (FORMAT JSON) " + sql).fetchone()[1])
        catalog = conn.execute("SELECT current_database()").fetchone()[0]
        raw_names = {f"{catalog}.main.{e['binding']['table']}".replace('"', '').casefold() for e in entries}
        def check(nodes):
            for node in nodes:
                if str(node.get("extra_info", {}).get("Table", "")).replace('"', '').casefold() in raw_names:
                    raise CleaningError("Query bypasses a cleaned table; use its unqualified table name")
                check(node.get("children", []))
        check(plan)
        conn.execute("PRAGMA enable_optimizer")
        result = conn.execute(sql)
        columns = [c[0] for c in result.description]
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        receipt = {"status": "passed", "engine_version": ENGINE_VERSION, "project_root": str(root),
                   "manifest": MANIFEST, "generated_at": datetime.now(timezone.utc).isoformat(), "datasets": reports}
        report_path = _inside(root, ".echart-skill/cleaning/latest.json")
        _atomic_json(report_path, receipt)
        print("Project cleaning validated: " + ", ".join(e["binding"]["id"] for e in entries), file=sys.stderr)
        return rows, receipt
    finally:
        conn.close()  # rolls back; temp relations and data are discarded


def check_external_source(profile_name, root=None):
    """Do not silently analyze remote raw data when a governed local binding exists."""
    _, _, entries = load_registry(root)
    if any(e["binding"].get("origin", {}).get("profile") == profile_name for e in entries):
        raise CleaningError("This profile has project cleaning rules: refresh its local snapshot with db_cli import, then query the registered local DB")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    for name in ("preview", "approve"):
        cmd = sub.add_parser(name)
        cmd.add_argument("dataset")
    args = parser.parse_args(argv)
    try:
        root, manifest, entries = load_registry(args.project_root)
        if args.command == "status":
            print(json.dumps({"project_root": str(root), "status": "configured" if manifest else "not_configured",
                              "datasets": [{"id": e["binding"]["id"], "db": e["binding"]["db"],
                                            "table": e["binding"]["table"], "approved": e["approved"],
                                            "sha256": e["sha256"]} for e in entries]}, ensure_ascii=False, indent=2))
            return 0
        entry = next((e for e in entries if e["binding"]["id"] == args.dataset), None)
        if entry is None:
            raise CleaningError("Unknown cleaning dataset")
        conn = _snapshot(entry["db"])
        try:
            _, report = _apply(conn, entry)
        finally:
            conn.close()
        if args.command == "approve":
            entry["binding"]["approved_sha256"] = entry["sha256"]
            _atomic_json(_inside(root, MANIFEST), manifest)
        print(json.dumps({"status": args.command, "report": report}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f"Project cleaning blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
