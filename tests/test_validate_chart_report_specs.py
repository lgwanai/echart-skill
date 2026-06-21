from pathlib import Path

from scripts.validate_chart import validate


def test_validate_report_chart_specs_with_json_options(tmp_path):
    html = tmp_path / "report.html"
    html.write_text(
        """
        <!DOCTYPE html>
        <html><body>
        <div id="chart1"></div>
        <script>
        window.echarts = { init: function() { return { setOption: function() {} }; } };
        echarts.init(document.getElementById("chart1")).setOption({});
        window.reportChartSpecs = [{
          "id": "chart1",
          "recipe": "references/examples/line-simple.md",
          "option": {
            "xAxis": {"type": "category", "data": ["A", "B"]},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "data": [1, 2]}]
          }
        }];
        </script>
        </body></html>
        """,
        encoding="utf-8",
    )

    assert validate(str(html)) == 0


def test_validate_does_not_count_library_type_without_chart_option(tmp_path):
    html = tmp_path / "broken.html"
    html.write_text(
        """
        <!DOCTYPE html>
        <html><body>
        <div id="chart1"></div>
        <script>
        // Simulates library internals. This must not count as a real chart.
        const internal = {type: "line", data: [1, 2, 3]};
        echarts.init(document.getElementById("chart1")).setOption({});
        window.reportChartSpecs = [];
        </script>
        </body></html>
        """,
        encoding="utf-8",
    )

    assert validate(str(html)) == 1
