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
          .dashboard-container{{}}
          .dashboard-header{{}}
          .dashboard-toolbar{{}}
          .chart-card{{}}
          .chart-card-header{{}}
          .toast-container{{}}
        </style>
      </head>
      <body class="dashboard-container">
        <script>{FAKE_ECHARTS_LIBRARY}</script>
        <script>
          window.html2canvas = function(){{}};
          window.jspdf = {{ jsPDF: function(){{}} }};
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
