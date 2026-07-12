import json
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_evidence_pack_matches_lineage_and_audit(tmp_path, monkeypatch):
    import scripts.evidence_pack as ep
    from scripts.lineage_manager import LineageRecord, hash_query, record_lineage

    artifact = tmp_path / "report.md"
    artifact.write_text("# Report\n\nvalue 100\n", encoding="utf-8")
    lineage_path = tmp_path / "lineage.jsonl"
    audit_path = tmp_path / "audit.log"
    query = "SELECT SUM(amount) FROM sales"
    query_hash = hash_query(query)

    record_lineage(
        LineageRecord(
            artifact_path=str(artifact.resolve()),
            artifact_type="report",
            source_tables=["sales"],
            columns=["amount"],
            query_hashes=[query_hash],
            metric_scopes=["GMV"],
        ),
        lineage_path,
    )
    audit_path.write_text(
        json.dumps({"ts": "2026-07-08T10:00:00", "tbl": "sales", "q": query_hash, "n": 1, "mask": False}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ep, "render_effective_metrics", lambda cwd=None: "# 当前生效统计口径\n\nGMV")

    pack = ep.build_evidence_pack(str(artifact), lineage_path=str(lineage_path), audit_log_path=str(audit_path))
    assert pack.artifact_sha256
    assert len(pack.lineage) == 1
    assert len(pack.audit_entries) == 1
    assert "GMV" in ep.render_evidence_markdown(pack)

