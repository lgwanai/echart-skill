from pathlib import Path

import pytest

from scripts.browser_smoke_test import find_playwright_runtime, run_smoke_test


pytestmark = pytest.mark.skipif(
    find_playwright_runtime() is None,
    reason="Playwright Chromium runtime unavailable",
)


def test_browser_smoke_rejects_fake_chart_surface(tmp_path: Path):
    html = tmp_path / "ok.html"
    html.write_text(
        """<html><body><div id="chart" aria-label="Revenue trend" style="width:400px;height:300px"></div>
        <script>
        window.echarts = {init(root) {
          root.setAttribute('_echarts_instance_', 'ec_1');
          const canvas = document.createElement('canvas');
          canvas.width = 400; canvas.height = 300; root.appendChild(canvas);
          return {setOption(){}};
        }};
        const chart = echarts.init(document.getElementById('chart'));
        chart.setOption({series:[{type:'bar',data:[1]}]});
        </script></body></html>""",
        encoding="utf-8",
    )

    code, report = run_smoke_test(html)

    assert code == 1, report
    assert report["runtime"]["chartCount"] == 1
    assert any('no live ECharts series' in e for e in report['errors'])


def test_browser_smoke_rejects_runtime_exception(tmp_path: Path):
    html = tmp_path / "broken.html"
    html.write_text(
        "<html><body><script>console.error('boom'); throw new Error('broken runtime')</script></body></html>",
        encoding="utf-8",
    )

    code, report = run_smoke_test(html)

    assert code == 1
    assert any("pageerror" in error or "console error" in error for error in report["errors"])
