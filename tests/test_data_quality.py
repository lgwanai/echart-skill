import os
import tempfile

import duckdb


def test_data_quality_detects_missing_and_duplicate_rows():
    from scripts.data_quality import analyze_table_quality, render_quality_markdown

    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name
    os.unlink(db_path)
    conn = duckdb.connect(db_path)
    conn.execute("CREATE TABLE orders (id INTEGER, region TEXT, amount DOUBLE)")
    conn.execute("""
        INSERT INTO orders VALUES
        (1, '华东', 100.0),
        (1, '华东', 100.0),
        (2, NULL, 200.0),
        (3, NULL, 300.0),
        (4, NULL, 400.0)
    """)
    conn.close()

    try:
        report = analyze_table_quality("orders", db_path)
        assert report.table == "orders"
        assert report.row_count == 5
        assert report.score < 100
        assert any(issue.category == "completeness" for issue in report.issues)
        assert any(issue.category == "duplicate" for issue in report.issues)

        markdown = render_quality_markdown(report)
        assert "数据质量报告" in markdown
        assert "region" in markdown
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass


def test_data_quality_empty_table_scores_zero():
    from scripts.data_quality import analyze_table_quality

    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name
    os.unlink(db_path)
    conn = duckdb.connect(db_path)
    conn.execute("CREATE TABLE empty_t (id INTEGER)")
    conn.close()

    try:
        report = analyze_table_quality("empty_t", db_path)
        assert report.score == 0
        assert report.grade == "D"
        assert report.issues[0].category == "volume"
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass
