import os
import sys

import duckdb


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_analyze_cohort_monthly_retention(tmp_path):
    from scripts.cohort_analysis import analyze_cohort, render_cohort_markdown

    db_path = tmp_path / "cohort.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute(
        "CREATE TABLE activity AS SELECT * FROM (VALUES "
        "('u1', DATE '2024-01-01', DATE '2024-01-02'), "
        "('u1', DATE '2024-01-01', DATE '2024-02-02'), "
        "('u2', DATE '2024-01-15', DATE '2024-01-20'), "
        "('u3', DATE '2024-02-01', DATE '2024-02-03')"
        ") AS t(user_id, cohort_date, activity_date)"
    )
    conn.close()

    report = analyze_cohort("activity", "user_id", "cohort_date", "activity_date", str(db_path), "month", 2)
    lookup = {(cell.cohort, cell.period_index): cell for cell in report.cells}
    assert lookup[("2024-01-01", 0)].users == 2
    assert lookup[("2024-01-01", 1)].retention_pct == 50.0
    assert "留存/队列分析" in render_cohort_markdown(report)

