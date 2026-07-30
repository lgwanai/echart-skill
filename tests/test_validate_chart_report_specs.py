from pathlib import Path

from scripts.validate_chart import validate


FAKE_ECHARTS_LIBRARY = (
    "/* Apache Software Foundation */ var echarts = {"
    "init:function(){return {setOption:function(){}};}"
    "};"
    + ("/* echarts filler */" * 8000)
)


def test_validate_report_chart_specs_with_json_options(tmp_path):
    html = tmp_path / "report.html"
    html.write_text(
        """
        <!DOCTYPE html>
        <html><body>
        <section class="chart-panel">
          <div class="chart-head">
            <div>
              <div class="chart-title">趋势图</div>
              <div class="chart-scope">统计口径：COUNT(*)</div>
              <div class="chart-source">数据来源：orders / query hash abc</div>
            </div>
            <button data-action="view-data" onclick="toggleChartData('chart1-table')">查看数据</button>
          </div>
          <div id="chart1"></div>
          <div id="chart1-table" class="chart-data-table" hidden><table><tr><th>维度</th><th>值</th></tr><tr><td>A</td><td>1</td></tr></table></div>
        </section>
        <script>
        """ + FAKE_ECHARTS_LIBRARY + """
        </script>
        <script>
        function toggleChartData(id){ var el = document.getElementById(id); if (el) el.hidden = !el.hidden; }
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
        <section class="chart-panel">
          <div class="chart-head">
            <div><div class="chart-scope">统计口径：COUNT(*)</div><div class="chart-source">数据来源：orders / query hash abc</div></div>
            <button data-action="view-data" onclick="toggleChartData('chart1-table')">查看数据</button>
          </div>
          <div id="chart1"></div>
          <div id="chart1-table" class="chart-data-table" hidden><table><tr><td>A</td></tr></table></div>
        </section>
        <script>
        """ + FAKE_ECHARTS_LIBRARY + """
        </script>
        <script>
        function toggleChartData(id){ var el = document.getElementById(id); if (el) el.hidden = !el.hidden; }
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
