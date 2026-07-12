import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_generate_executive_brief_extracts_sections(tmp_path):
    from scripts.executive_brief import generate_brief, render_brief_markdown

    report = tmp_path / "report.md"
    report.write_text(
        "# 报告\n\n结论：收入增长 12.5%，华东贡献 60%。\n"
        "建议：优先优化渠道投放。\n"
        "口径：样本限制为 2024 年订单数据。\n",
        encoding="utf-8",
    )

    brief = generate_brief(str(report))
    assert "12.5%" in brief.key_numbers
    assert brief.likely_conclusions
    assert brief.action_items
    assert brief.caveats
    assert "高管摘要" in render_brief_markdown(brief)

