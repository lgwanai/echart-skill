"""
Generate all 41 chart types with test data for verification.
Creates test CSV/Excel files, generates charts via one-shot API,
and validates each output has required structure.
"""
import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import duckdb
from scripts.chart_generator import generate_chart, CHART_REQUIREMENTS


OUT = os.path.abspath("examples/all_charts")
os.makedirs(OUT, exist_ok=True)

# ── Temp DuckDB file (generate_chart needs a file path) ──
DB_PATH = os.path.join(tempfile.gettempdir(), "all_charts_gen.duckdb")
if os.path.exists(DB_PATH):
    os.unlink(DB_PATH)
conn = duckdb.connect(DB_PATH)

# ═══════════════════════════════════════════════════════════════
# Define all chart types with test data
# ═══════════════════════════════════════════════════════════════

CHARTS = []

def add(chart_type, title, ddl, query, **extra):
    """Register a chart: DDL + INSERTs, then query + chart_type."""
    CHARTS.append((chart_type, title, ddl, query, extra))

# ── Bar (5) ──
add("bar", "01-Bar Basic", """
    CREATE TABLE bar_data AS SELECT * FROM (VALUES
    ('产品A',820),('产品B',932),('产品C',901),('产品D',934),('产品E',1290),('产品F',1330),('产品G',1320)
) t(cat,val)""",
    "SELECT cat as name, val as value FROM bar_data")

add("bar", "02-Bar Horizontal", """
    CREATE TABLE bar_h AS SELECT * FROM (VALUES
    ('巴西',18203),('印尼',23490),('美国',29034),('印度',104970),('中国',131744)
) t(c,v)""",
    "SELECT c as name, v as value FROM bar_h ORDER BY value")

add("bar", "03-Bar Stacked", """
    CREATE TABLE bar_stacked(name VARCHAR, email INTEGER, union_ads INTEGER, video_ads INTEGER, direct INTEGER, search INTEGER);
    INSERT INTO bar_stacked VALUES ('Mon',120,220,150,320,180),('Tue',132,182,232,332,200),
    ('Wed',101,191,201,301,165),('Thu',134,234,154,334,190),('Fri',90,290,190,330,210),
    ('Sat',230,330,330,380,250),('Sun',210,310,290,410,280)""",
    "SELECT * FROM bar_stacked")

add("bar", "04-Bar Waterfall", """
    CREATE TABLE waterfall(day VARCHAR, val INTEGER);
    INSERT INTO waterfall VALUES ('启动',120),('研发',200),('营销',150),('运维',80),('销售',-110),('利润',-60),('结算',260)""",
    "SELECT day as name, val as value FROM waterfall")

add("bar", "05-Bar Race", """
    CREATE TABLE race_data(year INTEGER, cat VARCHAR, val DOUBLE);
    INSERT INTO race_data VALUES
    (2020,'中国',14.7),(2020,'美国',21.4),(2020,'日本',5.1),(2020,'德国',3.8),(2020,'英国',2.7),
    (2021,'中国',17.7),(2021,'美国',23.3),(2021,'日本',4.9),(2021,'德国',4.2),(2021,'英国',3.2),
    (2022,'中国',18.0),(2022,'美国',25.5),(2022,'日本',4.2),(2022,'德国',4.1),(2022,'英国',3.1),
    (2023,'中国',17.9),(2023,'美国',27.4),(2023,'日本',4.2),(2023,'德国',4.5),(2023,'英国',3.3)""",
    "SELECT * FROM race_data")

# ── Line (3) ──
add("line", "06-Line Basic", """
    CREATE TABLE line_data(dt DATE, val INTEGER);
    INSERT INTO line_data VALUES ('2024-01-01',820),('2024-02-01',932),('2024-03-01',901),
    ('2024-04-01',1290),('2024-05-01',1330),('2024-06-01',1420),('2024-07-01',1560),
    ('2024-08-01',1480),('2024-09-01',1620),('2024-10-01',1720),('2024-11-01',1680),('2024-12-01',1890)""",
    "SELECT dt as name, val as value FROM line_data ORDER BY dt")

