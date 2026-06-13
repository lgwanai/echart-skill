"""
Generate all ECharts chart types with hand-crafted options.
Each type gets proper test data + explicit echarts_option.
Output: examples/all_charts/
"""
import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import duckdb
from scripts.chart_generator import generate_chart

OUT = os.path.abspath("examples/all_charts")
os.makedirs(OUT, exist_ok=True)
DB_PATH = os.path.join(tempfile.gettempdir(), "all_charts_v2.duckdb")
if os.path.exists(DB_PATH): os.unlink(DB_PATH)
conn = duckdb.connect(DB_PATH)

CHARTS = []

def add(title, ddl, query, option, chart_type=""):
    """Register a chart with explicit echarts_option."""
    CHARTS.append((title, ddl, query, option, chart_type))

# ═══════════════════════════════════════════════════════════
# 01-05: Bar
# ═══════════════════════════════════════════════════════════
add("01_Bar_Basic", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(cat VARCHAR, val DOUBLE);
    INSERT INTO tmp VALUES ('Mon',120),('Tue',200),('Wed',150),('Thu',80),('Fri',70),('Sat',110),('Sun',130)
""", "SELECT cat, val FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"bar","encode":{"x":"cat","y":"val"}}]}, "bar")

add("02_Bar_Horizontal", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(c VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('巴西',18203),('印尼',23490),('美国',29034),('印度',104970),('中国',131744)
""", "SELECT c, v FROM tmp ORDER BY v",
    {"yAxis":{"type":"category"},"xAxis":{"type":"value"},"series":[{"type":"bar","encode":{"x":"v","y":"c"}}]}, "bar")

