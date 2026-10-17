import json
from pathlib import Path

import duckdb
import pytest

from scripts import project_cleaning as pc
from scripts.sql_runner import _execute_duckdb, main as query_main


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "business"
    rules_dir = root / "config/data_cleaning"
    rules_dir.mkdir(parents=True)
    db = root / "data.duckdb"
    with duckdb.connect(str(db)) as conn:
        conn.execute("CREATE TABLE orders(id INTEGER, region VARCHAR, amount VARCHAR)")
        conn.execute("INSERT INTO orders VALUES (1, ' East ', '10'), (1, ' East ', '10'), (2, 'West', '20')")
        conn.execute("CREATE TABLE other AS SELECT 7 AS amount")
    config = {"text_cleaning": [{"column": "region"}],
              "type_conversions": [{"column": "amount", "type": "number"}]}
    (rules_dir / "orders.json").write_text(json.dumps(config))
    manifest = {"version": 1, "datasets": [{"id": "orders", "db": "data.duckdb", "table": "orders",
                                            "rules": "config/data_cleaning/orders.json"}]}
    (rules_dir / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.chdir(root)
    monkeypatch.delenv("ECHART_PROJECT_ROOT", raising=False)
    return root, db


def approve():
    assert pc.main(["approve", "orders"]) == 0


def edit_binding(root, **changes):
    path = root / pc.MANIFEST
    manifest = json.loads(path.read_text())
    manifest["datasets"][0].update(changes)
    path.write_text(json.dumps(manifest))


def test_auto_query_keeps_raw_and_legitimate_duplicates(project):
    root, db = project
    approve()
    rows = _execute_duckdb("SELECT region, SUM(amount) total FROM orders GROUP BY region ORDER BY region", str(db), False)
    assert rows == [{"region": "East", "total": 20}, {"region": "West", "total": 20}]
    assert rows.cleaning["datasets"][0]["deduplication"]["mode"] == "none"
    with duckdb.connect(str(db)) as conn:
        assert conn.execute("SELECT region FROM orders LIMIT 1").fetchone()[0] == " East "
        assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 3
    assert (root / ".echart-skill/cleaning/latest.json").is_file()


def test_repeated_runs_refresh_raw_and_rules(project):
    root, db = project
    approve()
    first = _execute_duckdb("SELECT SUM(amount) total FROM orders", str(db), False)
    second = _execute_duckdb("SELECT SUM(amount) total FROM orders", str(db), False)
    assert first == second == [{"total": 40}]
    assert first.cleaning["datasets"][0]["source_sha256"] == second.cleaning["datasets"][0]["source_sha256"]
    with duckdb.connect(str(db)) as conn:
        conn.execute("INSERT INTO orders VALUES (3, 'South', '30')")
    third = _execute_duckdb("SELECT SUM(amount) total FROM orders", str(db), False)
    assert third == [{"total": 70}]
    assert third.cleaning["datasets"][0]["source_sha256"] != first.cleaning["datasets"][0]["source_sha256"]
    (root / "config/data_cleaning/orders.json").write_text(json.dumps({"deduplicate": True}))
    with pytest.raises(pc.CleaningError, match="new/changed"):
        _execute_duckdb("SELECT COUNT(*) FROM orders", str(db), False)


def test_preview_does_not_approve_or_write_data(project):
    root, db = project
    assert pc.main(["preview", "orders"]) == 0
    assert "approved_sha256" not in json.loads((root / pc.MANIFEST).read_text())["datasets"][0]
    assert not (root / ".echart-skill/cleaning/latest.json").exists()
    with pytest.raises(pc.CleaningError, match="new/changed"):
        _execute_duckdb("SELECT COUNT(*) FROM orders", str(db), False)


def test_source_drift_blocks_instead_of_reusing_success(project):
    root, db = project
    approve()
    _execute_duckdb("SELECT SUM(amount) FROM orders", str(db), False)
    with duckdb.connect(str(db)) as conn:
        conn.execute("INSERT INTO orders VALUES (3, 'South', 'bad-number')")
    with pytest.raises(pc.CleaningError, match="new nulls"):
        _execute_duckdb("SELECT SUM(amount) FROM orders", str(db), False)
    with duckdb.connect(str(db)) as conn:
        assert conn.execute("SELECT amount FROM orders WHERE id=3").fetchone()[0] == "bad-number"


def test_scopes_to_project_and_exact_db(project, tmp_path, monkeypatch):
    root, db = project
    approve()
    second = tmp_path / "other_project"
    second.mkdir()
    with duckdb.connect(str(second / "data.duckdb")) as conn:
        conn.execute("CREATE TABLE orders AS SELECT ' Untouched ' region")
    assert _execute_duckdb("SELECT region FROM orders", str(second / "data.duckdb"), False) == [{"region": " Untouched "}]
    nested = root / "outputs/reports"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    assert pc.project_root() == root
    assert _execute_duckdb("SELECT SUM(amount) n FROM orders", str(db), False) == [{"n": 40}]
    monkeypatch.chdir(second)
    assert pc.execute_project_query("SELECT * FROM orders", str(db)) is None
    monkeypatch.setenv("ECHART_PROJECT_ROOT", str(root))
    assert _execute_duckdb("SELECT SUM(amount) n FROM orders", str(db), False) == [{"n": 40}]


def test_full_row_dedupe_is_explicit(project):
    root, db = project
    path = root / "config/data_cleaning/orders.json"
    config = json.loads(path.read_text())
    config["deduplicate"] = True
    path.write_text(json.dumps(config))
    approve()
    assert _execute_duckdb("SELECT SUM(amount) total FROM orders", str(db), False) == [{"total": 30}]
    with duckdb.connect(str(db)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 3


@pytest.mark.parametrize("rules", [
    {"typo_rules": []}, {"missing_values": {"amount": "ask"}},
    {"outliers": [{"column": "amount", "method": "bogus"}]},
    {"text_cleaning": [{"column": "region", "stripp": True}]},
    {"rules": [{"name": "x", "left": "amount", "op": "LIKE"}]},
    {"unique_key": "id", "duplicate_keep": "latest"},
    {"unique_key": "id", "duplicate_keep": "latest", "duplicate_order_by": "id", "duplicate_order_ascending": False},
    {"boolean_mappings": {"amount": {"true_values": ["yes"], "false_values": ["yes"]}}},
    {"outliers": [{"column": "amount", "method": "iqr", "action": "clip"}]},
])
def test_unknown_or_ambiguous_options_block(project, rules):
    root, _ = project
    (root / "config/data_cleaning/orders.json").write_text(json.dumps(rules))
    with pytest.raises(pc.CleaningError):
        pc.load_registry()


def test_missing_column_blocks_preview(project):
    root, _ = project
    (root / "config/data_cleaning/orders.json").write_text(json.dumps({"text_cleaning": [{"column": "absent"}]}))
    assert pc.main(["approve", "orders"]) == 1


def test_conflicting_rules_block(project):
    root, _ = project
    path = root / pc.MANIFEST
    manifest = json.loads(path.read_text())
    duplicate = dict(manifest["datasets"][0], id="second")
    manifest["datasets"].append(duplicate)
    path.write_text(json.dumps(manifest))
    with pytest.raises(pc.CleaningError, match="Conflicting"):
        pc.load_registry()


def test_paths_cannot_escape_or_follow_outside_symlinks(project, tmp_path):
    root, _ = project
    edit_binding(root, rules="../outside.json")
    with pytest.raises(pc.CleaningError, match="escapes"):
        pc.load_registry()
    outside = tmp_path / "outside.json"
    outside.write_text("{}")
    (root / "link.json").symlink_to(outside)
    edit_binding(root, rules="link.json")
    with pytest.raises(pc.CleaningError, match="escapes"):
        pc.load_registry()


def test_orphaned_rules_are_not_silently_ignored(project):
    root, _ = project
    (root / pc.MANIFEST).unlink()
    with pytest.raises(pc.CleaningError, match="manifest.json is missing"):
        pc.load_registry()


def test_cte_joins_and_main_schema_use_clean_data(project):
    _, db = project
    approve()
    rows = _execute_duckdb("WITH x AS (SELECT SUM(amount) total FROM main.orders) SELECT total + amount total FROM x CROSS JOIN other", str(db), False)
    assert rows == [{"total": 47}]


@pytest.mark.parametrize("sql", ["SELECT SUM(CAST(amount AS INT)) FROM data.main.orders", "SELECT COUNT(*) FROM data.main.orders"])
def test_catalog_qualification_cannot_bypass_cleaning(project, sql):
    _, db = project
    approve()
    with pytest.raises(pc.CleaningError, match="bypasses"):
        _execute_duckdb(sql, str(db), False)


def test_no_writes_or_multi_statement_even_with_allow_write(project):
    _, db = project
    approve()
    for sql in ("DELETE FROM orders", "SELECT * FROM orders; SELECT 1"):
        with pytest.raises(pc.CleaningError, match="one SELECT"):
            _execute_duckdb(sql, str(db), True)


def test_metadata_binds_exact_cleaning_receipt(project, capsys):
    root, db = project
    approve()
    out = root / "result.json"
    query_main(["--db", str(db), "--sql", "SELECT SUM(amount) total FROM orders", "--output", "json", "--out", str(out)])
    assert json.loads(out.read_text()) == [{"total": 40}]
    meta = json.loads(Path(str(out) + ".meta.json").read_text())
    assert meta["project_cleaning"]["datasets"][0]["rule_sha256"]
    assert meta["project_cleaning"]["datasets"][0]["source_sha256"]
    assert " East " not in json.dumps(meta["project_cleaning"])


def test_named_external_profile_is_guarded(project):
    root, _ = project
    edit_binding(root, origin={"profile": "sales", "table": "public.orders"})
    with pytest.raises(pc.CleaningError, match="local snapshot"):
        pc.check_external_source("sales")
    pc.check_external_source("other")


def test_failed_checks_do_not_approve(project):
    root, _ = project
    edit_binding(root, checks={"min_output_rows": 4})
    assert pc.main(["approve", "orders"]) == 1
    assert not pc.load_registry()[2][0]["approved"]


def test_no_project_rules_preserves_existing_behavior(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ECHART_PROJECT_ROOT", raising=False)
    assert pc.load_registry()[2] == []
    assert _execute_duckdb("SELECT 42 AS answer", str(tmp_path / "plain.duckdb"), False) == [{"answer": 42}]


def test_existing_view_cannot_bypass_cleaning(project):
    _, db = project
    with duckdb.connect(str(db)) as conn:
        conn.execute("CREATE VIEW raw_alias AS SELECT * FROM data.main.orders")
    approve()
    with pytest.raises(pc.CleaningError, match="bypasses"):
        _execute_duckdb("SELECT COUNT(*) FROM raw_alias", str(db), False)


def test_source_discovery_advertises_registry(project):
    from scripts.project_data_context import resolve_sources
    root, _ = project
    result = resolve_sources("orders", root)
    assert result["project_cleaning"]["status"] == "configured"
    assert result["project_cleaning"]["datasets"][0]["approved"] is False
    approve()
    assert resolve_sources("orders", root)["project_cleaning"]["datasets"][0]["approved"] is True


def test_approved_keyed_latest_is_deterministic(project):
    root, db = project
    with duckdb.connect(str(db)) as conn:
        conn.execute("ALTER TABLE orders ADD COLUMN updated TIMESTAMP DEFAULT '2026-01-01'")
        conn.execute("INSERT INTO orders VALUES (1, 'East', '15', '2026-01-02')")
    config = {"type_conversions": [{"column": "amount", "type": "number"}],
              "unique_key": ["id"], "duplicate_keep": "latest", "duplicate_order_by": "updated"}
    (root / "config/data_cleaning/orders.json").write_text(json.dumps(config))
    approve()
    assert _execute_duckdb("SELECT SUM(amount) n FROM orders", str(db), False) == [{"n": 35}]
    assert _execute_duckdb("SELECT SUM(amount) n FROM orders", str(db), False) == [{"n": 35}]


def test_nonfinite_values_block(project):
    _, db = project
    with duckdb.connect(str(db)) as conn:
        conn.execute("INSERT INTO orders VALUES (3, 'South', 'inf')")
    assert pc.main(["approve", "orders"]) == 1


def test_analysis_runner_also_applies_and_records_cleaning(project):
    from scripts.analysis_runner import main
    root, db = project
    approve()
    output = root / "segments.json"
    assert main(["segment", "--db", str(db), "--table", "orders", "--dimension", "region", "--metric", "amount",
                 "--output", "json", "--out", str(output)]) == 0
    assert {r["dimension"] for r in json.loads(output.read_text())} == {"East", "West"}
    meta = json.loads(Path(str(output) + ".meta.json").read_text())
    assert meta["project_cleaning"]["status"] == "passed"


def test_boolean_coercion_cannot_be_hidden_by_fill(project):
    root, _ = project
    (root / "config/data_cleaning/orders.json").write_text(json.dumps({
        "boolean_mappings": {"region": {"true_values": ["West"], "false_values": ["Other"]}},
        "missing_values": {"region": {"strategy": "constant", "value": False}}
    }))
    assert pc.main(["approve", "orders"]) == 1


def test_schema_change_missing_column_never_falls_back(project):
    _, db = project
    approve()
    with duckdb.connect(str(db)) as conn:
        conn.execute("ALTER TABLE orders RENAME COLUMN region TO territory")
    with pytest.raises(pc.CleaningError, match="warnings"):
        _execute_duckdb("SELECT COUNT(*) FROM orders", str(db), False)


def test_invalid_explicit_root_blocks(tmp_path, monkeypatch):
    monkeypatch.setenv("ECHART_PROJECT_ROOT", str(tmp_path / "typo"))
    with pytest.raises(pc.CleaningError, match="existing directory"):
        pc.load_registry()


@pytest.mark.parametrize("content", ['{"version":1,', '{"version":1,"version":1,"datasets":[]}', '{"version":1,"datasets":NaN}'])
def test_malformed_registry_never_becomes_no_rules(project, content):
    root, db = project
    (root / pc.MANIFEST).write_text(content)
    with pytest.raises(pc.CleaningError):
        _execute_duckdb("SELECT COUNT(*) FROM orders", str(db), False)
