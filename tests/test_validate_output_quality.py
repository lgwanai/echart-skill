import json
from pathlib import Path

from scripts.validate_output_quality import validate_artifact


def test_validate_output_quality_accepts_query_artifact_with_sidecar(tmp_path):
    artifact = tmp_path / "result.csv"
    artifact.write_text("region,total\n华东,40\n", encoding="utf-8")
    Path(str(artifact) + ".meta.json").write_text(
        json.dumps({
            "artifact_path": str(artifact),
            "artifact_type": "query_result",
            "generated_at": "2026-07-30T10:00:00",
            "row_count": 1,
            "columns": ["region", "total"],
            "query_hash": "abc123",
            "effective_metrics": "# 当前生效统计口径\n\n## GMV\n",
            "lineage_recorded": True,
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    assert validate_artifact(artifact) == []


def test_validate_output_quality_rejects_bare_query_artifact(tmp_path):
    artifact = tmp_path / "result.json"
    artifact.write_text("[{\"region\":\"华东\",\"total\":40}]", encoding="utf-8")

    errors = validate_artifact(artifact)

    assert any("metadata sidecar" in error for error in errors)


def test_validate_output_quality_rejects_report_without_scope_or_lineage(tmp_path):
    report = tmp_path / "report.md"
    report.write_text(
        "# 销售报告\n\n业绩表现很好，建议继续投入。\n",
        encoding="utf-8",
    )

    errors = validate_artifact(report, "text")

    assert any("统计口径" in error or "scope" in error for error in errors)
    assert any("lineage" in error or "血缘" in error for error in errors)


def test_validate_output_quality_accepts_enterprise_markdown_report(tmp_path):
    report = tmp_path / "report.md"
    report.write_text(
        """
# 销售经营分析报告

- 生成时间: 2026-07-30 10:00:00

## 核心结论

2026H1 GMV 为 120 万，同比下降 8.5%，订单数 3200 单。

## 关键发现

需求方 A 贡献 52 万，占比 43.3%；需求方 B 贡献 31 万，占比 25.8%。
主要下降来自需求方 A，同比减少 14 万，需要复核合同、价格和渠道策略。

## 统计口径说明

统计范围为已完成订单，GMV = SUM(pay_amount)，按自然月汇总。
本报告不包含取消订单、测试订单和未确认订单，因此不能代表全渠道询单规模。

## 数据血缘

来源表: orders。Query Hash: `abc123`。

## 行动建议

优先核查需求方 A 的下单频次、价格变动和竞品替代情况，并在下一版补充客户访谈证据。
        """,
        encoding="utf-8",
    )

    assert validate_artifact(report, "text") == []
