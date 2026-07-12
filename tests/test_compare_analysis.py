import os
import sys

import duckdb


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_compare_metric_sum(tmp_path):
    from scripts.compare_analysis import compare_metric, render_compare_markdown

    db_path = tmp_path / "compare.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute(
        "CREATE TABLE sales AS SELECT * FROM (VALUES "
        "('2024-01', 10.0), ('2024-01', 20.0), ('2024-02', 45.0)"
        ") AS t(month, amount)"
    )
    conn.close()

    result = compare_metric("sales", "amount", "month", "2024-01", "2024-02", str(db_path))
    assert result.baseline_value == 30.0
    assert result.current_value == 45.0
    assert result.pct_change == 50.0
    assert "指标对比分析" in render_compare_markdown(result)

