import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_report_reviewer_flags_weak_report(tmp_path):
    from scripts.report_reviewer import review_report, render_review_markdown

    report = tmp_path / "weak.md"
    report.write_text("# 销售报告\n\n业务表现显著提升，未来潜力巨大。\n", encoding="utf-8")

    review = review_report(str(report))
    assert review.score < 100
    assert any(issue.category == "evidence" for issue in review.issues)
    assert "报告质量审阅" in render_review_markdown(review)