add("03_Bar_Stacked", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(d VARCHAR, email INTEGER, ads INTEGER, video INTEGER, direct INTEGER, search INTEGER);
    INSERT INTO tmp VALUES ('Mon',120,220,150,320,180),('Tue',132,182,232,332,200),('Wed',101,191,201,301,165),('Thu',134,234,154,334,190),('Fri',90,290,190,330,210),('Sat',230,330,330,380,250),('Sun',210,310,290,410,280)
""", "SELECT * FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"bar","stack":"x","encode":{"x":"d","y":"email"}},{"type":"bar","stack":"x","encode":{"x":"d","y":"ads"}},{"type":"bar","stack":"x","encode":{"x":"d","y":"video"}},{"type":"bar","stack":"x","encode":{"x":"d","y":"direct"}},{"type":"bar","stack":"x","encode":{"x":"d","y":"search"}}]}, "bar")

add("04_Bar_Waterfall", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(d VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('启动',120),('研发',200),('营销',150),('运维',80),('销售',-110),('利润',-60),('结算',260)
""", "SELECT d, v FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"bar","encode":{"x":"d","y":"v"}}]}, "bar")

add("05_Bar_Race", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(y INTEGER, c VARCHAR, v DOUBLE); INSERT INTO tmp VALUES (2020,'中国',14.7),(2020,'美国',21.4),(2020,'日本',5.1),(2020,'德国',3.8),(2020,'英国',2.7),(2021,'中国',17.7),(2021,'美国',23.3),(2021,'日本',4.9),(2021,'德国',4.2),(2021,'英国',3.2),(2022,'中国',18.0),(2022,'美国',25.5),(2022,'日本',4.2),(2022,'德国',4.1),(2022,'英国',3.1),(2023,'中国',17.9),(2023,'美国',27.4),(2023,'日本',4.2),(2023,'德国',4.5),(2023,'英国',3.3)
""", "SELECT * FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"bar","encode":{"x":"c","y":"v"}}]}, "bar")

# ═══════════════════════════════════════════════════════════
# 06-08: Line
# ═══════════════════════════════════════════════════════════
add("06_Line_Basic", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(d VARCHAR, v INTEGER); INSERT INTO tmp VALUES ('Jan',820),('Feb',932),('Mar',901),('Apr',1290),('May',1330),('Jun',1420),('Jul',1560),('Aug',1480),('Sep',1620),('Oct',1720),('Nov',1680),('Dec',1890)
""", "SELECT d, v FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"line","encode":{"x":"d","y":"v"},"smooth":True}]}, "line")

add("07_Line_Stacked", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(d VARCHAR, email INTEGER, ads INTEGER, video INTEGER);
    INSERT INTO tmp VALUES ('Jan',120,220,150),('Feb',132,182,232),('Mar',101,191,201),('Apr',134,234,154),('May',90,290,190),('Jun',230,330,330)
""", "SELECT * FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"line","stack":"x","encode":{"x":"d","y":"email"}},{"type":"line","stack":"x","encode":{"x":"d","y":"ads"}},{"type":"line","stack":"x","encode":{"x":"d","y":"video"}}]}, "line")

add("08_Line_XY", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(x DOUBLE, y DOUBLE); INSERT INTO tmp VALUES (10.0,8.04),(8.0,6.95),(13.0,7.58),(9.0,8.81),(11.0,8.33),(14.0,9.96),(6.0,7.24),(4.0,4.26),(12.0,10.84),(7.0,4.82),(5.0,5.68)
""", "SELECT x, y FROM tmp",
    {"xAxis":{"type":"value"},"yAxis":{"type":"value"},"series":[{"type":"line","encode":{"x":"x","y":"y"}}]}, "line")

# ═══════════════════════════════════════════════════════════
# 09: Pie
# ═══════════════════════════════════════════════════════════
add("09_Pie_Basic", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(c VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('搜索',1048),('直接',735),('邮件',580),('联盟',484),('视频',300)
""", "SELECT c, v FROM tmp",
    {"series":[{"type":"pie","encode":{"itemName":"c","value":"v"},"radius":["40%","70%"]}]}, "pie")

add("38_Pie_Rose", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(c VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('A',40),('B',38),('C',32),('D',30),('E',28),('F',26),('G',22),('H',18)
""", "SELECT c, v FROM tmp",
    {"series":[{"type":"pie","encode":{"itemName":"c","value":"v"},"roseType":"area","radius":["20%","80%"]}]}, "pie")

# ═══════════════════════════════════════════════════════════
# 10-12: Scatter
# ═══════════════════════════════════════════════════════════
add("10_Scatter_Basic", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(x DOUBLE, y DOUBLE); INSERT INTO tmp VALUES (10.0,8.04),(8.0,6.95),(13.0,7.58),(9.0,8.81),(11.0,8.33),(14.0,9.96),(6.0,7.24),(4.0,4.26),(12.0,10.84),(7.0,4.82),(5.0,5.68)
""", "SELECT x, y FROM tmp",
    {"xAxis":{"type":"value"},"yAxis":{"type":"value"},"series":[{"type":"scatter","encode":{"x":"x","y":"y"}}]}, "scatter")

add("11_Scatter_Bubble", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(x DOUBLE, y DOUBLE, sz DOUBLE, label VARCHAR); INSERT INTO tmp VALUES (150,80,30,'北京'),(180,100,50,'上海'),(120,60,20,'广州'),(100,40,15,'深圳'),(200,120,45,'成都'),(80,50,10,'西安')
""", "SELECT x, y, sz, label FROM tmp",
    {"xAxis":{"type":"value"},"yAxis":{"type":"value"},"series":[{"type":"scatter","encode":{"x":"x","y":"y"},"symbolSize":"sz"}]}, "scatter")

add("12_Scatter_Geo", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(name VARCHAR, val DOUBLE, lat DOUBLE, lng DOUBLE); INSERT INTO tmp VALUES ('北京',100,39.9,116.4),('上海',95,31.2,121.5),('广州',80,23.1,113.3),('深圳',90,22.5,114.1),('成都',70,30.6,104.1)
""", "SELECT * FROM tmp",
    {"geo":{"map":"china","roam":True},"series":[{"type":"scatter","coordinateSystem":"geo","encode":{"value":"val","lng":"lng","lat":"lat"}}]}, "scatter")

add("30_EffectScatter", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(x DOUBLE, y DOUBLE, n VARCHAR); INSERT INTO tmp VALUES (20,50,'北京'),(30,80,'上海'),(50,40,'广州'),(70,70,'深圳'),(60,30,'成都'),(80,60,'杭州')
""", "SELECT x, y, n FROM tmp",
    {"xAxis":{"type":"value"},"yAxis":{"type":"value"},"series":[{"type":"effectScatter","encode":{"x":"x","y":"y"}}]}, "scatter")

# ═══════════════════════════════════════════════════════════
# 13: Map
# ═══════════════════════════════════════════════════════════
add("13_Map_China", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(name VARCHAR, val DOUBLE); INSERT INTO tmp VALUES ('广东',38072),('北京',26593),('上海',21073),('江苏',18296),('浙江',16976),('山东',14386),('四川',12852),('福建',12359),('湖北',10388),('湖南',9026),('安徽',8104),('河南',7328),('河北',6398),('辽宁',5384),('重庆',4314),('陕西',3284),('云南',2744),('贵州',2183),('广西',1653),('山西',1280),('吉林',982),('黑龙江',936),('新疆',760),('内蒙古',658),('甘肃',432),('海南',320),('宁夏',218),('青海',156),('西藏',98)
""", "SELECT name, val FROM tmp",
    {"visualMap":{"min":98,"max":38072,"inRange":{"color":["#e0f3f8","#abd9e9","#74add1","#4575b4","#313695"]},"calculable":True},"series":[{"type":"map","map":"china","data":[]}]}, "map")

# ═══════════════════════════════════════════════════════════
# 14: Radar
# ═══════════════════════════════════════════════════════════
add("14_Radar_Basic", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(n VARCHAR, budget INTEGER, spending INTEGER, sales INTEGER, profit INTEGER); INSERT INTO tmp VALUES ('预算',4200,3000,20000,35000),('实际',5000,14000,28000,26000)
""", "SELECT * FROM tmp",
    {"radar":{"indicator":[{"name":"预算分配","max":5000},{"name":"支出","max":15000},{"name":"销售","max":30000},{"name":"利润","max":40000}]},"series":[{"type":"radar","encode":{"itemName":"n","value":["budget","spending","sales","profit"]}}]}, "radar")

# ═══════════════════════════════════════════════════════════
# 15-18: Gauge / Funnel / Heatmap / Candlestick
# ═══════════════════════════════════════════════════════════
add("15_Gauge", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(v DOUBLE); INSERT INTO tmp VALUES (78.5)
""", "SELECT v FROM tmp",
    {"series":[{"type":"gauge","data":[{"value":78.5,"name":"完成率"}],"detail":{"formatter":"{value}%"}}]}, "")

add("16_Funnel", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(stage VARCHAR, cnt INTEGER); INSERT INTO tmp VALUES ('访问',10000),('注册',6500),('激活',4200),('下单',2800),('支付',1800)
""", "SELECT stage, cnt FROM tmp",
    {"series":[{"type":"funnel","encode":{"itemName":"stage","value":"cnt"},"sort":"descending"}]}, "")

add("17_Heatmap", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(h INTEGER, d VARCHAR, v DOUBLE); INSERT INTO tmp VALUES (0,'Mon',10),(1,'Mon',8),(6,'Mon',0),(12,'Mon',25),(18,'Mon',40),(23,'Mon',12),(0,'Tue',5),(6,'Tue',2),(12,'Tue',20),(18,'Tue',35),(23,'Tue',10),(0,'Wed',8),(6,'Wed',1),(12,'Wed',22),(18,'Wed',30),(23,'Wed',8),(0,'Thu',3),(6,'Thu',0),(12,'Thu',18),(18,'Thu',28),(23,'Thu',5)
""", "SELECT * FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"category"},"visualMap":{"min":0,"max":40,"inRange":{"color":["#fde0dd","#fa9fb5","#f768a1","#dd3497","#7a0177"]}},"series":[{"type":"heatmap","encode":{"x":"d","y":"h"}}]}, "")

add("18_Candlestick", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(d VARCHAR, o DOUBLE, cl DOUBLE, lo DOUBLE, hi DOUBLE); INSERT INTO tmp VALUES ('1日',20,34,10,38),('2日',40,35,30,50),('3日',31,38,33,44),('4日',38,15,5,42),('5日',11,35,8,35),('6日',29,43,20,49),('7日',41,26,18,42)
""", "SELECT * FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"candlestick","encode":{"x":"d","y":["lo","hi","o","cl"]}}]}, "")

# ═══════════════════════════════════════════════════════════
# 19-20: Treemap / Sunburst
# ═══════════════════════════════════════════════════════════
add("19_Treemap", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(n VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('电子产品',0),('手机',6000),('电脑',4000),('平板',2000),('家居',0),('家具',3000),('灯具',2000),('园艺',1000)
""", "SELECT n, v FROM tmp",
    {"series":[{"type":"treemap","data":[{"name":"电子产品","children":[{"name":"手机","value":6000},{"name":"电脑","value":4000},{"name":"平板","value":2000}]},{"name":"家居","children":[{"name":"家具","value":3000},{"name":"灯具","value":2000},{"name":"园艺","value":1000}]}]}]}, "")

add("20_Sunburst", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(n VARCHAR, v DOUBLE, p VARCHAR); INSERT INTO tmp VALUES ('根',0,''),('A',40,'根'),('B',30,'根'),('C',30,'根'),('A1',25,'A'),('A2',15,'A'),('B1',20,'B'),('B2',10,'B'),('C1',20,'C'),('C2',10,'C')
""", "SELECT n, v, p FROM tmp",
    {"series":[{"type":"sunburst","data":[{"name":"根","children":[{"name":"A","value":40,"children":[{"name":"A1","value":25},{"name":"A2","value":15}]},{"name":"B","value":30,"children":[{"name":"B1","value":20},{"name":"B2","value":10}]},{"name":"C","value":30,"children":[{"name":"C1","value":20},{"name":"C2","value":10}]}]}]}]}, "")

# ═══════════════════════════════════════════════════════════
# 21-23: Sankey / Graph / Tree
# ═══════════════════════════════════════════════════════════
add("21_Sankey", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(source VARCHAR, target VARCHAR, val DOUBLE); INSERT INTO tmp VALUES ('首页','搜索',40),('首页','推荐',30),('首页','分类',20),('搜索','详情',25),('推荐','详情',20),('分类','详情',15),('详情','下单',40),('详情','收藏',15)
""", "SELECT * FROM tmp",
    {"series":[{"type":"sankey","data":[{"name":"首页"},{"name":"搜索"},{"name":"推荐"},{"name":"分类"},{"name":"详情"},{"name":"下单"},{"name":"收藏"}],"links":[{"source":"首页","target":"搜索","value":40},{"source":"首页","target":"推荐","value":30},{"source":"首页","target":"分类","value":20},{"source":"搜索","target":"详情","value":25},{"source":"推荐","target":"详情","value":20},{"source":"分类","target":"详情","value":15},{"source":"详情","target":"下单","value":40},{"source":"详情","target":"收藏","value":15}]}]}, "")

add("22_Graph_Force", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(n VARCHAR, c INTEGER); INSERT INTO tmp VALUES ('A',0),('B',0),('C',1),('D',1),('E',2)
""", "SELECT * FROM tmp",
    {"series":[{"type":"graph","layout":"force","roam":True,"data":[{"name":"A","category":0},{"name":"B","category":0},{"name":"C","category":1},{"name":"D","category":1},{"name":"E","category":2}],"links":[{"source":"A","target":"B"},{"source":"A","target":"C"},{"source":"B","target":"D"},{"source":"C","target":"D"},{"source":"C","target":"E"},{"source":"D","target":"E"}],"categories":[{"name":"一类"},{"name":"二类"},{"name":"三类"}]}]}, "")

add("23_Tree", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(id INTEGER, n VARCHAR, pid INTEGER); INSERT INTO tmp VALUES (1,'CEO',0),(2,'CTO',1),(3,'CFO',1),(4,'工程师A',2),(5,'工程师B',2),(6,'会计A',3)
""", "SELECT * FROM tmp",
    {"series":[{"type":"tree","data":[{"name":"CEO","children":[{"name":"CTO","children":[{"name":"工程师A"},{"name":"工程师B"}]},{"name":"CFO","children":[{"name":"会计A"}]}]}]}]}, "")

# ═══════════════════════════════════════════════════════════
# 24-26: Boxplot / Parallel / Calendar
# ═══════════════════════════════════════════════════════════
add("24_Boxplot", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(c VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('A',850),('A',740),('A',900),('A',1070),('A',930),('A',850),('A',950),('A',980),('A',980),('A',880),('A',1000),('A',980),('B',960),('B',940),('B',960),('B',940),('B',880),('B',800),('B',850),('B',880),('B',900),('B',840),('B',830)
""", "SELECT c, v FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"boxplot","encode":{"x":"c","y":"v"}}]}, "")

add("25_Parallel", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(n VARCHAR, a DOUBLE, b DOUBLE, c DOUBLE, d DOUBLE, e DOUBLE); INSERT INTO tmp VALUES ('A',55,85,78,90,65),('B',70,80,82,95,72),('C',60,75,68,85,58),('D',80,90,88,92,78),('E',45,65,55,70,48)
""", "SELECT * FROM tmp",
    {"parallel":{"left":"5%","right":"13%","bottom":"10%","top":"20%"},"parallelAxis":[{"dim":0,"name":"A"},{"dim":1,"name":"B"},{"dim":2,"name":"C"},{"dim":3,"name":"D"},{"dim":4,"name":"E"}],"series":[{"type":"parallel","encode":{"itemName":"n","value":["a","b","c","d","e"]}}]}, "")

add("26_Calendar", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(d VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('2024-01-05',120),('2024-02-03',200),('2024-03-10',90),('2024-04-07',220),('2024-05-05',160),('2024-06-12',130),('2024-07-08',170),('2024-08-15',210),('2024-09-05',175),('2024-10-10',155),('2024-11-08',125),('2024-12-05',165)
""", "SELECT d, v FROM tmp",
    {"calendar":{"range":"2024"},"series":[{"type":"heatmap","coordinateSystem":"calendar","encode":{"value":"v"}}],"visualMap":{"min":80,"max":250,"orient":"horizontal","left":"center"}}, "")

# ═══════════════════════════════════════════════════════════
# 27: ThemeRiver
# ═══════════════════════════════════════════════════════════
add("27_ThemeRiver", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(d VARCHAR, c VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('Jan','A',30),('Jan','B',20),('Jan','C',15),('Feb','A',35),('Feb','B',25),('Feb','C',18),('Mar','A',40),('Mar','B',30),('Mar','C',22),('Apr','A',38),('Apr','B',28),('Apr','C',20),('May','A',45),('May','B',35),('May','C',25)
""", "SELECT * FROM tmp",
    {"series":[{"type":"themeRiver","encode":{"time":"d","value":"v"}}]}, "")

# ═══════════════════════════════════════════════════════════
# 28-31: PictorialBar / Chord / EffectScatter / Lines
# ═══════════════════════════════════════════════════════════
add("28_PictorialBar", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(c VARCHAR, v DOUBLE); INSERT INTO tmp VALUES ('大象',6500),('犀牛',3500),('河马',3000),('水牛',2000),('长颈鹿',1800)
""", "SELECT c, v FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"pictorialBar","encode":{"x":"c","y":"v"}}]}, "")

add("29_Chord", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(source VARCHAR, target VARCHAR, val DOUBLE); INSERT INTO tmp VALUES ('北京','上海',95),('北京','广州',60),('北京','深圳',45),('上海','广州',80),('上海','深圳',55),('广州','深圳',70),('北京','成都',35)
""", "SELECT * FROM tmp",
    {"series":[{"type":"chord","data":[{"name":"北京"},{"name":"上海"},{"name":"广州"},{"name":"深圳"},{"name":"成都"}],"links":[{"source":"北京","target":"上海","value":95},{"source":"北京","target":"广州","value":60},{"source":"北京","target":"深圳","value":45},{"source":"上海","target":"广州","value":80},{"source":"上海","target":"深圳","value":55},{"source":"广州","target":"深圳","value":70},{"source":"北京","target":"成都","value":35}]}]}, "")

# ═══════════════════════════════════════════════════════════
# 31: Lines Flights (geo lines)
# ═══════════════════════════════════════════════════════════
add("31_Lines_Flights", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(from_name VARCHAR,to_name VARCHAR,from_lat DOUBLE,from_lng DOUBLE,to_lat DOUBLE,to_lng DOUBLE,val DOUBLE); INSERT INTO tmp VALUES ('北京','上海',39.9,116.4,31.2,121.5,100),('北京','广州',39.9,116.4,23.1,113.3,80),('上海','深圳',31.2,121.5,22.5,114.1,90),('广州','成都',23.1,113.3,30.6,104.1,60)
""", "SELECT * FROM tmp",
    {"geo":{"map":"china","roam":True},"series":[{"type":"lines","coordinateSystem":"geo","polyline":False,"data":[{"coords":[[116.4,39.9],[121.5,31.2]],"name":"北京→上海","value":100},{"coords":[[116.4,39.9],[113.3,23.1]],"name":"北京→广州","value":80},{"coords":[[121.5,31.2],[114.1,22.5]],"name":"上海→深圳","value":90},{"coords":[[113.3,23.1],[104.1,30.6]],"name":"广州→成都","value":60}]}]}, "")

# ═══════════════════════════════════════════════════════════
# 32: Mix Line-Bar (dual y-axis)
# ═══════════════════════════════════════════════════════════
add("32_Mix_Line_Bar", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(d VARCHAR, bar_val DOUBLE, line_val DOUBLE); INSERT INTO tmp VALUES ('Jan',320,220),('Feb',332,182),('Mar',301,191),('Apr',334,234),('May',390,290),('Jun',330,310)
""", "SELECT * FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":[{"type":"value","name":"柱"},{"type":"value","name":"线"}],"series":[{"type":"bar","encode":{"x":"d","y":"bar_val"}},{"type":"line","yAxisIndex":1,"encode":{"x":"d","y":"line_val"}}]}, "")

# ═══════════════════════════════════════════════════════════
# 33-37: 3D Charts (require echarts-gl)
# ═══════════════════════════════════════════════════════════
add("33_3D_Bar", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(x VARCHAR, y VARCHAR, z DOUBLE); INSERT INTO tmp VALUES ('A','Q1',120),('A','Q2',200),('A','Q3',150),('A','Q4',180),('B','Q1',90),('B','Q2',130),('B','Q3',110),('B','Q4',100),('C','Q1',160),('C','Q2',220),('C','Q3',190),('C','Q4',210)
""", "SELECT * FROM tmp",
    {"xAxis3D":{"type":"category"},"yAxis3D":{"type":"category"},"zAxis3D":{"type":"value"},"series":[{"type":"bar3D","encode":{"x":"x","y":"y","z":"z"}}]}, "")

add("34_3D_Scatter", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(x DOUBLE, y DOUBLE, z DOUBLE, n VARCHAR); INSERT INTO tmp VALUES (10,20,30,'A'),(20,10,40,'B'),(30,30,20,'C'),(15,25,35,'D'),(25,15,25,'E')
""", "SELECT * FROM tmp",
    {"xAxis3D":{"type":"value"},"yAxis3D":{"type":"value"},"zAxis3D":{"type":"value"},"series":[{"type":"scatter3D","encode":{"x":"x","y":"y","z":"z"}}]}, "")

add("35_3D_Surface", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(x INTEGER, y INTEGER, z DOUBLE); INSERT INTO tmp VALUES (0,0,10),(0,1,15),(0,2,20),(0,3,25),(1,0,12),(1,1,18),(1,2,22),(1,3,28),(2,0,15),(2,1,22),(2,2,25),(2,3,30),(3,0,18),(3,1,25),(3,2,28),(3,3,32)
""", "SELECT * FROM tmp",
    {"xAxis3D":{"type":"value"},"yAxis3D":{"type":"value"},"zAxis3D":{"type":"value"},"series":[{"type":"surface","equation":{}}]}, "")

add("36_3D_Globe", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(v DOUBLE); INSERT INTO tmp VALUES (100)
""", "SELECT * FROM tmp",
    {"globe":{"baseTexture":""},"series":[{"type":"scatter3D","coordinateSystem":"globe"}]}, "")

add("37_3D_Lines3D", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(x DOUBLE, y DOUBLE, z DOUBLE); INSERT INTO tmp VALUES (0,0,0),(1,1,5),(2,3,8),(3,5,12),(4,8,15),(5,10,18)
""", "SELECT * FROM tmp",
    {"xAxis3D":{"type":"value"},"yAxis3D":{"type":"value"},"zAxis3D":{"type":"value"},"series":[{"type":"line3D","data":[]}]}, "")

# ═══════════════════════════════════════════════════════════
# 39-41: Custom Error-Bar / Geo Lines / Mix Timeline
# ═══════════════════════════════════════════════════════════
add("39_Custom_Error_Bar", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(c VARCHAR, v DOUBLE, e_min DOUBLE, e_max DOUBLE); INSERT INTO tmp VALUES ('A',50,45,55),('B',65,60,72),('C',55,50,62),('D',70,65,80),('E',60,55,68)
""", "SELECT * FROM tmp",
    {"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"bar","encode":{"x":"c","y":"v"}}]}, "")

add("40_Geo_Lines", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(from_n VARCHAR, to_n VARCHAR, from_lat DOUBLE, from_lng DOUBLE, to_lat DOUBLE, to_lng DOUBLE); INSERT INTO tmp VALUES ('北京','上海',39.9,116.4,31.2,121.5),('上海','广州',31.2,121.5,23.1,113.3)
""", "SELECT * FROM tmp",
    {"geo":{"map":"china","roam":True},"series":[{"type":"lines","coordinateSystem":"geo","polyline":False,"data":[{"coords":[[116.4,39.9],[121.5,31.2]],"name":"北京→上海"},{"coords":[[121.5,31.2],[113.3,23.1]],"name":"上海→广州"}]}]}, "")

add("41_Mix_Timeline", """
    DROP TABLE IF EXISTS tmp; CREATE TABLE tmp(y INTEGER, c VARCHAR, v DOUBLE); INSERT INTO tmp VALUES (2020,'A',120),(2020,'B',90),(2020,'C',70),(2021,'A',145),(2021,'B',110),(2021,'C',85),(2022,'A',170),(2022,'B',130),(2022,'C',100)
""", "SELECT * FROM tmp",
    {"timeline":{"data":[2020,2021,2022],"autoPlay":True},"options":[{"xAxis":{"type":"category"},"yAxis":{"type":"value"},"series":[{"type":"bar","encode":{"x":"c","y":"v"}}]}]}, "")


# ═══════════════════════════════════════════════════════════
# Execute & Validate
# ═══════════════════════════════════════════════════════════
results = []
for title, ddl, query, option, chart_type in CHARTS:
    try:
        for stmt in ddl.strip().split(";"):
            stmt = stmt.strip()
            if stmt: conn.execute(stmt)
        if not query:
            results.append(("⏭️", title, "no query"))
            continue

        config = {
            "db_path": DB_PATH,
            "query": query,
            "title": title,
            "output_path": f"{OUT}/{title}.html",
            "echarts_option": option,
            "chart_type": chart_type or "",
        }

        path = generate_chart(config)
        if not path:
            results.append(("❌", title, "None result"))
            continue

        with open(path) as f:
            html = f.read()

        # Verify series type present
        errors = []
        if '"type":' not in html:
            errors.append("missing series type")
        if errors:
            results.append(("❌", title, "; ".join(errors)))
        else:
            results.append(("✅", title, f"{len(html)} bytes"))

    except Exception as e:
        results.append(("❌", title, str(e)[:100]))

ok = sum(1 for r in results if r[0] == "✅")
sk = sum(1 for r in results if r[0] == "⏭️")
bad = sum(1 for r in results if r[0] == "❌")
print(f"\n{'═'*60}")
print(f"  Results: {ok} passed, {bad} failed, {sk} skipped ({len(results)} total)")
print(f"{'═'*60}")
for s, t, d in results:
    if s != "✅": print(f"  {s} {t:<35s} {d}")

with open(f"{OUT}/_summary.json", "w") as f:
    json.dump([{"status": s, "title": t, "detail": d} for s, t, d in results], f, ensure_ascii=False, indent=2)
print(f"\nOutput: {OUT}")
sys.exit(0 if bad == 0 else 1)
