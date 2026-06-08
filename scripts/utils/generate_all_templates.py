import os
import re
import json
from pathlib import Path

base_dir = Path(__file__).resolve().parents[2]
support_file = base_dir / "support.md"
template_dir = base_dir / "references" / "echarts_templates"

os.makedirs(template_dir, exist_ok=True)

with support_file.open("r", encoding="utf-8") as f:
    lines = f.readlines()

types = set()
for line in lines:
    line = line.strip()
    if not line: continue
    # Match strings like "折线图 line" or "GL 散点图 scatterGL"
    match = re.match(r'^([\u4e00-\u9fa50-9A-Z\s/]+)\s+([a-zA-Z0-9_]+)$', line)
    if match:
        chart_type = match.group(2)
        if chart_type not in ['dataset', 'dataZoom', 'graphic', 'rich']:
            types.add(chart_type)

cartesian_types = {'scatter', 'candlestick', 'boxplot', 'heatmap', 'pictorialBar', 'themeRiver', 'line', 'bar'}

generated_count = 0

for t in types:
    tmpl_path = template_dir / t / "basic.json"
    if tmpl_path.exists():
        continue
        
    tmpl_path.parent.mkdir(parents=True, exist_ok=True)
    
    option = {
        "title": {"text": "{title}", "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"bottom": 0},
        "toolbox": {"feature": {"saveAsImage": {}}}
    }
    
    if t in cartesian_types:
        option["xAxis"] = {"type": "category"}
        option["yAxis"] = {"type": "value"}
        
    if t == 'radar':
        option["radar"] = {"indicator": [{"name": "A", "max": 100}, {"name": "B", "max": 100}]}
    elif t == 'parallel':
        option["parallelAxis"] = [{"dim": 0, "name": "Dim0"}]
        option["parallel"] = {}
    elif t == 'calendar':
        option["calendar"] = {"range": "2024"}
    elif t.endswith('3D') or t.endswith('GL'):
        if t not in ['globe', 'map3D', 'map']:
            option["grid3D"] = {}
            option["xAxis3D"] = {"type": "category"}
            option["yAxis3D"] = {"type": "category"}
            option["zAxis3D"] = {"type": "value"}
            
    template_data = {
        "_meta": {"description": f"基础{t}图"},
        "echarts_option": option,
        "series_template": {
            "type": t
        }
    }
    
    with open(tmpl_path, "w", encoding="utf-8") as f:
        json.dump(template_data, f, ensure_ascii=False, indent=4)
    generated_count += 1
        
print(f"Parsed {len(types)} chart types from support.md.")
print(f"Successfully generated {generated_count} missing basic templates.")
