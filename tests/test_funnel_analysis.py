import os
import sys

import duckdb


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_analyze_funnel_conversion(tmp_path):
    from scripts.funnel_analysis import analyze_funnel, render_funnel_markdown

    db_path = tmp_path / "funnel.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute(
        "CREATE TABLE events AS SELECT * FROM (VALUES "
        "('u1', 'visit'), ('u1', 'signup'), ('u1', 'pay'), "
        "('u2', 'visit'), ('u2', 'signup'), "
        "('u3', 'visit')"
        ") AS t(user_id, step)"
    )
    conn.close()

    report = analyze_funnel("events", "user_id", "step", ["visit", "signup", "pay"], str(db_path))
    assert [step.users for step in report.steps] == [3, 2, 1]
    assert report.steps[1].from_previous_pct == 66.67
    assert report.steps[2].from_start_pct == 33.33
    assert "漏斗分析" in render_funnel_markdown(report)