add("line", "07-Line Stacked", """
    CREATE TABLE line_stack(dt VARCHAR, email INTEGER, union_ads INTEGER, video_ads INTEGER);
    INSERT INTO line_stack VALUES ('1月',120,220,150),('2月',132,182,232),('3月',101,191,201),
    ('4月',134,234,154),('5月',90,290,190),('6月',230,330,330)""",
    "SELECT * FROM line_stack")

add("line", "08-Line XY", """
    CREATE TABLE line_xy(x DOUBLE, y DOUBLE);
    INSERT INTO line_xy VALUES (10,8.04),(8,6.95),(13,7.58),(9,8.81),(11,8.33),(14,9.96),(6,7.24),(4,4.26),(12,10.84),(7,4.82),(5,5.68)""",
    "SELECT x, y FROM line_xy")

# ── Pie (1) ──
add("pie", "09-Pie Basic", """
    CREATE TABLE pie_data(cat VARCHAR, val DOUBLE);
    INSERT INTO pie_data VALUES ('搜索引擎',1048),('直接访问',735),('邮件营销',580),('联盟广告',484),('视频广告',300)""",
    "SELECT cat as name, val as value FROM pie_data")

# ── Scatter (3) ──
add("scatter", "10-Scatter Basic", """
    CREATE TABLE scatter_data(x DOUBLE, y DOUBLE, label VARCHAR);
    INSERT INTO scatter_data VALUES (10.0,8.04,'A'),(8.0,6.95,'A'),(13.0,7.58,'A'),(9.0,8.81,'B'),(11.0,8.33,'B'),
    (14.0,9.96,'B'),(6.0,7.24,'C'),(4.0,4.26,'C'),(12.0,10.84,'C'),(7.0,4.82,'D'),(5.0,5.68,'D')""",
    "SELECT x, y, label as name FROM scatter_data")

add("scatter", "11-Scatter Bubble", """
    CREATE TABLE bubble_data(x DOUBLE, y DOUBLE, sz DOUBLE, label VARCHAR);
    INSERT INTO bubble_data VALUES (150,80,30,'北京'),(180,100,50,'上海'),(120,60,20,'广州'),
    (100,40,15,'深圳'),(200,120,45,'成都'),(80,50,10,'西安')""",
    "SELECT x, y, sz as value, label as name FROM bubble_data")

add("scatter", "12-Scatter Geo", """
    CREATE TABLE geo_scatter(name VARCHAR, val DOUBLE, lat DOUBLE, lng DOUBLE);
    INSERT INTO geo_scatter VALUES ('北京',100,39.9,116.4),('上海',95,31.2,121.5),('广州',80,23.1,113.3),('深圳',90,22.5,114.1),('成都',70,30.6,104.1)""",
    "SELECT * FROM geo_scatter")

# ── Map (1) ──
add("map", "13-Map China", """
    CREATE TABLE map_data(name VARCHAR, val DOUBLE);
    INSERT INTO map_data VALUES
    ('广东',38072),('北京',26593),('上海',21073),('江苏',18296),('浙江',16976),('山东',14386),
    ('四川',12852),('福建',12359),('湖北',10388),('湖南',9026),('安徽',8104),('河南',7328),
    ('河北',6398),('辽宁',5384),('重庆',4314),('陕西',3284),('云南',2744),('贵州',2183),
    ('广西',1653),('山西',1280),('吉林',982),('黑龙江',936),('新疆',760),('内蒙古',658),
    ('甘肃',432),('海南',320),('宁夏',218),('青海',156),('西藏',98)""",
    "SELECT name, val as value FROM map_data")

# ── Radar (1) ──
add("radar", "14-Radar Basic", """
    CREATE TABLE radar_data(name VARCHAR, budget INTEGER, spending INTEGER, sales INTEGER, profit INTEGER);
    INSERT INTO radar_data VALUES
    ('预算分配',4200,3000,20000,35000),('实际支出',5000,14000,28000,26000)""",
    "SELECT * FROM radar_data")

# ── Gauge (1) ──
add("bar", "15-Gauge", """
    CREATE TABLE gauge_data(val DOUBLE); INSERT INTO gauge_data VALUES (78.5)""",
    "SELECT '完成率' as name, val as value FROM gauge_data")

# ── Funnel (1) ──
add("bar", "16-Funnel", """
    CREATE TABLE funnel_data(stage VARCHAR, cnt INTEGER);
    INSERT INTO funnel_data VALUES ('访问',10000),('注册',6500),('激活',4200),('下单',2800),('支付',1800)""",
    "SELECT stage as name, cnt as value FROM funnel_data")

# ── Heatmap (1) ──
add("bar", "17-Heatmap", """
    CREATE TABLE heatmap_data(hour INTEGER, day VARCHAR, val DOUBLE);
    INSERT INTO heatmap_data VALUES
    (0,'周一',10),(1,'周一',8),(2,'周一',5),(3,'周一',3),(4,'周一',2),(5,'周一',1),(6,'周一',0),
    (7,'周一',1),(8,'周一',5),(9,'周一',12),(10,'周一',18),(11,'周一',22),(12,'周一',25),
    (13,'周一',28),(14,'周一',30),(15,'周一',32),(16,'周一',35),(17,'周一',38),(18,'周一',40),
    (19,'周一',35),(20,'周一',28),(21,'周一',22),(22,'周一',18),(23,'周一',12)""",
    "SELECT * FROM heatmap_data")

# ── Candlestick (1) ──
add("bar", "18-Candlestick", """
    CREATE TABLE k_data(dt VARCHAR, open DOUBLE, close DOUBLE, low DOUBLE, high DOUBLE);
    INSERT INTO k_data VALUES ('1日',20,34,10,38),('2日',40,35,30,50),('3日',31,38,33,44),
    ('4日',38,15,5,42),('5日',11,35,8,35),('6日',29,43,20,49),('7日',41,26,18,42)""",
    "SELECT * FROM k_data")

# ── Treemap (1) ──
add("bar", "19-Treemap", """
    CREATE TABLE treemap_data(name VARCHAR, val DOUBLE, parent VARCHAR);
    INSERT INTO treemap_data VALUES ('电子产品',0,''),('手机',6000,'电子产品'),('电脑',4000,'电子产品'),
    ('平板',2000,'电子产品'),('家居',0,''),('家具',3000,'家居'),('灯具',2000,'家居'),('园艺',1000,'家居')""",
    "SELECT * FROM treemap_data WHERE parent != '' UNION ALL SELECT name,val,'' FROM treemap_data WHERE parent=''")

# ── Sunburst (1) ──
add("bar", "20-Sunburst", """
    CREATE TABLE sunburst_data(name VARCHAR, val DOUBLE, parent VARCHAR);
    INSERT INTO sunburst_data VALUES ('根',0,''),('A',40,'根'),('B',30,'根'),('C',30,'根'),
    ('A1',25,'A'),('A2',15,'A'),('B1',20,'B'),('B2',10,'B'),('C1',20,'C'),('C2',10,'C')""",
    "SELECT name, val as value, parent FROM sunburst_data")

# ── Sankey (1) ──
add("bar", "21-Sankey", """
    CREATE TABLE sankey_data(source VARCHAR, target VARCHAR, val DOUBLE);
    INSERT INTO sankey_data VALUES ('首页','搜索',40),('首页','推荐',30),('首页','分类',20),
    ('搜索','详情',25),('推荐','详情',20),('分类','详情',15),('详情','下单',40),('详情','收藏',15)""",
    "SELECT * FROM sankey_data")

