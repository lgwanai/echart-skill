import argparse
import sqlite3
import pandas as pd
import json
import os
import io

from server import ensure_server_running

def get_baidu_ak():
    """Retrieve Baidu AK from config file or prompt user."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.txt')
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('BAIDU_AK='):
                    ak = line.strip().split('=', 1)[1]
                    if ak:
                        return ak
                        
    # If not found or empty
    print("\n" + "="*60)
    print("⚠️ 警告：使用 ECharts 地图功能需要百度地图 AK！")
    print("检测到 config.txt 中未配置 BAIDU_AK。")
    print("请前往申请：https://lbsyun.baidu.com/apiconsole/key")
    print(f"并在 {config_path} 中添加一行：BAIDU_AK=你的AK")
    print("="*60 + "\n")
    return None

def generate_echarts_html(df, config, output_path):
    """Generate an interactive HTML file using ECharts."""
    chart_type = config.get("chart_type", "bar").lower()
    x_col = config.get("x_col")
    y_col = config.get("y_col")
    title = config.get("title", f"{chart_type.capitalize()} Chart")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure data is JSON serializable
    x_data = df[x_col].tolist() if x_col in df.columns else []
    
    bmap_script = ""
    baidu_ak = ""
    
    # Handle map chart specifically
    if chart_type == 'map':
        baidu_ak = get_baidu_ak()
        if baidu_ak:
            bmap_script = f"""
            <script type="text/javascript" src="https://api.map.baidu.com/api?v=3.0&ak={baidu_ak}"></script>
            <script src="/assets/echarts/bmap.min.js"></script>
            """
        # ECharts map expects data in {name: '...', value: ...} format
        map_data = [{"name": str(row[x_col]), "value": float(row[y_col])} for _, row in df.iterrows()]
        series_data_str = json.dumps(map_data, ensure_ascii=False)
        x_data_str = "[]" # Not used for map
        y_data_str = "[]" # Not used for map
    else:
        y_data = [float(v) if pd.notnull(v) else 0 for v in df[y_col].tolist()] if y_col in df.columns else []
        x_data_str = json.dumps([str(x) for x in x_data], ensure_ascii=False)
        y_data_str = json.dumps(y_data, ensure_ascii=False)
        series_data_str = "[]"
        
        # Prepare pie data if needed
        if chart_type == 'pie':
            pie_data = [{"name": str(x), "value": y} for x, y in zip(x_data, y_data)]
            series_data_str = json.dumps(pie_data, ensure_ascii=False)
            
    # ECharts configuration template
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <!-- 使用本地离线 ECharts -->
        <script src="/assets/echarts/echarts.min.js"></script>
        {bmap_script}
        <!-- 如果是地图，引入相应的地图数据 china.js -->
        {"<script src='/assets/echarts/china.js'></script>" if chart_type == 'map' else ""}
    </head>
    <body>
        <div id="main" style="width: 100%; height: 800px;"></div>
        <script type="text/javascript">
            var myChart = echarts.init(document.getElementById('main'));
            var chartType = '{chart_type}';
            
            var option = {{
                title: {{
                    text: '{title}',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: chartType === 'pie' || chartType === 'map' ? 'item' : 'axis'
                }},
                legend: {{
                    orient: 'vertical',
                    left: 'left',
                    top: 'bottom'
                }},
                toolbox: {{
                    show: true,
                    feature: {{
                        saveAsImage: {{ show: true }}
                    }}
                }}
            }};
            
            if (chartType === 'bar' || chartType === 'line' || chartType === 'scatter') {{
                option.xAxis = {{
                    type: chartType === 'scatter' ? 'value' : 'category',
                    name: '{config.get("xlabel", "")}',
                    data: {x_data_str}
                }};
                option.yAxis = {{
                    type: 'value',
                    name: '{config.get("ylabel", "")}'
                }};
                option.series = [{{
                    data: {y_data_str},
                    type: chartType,
                    label: {{
                        show: {str(config.get("show_labels", True)).lower()},
                        position: 'top'
                    }}
                }}];
            }} else if (chartType === 'pie') {{
                option.series = [{{
                    type: 'pie',
                    radius: '50%',
                    data: {series_data_str},
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }},
                    label: {{
                        show: {str(config.get("show_labels", True)).lower()},
                        formatter: '{{b}}: {{c}} ({{d}}%)'
                    }}
                }}];
            }} else if (chartType === 'map') {{
                option.visualMap = {{
                    min: 0,
                    max: {df[y_col].max() if not df.empty and y_col in df.columns else 100},
                    left: 'left',
                    top: 'bottom',
                    text: ['高','低'],
                    calculable: true
                }};
                
                // 判断是否配置了百度地图AK
                var hasBmap = {str(bool(baidu_ak)).lower()};
                
                if (hasBmap) {{
                    option.bmap = {{
                        center: [104.114129, 37.550339], // 中国中心点
                        zoom: 5,
                        roam: true
                    }};
                    option.series = [{{
                        name: '{config.get("ylabel", y_col)}',
                        type: 'scatter', // bmap 扩展通常配合 scatter/effectScatter 使用
                        coordinateSystem: 'bmap',
                        data: {series_data_str}
                    }}];
                }} else {{
                    // 回退到普通 geojson 地图
                    option.series = [{{
                        name: '{config.get("ylabel", y_col)}',
                        type: 'map',
                        mapType: 'china',
                        roam: true,
                        label: {{
                            show: {str(config.get("show_labels", True)).lower()}
                        }},
                        data: {series_data_str}
                    }}];
                }}
            }}
            
            myChart.setOption(option);
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});
        </script>
    </body>
    </html>
    """
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with io.open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # 启动或获取本地服务
    base_url = ensure_server_running()
    
    # 计算相对路径，生成访问链接
    rel_path = os.path.relpath(output_path, base_dir)
    # Ensure forward slashes for URLs
    rel_path = rel_path.replace(os.sep, '/')
    access_url = f"{base_url}/{rel_path}"
    
    print(f"✅ 交互式 ECharts 图表已生成！")
    print(f"🌐 请点击或在浏览器打开以下链接访问: \n{access_url}")
    return output_path

def generate_chart(config):
    """
    Universal Chart Generator
    config = {
        "db_path": "workspace.db",
        "query": "SELECT category, SUM(value) as val FROM table GROUP BY category",
        "chart_type": "bar" | "pie" | "line" | "scatter" | "map",
        "x_col": "category", 
        "y_col": "val",      
        "title": "图表标题",
        "xlabel": "X轴标签",
        "ylabel": "Y轴标签",
        "output_path": "tmp/chart.html", 
        "show_labels": True 
    }
    """
    db_path = config.get("db_path", "workspace.db")
    query = config.get("query")
    
    if not query:
        raise ValueError("Missing SQL query in config")
        
    # 1. 提取数据
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("Warning: The query returned no data.")
        return None
        
    print(f"Data fetched successfully: {len(df)} rows.")
    
    output_path = config.get("output_path", "tmp/output_chart.html")
    if not output_path.endswith('.html'):
        output_path = os.path.splitext(output_path)[0] + '.html'
        
    return generate_echarts_html(df, config, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Chart Generator from SQLite")
    parser.add_argument("--config", required=True, help="JSON string or path to JSON file containing chart configuration")
    
    args = parser.parse_args()
    
    try:
        if os.path.isfile(args.config):
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = json.loads(args.config)
            
        generate_chart(config)
    except Exception as e:
        print(f"ERROR generating chart: {e}")
