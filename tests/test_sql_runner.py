import json
import os
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.sql_runner import main
from scripts.sql_runner import create_parser, _profile_from_connection_args


def _make_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    try:
        conn.execute("CREATE TABLE orders(region VARCHAR, amount INTEGER)")
        conn.execute("INSERT INTO orders VALUES ('华东', 10), ('华南', 20), ('华东', 30)")
    finally:
        conn.close()


def test_sql_runner_executes_duckdb_file_to_json(tmp_path, capsys):
    db_path = tmp_path / "workspace.duckdb"
    sql_path = tmp_path / "query.sql"
    _make_db(db_path)
    sql_path.write_text(
        "SELECT region, SUM(amount) AS total FROM orders GROUP BY region ORDER BY region",
        encoding="utf-8",
    )

    main(["--db", str(db_path), "--file", str(sql_path), "--output", "json"])

    rows = json.loads(capsys.readouterr().out)
    assert rows == [
        {"region": "华东", "total": 40},
        {"region": "华南", "total": 20},
    ]


def test_sql_runner_executes_direct_sql_option_to_json(tmp_path, capsys):
    db_path = tmp_path / "workspace.duckdb"
    _make_db(db_path)

    main([
        "--db",
        str(db_path),
        "--sql",
        "SELECT region, SUM(amount) AS total FROM orders GROUP BY region ORDER BY region",
        "--output",
        "json",
    ])

    rows = json.loads(capsys.readouterr().out)
    assert rows == [
        {"region": "华东", "total": 40},
        {"region": "华南", "total": 20},
    ]


def test_sql_runner_writes_csv_output(tmp_path, capsys):
    db_path = tmp_path / "workspace.duckdb"
    out_path = tmp_path / "result.csv"
    _make_db(db_path)

    main([
        "--db",
        str(db_path),
        "--output",
        "csv",
        "--out",
        str(out_path),
        "SELECT region, amount FROM orders ORDER BY amount",
    ])

    assert "Wrote result:" in capsys.readouterr().out
    assert out_path.read_text(encoding="utf-8").splitlines() == [
        "region,amount",
        "华东,10",
        "华南,20",
        "华东,30",
    ]
    meta = json.loads(Path(str(out_path) + ".meta.json").read_text(encoding="utf-8"))
    assert meta["artifact_type"] == "query_result"
    assert meta["row_count"] == 3
    assert meta["columns"] == ["region", "amount"]
    assert meta["query_hash"]
    assert meta["lineage_recorded"] is True


def test_sql_runner_out_writes_all_rows_by_default(tmp_path):
    db_path = tmp_path / "workspace.duckdb"
    out_path = tmp_path / "result.json"
    conn = duckdb.connect(str(db_path))
    try:
        conn.execute("CREATE TABLE numbers AS SELECT range AS n FROM range(205)")
    finally:
        conn.close()

    main([
        "--db",
        str(db_path),
        "--output",
        "json",
        "--out",
        str(out_path),
        "SELECT n FROM numbers ORDER BY n",
    ])

    rows = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(rows) == 205
    assert rows[-1] == {"n": 204}
    assert Path(str(out_path) + ".meta.json").exists()


def test_sql_runner_blocks_write_by_default(tmp_path):
    db_path = tmp_path / "workspace.duckdb"
    _make_db(db_path)

    try:
        main(["--db", str(db_path), "DROP TABLE orders"])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("DROP TABLE should be blocked without --allow-write")


def test_sql_runner_builds_direct_postgres_profile_from_args(monkeypatch):
    monkeypatch.setenv("PG_PASSWORD", "secret")
    parser = create_parser()
    args = parser.parse_args([
        "--type",
        "postgresql",
        "--host",
        "localhost",
        "--port",
        "5432",
        "--database",
        "china_mobile",
        "--username",
        "china_mobile",
        "--password-env",
        "PG_PASSWORD",
        "--file",
        "queries/city_h1_yoy.sql",
    ])

    profile = _profile_from_connection_args(args)

    assert profile.type == "postgresql"
    assert profile.host == "localhost"
    assert profile.port == 5432
    assert profile.database == "china_mobile"
    assert profile.username == "china_mobile"
    assert profile.password.get_secret_value() == "secret"


def test_sql_runner_direct_connection_requires_host():
    parser = create_parser()
    args = parser.parse_args([
        "--type",
        "postgresql",
        "--database",
        "china_mobile",
        "SELECT 1",
    ])

    try:
        _profile_from_connection_args(args)
    except SystemExit as exc:
        assert "host" in str(exc)
    else:
        raise AssertionError("direct connection should require --host")
