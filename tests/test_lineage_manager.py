from pathlib import Path


def test_record_and_find_lineage(tmp_path):
    from scripts.lineage_manager import (
        LineageRecord,
        find_lineage,
        hash_query,
        read_lineage,
        record_lineage,
        render_lineage_markdown,
    )

    lineage_path = tmp_path / "lineage.jsonl"
    artifact = tmp_path / "sales_report.html"
    record = LineageRecord(
        artifact_path=str(artifact),
        artifact_type="report",
        source_tables=["sales"],
        columns=["amount", "region"],
        query_hashes=[hash_query("SELECT region, SUM(amount) FROM sales GROUP BY region")],
        metric_scopes=["GMV"],
        generated_by="/report sales",
    )

    written = record_lineage(record, lineage_path)
    assert written == lineage_path

    records = read_lineage(lineage_path)
    assert len(records) == 1
    assert records[0].source_tables == ["sales"]

    by_table = find_lineage(source_table="sales", path=lineage_path)
    assert len(by_table) == 1

    by_artifact = find_lineage(artifact_path=str(artifact), path=lineage_path)
    assert len(by_artifact) == 1

    markdown = render_lineage_markdown(records)
    assert "数据血缘记录" in markdown
    assert "sales" in markdown
    assert "GMV" in markdown


def test_hash_query_is_stable():
    from scripts.lineage_manager import hash_query

    assert hash_query("select 1") == hash_query("select 1")
    assert hash_query("select 1") != hash_query("select 2")
