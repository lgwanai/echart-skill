#!/usr/bin/env python3
"""Generate e-commerce weekly operational analysis HTML report."""
import json
import os

# Read ECharts library
echarts_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'echarts', 'echarts.min.js')
with open(echarts_path, 'r', encoding='utf-8') as f:
    echarts_js = f.read()

# ===== DATA =====
kpi_this_week = {
    "gmv": 987089, "orders": 23032, "sales_volume": 24862,
    "visitors": 1301600, "impressions": 7055548, "cart_adds": 28954,
    "aov": 42.86, "order_conv": 1.77, "refunds": 830, "refund_pct": 3.34
}
kpi_last_week = {
    "gmv": 655806, "orders": 15075, "sales_volume": 16371,
    "visitors": 854273, "impressions": 4695807, "cart_adds": 18688,
    "aov": 43.50, "order_conv": 1.76, "refunds": 366, "refund_pct": 2.24
}

daily_data = [
    {"date": "08-03", "weekday": "周一", "gmv": 93428, "orders": 2124, "visitors": 123616, "cart_adds": 2618, "sales_volume": 2331, "refunds": 53},
    {"date": "08-04", "weekday": "周二", "gmv": 88565, "orders": 2040, "visitors": 113457, "cart_adds": 2421, "sales_volume": 2190, "refunds": 47},
    {"date": "08-05", "weekday": "周三", "gmv": 86306, "orders": 2092, "visitors": 115232, "cart_adds": 2561, "sales_volume": 2202, "refunds": 47},
    {"date": "08-06", "weekday": "周四", "gmv": 85819, "orders": 2014, "visitors": 115195, "cart_adds": 2543, "sales_volume": 2167, "refunds": 45},
    {"date": "08-07", "weekday": "周五", "gmv": 88631, "orders": 2099, "visitors": 123379, "cart_adds": 2604, "sales_volume": 2233, "refunds": 47},
    {"date": "08-08", "weekday": "周六", "gmv": 267041, "orders": 6237, "visitors": 353315, "cart_adds": 8105, "sales_volume": 6766, "refunds": 298},
    {"date": "08-09", "weekday": "周日", "gmv": 277299, "orders": 6426, "visitors": 357406, "cart_adds": 8102, "sales_volume": 6973, "refunds": 293}
]

channel_data = [
    {"channel": "天猫", "gmv": 269438, "orders": 5947, "sales_volume": 6179, "visitors": 218225, "conv_rate": 2.97, "refund_rate": 1.39, "aov": 45.31},
    {"channel": "京东", "gmv": 232352, "orders": 4658, "sales_volume": 5122, "visitors": 208977, "conv_rate": 2.47, "refund_rate": 0.92, "aov": 49.88},
    {"channel": "拼多多", "gmv": 209390, "orders": 6697, "sales_volume": 7364, "visitors": 602880, "conv_rate": 0.60, "refund_rate": 1.95, "aov": 31.27},
    {"channel": "抖音", "gmv": 181980, "orders": 3905, "sales_volume": 4214, "visitors": 214220, "conv_rate": 2.01, "refund_rate": 5.14, "aov": 46.60},
    {"channel": "微信小程序", "gmv": 93929, "orders": 1825, "sales_volume": 1983, "visitors": 57298, "conv_rate": 3.51, "refund_rate": 0.89, "aov": 51.47}
]

channel_wow = [
    {"channel": "天猫", "last_gmv": 186904, "this_gmv": 269438, "last_orders": 3897, "this_orders": 5947},
    {"channel": "京东", "last_gmv": 147636, "this_gmv": 232352, "last_orders": 2972, "this_orders": 4658},
    {"channel": "拼多多", "last_gmv": 137450, "this_gmv": 209390, "last_orders": 4412, "this_orders": 6697},
    {"channel": "抖音", "last_gmv": 120781, "this_gmv": 181980, "last_orders": 2575, "this_orders": 3905},
    {"channel": "微信小程序", "last_gmv": 63035, "this_gmv": 93929, "last_orders": 1219, "this_orders": 1825}
]

series_data = [
    {"series": "经典系列", "gmv": 489473, "orders": 9167, "sales_volume": 10004, "visitors": 567617, "conv_rate": 2.40, "refund_rate": 2.48, "aov": 53.40},
    {"series": "烘焙系列", "gmv": 181326, "orders": 3547, "sales_volume": 3549, "visitors": 148286, "conv_rate": 2.21, "refund_rate": 1.52, "aov": 51.12},
    {"series": "饮品系列", "gmv": 176438, "orders": 9135, "sales_volume": 10040, "visitors": 535252, "conv_rate": 2.44, "refund_rate": 2.89, "aov": 19.31},
    {"series": "联名系列", "gmv": 139852, "orders": 1183, "sales_volume": 1269, "visitors": 50445, "conv_rate": 2.23, "refund_rate": 1.47, "aov": 118.22}
]

product_data = [
    {"product": "锋味派午餐肉（原味）", "series": "经典系列", "gmv": 281316, "orders": 5179, "sales_volume": 5663, "visitors": 318072, "conv_rate": 2.41, "refund_rate": 2.45, "aov": 54.32, "inventory": 33038},
    {"product": "锋味派午餐肉（黑椒）", "series": "经典系列", "gmv": 208157, "orders": 3988, "sales_volume": 4341, "visitors": 249545, "conv_rate": 2.38, "refund_rate": 2.50, "aov": 52.20, "inventory": 23636},
    {"product": "锋味派港式奶茶（瓶装）", "series": "饮品系列", "gmv": 176438, "orders": 9135, "sales_volume": 10040, "visitors": 535252, "conv_rate": 2.44, "refund_rate": 2.89, "aov": 19.31, "inventory": 45435},
    {"product": "锋味派×海绵宝宝 曲奇礼盒", "series": "联名系列", "gmv": 139852, "orders": 1183, "sales_volume": 1269, "visitors": 50445, "conv_rate": 2.23, "refund_rate": 1.47, "aov": 118.22, "inventory": 8896},
    {"product": "锋味派蛋挞（原味）", "series": "烘焙系列", "gmv": 114823, "orders": 2083, "sales_volume": 2250, "visitors": 87212, "conv_rate": 2.20, "refund_rate": 1.75, "aov": 55.12, "inventory": 13154},
    {"product": "锋味派蛋挞（芝士）", "series": "烘焙系列", "gmv": 66503, "orders": 1464, "sales_volume": 1299, "visitors": 61074, "conv_rate": 2.21, "refund_rate": 1.28, "aov": 45.43, "inventory": 11302}
]

all_data = {
    "kpi_this_week": kpi_this_week,
    "kpi_last_week": kpi_last_week,
    "daily": daily_data,
    "channels": channel_data,
    "channel_wow": channel_wow,
    "series": series_data,
    "products": product_data
}
data_json = json.dumps(all_data, ensure_ascii=False)

# ===== Build HTML parts =====
# Part 1: Head + CSS (no f-string to avoid escaping issues)
HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>电商运营分析周报 | 2026.08.03 - 08.09</title>
<script>__ECHARTS_PLACEHOLDER__</script>
<style>
:root {
  --bg: #f0f2f5; --card-bg: #ffffff;
  --text-primary: #1a1a2e; --text-secondary: #6c757d; --text-muted: #adb5bd;
  --border: #e9ecef; --primary: #4f6df5; --primary-light: #e8edfe;
  --success: #00b42a; --success-light: #e8ffea;
  --danger: #f5392c; --danger-light: #ffece8;
  --warning: #ff7d00; --warning-light: #fff3e8;
  --orange: #fa8c16; --cyan: #13c2c2; --purple: #722ed1;
  --shadow: 0 2px 8px rgba(0,0,0,0.06); --shadow-hover: 0 4px 16px rgba(0,0,0,0.1);
  --radius: 12px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: var(--bg); color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 14px; line-height: 1.6; -webkit-font-smoothing: antialiased;
}
.container { max-width: 1280px; margin: 0 auto; padding: 24px; }

.report-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius); padding: 32px 40px; margin-bottom: 24px;
  color: #fff; position: relative; overflow: hidden;
}
.report-header::after {
  content: ''; position: absolute; top: -50%; right: -10%;
  width: 400px; height: 400px; background: rgba(255,255,255,0.05); border-radius: 50%;
}
.report-header h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; position: relative; z-index: 1; }
.report-header .subtitle { font-size: 15px; opacity: 0.9; position: relative; z-index: 1; }
.report-header .meta { display: flex; gap: 24px; margin-top: 16px; position: relative; z-index: 1; flex-wrap: wrap; }
.report-header .meta-item { display: flex; align-items: center; gap: 6px; font-size: 13px; opacity: 0.85; }
.report-header .meta-item::before {
  content: ''; width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.6);
}

.section { margin-bottom: 24px; }
.section-title {
  font-size: 18px; font-weight: 600; color: var(--text-primary);
  margin-bottom: 16px; padding-left: 12px; border-left: 4px solid var(--primary);
  display: flex; align-items: center; gap: 8px;
}
.section-title .badge {
  font-size: 12px; font-weight: 400; color: var(--text-secondary);
  background: var(--border); padding: 2px 10px; border-radius: 20px;
}

