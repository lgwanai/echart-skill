import os
import sys

import duckdb


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_analyze_segments_sum(tmp_path):
    from scripts.segment_analysis import analyze_segments, render_segment_markdown

    db_path = tmp_path / "segment.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute(
        "CREATE TABLE sales AS SELECT * FROM (VALUES "
        "('east', 10.0), ('east', 20.0), ('west', 5.0)"
        ") AS t(region, amount)"
    )
    conn.close()

    report = analyze_segments("sales", "region", "amount", str(db_path))
    assert report.rows[0].segment == "east"
    assert report.rows[0].metric_value == 30.0
    assert report.rows[0].share_pct == 85.71
    assert "分群分析" in render_segment_markdown(report)

