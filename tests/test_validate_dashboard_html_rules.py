from pathlib import Path

from scripts.validate_chart import validate


FAKE_ECHARTS_LIBRARY = (
    "/* Apache Software Foundation */ var echarts = {"
    "init:function(){return {setOption:function(){}};},"
    "graphic:{LinearGradient:function(){},RadialGradient:function(){}}"
    "};"
    + ("/* echarts filler */" * 8000)
)


def _dashboard_html(body: str) -> str:
    return f"""
    <html>
      <head>
        <style>
          .dashboard-container{{width:min(100%,1440px);margin:0 auto;padding:24px;}}
          .dashboard-header{{display:flex;justify-content:space-between;}}
          .dashboard-toolbar{{display:flex;gap:8px;}}
          .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;}}
          .kpi-card{{min-height:88px;min-width:0;overflow-wrap:anywhere;}}
          .kpi-card *{{min-width:0;overflow-wrap:anywhere;}}
          .dashboard-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:18px;}}
          .chart-card{{min-height:360px;}}
          .chart-card--wide{{grid-column:span 2;}}
          .chart-card-header{{display:flex;align-items:center;min-width:0;overflow-wrap:anywhere;}}
          .chart-surface{{height:340px;}}
          .chart-meta{{font-size:12px;}}
          .chart-data-table{{display:none;}}
          .chart-data-table.is-open{{display:block;}}
          .table-scroll{{max-height:520px;overflow:auto;}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <header class="dashboard-header"><h1>经营 Dashboard</h1><div class="dashboard-toolbar"></div></header>
        <section class="kpi-grid"><article class="kpi-card">KPI</article></section>
        <main class="dashboard-grid">
          <section class="chart-card">
            <div class="chart-card-header">
              <div>图表<div class="chart-meta chart-scope">统计口径：SUM(amount)</div><div class="chart-meta chart-source">数据来源：orders / query hash abc</div></div>
              <button data-action="view-data" onclick="toggleChartData('chart-table')">查看数据</button>
            </div>
            <div id="chart" class="chart-surface"></div>
            <div id="chart-table" class="chart-data-table" hidden><div class="table-scroll"><table><tr><th>维度</th><th>值</th></tr><tr><td>A</td><td>1</td></tr></table></div></div>
          </section>
        </main>
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
          function toggleChartData(id) {{
            var el = document.getElementById(id);
            if (el) {{ el.hidden = !el.hidden; el.classList.toggle('is-open', !el.hidden); }}
          }}
          class DashboardController {{
            downloadChart() {{}}
          }}
          var chart = echarts.init(document.getElementById('chart'));
          chart.setOption({{series:[{{type:'bar',data:[1]}}]}});
          {body}
        </script>
      </body>
    </html>
    """


def test_validate_rejects_runtime_external_loader(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("var s=document.createElement('script');s.src='https://cdn.example.com/echarts.js';"))

    assert validate(str(html)) == 1


def test_validate_rejects_runtime_fetch_external_dependency(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("fetch('https://geo.example.com/china.json');"))

    assert validate(str(html)) == 1


def test_validate_rejects_invalid_window_var_assignment(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("var window.dashboardCharts = [];"))

    assert validate(str(html)) == 1


def test_validate_rejects_pdf_incompatible_css_color_functions(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("<style>.dashboard-header{background:color-mix(in srgb,#fff 94%,transparent);}</style>"))

    assert validate(str(html)) == 1


def test_validate_rejects_iframe_file_self_load(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html('<iframe src="file:///tmp/dashboard.html"></iframe>'))

    assert validate(str(html)) == 1


def test_validate_rejects_runtime_location_navigation(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("window.location = 'file:///tmp/dashboard.html';"))

    assert validate(str(html)) == 1


def test_validate_rejects_dynamic_iframe_creation(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("const frame = document.createElement('iframe'); document.body.appendChild(frame);"))

    assert validate(str(html)) == 1


def test_validate_rejects_custom_script_syntax_error(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("function broken(){ return ); }"))

    assert validate(str(html)) == 1


def test_validate_rejects_raw_page_stack_as_dashboard(tmp_path: Path):
    html = tmp_path / "hotel_dashboard.html"
    html.write_text(f"""
    <html>
      <head>
        <title>Hotel Dashboard</title>
        <style>.page {{ display: flex; flex-direction: column; }}</style>
      </head>
      <body>
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <div class="page" style="display:flex;flex-direction:column;">
          <div id="chart1" class="chart-container" style="width:900px;height:500px;"></div>
          <div id="chart2" class="chart-container" style="width:900px;height:500px;"></div>
        </div>
        <script>
          var chart = echarts.init(document.getElementById('chart1'));
          chart.setOption({{series:[{{type:'bar',data:[1]}}]}});
        </script>
      </body>
    </html>
    """, encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_accepts_standard_dashboard_with_multiple_chart_containers(tmp_path: Path):
    html = tmp_path / "enterprise_dashboard.html"
    html.write_text(_dashboard_html("""
      document.querySelector('.dashboard-grid').insertAdjacentHTML('beforeend',
        `<section class="chart-card">
           <div class="chart-card-header">
             <div>辅助图表<div class="chart-meta chart-scope">统计口径：COUNT(*)</div><div class="chart-meta chart-source">数据来源：orders / query hash def</div></div>
             <button data-action="view-data" onclick="toggleChartData('chart2-table')">查看数据</button>
           </div>
           <div id="chart2" class="chart-container chart-surface"></div>
           <div id="chart2-table" class="chart-data-table" hidden><div class="table-scroll"><table><tr><th>月份</th><th>值</th></tr><tr><td>1月</td><td>1</td></tr></table></div></div>
         </section>`);
      const chart2 = echarts.init(document.getElementById('chart2'));
      chart2.setOption({series:[{type:'line',data:[1,2,3]}]});
    """), encoding="utf-8")

    assert validate(str(html)) == 0


def test_validate_rejects_chart_card_without_data_button_and_table(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    broken = _dashboard_html("""
      document.querySelector('[data-action="view-data"]').remove();
      document.querySelector('.chart-data-table').remove();
    """)
    html.write_text(
        broken
        .replace('<button data-action="view-data" onclick="toggleChartData(\'chart-table\')">查看数据</button>', '')
        .replace('<div id="chart-table" class="chart-data-table" hidden><div class="table-scroll"><table><tr><th>维度</th><th>值</th></tr><tr><td>A</td><td>1</td></tr></table></div></div>', ''),
        encoding="utf-8",
    )

    assert validate(str(html)) == 1


def test_validate_rejects_chart_card_without_scope_and_source(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(
        _dashboard_html("")
        .replace('<div class="chart-meta chart-scope">统计口径：SUM(amount)</div>', '')
        .replace('<div class="chart-meta chart-source">数据来源：orders / query hash abc</div>', ''),
        encoding="utf-8",
    )

    assert validate(str(html)) == 1


def test_validate_rejects_large_handwritten_data_object(tmp_path: Path):
    html = tmp_path / "analysis_dashboard.html"
    handwritten = "{items:[" + ",".join("{name:'A',value:1}" for _ in range(80)) + "]}"
    html.write_text(_dashboard_html(f"""
      const DATA = {handwritten};
      const chart2 = echarts.init(document.getElementById('chart'));
      chart2.setOption({{series:[{{type:'line',data:DATA.items.map(x=>x.value)}}]}});
    """), encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_narrow_fixed_dashboard_shell(tmp_path: Path):
    html = tmp_path / "narrow_dashboard.html"
    html.write_text(_dashboard_html("""
      const style = document.createElement('style');
      style.textContent = '.dashboard-container{max-width:720px;}';
      document.head.appendChild(style);
    """), encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_single_column_flex_chart_stack(tmp_path: Path):
    html = tmp_path / "stacked_dashboard.html"
    html.write_text(f"""
    <html>
      <head>
        <style>
          .dashboard-container{{width:min(100%,1440px);margin:0 auto;}}
          .dashboard-header{{}}
          .dashboard-toolbar{{}}
          .kpi-card{{}}
          .dashboard-grid{{display:flex;flex-direction:column;gap:12px;}}
          .chart-card{{min-height:360px;}}
          .chart-card-header{{}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <header class="dashboard-header">Header</header>
        <section class="kpi-card">KPI</section>
        <main class="dashboard-grid">
          <section class="chart-card"><div class="chart-card-header">A</div><div id="chart1"></div></section>
          <section class="chart-card"><div class="chart-card-header">B</div><div id="chart2"></div></section>
          <section class="chart-card"><div class="chart-card-header">C</div><div id="chart3"></div></section>
        </main>
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
          class DashboardController {{ downloadChart() {{}} }}
          ['chart1','chart2','chart3'].forEach(id => {{
            const chart = echarts.init(document.getElementById(id));
            chart.setOption({{series:[{{type:'bar',data:[1]}}]}});
          }});
        </script>
      </body>
    </html>
    """, encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_long_table_without_scroll_wrapper(tmp_path: Path):
    html = tmp_path / "table_dashboard.html"
    rows = "".join(f"<tr><td>集团{i}</td><td>{i}</td></tr>" for i in range(24))
    html.write_text(_dashboard_html(f"""
      document.querySelector('.dashboard-grid').insertAdjacentHTML('beforeend',
        `<section class="chart-card"><div class="chart-card-header">明细表</div><table>{rows}</table></section>`);
    """), encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_dense_time_series_card_without_wide_span(tmp_path: Path):
    html = tmp_path / "forecast_dashboard.html"
    html.write_text(f"""
    <html>
      <head>
        <style>
          .dashboard-container{{width:min(100%,1440px);margin:0 auto;}}
          .dashboard-header{{}}
          .dashboard-toolbar{{}}
          .kpi-card{{min-width:0;overflow-wrap:anywhere;}}
          .dashboard-grid{{display:grid;grid-template-columns:repeat(2,minmax(420px,1fr));gap:18px;}}
          .chart-card{{min-height:360px;}}
          .chart-card-header{{min-width:0;overflow-wrap:anywhere;}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <header class="dashboard-header">锦江集团 2026年间夜&GMV预测</header>
        <section class="kpi-card">2026全年预测间夜 2165</section>
        <main class="dashboard-grid">
          <section class="chart-card"><div class="chart-card-header">间夜量预测（含80%置信区间）</div><div id="chart1"></div></section>
          <section class="chart-card"><div class="chart-card-header">GMV预测</div><div id="chart2"></div></section>
          <section class="chart-card"><div class="chart-card-header">年度对比</div><div id="chart3"></div></section>
          <section class="chart-card"><div class="chart-card-header">月度季节指数</div><div id="chart4"></div></section>
        </main>
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
          class DashboardController {{ downloadChart() {{}} }}
          ['chart1','chart2','chart3','chart4'].forEach(id => {{
            const chart = echarts.init(document.getElementById(id));
            chart.setOption({{series:[{{type:'bar',data:[1,2,3,4,5,6,7,8,9,10,11,12]}}]}});
          }});
        </script>
      </body>
    </html>
    """, encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_wide_class_without_grid_column_rule(tmp_path: Path):
    html = tmp_path / "fake_wide_dashboard.html"
    html.write_text(f"""
    <html>
      <head>
        <style>
          .dashboard-container{{width:min(100%,1440px);margin:0 auto;}}
          .dashboard-header{{}}
          .dashboard-toolbar{{}}
          .kpi-card{{min-width:0;overflow-wrap:anywhere;}}
          .dashboard-grid{{display:grid;grid-template-columns:repeat(2,minmax(420px,1fr));gap:18px;}}
          .chart-card{{min-height:360px;}}
          .chart-card--wide{{min-height:420px;}}
          .chart-card-header{{min-width:0;overflow-wrap:anywhere;}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <header class="dashboard-header">锦江集团 2026年间夜&GMV预测</header>
        <section class="kpi-card">2026全年预测间夜 2165</section>
        <main class="dashboard-grid">
          <section class="chart-card chart-card--wide">
            <div class="chart-card-header">间夜量预测（含80%置信区间）</div>
            <div id="chart1"></div>
          </section>
          <section class="chart-card">
            <div class="chart-card-header">月度季节指数</div>
            <div id="chart2"></div>
          </section>
        </main>
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
          class DashboardController {{ downloadChart() {{}} }}
          ['chart1','chart2'].forEach(id => {{
            const chart = echarts.init(document.getElementById(id));
            chart.setOption({{series:[{{type:'bar',data:[1,2,3,4,5,6,7,8,9,10,11,12]}}]}});
          }});
        </script>
      </body>
    </html>
    """, encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_pseudo_full_row_grid_with_single_card(tmp_path: Path):
    html = tmp_path / "pseudo_full_dashboard.html"
    html.write_text(f"""
    <html>
      <head>
        <style>
          .dashboard-container{{width:min(100%,1440px);margin:0 auto;}}
          .dashboard-header{{}}
          .dashboard-toolbar{{}}
          .kpi-card{{min-width:0;overflow-wrap:anywhere;}}
          .dashboard-grid{{display:grid;grid-template-columns:repeat(2,minmax(420px,1fr));gap:18px;}}
          .row{{display:grid;grid-template-columns:1fr 1fr;gap:12px;}}
          .full{{grid-column:1/-1;}}
          .chart-card{{min-height:360px;}}
          .chart-card--wide{{grid-column:span 2;}}
          .chart-card-header{{min-width:0;overflow-wrap:anywhere;}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <header class="dashboard-header">如家集团 订单分析</header>
        <section class="kpi-card">2026 YoY -63%</section>
        <main class="dashboard-grid">
          <section class="row full">
            <div class="chart-card">
              <div class="chart-card-header">月度间夜趋势 (2024-2026)</div>
              <div id="chart1"></div>
            </div>
          </section>
          <section class="chart-card chart-card--wide">
            <div class="chart-card-header">年度间夜&GMV对比</div>
            <div id="chart2"></div>
          </section>
        </main>
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
          class DashboardController {{ downloadChart() {{}} }}
          ['chart1','chart2'].forEach(id => {{
            const chart = echarts.init(document.getElementById(id));
            chart.setOption({{series:[{{type:'bar',data:[1,2,3]}}]}});
          }});
        </script>
      </body>
    </html>
    """, encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_odd_half_width_dashboard_card_grid(tmp_path: Path):
    html = tmp_path / "orphan_half_width_dashboard.html"
    html.write_text(f"""
    <html>
      <head>
        <style>
          .dashboard-container{{width:min(100%,1440px);margin:0 auto;}}
          .dashboard-header{{}}
          .dashboard-toolbar{{}}
          .kpi-card{{min-width:0;overflow-wrap:anywhere;}}
          .dashboard-grid{{display:grid;grid-template-columns:repeat(2,minmax(420px,1fr));gap:18px;}}
          .chart-card{{min-height:360px;}}
          .chart-card--wide{{grid-column:span 2;}}
          .chart-card-header{{min-width:0;overflow-wrap:anywhere;}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <header class="dashboard-header">北京西单美爵酒店 × 金融街商圈竞争分析</header>
        <section class="kpi-card">H1 YoY -75%</section>
        <main class="dashboard-grid">
          <section class="chart-card"><div class="chart-card-header">需求方变化 H1</div><div id="chart1"></div></section>
          <section class="chart-card"><div class="chart-card-header">商圈三年对比</div><div id="chart2"></div></section>
          <section class="chart-card"><div class="chart-card-header">酒店间夜排名</div><div id="chart3"></div></section>
          <section class="chart-card"><div class="chart-card-header">商圈集团渠道分布</div><div id="chart4"></div></section>
          <section class="chart-card"><div class="chart-card-header">商圈变动明细</div><div id="chart5"></div></section>
        </main>
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
          class DashboardController {{ downloadChart() {{}} }}
          ['chart1','chart2','chart3','chart4','chart5'].forEach(id => {{
            const chart = echarts.init(document.getElementById(id));
            chart.setOption({{series:[{{type:'bar',data:[1,2,3]}}]}});
          }});
        </script>
      </body>
    </html>
    """, encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_first_chart_card_half_width_in_multi_chart_dashboard(tmp_path: Path):
    html = tmp_path / "first_card_half_width_dashboard.html"
    html.write_text(f"""
    <html>
      <head>
        <style>
          .dashboard-container{{width:min(100%,1440px);margin:0 auto;}}
          .dashboard-header{{}}
          .dashboard-toolbar{{}}
          .kpi-card{{min-width:0;overflow-wrap:anywhere;}}
          .dashboard-grid{{display:grid;grid-template-columns:repeat(2,minmax(420px,1fr));gap:18px;}}
          .chart-card{{min-height:360px;}}
          .chart-card--wide{{grid-column:span 2;}}
          .chart-card-header{{min-width:0;overflow-wrap:anywhere;}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <header class="dashboard-header">北京西单美爵酒店 × 金融街商圈竞争分析</header>
        <section class="kpi-card">H1 YoY -75%</section>
        <main class="dashboard-grid">
          <section class="chart-card"><div class="chart-card-header">需求方变化 H1</div><div id="chart1"></div></section>
          <section class="chart-card"><div class="chart-card-header">商圈三年对比</div><div id="chart2"></div></section>
          <section class="chart-card"><div class="chart-card-header">酒店间夜排名</div><div id="chart3"></div></section>
          <section class="chart-card"><div class="chart-card-header">商圈集团渠道分布</div><div id="chart4"></div></section>
        </main>
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
          class DashboardController {{ downloadChart() {{}} }}
          ['chart1','chart2','chart3','chart4'].forEach(id => {{
            const chart = echarts.init(document.getElementById(id));
            chart.setOption({{series:[{{type:'bar',data:[1,2,3]}}]}});
          }});
        </script>
      </body>
    </html>
    """, encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_kpi_cards_without_wrap_strategy(tmp_path: Path):
    html = tmp_path / "kpi_wrap_dashboard.html"
    html.write_text(_dashboard_html("""
      const style = document.createElement('style');
      style.textContent = '.kpi-card{white-space:nowrap;}';
      document.head.appendChild(style);
    """), encoding="utf-8")

    assert validate(str(html)) == 1


def test_validate_rejects_card_headers_without_wrap_strategy(tmp_path: Path):
    html = tmp_path / "header_wrap_dashboard.html"
    html.write_text(_dashboard_html("""
      const style = document.createElement('style');
      style.textContent = '.chart-card-header{white-space:nowrap;}';
      document.head.appendChild(style);
    """), encoding="utf-8")

    assert validate(str(html)) == 1


def _chart_html(library_close_tag: str) -> str:
    """Single-chart HTML where the inlined library uses the given closing tag."""
    return f"""<!DOCTYPE html>
    <html><head><meta charset="utf-8"></head>
    <body>
      <div class="header"><h1>标题</h1></div>
      <section class="chart-panel">
        <div class="chart-head">
          <div><div class="chart-scope">统计口径：COUNT(*)</div><div class="chart-source">数据来源：orders / query hash abc</div></div>
          <button data-action="view-data" onclick="toggleChartData('chart-table')">查看数据</button>
        </div>
        <div id="chart" style="height:300px"></div>
        <div id="chart-table" class="chart-data-table" hidden><table><tr><td>A</td><td>1</td></tr></table></div>
      </section>
      <script>{FAKE_ECHARTS_LIBRARY}{library_close_tag}
      <script>
        function toggleChartData(id) {{ var el = document.getElementById(id); if (el) el.hidden = !el.hidden; }}
        var chart = echarts.init(document.getElementById('chart'));
        chart.setOption({{series:[{{type:'bar',data:[1,2,3]}}]}});
      </script>
    </body></html>
    """


def test_validate_rejects_escaped_script_close_tag_blank_page(tmp_path: Path):
    # The classic blank-page bug: inlined library closed with an escaped
    # <\/script> tag the browser never recognizes → whole page renders blank.
    html = tmp_path / "chart.html"
    html.write_text(_chart_html("<\\/script>"))

    assert validate(str(html)) == 1


def test_validate_accepts_literal_script_close_tag(tmp_path: Path):
    # Same page with a correct literal </script> must pass.
    html = tmp_path / "chart.html"
    html.write_text(_chart_html("</script>"))

    assert validate(str(html)) == 0


def test_validate_accepts_escaped_script_close_inside_js_string(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("""
      const vendorTemplate = '<\\/script>';
      document.querySelector('.chart-card').classList.add('loading');
      const stateStyle = document.createElement('style');
      stateStyle.textContent = '.chart-card.loading .chart-card-body::after{width:40px;height:40px;}';
      document.head.appendChild(stateStyle);
    """), encoding="utf-8")

    assert validate(str(html)) == 0


def test_validate_rejects_unbalanced_script_tags(tmp_path: Path):
    # Missing closing </script> for the library block (unterminated) → blank page.
    html = tmp_path / "chart.html"
    html.write_text(_chart_html(""))

    assert validate(str(html)) == 1



def test_validate_rejects_html2canvas_export_without_ignore_elements(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("""
      class ExportController extends DashboardController {
        async exportDashboard() {
          try {
            const canvas = await html2canvas(document.body, { scale: 2 });
            const pdf = new window.jspdf.jsPDF('l', 'mm', 'a4');
            pdf.save('dashboard.pdf');
          } catch (error) {
            window.print();
          }
        }
      }
    """))

    assert validate(str(html)) == 1


def test_validate_rejects_direct_new_jspdf_without_namespace_fallback(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("""
      class ExportController extends DashboardController {
        async exportDashboard() {
          try {
            const canvas = await html2canvas(document.body, {
              scale: 2,
              ignoreElements: function () { return false; }
            });
            const pdf = new jsPDF('l', 'mm', 'a4');
            pdf.save('dashboard.pdf');
          } catch (error) {
            window.print();
          }
        }
      }
    """))

    assert validate(str(html)) == 1


def test_validate_rejects_chart_bootstrap_before_echarts_library(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    fake_echarts_library = "/* Apache Software Foundation */ var echarts = {};" + ("/* echarts filler */" * 8000)
    html.write_text(f"""
    <html>
      <head>
        <style>
          .dashboard-container{{}}
          .dashboard-header{{}}
          .dashboard-toolbar{{}}
          .chart-card{{}}
          .chart-card-header{{}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <script>
          window.dashboardCharts = [];
          var chart = echarts.init(document.getElementById('chart'));
          chart.setOption({{series:[{{type:'bar',data:[1]}}]}});
        </script>
        <script>{fake_echarts_library}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
          class DashboardController {{ downloadChart() {{}} }}
        </script>
      </body>
    </html>
    """)

    assert validate(str(html)) == 1


def test_validate_rejects_missing_inlined_echarts_library(tmp_path: Path):
    html = tmp_path / "chart.html"
    html.write_text("""
    <html>
      <body>
        <div id="chart"></div>
        <script>
          var chart = echarts.init(document.getElementById('chart'));
          chart.setOption({series:[{type:'bar',data:[1]}]});
        </script>
      </body>
    </html>
    """)

    assert validate(str(html)) == 1


def test_validate_rejects_echarts_cdn_script(tmp_path: Path):
    html = tmp_path / "chart.html"
    html.write_text("""
    <html>
      <body>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <div id="chart"></div>
        <script>
          var chart = echarts.init(document.getElementById('chart'));
          chart.setOption({series:[{type:'bar',data:[1]}]});
        </script>
      </body>
    </html>
    """)

    assert validate(str(html)) == 1


def test_validate_rejects_unclosed_echarts_linear_gradient(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("""
      var option = {
        series: [{
          type: 'line',
          data: [1, 2, 3],
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(56,239,125,0.3)' },
              { offset: 1, color: 'rgba(56,239,125,0)' }
            ] }
          }
        }]
      };
    """))

    assert validate(str(html)) == 1


def test_validate_rejects_raw_newline_inside_formatter_string(tmp_path: Path):
    html = tmp_path / "dashboard.html"
    html.write_text(_dashboard_html("""
      var option = {
        series: [{
          type: 'pie',
          data: [1],
          label: { formatter: '{b}
{d}%' }
        }]
      };
    """))

    assert validate(str(html)) == 1
