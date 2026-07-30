import json
import os
import sys
from pathlib import Path

import duckdb


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.analysis_runner import build_period_compare_sql, create_parser, main


def _make_orders_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    try:
        conn.execute(
            """
            CREATE TABLE orders AS SELECT * FROM (VALUES
              ('北京', DATE '2025-01-10', 10, 100.0),
              ('北京', DATE '2025-06-10', 20, 200.0),
              ('北京', DATE '2026-01-10', 15, 150.0),
              ('北京', DATE '2026-06-10', 30, 300.0),
              ('上海', DATE '2025-02-10', 40, 400.0),
              ('上海', DATE '2026-02-10', 20, 200.0)
            ) AS t(city_name, in_date, room_nights, gmv)
            """
        )
    finally:
        conn.close()


def test_analysis_runner_period_compare_by_dimension(tmp_path, capsys):
    db_path = tmp_path / "orders.duckdb"
    _make_orders_db(db_path)

    exit_code = main([
        "period-compare",
        "--db",
        str(db_path),
        "--table",
        "orders",
        "--date-column",
        "in_date",
        "--metric",
        "room_nights",
        "--dimension",
        "city_name",
        "--baseline-start",
        "2025-01-01",
        "--baseline-end",
        "2025-06-30",
        "--current-start",
        "2026-01-01",
        "--current-end",
        "2026-06-30",
        "--output",
        "json",
    ])

    assert exit_code == 0
    rows = json.loads(capsys.readouterr().out)
    beijing = next(row for row in rows if row["dimension"] == "北京")
    shanghai = next(row for row in rows if row["dimension"] == "上海")
    assert beijing["baseline_value"] == 30
    assert beijing["current_value"] == 45
    assert beijing["pct_change"] == 50
    assert shanghai["pct_change"] == -50


def test_analysis_runner_trend_and_topn(tmp_path, capsys):
    db_path = tmp_path / "orders.duckdb"
    _make_orders_db(db_path)

    assert main([
        "trend",
        "--db",
        str(db_path),
        "--table",
        "orders",
        "--date-column",
        "in_date",
        "--metric",
        "room_nights",
        "--start",
        "2026-01-01",
        "--end",
        "2026-12-31",
        "--output",
        "json",
    ]) == 0
    trend_rows = json.loads(capsys.readouterr().out)
    assert sum(row["metric_value"] for row in trend_rows) == 65

    assert main([
        "topn",
        "--db",
        str(db_path),
        "--table",
        "orders",
        "--dimension",
        "city_name",
        "--metric",
        "room_nights",
        "--output",
        "json",
    ]) == 0
    topn_rows = json.loads(capsys.readouterr().out)
    assert topn_rows[0]["dimension"] == "北京"


def test_analysis_runner_entity_search_and_structured_filters(tmp_path, capsys):
    db_path = tmp_path / "orders.duckdb"
    _make_orders_db(db_path)

    assert main([
        "entity-search",
        "--db",
        str(db_path),
        "--table",
        "orders",
        "--column",
        "city_name",
        "--contains-text",
        "京",
        "--output",
        "json",
    ]) == 0
    values = json.loads(capsys.readouterr().out)
    assert values == [{"value": "北京"}]

    assert main([
        "period-compare",
        "--db",
        str(db_path),
        "--table",
        "orders",
        "--date-column",
        "in_date",
        "--metric",
        "room_nights",
        "--baseline-start",
        "2025-01-01",
        "--baseline-end",
        "2025-06-30",
        "--current-start",
        "2026-01-01",
        "--current-end",
        "2026-06-30",
        "--contains-any",
        "city_name=京,深",
        "--any-contains",
        "city_name=沪",
        "--any-eq",
        "city_name=北京",
        "--output",
        "json",
    ]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert rows[0]["baseline_value"] == 30
    assert rows[0]["current_value"] == 45


def test_analysis_runner_rejects_unsafe_identifier():
    parser = create_parser()
    args = parser.parse_args([
        "period-compare",
        "--table",
        "orders; DROP TABLE orders",
        "--date-column",
        "in_date",
        "--metric",
        "room_nights",
        "--baseline-start",
        "2025-01-01",
        "--baseline-end",
        "2025-06-30",
        "--current-start",
        "2026-01-01",
        "--current-end",
        "2026-06-30",
    ])

    try:
        build_period_compare_sql(args)
    except SystemExit as exc:
        assert "unsafe identifier" in str(exc)
    else:
        raise AssertionError("unsafe table identifier should be rejected")
