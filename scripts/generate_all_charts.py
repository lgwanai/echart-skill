"""
Generate all 41 chart types using templates.
Reads each template's {{PLACEHOLDER}} markers first, then fills data.
"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.build_template import build

OUT = os.path.abspath("examples/all_charts")
os.makedirs(OUT, exist_ok=True)
TPL = "references/templates"

# Each entry: (output_name, template_path, data_dict)
CHARTS = []

D = json.dumps  # shortcut

# ═══ Bar ═══
CHARTS.append(("01_Bar_Basic", "bar/basic.html", {
    "TITLE":"01 基础柱状图","CATEGORIES":D(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]),
    "VALUES":D([120,200,150,80,70,110,130]),"ROTATE":0}))

CHARTS.append(("02_Bar_Horizontal", "bar/horizontal.html", {
    "TITLE":"02 横向柱状图","CATEGORIES":D(["巴西","印尼","美国","印度","中国"]),
    "VALUES":D([18203,23490,29034,104970,131744]),"ROTATE":0}))

CHARTS.append(("03_Bar_Stacked", "bar/stack.html", {
    "TITLE":"03 堆叠柱状图","CATEGORIES":D(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]),
    "SERIES":D([{"name":"Email","stack":"x","data":[120,132,101,134,90,230,210]},
                {"name":"Union Ads","stack":"x","data":[220,182,191,234,290,330,310]},
                {"name":"Video Ads","stack":"x","data":[150,232,201,154,190,330,410]}])}))

CHARTS.append(("04_Bar_Waterfall", "bar/waterfall.html", {
    "TITLE":"04 瀑布图","CATEGORIES":D(["启动","研发","营销","运维","销售","利润","结算"]),
    "INCREASE":D([120,200,150,80,0,0,260]),"DECREASE":D([0,0,0,0,110,60,0])}))

CHARTS.append(("05_Bar_Race", "bar/race.html", {
    "TITLE":"05 动态排序","VALUES":D([120,200,150,80,70,110,130]),
    "CATEGORIES":D(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]),"MAX_DISPLAY":7,
    "SMOOTH":"false","AREA_STYLE":"false","STEP":"false"}))

# ═══ Line ═══
CHARTS.append(("06_Line_Basic", "line/basic.html", {
    "TITLE":"06 基础折线","CATEGORIES":D(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]),
    "VALUES":D([820,932,901,1290,1330,1420,1560,1480,1620,1720,1680,1890]),
    "SMOOTH":"false","AREA_STYLE":"false","STEP":"false"}))

CHARTS.append(("07_Line_Stacked", "line/stack.html", {
    "TITLE":"07 堆叠折线","CATEGORIES":D(["Jan","Feb","Mar","Apr","May","Jun"]),
    "SERIES":D([{"name":"Email","stack":"x","data":[120,132,101,134,90,230]},
                {"name":"Union Ads","stack":"x","data":[220,182,191,234,290,330]},
                {"name":"Video Ads","stack":"x","data":[150,232,201,154,190,330]}]),
    "SMOOTH":"false"}))

CHARTS.append(("08_Line_XY", "line/xy.html", {
    "TITLE":"08 XY折线","SMOOTH":"false",
    "DATA":D([[10,8.04],[8,6.95],[13,7.58],[9,8.81],[11,8.33],[14,9.96],[6,7.24],[4,4.26],[12,10.84],[7,4.82],[5,5.68]])}))

# ═══ Pie ═══
CHARTS.append(("09_Pie_Basic", "pie/basic.html", {
    "TITLE":"09 基础饼图","ROSE_TYPE":"","LABEL_SHOW":"true","RADIUS":"['40%','70%']",
    "DATA":D([{"name":"搜索","value":1048},{"name":"直接","value":735},{"name":"邮件","value":580},{"name":"联盟","value":484},{"name":"视频","value":300}])}))

CHARTS.append(("38_Pie_Rose", "pie/basic.html", {
    "TITLE":"38 玫瑰图","ROSE_TYPE":"area","LABEL_SHOW":"true","RADIUS":"['20%','80%']",
    "DATA":D([{"name":"A","value":40},{"name":"B","value":38},{"name":"C","value":32},{"name":"D","value":30},{"name":"E","value":28},{"name":"F","value":26},{"name":"G","value":22},{"name":"H","value":18}])}))

# ═══ Scatter ═══
CHARTS.append(("10_Scatter_Basic", "scatter/basic.html", {
    "TITLE":"10 基础散点","SYMBOL_SIZE":10,
    "DATA":D([[10,8.04],[8,6.95],[13,7.58],[9,8.81],[11,8.33],[14,9.96],[6,7.24],[4,4.26],[12,10.84],[7,4.82],[5,5.68]])}))

CHARTS.append(("11_Scatter_Bubble", "scatter/bubble.html", {
    "TITLE":"11 气泡散点","X_NAME":"GDP","Y_NAME":"Life","VMIN":0,"VMAX":100,
    "DATA":D([[28604,77,17096869],[31163,77.4,27662440],[1516,68,1154605773],[13670,74.7,10582082]])}))

CHARTS.append(("12_Scatter_Geo", "scatter/geo.html", {
    "TITLE":"12 地理散点","MAP_NAME":"china","MAP_INLINE":"","VMIN":0,"VMAX":100,"SIZE_SCALE":"1",
    "GEO_COORD_MAP":D({"北京":[116.46,39.92],"上海":[121.48,31.22],"广州":[113.23,23.16],"深圳":[114.07,22.62],"成都":[104.06,30.67]}),
    "DATA":D([{"name":"北京","value":100},{"name":"上海","value":95},{"name":"广州","value":80},{"name":"深圳","value":90},{"name":"成都","value":70}])}))

CHARTS.append(("30_EffectScatter", "effectScatter/basic.html", {
    "GEO_COORD_MAP":"{}",
    "TITLE":"30 涟漪散点","SIZE_SCALE":"1","MAP_NAME":"","MAP_INLINE":"",
    "DATA":D([[20,50],[30,80],[50,40],[70,70],[60,30],[80,60]])}))

# ═══ Map ═══
CHARTS.append(("13_Map_China", "map/basic.html", {
    "TITLE":"13 中国地图","MAP_NAME":"china","MAP_INLINE":"","VMIN":98,"VMAX":38072,"LABEL_SHOW":"false",
    "DATA":D([{"name":"广东","value":38072},{"name":"北京","value":26593},{"name":"上海","value":21073},{"name":"江苏","value":18296},{"name":"浙江","value":16976},{"name":"山东","value":14386},{"name":"四川","value":12852},{"name":"福建","value":12359},{"name":"湖北","value":10388}])}))

# ═══ Radar ═══
CHARTS.append(("14_Radar_Basic", "radar/basic.html", {
    "TITLE":"14 雷达图","LEGEND_NAMES":D(["预算","实际"]),"SHAPE":"polygon",
    "INDICATORS":D([{"name":"预算","max":5000},{"name":"支出","max":15000},{"name":"销售","max":30000},{"name":"利润","max":40000}]),
    "DATA":D([{"name":"预算","value":[4200,3000,20000,35000]},{"name":"实际","value":[5000,14000,28000,26000]}])}))

# ═══ Gauge ═══
CHARTS.append(("15_Gauge", "gauge/basic.html", {
    "TITLE":"15 仪表盘","VALUE":78.5,"NAME":"完成率","UNIT":"%","MIN":0,"MAX":100,
    "START_ANGLE":225,"END_ANGLE":-45,"AXIS_WIDTH":30,"LABEL_SHOW":"true","PROGRESS_SHOW":"false"}))

# ═══ Funnel ═══
CHARTS.append(("16_Funnel", "funnel/basic.html", {
    "TITLE":"16 漏斗图","SORT":"descending","MAX_VALUE":10000,"MIN_VALUE":1800,"LABEL_POS":"inside",
    "DATA":D([{"name":"访问","value":10000},{"name":"注册","value":6500},{"name":"激活","value":4200},{"name":"下单","value":2800},{"name":"支付","value":1800}])}))

# ═══ Heatmap ═══
CHARTS.append(("17_Heatmap", "heatmap/basic.html", {
    "TITLE":"17 热力图","LABEL_SHOW":"false","VMIN":0,"VMAX":30,
    "X_LABELS":D(["Mon","Tue","Wed","Thu","Fri"]),
    "Y_LABELS":D(["0h","2h","4h","6h","8h","10h","12h","14h","16h","18h","20h","22h"]),
    "DATA":D([[0,0,5],[0,1,10],[0,2,8],[0,3,7],[0,4,12],[0,5,15],[0,6,10],[0,7,8],[0,8,5],[0,9,12],[0,10,18],[0,11,15]])}))

# ═══ Candlestick ═══
CHARTS.append(("18_Candlestick", "candlestick/basic.html", {
    "TITLE":"18 K线图","DATES":D(["1日","2日","3日","4日","5日","6日","7日"]),
    "DATA":D([[20,34,10,38],[40,35,30,50],[31,38,33,44],[38,15,5,42],[11,35,8,35],[29,43,20,49],[41,26,18,42]])}))

# ═══ Treemap ═══
CHARTS.append(("19_Treemap", "treemap/basic.html", {
    "TITLE":"19 矩形树图","NODE_CLICK":"false","UPPER_LABEL_SHOW":"false","BREADCRUMB_SHOW":"true",
    "DATA":D([{"name":"电子","children":[{"name":"手机","value":6000},{"name":"电脑","value":4000}]},
              {"name":"家居","children":[{"name":"家具","value":3000},{"name":"灯具","value":2000}]}])}))

# ═══ Sunburst ═══
CHARTS.append(("20_Sunburst", "sunburst/basic.html", {
    "TITLE":"20 旭日图","LABEL_SHOW":"true","NODE_CLICK":"false","FOCUS":"none","RADIUS":"['0%','90%']","ROTATE":0,
    "DATA":D([{"name":"A","itemStyle":{"color":"#5470c6"},"children":[{"name":"A1","value":25},{"name":"A2","value":15}]},
              {"name":"B","itemStyle":{"color":"#91cc75"},"children":[{"name":"B1","value":20},{"name":"B2","value":10}]}])}))

# ═══ Sankey ═══
CHARTS.append(("21_Sankey", "sankey/basic.html", {
    "TITLE":"21 桑基图","NODE_ALIGN":"left","LABEL_POS":"right","ORIENT":"horizontal",
    "NODES":D([{"name":"首页"},{"name":"搜索"},{"name":"详情"},{"name":"下单"}]),
    "LINKS":D([{"source":"首页","target":"搜索","value":40},{"source":"首页","target":"详情","value":20},{"source":"搜索","target":"详情","value":25},{"source":"详情","target":"下单","value":35}])}))

# ═══ Graph ═══
CHARTS.append(("22_Graph_Force", "graph/force.html", {
    "TITLE":"22 力导向图","LAYOUT":"force","REPULSION":50,"EDGE_LENGTH":100,"GRAVITY":0.1,
    "LAYOUT_ANIMATION":"true","LABEL_SHOW":"true","SYMBOL_SIZE":30,"LEGEND":"false",
    "NODES":D([{"name":"A","category":0},{"name":"B","category":0},{"name":"C","category":1},{"name":"D","category":1},{"name":"E","category":2}]),
    "LINKS":D([{"source":"A","target":"B"},{"source":"A","target":"C"},{"source":"B","target":"D"},{"source":"C","target":"D"},{"source":"C","target":"E"}]),
    "CATEGORIES":D([{"name":"一类"},{"name":"二类"},{"name":"三类"}])}))

# ═══ Tree ═══
CHARTS.append(("23_Tree", "tree/basic.html", {
    "TITLE":"23 树图","LAYOUT":"orthogonal","ORIENT":"LR","LABEL_POS":"right","EXPAND_COLLAPSE":"true","LEAF_POS":"none",
    "DATA":D({"name":"CEO","children":[{"name":"CTO","children":[{"name":"工程师A"},{"name":"工程师B"}]},{"name":"CFO","children":[{"name":"会计A"}]}]})}))

# ═══ Boxplot ═══
CHARTS.append(("24_Boxplot", "boxplot/basic.html", {
    "TITLE":"24 箱线图","Y_AXIS_NAME":"","CATEGORIES":D(["A","B"]),
    "RAW_DATA":D([[850,740,900,1070,930,850,950,980,980,880,1000,980],[960,940,960,940,880,800,850,880,900,840,830,880]])}))

# ═══ Parallel ═══
CHARTS.append(("25_Parallel", "parallel/basic.html", {
    "TITLE":"25 平行坐标",
    "DATA":D([[55,85,78,90,65,"A"],[70,80,82,95,72,"B"],[60,75,68,85,58,"C"],[80,90,88,92,78,"D"],[45,65,55,70,48,"E"]]),
    "PARALLEL_AXIS":D([{"dim":0,"name":"A"},{"dim":1,"name":"B"},{"dim":2,"name":"C"},{"dim":3,"name":"D"},{"dim":4,"name":"E"}])}))

# ═══ Calendar ═══
CHARTS.append(("26_Calendar", "calendar/heatmap.html", {
    "TITLE":"26 日历热力","RANGE_START":"2024-01-01","RANGE_END":"2024-12-31","VMIN":0,"VMAX":250,"ORIENT":"horizontal",
    "DATA":D([["2024-01-05",120],["2024-02-03",200],["2024-03-10",90],["2024-04-07",220],["2024-05-05",160],["2024-06-12",130]])}))

# ═══ ThemeRiver ═══
CHARTS.append(("27_ThemeRiver", "themeRiver/basic.html", {
    "TITLE":"27 主题河流","LEGEND":"true",
    "DATA":D([["2015/11/08",10,"Evolution"],["2015/11/09",15,"Evolution"],["2015/11/08",10,"Natural"],["2015/11/09",15,"Natural"],["2015/11/08",10,"Deep"],["2015/11/09",20,"Deep"]])}))

# ═══ PictorialBar ═══
CHARTS.append(("28_PictorialBar", "pictorialBar/basic.html", {
    "TITLE":"28 象形柱图","SYMBOL":"rect","SYMBOL_SIZE":30,"SYMBOL_MARGIN":5,"SYMBOL_CLIP":"false",
    "SYMBOL_BOUNDING":"false","SYMBOL_REPEAT":"false","SYMBOL_POS":"end","COLOR":"#5470c6","LABEL_SHOW":"false",
    "CATEGORIES":D(["大象","犀牛","河马","水牛","长颈鹿"]),
    "VALUES":D([6500,3500,3000,2000,1800])}))

# ═══ Chord ═══
CHARTS.append(("29_Chord", "chord/basic.html", {
    "TITLE":"29 和弦图","LABEL_ROTATE":"false",
    "NODES":D([{"name":"北京"},{"name":"上海"},{"name":"广州"},{"name":"深圳"},{"name":"成都"}]),
    "LINKS":D([{"source":"北京","target":"上海","value":95},{"source":"北京","target":"广州","value":60},{"source":"上海","target":"深圳","value":55},{"source":"广州","target":"深圳","value":70}])}))

# ═══ Lines (flights) ═══
CHARTS.append(("31_Lines_Flights", "lines/flights.html", {
    "GEO_COORD_MAP":D({}),
    "TITLE":"31 航班线路","MAP_NAME":"china","MAP_INLINE":"","LINE_SCALE":"1",
    "FLIGHTS":D([{"fromName":"北京","toName":"上海","coords":[[116.46,39.92],[121.48,31.22]]},
                 {"fromName":"北京","toName":"广州","coords":[[116.46,39.92],[113.23,23.16]]},
                 {"fromName":"上海","toName":"深圳","coords":[[121.48,31.22],[114.07,22.62]]}])}))

# ═══ Mix ═══
CHARTS.append(("32_Mix_Line_Bar", "mix/line-bar.html", {
    "TITLE":"32 混合图表","LINE_NAME":"折线","BAR_NAME":"柱状",
    "CATEGORIES":D(["Jan","Feb","Mar","Apr","May","Jun"]),
    "BAR_DATA":D([320,332,301,334,390,330]),
    "LINE_DATA":D([220,182,191,234,290,310])}))

CHARTS.append(("41_Mix_Timeline", "mix/timeline.html", {
    "OPTIONS":"[]",
    "TITLE":"41 时间轴",
    "TIMELINE":D([2020,2021,2022]),
    "CATEGORIES":D(["A","B","C"]),
    "SERIES":D([{"name":"A","type":"bar","data":[120,145,170]},{"name":"B","type":"bar","data":[90,110,130]},{"name":"C","type":"bar","data":[70,85,100]}])}))

# ═══ 3D ═══
CHARTS.append(("33_3D_Bar", "3d/bar3d.html", {
    "DATA":D([["A","Q1",120],["A","Q2",200],["B","Q1",90],["B","Q2",130],["C","Q1",160],["C","Q2",220]]),
    "TITLE":"33 3D柱状","GL_INLINE":"","VMAX":250,"COORD_SYSTEM":"cartesian3D","BAR_SIZE":0.3,
    "AXIS_3D":D([{"name":"X","data":["A","B","C"]},{"name":"Y","data":["Q1","Q2","Q3","Q4"]},{"name":"Z"}])}))

CHARTS.append(("34_3D_Scatter", "3d/scatter3d.html", {
    "DATA":D([[10,20,30],[20,10,40],[30,30,20],[15,25,35],[25,15,25]]),
    "TITLE":"34 3D散点","GL_INLINE":"","SYMBOL_SIZE":10,
    "AXIS_3D":D([{"name":"X"},{"name":"Y"},{"name":"Z"}])}))

CHARTS.append(("35_3D_Surface", "3d/surface.html", {
    "TITLE":"35 3D曲面","GL_INLINE":"","PROJECTION":"perspective","WIREFRAME":"false","COLOR":"#5470c6",
    "DATA_OR_EQUATION":"function(x,y){return Math.sin(x)*Math.cos(y)}","PARAMETRIC":"false"}))

CHARTS.append(("36_3D_Globe", "3d/globe.html", {
    "TITLE":"36 3D地球","GL_INLINE":"","AUTO_ROTATE":"true","SHADING":"lambert","ENVIRONMENT":"","BASE_TEXTURE":"","HEIGHT_TEXTURE":"",
    "SCATTER_SERIES":"[]","LAYERS":"[]"}))

CHARTS.append(("37_3D_Lines3D", "3d/lines3d.html", {
    "GEO_COORD_MAP":"{}",
    "TITLE":"37 3D折线","GL_INLINE":"","AUTO_ROTATE":"false","ENVIRONMENT":"","BASE_TEXTURE":"","LINE_COLOR":"#ff6600",
    "FLIGHTS":D([{"fromName":"A","toName":"B","coords":[[0,0,0],[10,10,10]]},
                 {"fromName":"B","toName":"C","coords":[[10,10,10],[20,20,30]]}])}))

# ═══ Misc ═══
CHARTS.append(("39_Custom_Error_Bar", "custom/error-bar.html", {
    "TITLE":"39 误差柱图","RENDER_ITEM":"false","ENCODE":"{}",
    "CATEGORIES":D(["A","B","C","D","E"]),
    "DATA":D([[50,45,55],[65,60,72],[55,50,62],[70,65,80],[60,55,68]])}))

CHARTS.append(("40_Geo_Lines", "geo/lines.html", {
    "GEO_COORD_MAP":D({"北京":[116.4,39.9],"上海":[121.5,31.2],"广州":[113.3,23.1]}),
    "TITLE":"40 全国线路","MAP_NAME":"china","MAP_INLINE":"","SIZE_SCALE":"1","EFFECT_DATA":"[]",
    "FLIGHTS":D([{"fromName":"北京","toName":"上海","coords":[[116.4,39.9],[121.5,31.2]]},
                 {"fromName":"上海","toName":"广州","coords":[[121.5,31.2],[113.3,23.1]]}])}))

# ═════════════════════════════════════════════════════════
# Validate & Generate
# ═════════════════════════════════════════════════════════
results = []
for name, tpl_rel, data in CHARTS:
    tpl_path = os.path.join(TPL, tpl_rel)
    if not os.path.exists(tpl_path):
        results.append(("⏭️", name, f"missing: {tpl_rel}"))
        continue
    # Check placeholder coverage
    with open(tpl_path) as f:
        tpl_content = f.read()
    needed = set(re.findall(r'\{\{(\w+)\}\}', tpl_content)) - {'ECHARTS_INLINE'}
    missing = needed - set(data.keys())
    if missing:
        results.append(("❌", name, f"missing keys: {missing}"))
        continue
    try:
        out = os.path.join(OUT, f"{name}.html")
        build(tpl_path, data, out)
        # Verify no unresolved placeholders remain
        with open(out) as f:
            out_content = f.read()
        remaining = re.findall(r'\{\{(\w+)\}\}', out_content)
        if remaining:
            results.append(("❌", name, f"unresolved: {remaining}"))
        else:
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
    if s != "✅": print(f"  {s} {n:<30s} {d}")
with open(f"{OUT}/_summary.json","w") as f:
    json.dump([{"status":s,"name":n,"detail":d} for s,n,d in results], f, ensure_ascii=False, indent=2)
print(f"\nOutput: {OUT}")
