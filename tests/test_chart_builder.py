import copy
import json
from pathlib import Path

import pytest

from scripts.chart_builder import build_html, compile_chart, SUPPORTED
from scripts.browser_smoke_test import find_playwright_runtime, run_smoke_test


def spec(view="column"):
    return dict(
        id="chart1",
        title="Revenue",
        view=view,
        scope="Sum per month",
        source="q1",
        query_hash="q1hash",
        x="month",
        x_order="explicit",
        metrics=[dict(field="value", name="Revenue", unit="CNY")],
    )


@pytest.mark.parametrize(
    "value", ["12", True, float("nan"), float("inf"), 2**53, 10**400]
)
def test_rejects_non_numeric_or_non_finite(value):
    with pytest.raises(ValueError):
        compile_chart(spec(), [{"month": "Jan", "value": value}])


def test_preserves_negative_null_zero_and_rejects_duplicate_categories():
    rows = [
        {"month": name, "value": v}
        for name, v in [("Jan", -3), ("Feb", None), ("Mar", 0)]
    ]
    assert compile_chart(spec("line"), rows)["series"][0]["data"] == [-3, None, 0]
    with pytest.raises(ValueError, match="Duplicate categories"):
        compile_chart(spec(), rows + [rows[0]])


@pytest.mark.parametrize("view", sorted(SUPPORTED))
def test_every_supported_view_renders_real_echarts_and_matches_data(view, tmp_path):
    if not find_playwright_runtime():
        pytest.fail("Real Chromium is required for compiler certification")
    chart = spec(view)
    rows = [
        {"month": "Jan", "value": 10.0, "rate": 2},
        {"month": "Feb", "value": 20.5, "rate": 3},
    ]
    if view == "mixed":
        chart["metrics"][0]["type"] = "bar"
        chart["metrics"].append(dict(field="rate", name="Rate", unit="%", type="line"))
    if view == "scatter":
        chart["x_unit"] = "CNY"
        rows = [{"month": 4, "value": 10}, {"month": 6, "value": 20}]
    data = tmp_path / "rows.json"
    data.write_text(json.dumps(rows))
    chart["rows_path"] = "rows.json"
    content = build_html({"charts": [chart]}, tmp_path)
    output = tmp_path / "chart.html"
    output.write_text(content)
    code, report = run_smoke_test(output)
    assert code == 0, report
    assert report["runtime"]["chartCount"] == 1
    assert report["runtime"]["reconciliationErrors"] == []


def test_browser_rejects_one_missing_chart_and_altered_series(tmp_path):
    chart = spec()
    chart["rows_path"] = "rows.json"
    (tmp_path / "rows.json").write_text('[{"month":"</script><img src=x>","value":10}]')
    content = build_html({"charts": [chart]}, tmp_path)
    assert "\\u003c/script" in content
    content = content.replace("<td>10</td>", "<td>888</td>")
    end = content.rfind("</body>")
    content = (
        content[:end]
        + '<div data-echart-chart id="missing"></div><script>echarts.getInstanceByDom(document.getElementById("chart1")).setOption({series:[{data:[999]}]})</script>'
        + content[end:]
    )
    output = tmp_path / "broken.html"
    output.write_text(content)
    code, report = run_smoke_test(output)
    assert code == 1
    assert any("missing" in e for e in report["errors"])
    assert any("data differs" in e for e in report["errors"]), report
    assert any("source table differs" in e for e in report["errors"]), report


def test_complete_delivery_with_actual_evidence_and_rejects_changed_source(tmp_path):
    from scripts.artifact_manifest import materialize_manifest, embed_manifest
    from scripts.validate_delivery import validate_delivery
    from scripts.chart_builder import validate_compiled_html

    chart = spec("line")
    chart["rows_path"] = "rows.json"
    data = tmp_path / "rows.json"
    data.write_text(
        '[{"month":"2026-01-01","value":10},{"month":"2026-02-01","value":20}]'
    )
    output = tmp_path / "complete.html"
    output.write_text(build_html({"charts": [chart]}, tmp_path))
    draft = {
        "queries": [
            {
                "id": "q1",
                "result_path": "rows.json",
                "query_hash": "q1hash",
                "date_field": "month",
            }
        ]
    }
    embed_manifest(output, materialize_manifest(draft, tmp_path / "draft.json", output))
    assert validate_delivery(output) == []
    data.write_text('[{"month":"2026-01-01","value":999}]')
    assert validate_compiled_html(output)


@pytest.mark.parametrize("slots,valid", [
    ("<!-- ECHART_CHART:chart1 -->", True),
    ("<!-- ECHART_CHART:chart1 --><!-- ECHART_CHART:chart1 -->", False),
    ("<!-- ECHART_CHART:wrong -->", False),
    ("<!-- ECHART_CHARTS --><!-- ECHART_CHART:chart1 -->", False),
    ("", False),
])
def test_named_shell_slots_are_exact(tmp_path, slots, valid):
    chart = spec()
    chart["rows_path"] = "rows.json"
    (tmp_path / "rows.json").write_text('[{"month":"Jan","value":10}]')
    shell = '<html><head><style>.chart-card{padding:5px}</style></head><body>' + slots + '</body></html>'
    if valid:
        result = build_html({"charts": [chart]}, tmp_path, shell)
        assert result.count('id="chart1"') == 1
        assert '<!-- ECHART_CHART:' not in result
    else:
        with pytest.raises(ValueError, match="Shell needs"):
            build_html({"charts": [chart]}, tmp_path, shell)