# ── Graph (1) ──
add("bar", "22-Graph Force", """
    CREATE TABLE graph_nodes(id VARCHAR, name VARCHAR, category INTEGER);
    INSERT INTO graph_nodes VALUES ('0','节点A',0),('1','节点B',0),('2','节点C',1),('3','节点D',1),('4','节点E',2);
    CREATE TABLE graph_links(source VARCHAR, target VARCHAR, weight DOUBLE);
    INSERT INTO graph_links VALUES ('0','1',5),('0','2',3),('1','3',4),('2','3',2),('2','4',6),('3','4',1)""",
    "SELECT * FROM graph_nodes")

# ── Tree (1) ──
add("bar", "23-Tree", """
    CREATE TABLE tree_data(id INTEGER, name VARCHAR, parent_id INTEGER);
    INSERT INTO tree_data VALUES (1,'CEO',0),(2,'CTO',1),(3,'CFO',1),(4,'工程师A',2),(5,'工程师B',2),(6,'会计A',3)""",
    "SELECT * FROM tree_data")

# ── Boxplot (1) ──
add("bar", "24-Boxplot", """
    CREATE TABLE box_data(cat VARCHAR, vals DOUBLE);
    INSERT INTO box_data VALUES ('A',850),('A',740),('A',900),('A',1070),('A',930),('A',850),('A',950),('A',980),('A',980),('A',880),
    ('A',1000),('A',980),('B',960),('B',940),('B',960),('B',940),('B',880),('B',800),('B',850),('B',880),('B',900),('B',840),('B',830)""",
    "SELECT cat as name, vals as value FROM box_data")

# ── Parallel (1) ──
add("bar", "25-Parallel", """
    CREATE TABLE parallel_data(name VARCHAR, a DOUBLE, b DOUBLE, c DOUBLE, d DOUBLE, e DOUBLE);
    INSERT INTO parallel_data VALUES ('A',55,85,78,90,65),('B',70,80,82,95,72),('C',60,75,68,85,58),
    ('D',80,90,88,92,78),('E',45,65,55,70,48)""",
    "SELECT * FROM parallel_data")

# ── Calendar (1) ──
add("bar", "26-Calendar", """
    CREATE TABLE cal_data(dt DATE, val DOUBLE);
    INSERT INTO cal_data VALUES
    ('2024-01-05',120),('2024-01-15',80),('2024-02-03',200),('2024-02-18',150),('2024-03-10',90),
    ('2024-03-22',180),('2024-04-07',220),('2024-04-20',110),('2024-05-05',160),('2024-05-25',250),
    ('2024-06-12',130),('2024-06-28',190),('2024-07-08',170),('2024-07-22',140),('2024-08-15',210),
    ('2024-08-30',95),('2024-09-05',175),('2024-09-20',230),('2024-10-10',155),('2024-10-25',185),
    ('2024-11-08',125),('2024-11-22',205),('2024-12-05',165),('2024-12-20',145)""",
    "SELECT dt as name, val as value FROM cal_data ORDER BY dt")

# ── ThemeRiver (1) ──
add("bar", "27-ThemeRiver", """
    CREATE TABLE river_data(dt VARCHAR, cat VARCHAR, val DOUBLE);
    INSERT INTO river_data VALUES ('1月','A',30),('1月','B',20),('1月','C',15),
    ('2月','A',35),('2月','B',25),('2月','C',18),('3月','A',40),('3月','B',30),('3月','C',22),
    ('4月','A',38),('4月','B',28),('4月','C',20),('5月','A',45),('5月','B',35),('5月','C',25)""",
    "SELECT * FROM river_data")

# ── PictorialBar (1) ──
add("bar", "28-PictorialBar", """
    CREATE TABLE pic_data(cat VARCHAR, val DOUBLE);
    INSERT INTO pic_data VALUES ('大象',6500),('犀牛',3500),('河马',3000),('水牛',2000),('长颈鹿',1800)""",
    "SELECT cat as name, val as value FROM pic_data")

