from pathlib import Path

from scripts.validate_accessibility_performance import validate_accessibility_performance


def test_accessible_chart_and_reduced_motion_pass(tmp_path: Path):
    html = tmp_path / "accessible.html"
    html.write_text(
        """<html><head><style>
        @keyframes fade {from{opacity:0}to{opacity:1}}
        @media (prefers-reduced-motion: reduce){*{animation:none!important}}
        </style></head><body>
        <div id="chart" aria-label="Monthly revenue"></div>
        <table><tr><th scope="col">Month</th></tr></table>
        <script>const chart=echarts.init(document.getElementById('chart'));</script>
        </body></html>""",
        encoding="utf-8",
    )

    assert validate_accessibility_performance(html) == []


def test_rejects_unnamed_chart_headerless_table_and_uncontrolled_motion(tmp_path: Path):
    html = tmp_path / "inaccessible.html"
    html.write_text(
        """<html><head><style>@keyframes fade{from{opacity:0}to{opacity:1}}</style></head>
        <body><div id="chart"></div><table><tr><td>1</td></tr></table>
        <script>echarts.init(document.getElementById('chart'));</script></body></html>""",
        encoding="utf-8",
    )

    errors = validate_accessibility_performance(html)

    assert any("chart name" in error for error in errors)
    assert any("header cells" in error for error in errors)
    assert any("reduced-motion" in error for error in errors)