.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 24px; }
.kpi-card {
  background: var(--card-bg); border-radius: var(--radius); padding: 20px;
  box-shadow: var(--shadow); transition: box-shadow 0.3s; position: relative; overflow: hidden; min-width: 0;
}
.kpi-card:hover { box-shadow: var(--shadow-hover); }
.kpi-card .kpi-icon {
  position: absolute; top: 16px; right: 16px;
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.kpi-card .kpi-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; overflow-wrap: anywhere; }
.kpi-card .kpi-value { font-size: 26px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; overflow-wrap: anywhere; }
.kpi-card .kpi-compare { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.kpi-card .change-up { color: #f5392c; font-weight: 600; }
.kpi-card .change-down { color: #00b42a; font-weight: 600; }
.kpi-card .change-neutral { color: #adb5bd; font-weight: 600; }
.kpi-card .kpi-compare .label { color: var(--text-muted); }

.chart-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 24px; }
.chart-grid .full-width { grid-column: 1 / -1; }
.chart-card {
  background: var(--card-bg); border-radius: var(--radius); padding: 24px;
  box-shadow: var(--shadow); min-width: 0; display: flex; flex-direction: column;
}
.chart-card .chart-header { margin-bottom: 16px; display: flex; justify-content: space-between; align-items: flex-start; }
.chart-card .chart-header-left { flex: 1; min-width: 0; }
.chart-card .chart-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; overflow-wrap: anywhere; }
.chart-card .chart-scope { font-size: 12px; color: var(--text-muted); }
.btn-view-data {
  flex-shrink: 0; background: var(--primary-light); color: var(--primary); border: none;
  padding: 4px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
  transition: background 0.2s; white-space: nowrap;
}
.btn-view-data:hover { background: #d0d8fc; }
.chart-container { width: 100%; }
.chart-data-table { display: none; margin-top: 16px; overflow-x: auto; }
.chart-data-table.show { display: block; }
.chart-data-table table { width: 100%; border-collapse: collapse; font-size: 12px; }
.chart-data-table th { background: #f8f9fa; padding: 8px 12px; text-align: left; color: #6c757d; font-weight: 600; border-bottom: 1px solid var(--border); }
.chart-data-table td { padding: 6px 12px; border-bottom: 1px solid var(--border); }

.data-table-card {
  background: var(--card-bg); border-radius: var(--radius); padding: 24px;
  box-shadow: var(--shadow); margin-bottom: 24px; min-width: 0;
}
.data-table-card .table-header { margin-bottom: 16px; }
.data-table-card .table-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.data-table-card .table-scope { font-size: 12px; color: var(--text-muted); }
.table-wrapper { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead th {
  background: #f8f9fa; color: var(--text-secondary); font-weight: 600;
  padding: 12px 16px; text-align: left; border-bottom: 2px solid var(--border);
  white-space: nowrap; position: sticky; top: 0;
}
tbody td { padding: 10px 16px; border-bottom: 1px solid var(--border); color: var(--text-primary); }
tbody tr:hover { background: #f8f9fa; }
tbody td.num { text-align: right; font-variant-numeric: tabular-nums; }
.tag { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; }
.tag-blue { background: var(--primary-light); color: var(--primary); }
.tag-green { background: var(--success-light); color: var(--success); }
.tag-orange { background: var(--warning-light); color: var(--warning); }
.tag-purple { background: #f5f0ff; color: var(--purple); }

.insight-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.insight-card {
  background: var(--card-bg); border-radius: var(--radius); padding: 20px;
  box-shadow: var(--shadow); border-left: 4px solid var(--primary); min-width: 0;
}
.insight-card.danger { border-left-color: var(--danger); }
.insight-card.success { border-left-color: var(--success); }
.insight-card.warning { border-left-color: var(--warning); }
.insight-card .insight-tag {
  display: inline-block; font-size: 11px; font-weight: 600;
  padding: 2px 8px; border-radius: 4px; margin-bottom: 8px;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.insight-card.danger .insight-tag { background: var(--danger-light); color: var(--danger); }
.insight-card.success .insight-tag { background: var(--success-light); color: var(--success); }
.insight-card.warning .insight-tag { background: var(--warning-light); color: var(--warning); }
.insight-card .insight-tag.default { background: var(--primary-light); color: var(--primary); }
.insight-card h4 { font-size: 15px; font-weight: 600; margin-bottom: 8px; color: var(--text-primary); overflow-wrap: anywhere; }
.insight-card p { font-size: 13px; color: var(--text-secondary); line-height: 1.7; overflow-wrap: anywhere; }
.insight-card .highlight { color: var(--danger); font-weight: 600; }
.insight-card .highlight-green { color: var(--success); font-weight: 600; }

.report-footer {
  text-align: center; padding: 24px; color: var(--text-muted); font-size: 12px;
  border-top: 1px solid var(--border); margin-top: 16px;
}
.report-footer .footer-info { margin-top: 8px; }

@media (max-width: 1024px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
  .chart-grid { grid-template-columns: 1fr; }
  .insight-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .container { padding: 12px; }
}
</style>
</head>
<body>
<div class="container">

  <div class="report-header">
    <h1>电商运营分析周报</h1>
    <div class="subtitle">锋味派品牌全渠道电商运营数据周报</div>
    <div class="meta">
      <span class="meta-item">报告周期: 2026年8月3日 - 8月9日</span>
      <span class="meta-item">对比周期: 2026年7月27日 - 8月2日</span>
      <span class="meta-item">数据来源: 电商销售宽表 (2220条记录)</span>
    </div>
  </div>

  <div class="section">
    <div class="section-title">核心指标总览 <span class="badge">本周 vs 上周</span></div>
    <div class="kpi-grid" id="kpiGrid"></div>
  </div>

  <div class="section">
    <div class="section-title">每日运营趋势 <span class="badge">08.03 - 08.09</span></div>
    <div class="chart-grid">
      <div class="chart-card full-width">
        <div class="chart-header">
          <div class="chart-header-left">
            <h3>每日GMV与订单量趋势</h3>
            <div class="chart-scope">统计口径: 按日汇总全渠道GMV及支付订单数 | 数据来源: ecommerce_sales表</div>
          </div>
          <button class="btn-view-data" data-action="view-data" data-target="dt-daily">查看数据</button>
        </div>
        <div class="chart-container" id="chartDailyGMV" style="height: 360px;"></div>
        <div class="chart-data-table" id="dt-daily"></div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">渠道分析 <span class="badge">5个电商渠道</span></div>
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-header-left">
            <h3>各渠道GMV分布</h3>
            <div class="chart-scope">统计口径: 本周各渠道GMV汇总 | 数据来源: ecommerce_sales表</div>
          </div>
          <button class="btn-view-data" data-action="view-data" data-target="dt-channel-pie">查看数据</button>
        </div>
        <div class="chart-container" id="chartChannelPie" style="height: 320px;"></div>
        <div class="chart-data-table" id="dt-channel-pie"></div>
      </div>
      <div class="chart-card full-width">
        <div class="chart-header">
          <div class="chart-header-left">
            <h3>渠道GMV环比增长对比</h3>
            <div class="chart-scope">统计口径: 本周vs上周各渠道GMV | 数据来源: ecommerce_sales表</div>
          </div>
          <button class="btn-view-data" data-action="view-data" data-target="dt-channel-wow">查看数据</button>
        </div>
        <div class="chart-container" id="chartChannelWoW" style="height: 320px;"></div>
        <div class="chart-data-table" id="dt-channel-wow"></div>
      </div>
    </div>
  </div>

  <div class="data-table-card">
    <div class="table-header">
      <h3>各渠道运营明细</h3>
      <div class="table-scope">统计口径: 本周(08.03-08.09)各渠道核心指标汇总 | 数据来源: ecommerce_sales表</div>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr><th>渠道</th><th class="num">GMV(元)</th><th class="num">订单数</th><th class="num">销量(件)</th><th class="num">访客数</th><th class="num">转化率(%)</th><th class="num">客单价(元)</th><th class="num">退款率(%)</th></tr>
        </thead>
        <tbody id="channelTableBody"></tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <div class="section-title">产品系列分析 <span class="badge">4大系列</span></div>
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-header-left">
            <h3>各产品系列GMV贡献</h3>
            <div class="chart-scope">统计口径: 本周各产品系列GMV汇总 | 数据来源: ecommerce_sales表</div>
          </div>
          <button class="btn-view-data" data-action="view-data" data-target="dt-series-bar">查看数据</button>
        </div>
        <div class="chart-container" id="chartSeriesBar" style="height: 320px;"></div>
        <div class="chart-data-table" id="dt-series-bar"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-header-left">
            <h3>系列客单价 vs 转化率</h3>
            <div class="chart-scope">统计口径: 本周各系列客单价及转化率对比 | 数据来源: ecommerce_sales表</div>
          </div>
          <button class="btn-view-data" data-action="view-data" data-target="dt-series-scatter">查看数据</button>
        </div>
        <div class="chart-container" id="chartSeriesScatter" style="height: 320px;"></div>
        <div class="chart-data-table" id="dt-series-scatter"></div>
      </div>
    </div>
  </div>

  <div class="data-table-card">
    <div class="table-header">
      <h3>单品运营表现</h3>
      <div class="table-scope">统计口径: 本周(08.03-08.09)各SKU核心指标汇总, 按GMV降序 | 数据来源: ecommerce_sales表</div>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr><th>排名</th><th>产品名称</th><th>系列</th><th class="num">GMV(元)</th><th class="num">订单数</th><th class="num">销量(件)</th><th class="num">访客数</th><th class="num">转化率(%)</th><th class="num">客单价(元)</th><th class="num">退款率(%)</th><th class="num">库存(件)</th></tr>
        </thead>
        <tbody id="productTableBody"></tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <div class="section-title">转化漏斗分析 <span class="badge">曝光-访客-加购-支付</span></div>
    <div class="chart-grid">
      <div class="chart-card full-width">
        <div class="chart-header">
          <div class="chart-header-left">
            <h3>本周全渠道转化漏斗</h3>
            <div class="chart-scope">统计口径: 本周全渠道汇总, 曝光-访客-加购-支付订单逐级转化 | 数据来源: ecommerce_sales表</div>
          </div>
          <button class="btn-view-data" data-action="view-data" data-target="dt-funnel">查看数据</button>
        </div>
        <div class="chart-container" id="chartFunnel" style="height: 360px;"></div>
        <div class="chart-data-table" id="dt-funnel"></div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">关键洞察与建议</div>
    <div class="insight-grid">
      <div class="insight-card success">
        <span class="insight-tag">增长亮点</span>
        <h4>GMV环比增长50.5%, 周末爆发显著</h4>
        <p>本周GMV达<span class="highlight-green">98.7万元</span>, 较上周增长50.5%。周六周日两天贡献GMV占比达<span class="highlight-green">55.1%</span>, 周末大促效应明显, 建议持续加码周末营销资源投入。</p>
      </div>
      <div class="insight-card danger">
        <span class="insight-tag">风险预警</span>
        <h4>退款率上升至3.34%, 需重点关注</h4>
        <p>本周退款率从上周2.24%升至<span class="highlight">3.34%</span>, 增幅49.1%。其中抖音渠道退款率高达<span class="highlight">5.14%</span>, 为全渠道最高, 需排查产品质量及物流履约问题。</p>
      </div>
      <div class="insight-card warning">
        <span class="insight-tag">效率关注</span>
        <h4>拼多多转化率仅0.60%, 流量效率偏低</h4>
        <p>拼多多渠道访客数达60.3万(占比46.3%), 但转化率仅<span class="highlight">0.60%</span>, 远低于其他渠道。GMV占比仅21.2%, 流量变现效率亟需提升, 建议优化商品详情页及价格策略。</p>
      </div>
      <div class="insight-card">
        <span class="insight-tag default">结构分析</span>
        <h4>经典系列贡献近半GMV, 联名系列高客单</h4>
        <p>经典系列GMV占比<span class="highlight-green">49.6%</span>, 为核心利润来源。联名系列客单价达118.22元, 远超其他系列, 但销量偏低, 建议扩大联名产品线提升整体GMV。</p>
      </div>
      <div class="insight-card">
        <span class="insight-tag default">渠道策略</span>
        <h4>微信小程序转化率最优, 客单价最高</h4>
        <p>微信小程序转化率<span class="highlight-green">3.51%</span>、客单价51.47元, 均为全渠道最优。虽GMV体量较小, 但私域运营质量高, 建议加大私域引流投入。</p>
      </div>
      <div class="insight-card warning">
        <span class="insight-tag">库存预警</span>
        <h4>联名系列库存需关注补货节奏</h4>
        <p>锋味派x海绵宝宝曲奇礼盒库存仅8,896件, 按本周日均销量181件计算, 可售约<span class="highlight">49天</span>。建议关注联名系列补货节奏, 避免断货影响销售。</p>
      </div>
    </div>
  </div>

  <div class="report-footer">
    <div>锋味派电商运营分析周报 | 报告周期: 2026.08.03 - 2026.08.09</div>
    <div class="footer-info">数据来源: 电商销售宽表(共2,220条记录, 覆盖5渠道/4系列/6SKU) | 生成时间: 2026-08-14 | 统计口径: 按日全渠道汇总</div>
  </div>
</div>
"""

# Part 2: JavaScript (as a plain string, no f-string)
HTML_JS = r"""<script>
var D = __DATA_PLACEHOLDER__;

// ===== Helper =====
function fmt(n) {
  if (n >= 10000) return (n / 10000).toFixed(2) + '万';
  return n.toLocaleString();
}
function toggleChartData(targetId) {
  var el = document.getElementById(targetId);
  if (el) el.classList.toggle('show');
}
function openChartData(targetId) { toggleChartData(targetId); }
function showChartData(targetId) { toggleChartData(targetId); }
document.querySelectorAll('[data-action="view-data"]').forEach(function(btn) {
  btn.addEventListener('click', function() {
    toggleChartData(this.getAttribute('data-target'));
  });
});
function makeTable(headers, rows) {
  var h = '<table><thead><tr>';
  headers.forEach(function(hd) { h += '<th>' + hd + '</th>'; });
  h += '</tr></thead><tbody>';
  rows.forEach(function(r) {
    h += '<tr>';
    r.forEach(function(c) { h += '<td>' + c + '</td>'; });
    h += '</tr>';
  });
  h += '</tbody></table>';
  return h;
}

// ===== KPI Cards =====
(function() {
  var tw = D.kpi_this_week, lw = D.kpi_last_week;
  function pct(curr, prev) { return prev === 0 ? 0 : ((curr - prev) / prev * 100); }
  function changeClass(v, higherIsBad) {
    if (Math.abs(v) < 0.1) return 'change-neutral';
    if (v > 0) return higherIsBad ? 'change-up' : 'change-down';
    return higherIsBad ? 'change-down' : 'change-up';
  }
  function arrow(v) { return Math.abs(v) < 0.1 ? '→' : (v > 0 ? '↑' : '↓'); }

  var cards = [
    {label: 'GMV', value: fmt(tw.gmv) + '元', icon: '💰', iconBg: '#e8edfe', iconColor: '#4f6df5', change: pct(tw.gmv, lw.gmv), lastVal: fmt(lw.gmv) + '元', higherIsBad: false},
    {label: '支付订单数', value: fmt(tw.orders), icon: '📦', iconBg: '#e8ffea', iconColor: '#00b42a', change: pct(tw.orders, lw.orders), lastVal: fmt(lw.orders), higherIsBad: false},
    {label: '访客数', value: fmt(tw.visitors), icon: '👥', iconBg: '#fff3e8', iconColor: '#ff7d00', change: pct(tw.visitors, lw.visitors), lastVal: fmt(lw.visitors), higherIsBad: false},
    {label: '客单价', value: '¥' + tw.aov, icon: '🏷️', iconBg: '#f5f0ff', iconColor: '#722ed1', change: pct(tw.aov, lw.aov), lastVal: '¥' + lw.aov, higherIsBad: false},
    {label: '退款率', value: tw.refund_pct + '%', icon: '⚠️', iconBg: '#ffece8', iconColor: '#f5392c', change: tw.refund_pct - lw.refund_pct, lastVal: lw.refund_pct + '%', higherIsBad: true, isPP: true}
  ];

  var html = '';
  cards.forEach(function(c) {
    var chgText = c.isPP ? c.change.toFixed(2) + 'pp' : Math.abs(c.change).toFixed(1) + '%';
    html += '<div class="kpi-card">' +
      '<div class="kpi-icon" style="background:' + c.iconBg + ';color:' + c.iconColor + ';">' + c.icon + '</div>' +
      '<div class="kpi-label">' + c.label + '</div>' +
      '<div class="kpi-value">' + c.value + '</div>' +
      '<div class="kpi-compare">' +
        '<span class="' + changeClass(c.change, c.higherIsBad) + '">' + arrow(c.change) + ' ' + chgText + '</span>' +
        '<span class="label">vs上周 ' + c.lastVal + '</span>' +
      '</div></div>';
  });
  document.getElementById('kpiGrid').innerHTML = html;
})();

// ===== Daily GMV Chart =====
(function() {
  var chart = echarts.init(document.getElementById('chartDailyGMV'));
  var days = D.daily.map(function(d) { return d.weekday + '(' + d.date + ')'; });
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: ['GMV(元)', '支付订单数', '访客数'], top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: days, axisLabel: { fontSize: 12 } },
    yAxis: [
      { type: 'value', name: 'GMV/订单', position: 'left', axisLabel: { formatter: function(v) { return v >= 10000 ? (v/10000).toFixed(0) + '万' : v; } } },
      { type: 'value', name: '访客数', position: 'right', axisLabel: { formatter: function(v) { return v >= 10000 ? (v/10000).toFixed(0) + '万' : v; } } }
    ],
    series: [
      { name: 'GMV(元)', type: 'bar', barWidth: '40%', itemStyle: { color: '#4f6df5', borderRadius: [4, 4, 0, 0] }, data: D.daily.map(function(d) { return d.gmv; }) },
      { name: '支付订单数', type: 'line', yAxisIndex: 0, smooth: true, itemStyle: { color: '#00b42a' }, lineStyle: { width: 2 }, data: D.daily.map(function(d) { return d.orders; }) },
      { name: '访客数', type: 'line', yAxisIndex: 1, smooth: true, itemStyle: { color: '#ff7d00' }, lineStyle: { width: 2 }, data: D.daily.map(function(d) { return d.visitors; }) }
    ]
  });
  window.addEventListener('resize', function() { chart.resize(); });

  // Data table
  var rows = D.daily.map(function(d) {
    return [d.weekday, d.date, fmt(d.gmv), d.orders.toLocaleString(), d.visitors.toLocaleString(), d.cart_adds.toLocaleString(), d.sales_volume.toLocaleString(), d.refunds];
  });
  document.getElementById('dt-daily').innerHTML = makeTable(['星期','日期','GMV(元)','订单数','访客数','加购量','销量(件)','退款量'], rows);
})();

// ===== Channel Pie =====
(function() {
  var chart = echarts.init(document.getElementById('chartChannelPie'));
  var colors = ['#4f6df5', '#00b42a', '#ff7d00', '#722ed1', '#13c2c2'];
  var total = D.channels.reduce(function(s, c) { return s + c.gmv; }, 0);
  chart.setOption({
    tooltip: { trigger: 'item', formatter: function(p) { return p.name + '<br/>GMV: ¥' + p.value.toLocaleString() + ' (' + p.percent + '%)'; } },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { fontSize: 13 } },
    color: colors,
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['40%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: function(p) { return p.name + '\n' + p.percent + '%'; }, fontSize: 12 },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: D.channels.map(function(c, i) { return { name: c.channel, value: c.gmv, itemStyle: { color: colors[i] } }; })
    }]
  });
  window.addEventListener('resize', function() { chart.resize(); });

  var rows = D.channels.map(function(c) {
    return [c.channel, '¥' + c.gmv.toLocaleString(), (c.gmv/total*100).toFixed(1) + '%'];
  });
  document.getElementById('dt-channel-pie').innerHTML = makeTable(['渠道','GMV(元)','占比'], rows);
})();

// ===== Channel WoW =====
(function() {
  var chart = echarts.init(document.getElementById('chartChannelWoW'));
  var channels = D.channel_wow.map(function(c) { return c.channel; });
  var lastData = D.channel_wow.map(function(c) { return c.last_gmv; });
  var thisData = D.channel_wow.map(function(c) { return c.this_gmv; });
  var growthRates = D.channel_wow.map(function(c) { return ((c.this_gmv - c.last_gmv) / c.last_gmv * 100).toFixed(1); });
  chart.setOption({
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: function(params) {
        var s = params[0].name + '<br/>';
        params.forEach(function(p) { s += p.marker + p.seriesName + ': ¥' + p.value.toLocaleString() + '<br/>'; });
        var idx = channels.indexOf(params[0].name);
        s += '增长率: +' + growthRates[idx] + '%';
        return s;
      }
    },
    legend: { data: ['上周GMV', '本周GMV'], top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: channels, axisLabel: { fontSize: 13 } },
    yAxis: { type: 'value', name: 'GMV(元)', axisLabel: { formatter: function(v) { return v >= 10000 ? (v/10000).toFixed(0) + '万' : v; } } },
    series: [
      { name: '上周GMV', type: 'bar', barGap: 0, itemStyle: { color: '#c5cae9', borderRadius: [4, 4, 0, 0] }, data: lastData },
      { name: '本周GMV', type: 'bar', itemStyle: { color: '#4f6df5', borderRadius: [4, 4, 0, 0] }, data: thisData,
        label: { show: true, position: 'top', formatter: function(p) { return '+' + growthRates[p.dataIndex] + '%'; }, color: '#f5392c', fontSize: 11, fontWeight: 'bold' } }
    ]
  });
  window.addEventListener('resize', function() { chart.resize(); });

  var rows = D.channel_wow.map(function(c, i) {
    var gr = ((c.this_gmv - c.last_gmv) / c.last_gmv * 100).toFixed(1);
    return [c.channel, '¥' + c.last_gmv.toLocaleString(), '¥' + c.this_gmv.toLocaleString(), '+' + gr + '%'];
  });
  document.getElementById('dt-channel-wow').innerHTML = makeTable(['渠道','上周GMV','本周GMV','增长率'], rows);
})();

// ===== Channel Table =====
(function() {
  var html = '';
  var colors = { '天猫': 'tag-blue', '京东': 'tag-orange', '拼多多': 'tag-green', '抖音': 'tag-purple', '微信小程序': 'tag-blue' };
  D.channels.forEach(function(c) {
    html += '<tr>' +
      '<td><span class="tag ' + (colors[c.channel] || 'tag-blue') + '">' + c.channel + '</span></td>' +
      '<td class="num">¥' + c.gmv.toLocaleString() + '</td>' +
      '<td class="num">' + c.orders.toLocaleString() + '</td>' +
      '<td class="num">' + c.sales_volume.toLocaleString() + '</td>' +
      '<td class="num">' + c.visitors.toLocaleString() + '</td>' +
      '<td class="num">' + c.conv_rate.toFixed(2) + '%</td>' +
      '<td class="num">¥' + c.aov.toFixed(2) + '</td>' +
      '<td class="num" style="color:' + (c.refund_rate > 3 ? '#f5392c' : c.refund_rate > 1.5 ? '#ff7d00' : '#00b42a') + ';">' + c.refund_rate.toFixed(2) + '%</td>' +
    '</tr>';
  });
  document.getElementById('channelTableBody').innerHTML = html;
})();

// ===== Series Bar =====
(function() {
  var chart = echarts.init(document.getElementById('chartSeriesBar'));
  var colors = ['#4f6df5', '#00b42a', '#ff7d00', '#722ed1'];
  var total = D.series.reduce(function(s, x) { return s + x.gmv; }, 0);
  chart.setOption({
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: function(params) {
        var p = params[0];
        var pct = (p.value / total * 100).toFixed(1);
        return p.name + '<br/>GMV: ¥' + p.value.toLocaleString() + '<br/>占比: ' + pct + '%';
      }
    },
    grid: { left: '3%', right: '12%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', axisLabel: { formatter: function(v) { return v >= 10000 ? (v/10000).toFixed(0) + '万' : v; } } },
    yAxis: { type: 'category', data: D.series.map(function(s) { return s.series; }).reverse(), axisLabel: { fontSize: 13 } },
    series: [{
      type: 'bar', barWidth: '50%',
      itemStyle: { borderRadius: [0, 6, 6, 0], color: function(p) { return colors[D.series.length - 1 - p.dataIndex]; } },
      label: { show: true, position: 'right', formatter: function(p) { return '¥' + (p.value / 10000).toFixed(1) + '万'; }, fontSize: 12, color: '#333' },
      data: D.series.map(function(s) { return s.gmv; }).reverse()
    }]
  });
  window.addEventListener('resize', function() { chart.resize(); });

  var rows = D.series.map(function(s) {
    return [s.series, '¥' + s.gmv.toLocaleString(), (s.gmv/total*100).toFixed(1) + '%', s.orders.toLocaleString(), s.sales_volume.toLocaleString(), '¥' + s.aov.toFixed(2)];
  });
  document.getElementById('dt-series-bar').innerHTML = makeTable(['系列','GMV(元)','占比','订单数','销量(件)','客单价(元)'], rows);
})();

// ===== Series Scatter =====
(function() {
  var chart = echarts.init(document.getElementById('chartSeriesScatter'));
  var colors = ['#4f6df5', '#00b42a', '#ff7d00', '#722ed1'];
  chart.setOption({
    tooltip: {
      formatter: function(p) {
        return p.data.name + '<br/>客单价: ¥' + p.data.value[0] + '<br/>转化率: ' + p.data.value[1] + '%<br/>GMV: ¥' + p.data.value[2].toLocaleString();
      }
    },
    grid: { left: '8%', right: '5%', bottom: '10%', containLabel: true },
    xAxis: { type: 'value', name: '客单价(元)', nameLocation: 'middle', nameGap: 30, min: 0, max: 140 },
    yAxis: { type: 'value', name: '转化率(%)', min: 1.5, max: 3 },
    series: [{
      type: 'scatter',
      symbolSize: function(data) { return Math.sqrt(data[2]) / 3 + 20; },
      data: D.series.map(function(s, i) { return { name: s.series, value: [s.aov, s.conv_rate, s.gmv], itemStyle: { color: colors[i] } }; }),
      label: { show: true, formatter: function(p) { return p.data.name; }, fontSize: 12, position: 'top' }
    }]
  });
  window.addEventListener('resize', function() { chart.resize(); });

  var rows = D.series.map(function(s) {
    return [s.series, '¥' + s.aov.toFixed(2), s.conv_rate.toFixed(2) + '%', '¥' + s.gmv.toLocaleString()];
  });
  document.getElementById('dt-series-scatter').innerHTML = makeTable(['系列','客单价(元)','转化率(%)','GMV(元)'], rows);
})();

// ===== Product Table =====
(function() {
  var html = '';
  var seriesColors = { '经典系列': 'tag-blue', '烘焙系列': 'tag-orange', '饮品系列': 'tag-green', '联名系列': 'tag-purple' };
  D.products.forEach(function(p, i) {
    html += '<tr>' +
      '<td style="font-weight:600;color:#4f6df5;">#' + (i + 1) + '</td>' +
      '<td style="font-weight:500;">' + p.product + '</td>' +
      '<td><span class="tag ' + (seriesColors[p.series] || 'tag-blue') + '">' + p.series + '</span></td>' +
      '<td class="num" style="font-weight:600;">¥' + p.gmv.toLocaleString() + '</td>' +
      '<td class="num">' + p.orders.toLocaleString() + '</td>' +
      '<td class="num">' + p.sales_volume.toLocaleString() + '</td>' +
      '<td class="num">' + p.visitors.toLocaleString() + '</td>' +
      '<td class="num">' + p.conv_rate.toFixed(2) + '%</td>' +
      '<td class="num">¥' + p.aov.toFixed(2) + '</td>' +
      '<td class="num" style="color:' + (p.refund_rate > 2.5 ? '#f5392c' : p.refund_rate > 1.5 ? '#ff7d00' : '#00b42a') + ';">' + p.refund_rate.toFixed(2) + '%</td>' +
      '<td class="num">' + p.inventory.toLocaleString() + '</td>' +
    '</tr>';
  });
  document.getElementById('productTableBody').innerHTML = html;
})();

// ===== Funnel =====
(function() {
  var chart = echarts.init(document.getElementById('chartFunnel'));
  var tw = D.kpi_this_week;
  var rates = [
    (tw.visitors / tw.impressions * 100).toFixed(2),
    (tw.cart_adds / tw.visitors * 100).toFixed(2),
    (tw.orders / tw.cart_adds * 100).toFixed(2)
  ];
  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: function(p) {
        var s = p.name + ': ' + p.value.toLocaleString();
        if (p.dataIndex > 0) {
          var vals = [tw.impressions, tw.visitors, tw.cart_adds, tw.orders];
          var prev = vals[p.dataIndex - 1];
          var r = (p.value / prev * 100).toFixed(2);
          s += '<br/>相对上步转化率: ' + r + '%';
        }
        if (p.dataIndex === 0) {
          s += '<br/>整体曝光到支付转化率: ' + (tw.orders / tw.impressions * 100).toFixed(3) + '%';
        }
        return s;
      }
    },
    legend: { orient: 'vertical', right: '5%', top: 'center', textStyle: { fontSize: 13 } },
    series: [{
      type: 'funnel', left: '10%', right: '22%', top: 20, bottom: 20,
      minSize: '20%', maxSize: '100%', sort: 'descending', gap: 4,
      label: {
        show: true, position: 'inside', fontSize: 14, fontWeight: 'bold',
        formatter: function(p) {
          var v = p.value;
          if (v >= 10000) return p.name + ' ' + (v / 10000).toFixed(1) + '万';
          return p.name + ' ' + v.toLocaleString();
        }
      },
      labelLine: { show: false },
      itemStyle: { borderWidth: 0 },
      data: [
        { value: tw.impressions, name: '曝光量', itemStyle: { color: '#4f6df5' } },
        { value: tw.visitors, name: '访客数', itemStyle: { color: '#5b8def' } },
        { value: tw.cart_adds, name: '加购量', itemStyle: { color: '#722ed1' } },
        { value: tw.orders, name: '支付订单', itemStyle: { color: '#f5392c' } }
      ]
    }],
    graphic: [
      { type: 'text', right: '6%', top: '22%', style: { text: '曝光->访客 ' + rates[0] + '%', fill: '#6c757d', fontSize: 12 } },
      { type: 'text', right: '6%', top: '42%', style: { text: '访客->加购 ' + rates[1] + '%', fill: '#6c757d', fontSize: 12 } },
      { type: 'text', right: '6%', top: '62%', style: { text: '加购->支付 ' + rates[2] + '%', fill: '#6c757d', fontSize: 12 } }
    ]
  });
  window.addEventListener('resize', function() { chart.resize(); });

  var rows = [
    ['曝光量', tw.impressions.toLocaleString(), '100.00%'],
    ['访客数', tw.visitors.toLocaleString(), rates[0] + '%'],
    ['加购量', tw.cart_adds.toLocaleString(), rates[1] + '%'],
    ['支付订单', tw.orders.toLocaleString(), rates[2] + '%']
  ];
  document.getElementById('dt-funnel').innerHTML = makeTable(['阶段','数值','相对上步转化率'], rows);
})();
</script>
</body>
</html>"""

# Assemble final HTML
html = HTML_HEAD.replace('__ECHARTS_PLACEHOLDER__', echarts_js) + HTML_JS.replace('__DATA_PLACEHOLDER__', data_json)

output_path = '/Users/wuliang/workspace/腾讯课堂-demo/Skill技能/outputs/html/电商运营周报_20260803-0809.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Report generated: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.0f} KB")
