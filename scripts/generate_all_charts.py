"""
Generate all charts using TEMPLATES — proven ECharts option structures.
Reads template comment header for data format, fills {{PLACEHOLDER}} markers.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.build_template import build

TEMPLATES = os.path.abspath("references/templates")
OUT = os.path.abspath("examples/all_charts_v3")
os.makedirs(OUT, exist_ok=True)

CHARTS = []

def add(name, tpl, data):
    CHARTS.append((name, tpl, data))

# ═══ Bar (5) ═══
add("01_Bar_Basic", "bar/basic.html", {
    "TITLE": "01 基础柱状图",
    "CATEGORIES": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    "VALUES": [120, 200, 150, 80, 70, 110, 130], "ROTATE": 0,
})
add("02_Bar_Horizontal", "bar/horizontal.html", {
    "TITLE": "02 横向柱状图",
    "CATEGORIES": ["巴西","印尼","美国","印度","中国"],
    "VALUES": [18203, 23490, 29034, 104970, 131744], "ROTATE": 0,
})
add("03_Bar_Stacked", "bar/stack.html", {
    "TITLE": "03 堆叠柱状图",
    "CATEGORIES": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    "SERIES": [
        {"name":"Email","stack":"x","data":[120,132,101,134,90,230,210]},
        {"name":"Union Ads","stack":"x","data":[220,182,191,234,290,330,310]},
        {"name":"Video Ads","stack":"x","data":[150,232,201,154,190,330,410]},
    ],
})
add("04_Bar_Waterfall", "bar/waterfall.html", {
    "TITLE": "04 瀑布图",
    "CATEGORIES": ["启动","研发","营销","运维","销售","利润","结算"],
    "VALUES": [120, 200, 150, 80, -110, -60, 260],
})
add("05_Bar_Race", "bar/race.html", {
    "TITLE": "05 动态排序柱状图",
    "DATA_JSON": json.dumps({
        "2020":[["中国",14.7],["美国",21.4],["日本",5.1],["德国",3.8],["英国",2.7]],
        "2021":[["中国",17.7],["美国",23.3],["日本",4.9],["德国",4.2],["英国",3.2]],
        "2022":[["中国",18.0],["美国",25.5],["日本",4.2],["德国",4.1],["英国",3.1]],
        "2023":[["中国",17.9],["美国",27.4],["日本",4.2],["德国",4.5],["英国",3.3]],
    }),
})

# ═══ Line (3) ═══
add("06_Line_Basic", "line/basic.html", {
    "TITLE": "06 基础折线图",
    "CATEGORIES": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    "VALUES": [820,932,901,1290,1330,1420,1560,1480,1620,1720,1680,1890],
})
add("07_Line_Stacked", "line/stack.html", {
    "TITLE": "07 堆叠折线图",
    "CATEGORIES": ["Jan","Feb","Mar","Apr","May","Jun"],
    "SERIES": [
        {"name":"Email","stack":"x","data":[120,132,101,134,90,230]},
        {"name":"Union Ads","stack":"x","data":[220,182,191,234,290,330]},
        {"name":"Video Ads","stack":"x","data":[150,232,201,154,190,330]},
    ],
})
add("08_Line_XY", "line/xy.html", {
    "TITLE": "08 XY 折线图",
    "DATA": [[10,8.04],[8,6.95],[13,7.58],[9,8.81],[11,8.33],[14,9.96],[6,7.24],[4,4.26],[12,10.84],[7,4.82],[5,5.68]],
})

# ═══ Pie (2) ═══
add("09_Pie_Basic", "pie/basic.html", {
    "TITLE": "09 基础饼图",
    "DATA": [{"name":"搜索","value":1048},{"name":"直接","value":735},{"name":"邮件","value":580},{"name":"联盟","value":484},{"name":"视频","value":300}],
})
add("38_Pie_Rose", "pie/basic.html", {
    "TITLE": "38 玫瑰图",
    "DATA": [{"name":"A","value":40},{"name":"B","value":38},{"name":"C","value":32},{"name":"D","value":30},{"name":"E","value":28},{"name":"F","value":26},{"name":"G","value":22},{"name":"H","value":18}],
    "ROSE_TYPE": "area",
})

# ═══ Scatter (4) ═══
add("10_Scatter_Basic", "scatter/basic.html", {
    "TITLE": "10 基础散点图",
    "DATA": [[10,8.04],[8,6.95],[13,7.58],[9,8.81],[11,8.33],[14,9.96],[6,7.24],[4,4.26],[12,10.84],[7,4.82],[5,5.68]],
})
add("11_Scatter_Bubble", "scatter/bubble.html", {
    "TITLE": "11 气泡散点图",
    "DATA": [[28604,77,17096869],[31163,77.4,27662440],[1516,68,1154605773],[13670,74.7,10582082],[28599,75,4986705],[29476,77.1,56943299],[31476,75.4,78958237],[28666,78.1,254830],[12124,72.6,15770000],[11173,72.8,31570000]],
})
add("12_Scatter_Geo", "scatter/geo.html", {
    "TITLE": "12 地理散点图",
    "DATA": json.dumps([{"name":"北京","value":[116.46,39.92,100]},{"name":"上海","value":[121.48,31.22,95]},{"name":"广州","value":[113.23,23.16,80]},{"name":"深圳","value":[114.07,22.62,90]},{"name":"成都","value":[104.06,30.67,70]}]),
})
add("30_EffectScatter", "effectScatter/basic.html", {
    "TITLE": "30 涟漪散点图",
    "DATA": [[20,50,"北京"],[30,80,"上海"],[50,40,"广州"],[70,70,"深圳"],[60,30,"成都"],[80,60,"杭州"]],
})

# ═══ Map ═══
add("13_Map_China", "map/basic.html", {
    "TITLE": "13 中国地图",
    "DATA": [{"name":"广东","value":38072},{"name":"北京","value":26593},{"name":"上海","value":21073},{"name":"江苏","value":18296},{"name":"浙江","value":16976},{"name":"山东","value":14386},{"name":"四川","value":12852},{"name":"福建","value":12359},{"name":"湖北","value":10388},{"name":"湖南","value":9026},{"name":"安徽","value":8104},{"name":"河南","value":7328},{"name":"河北","value":6398},{"name":"辽宁","value":5384},{"name":"重庆","value":4314},{"name":"陕西","value":3284},{"name":"云南","value":2744},{"name":"贵州","value":2183},{"name":"广西","value":1653},{"name":"山西","value":1280},{"name":"吉林","value":982},{"name":"黑龙江","value":936},{"name":"新疆","value":760},{"name":"内蒙古","value":658},{"name":"甘肃","value":432},{"name":"海南","value":320},{"name":"宁夏","value":218},{"name":"青海","value":156},{"name":"西藏","value":98}],
})

# ═══ Radar ═══
add("14_Radar_Basic", "radar/basic.html", {
    "TITLE": "14 雷达图",
    "INDICATORS": json.dumps([{"name":"预算","max":5000},{"name":"支出","max":15000},{"name":"销售","max":30000},{"name":"利润","max":40000}]),
    "SERIES_DATA": json.dumps([{"name":"预算","value":[4200,3000,20000,35000]},{"name":"实际","value":[5000,14000,28000,26000]}]),
})

# ═══ Gauge / Funnel / Heatmap / Candlestick ═══
add("15_Gauge", "gauge/basic.html", {"TITLE": "15 仪表盘", "VALUE": 78.5, "NAME": "完成率"})
add("16_Funnel", "funnel/basic.html", {
    "TITLE": "16 漏斗图",
    "DATA": [{"name":"访问","value":10000},{"name":"注册","value":6500},{"name":"激活","value":4200},{"name":"下单","value":2800},{"name":"支付","value":1800}],
})
add("17_Heatmap", "heatmap/basic.html", {
    "TITLE": "17 热力图",
    "X_LABELS": json.dumps(["Mon","Tue","Wed","Thu","Fri"]),
    "Y_LABELS": json.dumps(["0h","2h","4h","6h","8h","10h","12h","14h","16h","18h","20h","22h"]),
    "DATA": [[0,0,5],[0,1,10],[0,2,8],[0,3,0],[0,4,3],[0,5,1],[0,6,0],[0,7,0],[0,8,5],[0,9,12],[0,10,18],[0,11,15],[1,0,3],[1,1,8],[1,2,6],[1,3,2],[1,4,0],[1,5,0],[1,6,0],[1,7,2],[1,8,8],[1,9,15],[1,10,22],[1,11,18],[2,0,2],[2,1,5],[2,2,4],[2,3,0],[2,4,0],[2,5,0],[2,6,1],[2,7,4],[2,8,10],[2,9,18],[2,10,25],[2,11,20],[3,0,0],[3,1,3],[3,2,2],[3,3,0],[3,4,0],[3,5,1],[3,6,3],[3,7,6],[3,8,12],[3,9,20],[3,10,28],[3,11,22],[4,0,0],[4,1,2],[4,2,0],[4,3,0],[4,4,2],[4,5,3],[4,6,5],[4,7,8],[4,8,14],[4,9,22],[4,10,30],[4,11,25]],
})
add("18_Candlestick", "candlestick/basic.html", {
    "TITLE": "18 K线图",
    "CATEGORIES": json.dumps(["1日","2日","3日","4日","5日","6日","7日"]),
    "DATA": [[20,34,10,38],[40,35,30,50],[31,38,33,44],[38,15,5,42],[11,35,8,35],[29,43,20,49],[41,26,18,42]],
})

# ═══ Treemap / Sunburst ═══
add("19_Treemap", "treemap/basic.html", {
    "TITLE": "19 矩形树图",
    "DATA": json.dumps([{"name":"电子","children":[{"name":"手机","value":6000},{"name":"电脑","value":4000},{"name":"平板","value":2000}]},{"name":"家居","children":[{"name":"家具","value":3000},{"name":"灯具","value":2000},{"name":"园艺","value":1000}]}]),
})
add("20_Sunburst", "sunburst/basic.html", {
    "TITLE": "20 旭日图",
    "DATA": json.dumps([{"name":"A","itemStyle":{"color":"#5470c6"},"children":[{"name":"A1","value":25},{"name":"A2","value":15}]},{"name":"B","itemStyle":{"color":"#91cc75"},"children":[{"name":"B1","value":20},{"name":"B2","value":10}]},{"name":"C","itemStyle":{"color":"#fac858"},"children":[{"name":"C1","value":20},{"name":"C2","value":10}]}]),
})

# ═══ Sankey / Graph / Tree ═══
add("21_Sankey", "sankey/basic.html", {
    "TITLE": "21 桑基图",
    "DATA": json.dumps({"nodes":[{"name":"首页"},{"name":"搜索"},{"name":"推荐"},{"name":"分类"},{"name":"详情"},{"name":"下单"},{"name":"收藏"}],"links":[{"source":"首页","target":"搜索","value":40},{"source":"首页","target":"推荐","value":30},{"source":"首页","target":"分类","value":20},{"source":"搜索","target":"详情","value":25},{"source":"推荐","target":"详情","value":20},{"source":"分类","target":"详情","value":15},{"source":"详情","target":"下单","value":40},{"source":"详情","target":"收藏","value":15}]}),
})
add("22_Graph_Force", "graph/force.html", {
    "TITLE": "22 力导向图",
    "DATA": json.dumps({"nodes":[{"name":"A","category":0},{"name":"B","category":0},{"name":"C","category":1},{"name":"D","category":1},{"name":"E","category":2}],"links":[{"source":"A","target":"B"},{"source":"A","target":"C"},{"source":"B","target":"D"},{"source":"C","target":"D"},{"source":"C","target":"E"},{"source":"D","target":"E"}]}),
})
add("23_Tree", "tree/basic.html", {
    "TITLE": "23 树图",
    "DATA": json.dumps({"name":"CEO","children":[{"name":"CTO","children":[{"name":"工程师A"},{"name":"工程师B"}]},{"name":"CFO","children":[{"name":"会计A"}]}]}),
})

# ═══ Boxplot / Parallel / Calendar ═══
add("24_Boxplot", "boxplot/basic.html", {
    "TITLE": "24 箱线图",
    "DATA": json.dumps([["A",850,740,900,1070,930,850,950,980,980,880,1000,980],["B",960,940,960,940,880,800,850,880,900,840,830,880]]),
})
add("25_Parallel", "parallel/basic.html", {
    "TITLE": "25 平行坐标",
    "DATA": json.dumps([[55,85,78,90,65,"A"],[70,80,82,95,72,"B"],[60,75,68,85,58,"C"],[80,90,88,92,78,"D"],[45,65,55,70,48,"E"]]),
})
add("26_Calendar", "calendar/heatmap.html", {
    "TITLE": "26 日历热力图",
    "YEAR": "2024",
    "DATA": json.dumps([["2024-01-05",120],["2024-02-03",200],["2024-03-10",90],["2024-04-07",220],["2024-05-05",160],["2024-06-12",130],["2024-07-08",170],["2024-08-15",210],["2024-09-05",175],["2024-10-10",155],["2024-11-08",125],["2024-12-05",165]]),
})

# ═══ ThemeRiver / PictorialBar / Chord ═══
add("27_ThemeRiver", "themeRiver/basic.html", {
    "TITLE": "27 主题河流图",
    "DATA": json.dumps([["2015/11/08",10,"Evolution"],["2015/11/09",15,"Evolution"],["2015/11/10",35,"Evolution"],["2015/11/08",10,"Natural"],["2015/11/09",15,"Natural"],["2015/11/10",25,"Natural"],["2015/11/08",10,"Deep"],["2015/11/09",20,"Deep"],["2015/11/10",30,"Deep"]]),
})
add("28_PictorialBar", "pictorialBar/basic.html", {
    "TITLE": "28 象形柱图",
    "DATA": [{"name":"大象","value":6500},{"name":"犀牛","value":3500},{"name":"河马","value":3000},{"name":"水牛","value":2000},{"name":"长颈鹿","value":1800}],
})
add("29_Chord", "chord/basic.html", {
    "TITLE": "29 和弦图",
    "DATA": json.dumps([["北京","上海",95],["北京","广州",60],["北京","深圳",45],["上海","广州",80],["上海","深圳",55],["广州","深圳",70],["北京","成都",35]]),
})

# ═══ Lines / Mix ═══
add("31_Lines_Flights", "lines/flights.html", {
    "TITLE": "31 航班线路图",
    "DATA": json.dumps([{"fromName":"北京","toName":"上海","coords":[[116.46,39.92],[121.48,31.22]]},{"fromName":"北京","toName":"广州","coords":[[116.46,39.92],[113.23,23.16]]},{"fromName":"上海","toName":"深圳","coords":[[121.48,31.22],[114.07,22.62]]}]),
})
add("32_Mix_Line_Bar", "mix/line-bar.html", {
    "TITLE": "32 混合图表",
    "CATEGORIES": json.dumps(["Jan","Feb","Mar","Apr","May","Jun"]),
    "BAR_DATA": [320,332,301,334,390,330],
    "LINE_DATA": [220,182,191,234,290,310],
})
add("41_Mix_Timeline", "mix/timeline.html", {
    "TITLE": "41 时间轴",
    "DATA": json.dumps({"2020":[["A",120],["B",90],["C",70]],"2021":[["A",145],["B",110],["C",85]],"2022":[["A",170],["B",130],["C",100]]}),
})

# ═══ 3D (5) ═══
add("33_3D_Bar", "3d/bar3d.html", {
    "TITLE": "33 3D柱状图",
    "DATA": json.dumps([["A","Q1",120],["A","Q2",200],["A","Q3",150],["A","Q4",180],["B","Q1",90],["B","Q2",130],["B","Q3",110],["B","Q4",100],["C","Q1",160],["C","Q2",220],["C","Q3",190],["C","Q4",210]]),
})
add("34_3D_Scatter", "3d/scatter3d.html", {
    "TITLE": "34 3D散点图",
    "DATA": json.dumps([[10,20,30],[20,10,40],[30,30,20],[15,25,35],[25,15,25]]),
})
add("35_3D_Surface", "3d/surface.html", {
    "TITLE": "35 3D曲面图",
    "DATA": json.dumps({"equation":"sin(x) * cos(y)"}),
})
add("36_3D_Globe", "3d/globe.html", {
    "TITLE": "36 3D地球",
    "DATA": json.dumps([["北京",39.9,116.4,100],["上海",31.2,121.5,95],["纽约",40.7,-74.0,200],["伦敦",51.5,-0.1,150],["东京",35.7,139.7,180]]),
})
add("37_3D_Lines3D", "3d/lines3d.html", {
    "TITLE": "37 3D折线",
    "DATA": json.dumps([[1,2,3],[2,3,7],[3,5,11],[4,7,14],[5,9,18]]),
})

# ═══ Misc ═══
add("39_Custom_Error_Bar", "custom/error-bar.html", {
    "TITLE": "39 误差柱图",
    "DATA": json.dumps([["A",50,45,55],["B",65,60,72],["C",55,50,62],["D",70,65,80],["E",60,55,68]]),
})
add("40_Geo_Lines", "geo/lines.html", {
    "TITLE": "40 全国线路",
    "DATA": json.dumps([{"fromName":"北京","toName":"上海","coords":[[116.4,39.9],[121.5,31.2]]},{"fromName":"上海","toName":"广州","coords":[[121.5,31.2],[113.3,23.1]]}]),
})

# ═════════════════════════════════════════════════════════
# Generate
# ═════════════════════════════════════════════════════════
results = []
for name, tpl_rel, data in CHARTS:
    tpl_path = os.path.join(TEMPLATES, tpl_rel)
    if not os.path.exists(tpl_path):
        results.append(("⏭️", name, f"template missing: {tpl_rel}"))
        continue
    try:
        out = os.path.join(OUT, f"{name}.html")
        build(tpl_path, data, out)
        results.append(("✅", name, f"{os.path.getsize(out)} bytes"))
    except Exception as e:
        results.append(("❌", name, str(e)[:120]))

ok = sum(1 for r in results if r[0]=="✅")
sk = sum(1 for r in results if r[0]=="⏭️")
bad = sum(1 for r in results if r[0]=="❌")
print(f"\n{'='*60}")
print(f"  Results: {ok} passed, {bad} failed, {sk} skipped ({len(results)} total)")
print(f"{'='*60}")
for s,n,d in results:
    if s != "✅": print(f"  {s} {n:<35s} {d}")
with open(f"{OUT}/_summary.json","w") as f:
    json.dump([{"status":s,"name":n,"detail":d} for s,n,d in results], f, ensure_ascii=False, indent=2)
print(f"\nOutput: {OUT}")
sys.exit(0 if bad==0 else 1)