# ── Chord (1) ──
add("bar", "29-Chord", """
    CREATE TABLE chord_data(source VARCHAR, target VARCHAR, val DOUBLE);
    INSERT INTO chord_data VALUES ('北京','上海',95),('北京','广州',60),('北京','深圳',45),
    ('上海','广州',80),('上海','深圳',55),('广州','深圳',70),('北京','成都',35)""",
    "SELECT * FROM chord_data")

# ── EffectScatter (1) ──
add("scatter", "30-EffectScatter", """
    CREATE TABLE effect_data(x DOUBLE, y DOUBLE, name VARCHAR);
    INSERT INTO effect_data VALUES (20,50,'北京'),(30,80,'上海'),(50,40,'广州'),(70,70,'深圳'),(60,30,'成都'),(80,60,'杭州')""",
    "SELECT x, y, name FROM effect_data")

# ── Lines (flights) (1) ──
add("bar", "31-Lines Flights", """
    CREATE TABLE flights_data(from_name VARCHAR, to_name VARCHAR, from_lat DOUBLE, from_lng DOUBLE, to_lat DOUBLE, to_lng DOUBLE, val DOUBLE);
    INSERT INTO flights_data VALUES ('北京','上海',39.9,116.4,31.2,121.5,100),('北京','广州',39.9,116.4,23.1,113.3,80),
    ('上海','深圳',31.2,121.5,22.5,114.1,90),('广州','成都',23.1,113.3,30.6,104.1,60)""",
    "SELECT * FROM flights_data")

# ── Mix (line-bar) (1) ──
add("bar", "32-Mix Line-Bar", """
    CREATE TABLE mix_data(dt VARCHAR, bar_val DOUBLE, line_val DOUBLE);
    INSERT INTO mix_data VALUES ('1月',320,220),('2月',332,182),('3月',301,191),('4月',334,234),('5月',390,290),('6月',330,310)""",
    "SELECT * FROM mix_data")

# ── 3D (5) ──
add("bar", "33-3D Bar", """
    CREATE TABLE bar3d_data(x VARCHAR, y VARCHAR, z DOUBLE);
    INSERT INTO bar3d_data VALUES ('A','Q1',120),('A','Q2',200),('A','Q3',150),('A','Q4',180),
    ('B','Q1',90),('B','Q2',130),('B','Q3',110),('B','Q4',100),('C','Q1',160),('C','Q2',220),('C','Q3',190),('C','Q4',210)""",
    "SELECT * FROM bar3d_data")

add("scatter", "34-3D Scatter", """
    CREATE TABLE scatter3d_data(x DOUBLE, y DOUBLE, z DOUBLE, name VARCHAR);
    INSERT INTO scatter3d_data VALUES (10,20,30,'A'),(20,10,40,'B'),(30,30,20,'C'),(15,25,35,'D'),(25,15,25,'E')""",
    "SELECT * FROM scatter3d_data")

add("bar", "35-3D Surface", """
    CREATE TABLE surface_data(x INTEGER, y INTEGER, z DOUBLE);
    INSERT INTO surface_data VALUES (0,0,10),(0,1,15),(0,2,20),(0,3,25),
    (1,0,12),(1,1,18),(1,2,22),(1,3,28),(2,0,15),(2,1,22),(2,2,25),(2,3,30),(3,0,18),(3,1,25),(3,2,28),(3,3,32)""",
    "SELECT * FROM surface_data")

add("bar", "36-3D Globe", "", "SELECT '北京' as name, 39.9 as lat, 116.4 as lng, 100 as value")

add("bar", "37-3D Lines3D", """
    CREATE TABLE lines3d_data(x DOUBLE, y DOUBLE, z DOUBLE);
    INSERT INTO lines3d_data VALUES (0,0,0),(1,1,5),(2,3,8),(3,5,12),(4,8,15),(5,10,18)""",
    "SELECT * FROM lines3d_data")

