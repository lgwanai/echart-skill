import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_dashboard_reviewer_flags_external_refs(tmp_path):
    from scripts.dashboard_reviewer import review_dashboard, render_dashboard_review_markdown

    dashboard = tmp_path / "dashboard.html"
    dashboard.write_text(
        """
        <html><head><title>经营 Dashboard</title>
        <script src="https://cdn.example.com/echarts.js"></script></head>
        <body><h1>KPI 总览</h1><div id="chart" style="height:400px"></div>
        <script>const c = echarts.init(document.getElementById('chart'));</script>
        <p>洞察：收入异常波动，建议复核。</p></body></html>
        """,
        encoding="utf-8",
    )

    review = review_dashboard(str(dashboard))
    assert any(issue.category == "security" for issue in review.issues)
    assert review.metrics["echarts_init_count"] == 1
    assert "Dashboard 质量审阅" in render_dashboard_review_markdown(review)

