import os
import sys

import duckdb


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_validate_contract_detects_missing_and_nulls(tmp_path):
    from scripts.data_contract import parse_contract_columns, validate_contract, render_contract_markdown

    db_path = tmp_path / "contract.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute("CREATE TABLE orders AS SELECT * FROM (VALUES (1, 10.0), (NULL, 20.0)) AS t(order_id, amount)")
    conn.close()

    columns = parse_contract_columns("order_id:INT:required,amount:DECIMAL,region:VARCHAR")
    report = validate_contract("orders", columns, str(db_path))
    assert not report.passed
    assert any(issue.category == "required_nulls" for issue in report.issues)
    assert any(issue.category == "missing_column" for issue in report.issues)
    assert "数据契约校验报告" in render_contract_markdown(report)

