import os
import sys

import duckdb


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_build_catalog_lists_tables_and_roles(tmp_path):
    from scripts.catalog_manager import build_catalog, render_catalog_markdown

    db_path = tmp_path / "catalog.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute(
        "CREATE TABLE sales AS SELECT * FROM (VALUES "
        "(1, DATE '2024-01-01', 'east', 10.0), "
        "(2, DATE '2024-01-02', 'west', 20.0)"
        ") AS t(order_id, order_date, region, amount)"
    )
    conn.close()

    catalog = build_catalog(str(db_path))
    assert [table.name for table in catalog.tables] == ["sales"]
    table = catalog.tables[0]
    roles = {column.name: column.role for column in table.columns}
    assert roles["order_date"] == "time"
    assert roles["amount"] == "measure"
    assert "数据资产目录" in render_catalog_markdown(catalog)