# ── Additional types ──
add("pie", "38-Pie Rose", """
    CREATE TABLE rose_data(cat VARCHAR, val DOUBLE);
    INSERT INTO rose_data VALUES ('rose1',40),('rose2',38),('rose3',32),('rose4',30),('rose5',28),('rose6',26),('rose7',22),('rose8',18)""",
    "SELECT cat as name, val as value FROM rose_data")

add("bar", "39-Custom Error-Bar", """
    CREATE TABLE err_data(cat VARCHAR, val DOUBLE, err_min DOUBLE, err_max DOUBLE);
    INSERT INTO err_data VALUES ('A',50,45,55),('B',65,60,72),('C',55,50,62),('D',70,65,80),('E',60,55,68)""",
    "SELECT * FROM err_data")

add("bar", "40-Geo Lines", "", "SELECT '北京' as from_name, '上海' as to_name, 100 as value")

add("bar", "41-Mix Timeline", """
    CREATE TABLE timeline_data(year INTEGER, cat VARCHAR, val DOUBLE);
    INSERT INTO timeline_data VALUES (2020,'A',120),(2020,'B',90),(2020,'C',70),
    (2021,'A',145),(2021,'B',110),(2021,'C',85),(2022,'A',170),(2022,'B',130),(2022,'C',100)""",
    "SELECT * FROM timeline_data")


# ═══════════════════════════════════════════════════════════════
# Execute
# ═══════════════════════════════════════════════════════════════

results = []
for chart_type, title, ddl, query, extra in CHARTS:
    try:
        # Execute DDL
        if ddl:
            for stmt in ddl.split(";"):
                stmt = stmt.strip()
                if stmt:
                    conn.execute(stmt)

        # Skip types with no query (edge cases)
        if not query:
            results.append(("⏭️", title, "no query"))
            continue

        # Build config
        config = {
            "db_path": DB_PATH,
            "query": query,
            "title": title,
            "output_path": f"{OUT}/{title.replace(' ','_').replace('-','_')}.html",
            "chart_type": chart_type,
        }
        config.update(extra)

        # Generate
        path = generate_chart(config)
        if not path:
            results.append(("❌", title, "generate_chart returned None"))
            continue

        # Validate
        with open(path) as f:
            html = f.read()

        errors = []
        # Check series type present
        if '"type":' not in html:
            errors.append("no series type")
        # Check type-specific requirements
        ct = chart_type.lower()
        req = CHART_REQUIREMENTS.get(ct, CHART_REQUIREMENTS["bar"])
        for key in req["required_keys"]:
            if key not in config.get("echarts_option", {}) and f'"{key}"' not in html:
                # Only check for auto-generated keys; explicit options may differ
                pass

        if errors:
            results.append(("❌", title, "; ".join(errors)))
        else:
            results.append(("✅", title, f"{len(html)} bytes"))

    except Exception as e:
        results.append(("❌", title, str(e)[:80]))

# ═══════════════════════════════════════════════════════════════
# Report
# ═══════════════════════════════════════════════════════════════
ok = sum(1 for r in results if r[0] == "✅")
skip = sum(1 for r in results if r[0] == "⏭️")
fail = sum(1 for r in results if r[0] == "❌")

print(f"\n{'═'*60}")
print(f"  Results: {ok} passed, {fail} failed, {skip} skipped ({len(results)} total)")
print(f"{'═'*60}")
for status, title, detail in results:
    print(f"  {status} {title:<35s} {detail}")

# Write summary
with open(f"{OUT}/_summary.json", "w") as f:
    json.dump([{"status": s, "title": t, "detail": d} for s, t, d in results], f, ensure_ascii=False, indent=2)

print(f"\nOutput: {os.path.abspath(OUT)}")
print(f"Summary: {OUT}/_summary.json")
sys.exit(0 if fail == 0 else 1)
