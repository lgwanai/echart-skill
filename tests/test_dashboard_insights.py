"""Tests for Dashboard Insight Cards module."""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.dashboard_insights import (
    generate_insight_cards,
    generate_insight_cards_from_insights,
    _build_insight_card,
    _empty_insights_html,
    _count_by_severity,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db_path(request):
    import duckdb

    test_name = request.node.name.replace("[", "_").replace("]", "_").replace("/", "_")
    tmp = os.path.join(tempfile.gettempdir(), f"test_di_{os.getpid()}_{test_name}.duckdb")
    if os.path.exists(tmp):
        try:
            os.unlink(tmp)
        except OSError:
            pass

    conn = duckdb.connect(tmp)
    conn.execute("""CREATE TABLE sales (
        order_date DATE, region VARCHAR, category VARCHAR, amount DOUBLE, qty INTEGER
    )""")
    conn.execute("""INSERT INTO sales VALUES
        ('2024-01-15','北京','电子',10000,20),('2024-01-20','上海','家居',5000,10),
        ('2024-02-10','广东','电子',12000,25),('2024-02-15','北京','家居',4000,8),
        ('2024-03-05','上海','电子',15000,30),('2024-03-10','广东','家居',3000,6),
        ('2024-04-01','北京','电子',18000,35),('2024-04-10','上海','家居',6000,12),
        ('2024-05-15','广东','电子',20000,40),('2024-05-20','北京','家居',3500,7),
        ('2024-06-01','上海','电子',22000,45),('2024-06-15','广东','家居',4000,8)
    """)
    conn.close()
    yield tmp
    try:
        os.unlink(tmp)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGenerateInsightCards:
    def test_generates_html_from_table(self, db_path):
        html = generate_insight_cards("sales", db_path=db_path, max_cards=4)
        assert "insights-panel" in html
        assert "insight-card" in html
        # Verify the header renders (avoid coupling to exact locale text)
        assert "insights-panel-header" in html

    def test_includes_css_by_default(self, db_path):
        html = generate_insight_cards("sales", db_path=db_path)
        assert "<style>" in html

    def test_exclude_css(self, db_path):
        html = generate_insight_cards("sales", db_path=db_path, include_css=False)
        assert "<style>" not in html

    def test_respects_max_cards(self, db_path):
        html = generate_insight_cards("sales", db_path=db_path, max_cards=2)
        count = html.count("insight-card severity-")
        assert count <= 2

    def test_with_dimensions(self, db_path):
        html = generate_insight_cards("sales", db_path=db_path, dimensions=["region"])
        assert "insights-panel" in html

    def test_with_date_column(self, db_path):
        html = generate_insight_cards("sales", db_path=db_path, date_column="order_date")
        assert "insights-panel" in html


class TestGenerateFromInsights:
    def test_accepts_insight_list(self, db_path):
        from scripts.insight_engine import InsightEngine
        ie = InsightEngine(db_path)
        insights = ie.analyze("sales")
        html = generate_insight_cards_from_insights(insights, max_cards=4)
        assert "insights-panel" in html
        assert "insight-card" in html

    def test_empty_insights(self):
        html = generate_insight_cards_from_insights([])
        assert "暂无显著洞察" in html

    def test_empty_insights_with_css(self):
        html = generate_insight_cards_from_insights([], include_css=False)
        assert "<style>" not in html


class TestBuildInsightCard:
    def test_card_structure(self, db_path):
        from scripts.insight_engine import InsightEngine
        ie = InsightEngine(db_path)
        insights = ie.analyze("sales")
        if insights:
            card = _build_insight_card(insights[0], 0)
            assert "insight-card" in card
            assert "insight-card-header" in card
            assert "insight-card-title" in card

    def test_card_with_change_pct(self):
        from scripts.insight_engine import Insight, InsightType, Severity
        ins = Insight(
            type=InsightType.CHANGE,
            severity=Severity.HIGH,
            title="销售额增长显著",
            description="销售额环比增长25%",
            evidence={"change_pct": 25.0},
            related_columns=["amount", "order_date"],
        )
        card = _build_insight_card(ins, 0)
        assert "metric-value up" in card
        assert "+25.0%" in card

    def test_card_negative_change(self):
        from scripts.insight_engine import Insight, InsightType, Severity
        ins = Insight(
            type=InsightType.TREND,
            severity=Severity.CRITICAL,
            title="数量持续下降",
            description="数量环比下降15%",
            evidence={"change_pct": -15.0},
            related_columns=["qty"],
        )
        card = _build_insight_card(ins, 1)
        assert "metric-value down" in card
        assert "-15.0%" in card

    def test_card_severity_class(self):
        from scripts.insight_engine import Insight, InsightType, Severity
        for sev in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            ins = Insight(type=InsightType.SUMMARY, severity=sev, title="T", description="D")
            card = _build_insight_card(ins, 0)
            assert f"severity-{sev.value}" in card

    def test_card_has_drill_hint(self):
        from scripts.insight_engine import Insight, InsightType, Severity
        ins = Insight(type=InsightType.RANKING, severity=Severity.MEDIUM, title="T", description="D")
        card = _build_insight_card(ins, 0)
        assert "drill-hint" in card


class TestHelpers:
    def test_empty_html(self):
        html = _empty_insights_html()
        assert "暂无显著洞察" in html

    def test_count_by_severity(self):
        from scripts.insight_engine import Insight, InsightType, Severity
        insights = [
            Insight(type=InsightType.ANOMALY, severity=Severity.CRITICAL, title="A", description=""),
            Insight(type=InsightType.ANOMALY, severity=Severity.CRITICAL, title="B", description=""),
            Insight(type=InsightType.TREND, severity=Severity.HIGH, title="C", description=""),
        ]
        counts = _count_by_severity(insights)
        assert counts["critical"] == 2
        assert counts["high"] == 1
        assert counts["medium"] == 0

    def test_severity_style_mapping(self):
        from scripts.dashboard_insights import SEVERITY_STYLE
        assert "critical" in SEVERITY_STYLE
        assert "high" in SEVERITY_STYLE
        assert all("color" in v and "bg" in v for v in SEVERITY_STYLE.values())

    def test_type_meta_mapping(self):
        from scripts.dashboard_insights import TYPE_META
        assert "trend" in TYPE_META
        assert "anomaly" in TYPE_META
        assert "ranking" in TYPE_META


class TestCLIOutput:
    def test_json_output(self, db_path):
        """Verify CLI --json mode works (via code path)."""
        from scripts.insight_engine import InsightEngine
        ie = InsightEngine(db_path)
        insights = ie.analyze("sales")
        data = [i.to_dict() for i in insights]
        assert isinstance(data, list)
        if data:
            entry = data[0]
            for key in ("type", "severity", "title", "description", "evidence"):
                assert key in entry, f"Missing key: {key}"
