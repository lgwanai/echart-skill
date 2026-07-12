import os
import sys

import duckdb


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_analyze_whatif_projects_scenarios(tmp_path):
    from scripts.whatif_analysis import analyze_whatif, render_whatif_markdown

    db_path = tmp_path / "whatif.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute("CREATE TABLE sales AS SELECT * FROM (VALUES (100.0), (50.0)) AS t(amount)")
    conn.close()

    report = analyze_whatif("sales", "amount", [("growth", 0.1), ("downside", -0.2)], str(db_path))
    assert report.baseline_value == 150.0
    assert report.scenarios[0].projected_value == 165.0
    assert report.scenarios[1].absolute_change == -30.0
    assert "假设推演分析" in render_whatif_markdown(report)

