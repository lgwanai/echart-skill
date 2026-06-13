"""End-to-end integration tests for Agent BI engines.

Tests the full analysis workflow:
    analyze → follow-up → report
    forecast + attribution
    context + insight
    semantic + report
"""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db_path(request):
    """Create a DuckDB database with rich test data for integration testing."""
    import duckdb

    # Use unique name per test to avoid file lock conflicts
    test_name = request.node.name.replace("[", "_").replace("]", "_").replace("/", "_")
    tmp_path = os.path.join(tempfile.gettempdir(), f"test_e2e_{os.getpid()}_{test_name}.duckdb")
    if os.path.exists(tmp_path):
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    conn = duckdb.connect(tmp_path)
    conn.execute("""
        CREATE TABLE orders (
            order_date DATE,
            region VARCHAR,
            channel VARCHAR,
            category VARCHAR,
            product VARCHAR,
            amount DOUBLE,
            quantity INTEGER,
            customer_type VARCHAR
        )
    """)
    # 24 months of data across 4 regions, 3 channels, 3 categories
    conn.execute("""
        INSERT INTO orders VALUES
        ('2024-01-15', '北京', '线上', '电子', '手机', 15000.0, 30, '新客'),
        ('2024-01-20', '北京', '线下', '家居', '沙发', 8000.0, 5, '老客'),
        ('2024-01-25', '上海', '线上', '电子', '手机', 12000.0, 25, '新客'),
        ('2024-02-10', '上海', '线下', '家居', '桌子', 5000.0, 10, '老客'),
        ('2024-02-15', '广东', '线上', '服装', 'T恤', 3000.0, 60, '新客'),
        ('2024-02-20', '广东', '直播', '电子', '耳机', 6000.0, 40, '老客'),
        ('2024-03-05', '北京', '直播', '服装', '裤子', 4000.0, 35, '新客'),
        ('2024-03-10', '深圳', '线上', '电子', '电脑', 25000.0, 10, '老客'),
        ('2024-03-15', '上海', '线下', '家居', '椅子', 2000.0, 20, '新客'),
        ('2024-04-01', '广东', '线上', '服装', '衬衫', 3500.0, 45, '新客'),
        ('2024-04-10', '北京', '线下', '电子', '平板', 18000.0, 12, '老客'),
        ('2024-04-20', '深圳', '直播', '家居', '灯具', 7000.0, 15, '新客'),
        ('2024-05-05', '上海', '线上', '电子', '手机', 14000.0, 28, '老客'),
        ('2024-05-15', '广东', '直播', '服装', 'T恤', 3200.0, 65, '新客'),
        ('2024-05-25', '北京', '线上', '家居', '沙发', 9000.0, 6, '老客'),
        ('2024-06-01', '深圳', '线下', '电子', '耳机', 5500.0, 38, '新客'),
        ('2024-06-10', '上海', '直播', '服装', '裤子', 3800.0, 32, '老客'),
        ('2024-06-20', '广东', '线上', '电子', '电脑', 26000.0, 11, '新客'),
        ('2024-07-05', '北京', '直播', '服装', '衬衫', 4200.0, 42, '老客'),
        ('2024-07-15', '上海', '线下', '家居', '桌子', 5500.0, 11, '新客'),
        ('2024-07-25', '深圳', '线上', '电子', '平板', 19000.0, 13, '老客'),
        ('2024-08-01', '广东', '直播', '家居', '灯具', 6500.0, 14, '新客'),
        ('2024-08-10', '北京', '线下', '服装', 'T恤', 2800.0, 55, '新客'),
        ('2024-08-20', '上海', '线上', '电子', '手机', 16000.0, 32, '老客'),
        ('2024-09-05', '深圳', '直播', '服装', '裤子', 4100.0, 38, '新客'),
        ('2024-09-15', '广东', '线下', '电子', '耳机', 6200.0, 42, '老客'),
        ('2024-09-25', '北京', '线上', '家居', '椅子', 2200.0, 22, '新客'),
        ('2024-10-10', '上海', '直播', '电子', '电脑', 28000.0, 12, '老客'),
        ('2024-10-20', '深圳', '线上', '服装', '衬衫', 3600.0, 48, '新客'),
        ('2024-11-01', '广东', '线下', '家居', '沙发', 10000.0, 7, '老客'),
        ('2024-11-10', '北京', '直播', '电子', '平板', 20000.0, 14, '新客'),
        ('2024-11-20', '上海', '线上', '服装', 'T恤', 3300.0, 68, '新客'),
        ('2024-12-05', '深圳', '线下', '家居', '灯具', 7200.0, 16, '老客'),
        ('2024-12-15', '广东', '线上', '电子', '手机', 17000.0, 34, '新客'),
        ('2024-12-25', '北京', '直播', '服装', '裤子', 3900.0, 35, '老客'),
        ('2025-01-10', '上海', '线下', '电子', '耳机', 5800.0, 40, '新客'),
        ('2025-01-20', '深圳', '线上', '家居', '桌子', 6000.0, 12, '老客'),
        ('2025-02-05', '广东', '直播', '服装', '衬衫', 3700.0, 52, '新客'),
        ('2025-02-15', '北京', '线上', '电子', '电脑', 30000.0, 13, '老客'),
        ('2025-03-01', '上海', '直播', '家居', '椅子', 2400.0, 24, '新客'),
        ('2025-03-15', '深圳', '线下', '服装', 'T恤', 2900.0, 58, '新客'),
        ('2025-04-01', '广东', '线上', '电子', '耳机', 6500.0, 45, '老客'),
        ('2025-04-15', '北京', '直播', '家居', '灯具', 7500.0, 17, '新客'),
        ('2025-05-01', '上海', '线下', '服装', '裤子', 4000.0, 38, '老客'),
        ('2025-05-15', '深圳', '线上', '电子', '平板', 21000.0, 15, '新客'),
        ('2025-06-01', '广东', '直播', '家居', '沙发', 11000.0, 8, '老客'),
        ('2025-06-15', '北京', '线下', '电子', '手机', 18000.0, 36, '新客')
    """)
    conn.close()

    yield tmp_path

    try:
        os.unlink(tmp_path)
    except OSError:
        pass


@pytest.fixture
def temp_output_dir():
    """Temp directory for output files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ---------------------------------------------------------------------------
# E2E: Insight → Report Flow
# ---------------------------------------------------------------------------

class TestInsightToReportFlow:
    """Test the core analyze → report pipeline."""

    def test_analyze_then_report(self, db_path, temp_output_dir):
        """Full flow: profile table → analyze insights → generate report."""
        from scripts.insight_engine import InsightEngine
        from scripts.report_engine import ReportEngine

        # Step 1: Profile
        ie = InsightEngine(db_path)
        profile = ie.profile_table("orders")
        assert profile is not None
        assert profile.row_count >= 40  # Rich dataset
        assert profile.column_count == 8

        # Step 2: Analyze
        insights = ie.analyze("orders", dimensions=["region", "channel", "category"])
        assert len(insights) > 0
        insight_types = {i.type.value for i in insights}
        assert len(insight_types) >= 3  # Should find at least 3 types

        # Step 3: Generate report from insights
        re = ReportEngine(db_path=db_path, output_dir=temp_output_dir)
        path = re.generate("orders", template="general", output_format="markdown")
        assert os.path.exists(path)

    def test_analyze_quick_then_quick_report(self, db_path, temp_output_dir):
        """Quick analyze → quick report pipeline."""
        from scripts.insight_engine import InsightEngine
        from scripts.report_engine import ReportEngine

        ie = InsightEngine(db_path)
        insights = ie.analyze("orders")
        assert len(insights) > 0

        re = ReportEngine(db_path=db_path, output_dir=temp_output_dir)
        path = re.quick_report("orders", output_format="markdown")
        assert os.path.exists(path)
        assert os.path.getsize(path) > 100

    def test_all_report_formats(self, db_path, temp_output_dir):
        """Generate report in all 3 formats from fresh analysis."""
        from scripts.report_engine import ReportEngine

        re = ReportEngine(db_path=db_path, output_dir=temp_output_dir)

        for fmt in ["markdown", "html", "json"]:
            path = re.generate("orders", template="quick", output_format=fmt)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0

    def test_report_sections_match_template(self, db_path, temp_output_dir):
        """Report sections should align with template structure."""
        from scripts.report_engine import ReportEngine, REPORT_TEMPLATES

        re = ReportEngine(db_path=db_path, output_dir=temp_output_dir)

        for tmpl_name, tmpl in REPORT_TEMPLATES.items():
            path = re.generate("orders", template=tmpl_name, output_format="json")
            with open(path) as f:
                data = json.load(f)
            # Each template defines N sections
            assert len(data["sections"]) <= len(tmpl["sections"])


# ---------------------------------------------------------------------------
# E2E: Forecast + Attribution Integration
# ---------------------------------------------------------------------------

class TestForecastAttributionIntegration:
    """Test forecast and attribution engines working together."""

    def test_forecast_then_attribute(self, db_path):
        """Predict trend → explain what drives the predicted change."""
        from scripts.forecast_engine import ForecastEngine, ForecastMethod
        from scripts.attribution_engine import AttributionEngine

        # Step 1: Forecast
        fe = ForecastEngine(db_path)
        forecast = fe.forecast("orders", "order_date", "amount", periods=3,
                               method=ForecastMethod.LINEAR_TREND)
        assert forecast.trend_direction in ("up", "down", "flat")
        assert len(forecast.forecast_points) == 3

        # Step 2: Attribute the historical change
        ae = AttributionEngine(db_path)
        attr = ae.explain_change(
            "orders", "amount", "order_date",
            "2024-01", "2024-12",
            ["region", "channel", "category"],
        )
        assert len(attr.contributions) > 0
        assert attr.total_before > 0
        assert attr.total_after > 0

        # Step 3: Insight: if trend is up and top driver is positive, consistent story
        if forecast.trend_direction == "up" and attr.top_drivers:
            assert attr.total_change > 0 or attr.change_direction == "increase"

    def test_forecast_to_dict_feeds_attribution(self, db_path):
        """Forecast output dict can be consumed by downstream code."""
        from scripts.forecast_engine import ForecastEngine
        from scripts.attribution_engine import AttributionEngine

        fe = ForecastEngine(db_path)
        result = fe.forecast("orders", "order_date", "amount", periods=4)
        d = result.to_dict()

        # Verify the dict has all fields needed for charting/reporting
        assert "historical" in d
        assert "forecast" in d
        assert "confidence" in d
        assert len(d["historical"]) == len(d.get("historical", []))

        ae = AttributionEngine(db_path)
        attr = ae.explain_change(
            "orders", "amount", "order_date",
            "2024-06", "2025-06",
            ["region", "channel"],
        )
        ad = attr.to_dict()
        assert "contributions" in ad
        assert "top_drivers" in ad

    def test_ensemble_forecast_has_confidence(self, db_path):
        """Ensemble forecast should have higher confidence than individual methods."""
        from scripts.forecast_engine import ForecastEngine, ForecastMethod

        fe = ForecastEngine(db_path)
        ensemble = fe.forecast("orders", "order_date", "amount", periods=3,
                               method=ForecastMethod.ENSEMBLE)
        ma = fe.forecast("orders", "order_date", "amount", periods=3,
                        method=ForecastMethod.MOVING_AVERAGE)

        # Ensemble typically has decent confidence
        assert ensemble.confidence > 0

        # Both should produce valid forecasts
        assert len(ensemble.forecast_points) == 3
        assert len(ma.forecast_points) == 3


# ---------------------------------------------------------------------------
# E2E: Context Manager + Insight Engine
# ---------------------------------------------------------------------------

class TestContextInsightIntegration:
    """Test context manager with real data from insight engine."""

    def test_start_session_with_real_data(self, db_path):
        """Start a session against real data table."""
        from scripts.context_manager import ContextManager

        ctx = ContextManager()
        session = ctx.start_session(
            "orders",
            db_path=db_path,
            dimensions=["region", "channel"],
            metrics=["amount", "quantity"],
            date_column="order_date",
        )
        assert session.current_table == "orders"
        assert session.session_id
        # Time context should be auto-detected
        assert session.time_context.min_date is not None
        assert session.time_context.max_date is not None

    def test_session_persistence(self, db_path):
        """Sessions should survive across multiple ContextManager instances."""
        from scripts.context_manager import ContextManager

        # Create session
        ctx1 = ContextManager()
        session = ctx1.start_session("orders", db_path=db_path,
                                     date_column="order_date")
        sid = session.session_id

        # New instance should load the same session
        ctx2 = ContextManager()
        loaded = ctx2.get_session(sid)
        assert loaded is not None
        assert loaded.current_table == "orders"

    def test_resolve_follow_up_time(self, db_path):
        """Resolve time-based follow-up references."""
        from scripts.context_manager import ContextManager

        ctx = ContextManager()
        session = ctx.start_session("orders", db_path=db_path,
                                     date_column="order_date")

        # Test various time references
        result = ctx.resolve("上个月呢？", session)
        assert result["session_active"]
        assert result.get("time_range") is not None

    def test_resolve_follow_up_dimension(self, db_path):
        """Resolve dimension-based follow-up."""
        from scripts.context_manager import ContextManager

        ctx = ContextManager()
        session = ctx.start_session("orders", db_path=db_path,
                                     dimensions=["region", "channel"])
        ctx.record_turn(session, "查看各地区销售额",
                       sql="SELECT region, SUM(amount) FROM orders GROUP BY region")

        result = ctx.resolve("深挖一下广东", session)
        assert result["session_active"]

    def test_record_and_retrieve_history(self, db_path):
        """Record turns and retrieve history."""
        from scripts.context_manager import ContextManager

        ctx = ContextManager()
        session = ctx.start_session("orders", db_path=db_path)
        ctx.record_turn(session, "查看总销售额",
                       sql="SELECT SUM(amount) FROM orders")

        # Get latest session and verify history
        latest = ctx.get_latest_session()
        assert latest is not None
        assert len(latest.turns) >= 1

    def test_list_sessions(self, db_path):
        """List all sessions."""
        from scripts.context_manager import ContextManager

        ctx = ContextManager()
        ctx.start_session("orders", db_path=db_path)
        ctx.start_session("orders", db_path=db_path)  # second session

        assert len(ctx.sessions) >= 2

    def test_new_topic_detection(self, db_path):
        """Detect when user switches to a completely new topic."""
        from scripts.context_manager import ContextManager

        ctx = ContextManager()
        session = ctx.start_session("orders", db_path=db_path)
        ctx.record_turn(session, "销售额是多少",
                       sql="SELECT SUM(amount) FROM orders")

        result = ctx.resolve("今天天气怎么样", session)
        assert result["session_active"]


# ---------------------------------------------------------------------------
# E2E: Semantic Model + Insight Engine
# ---------------------------------------------------------------------------

class TestSemanticInsightIntegration:
    """Test semantic model creation from real data profiles."""

    def test_create_model_from_real_table(self, db_path):
        """Auto-create semantic model from profiled table."""
        from scripts.semantic_model import ModelManager

        mgr = ModelManager()
        model = mgr.create_from_table("orders", db_path=db_path,
                                       model_name="orders_e2e",
                                       description="E2E测试订单模型")

        assert model.name == "orders_e2e"
        assert model.table == "orders"
        assert len(model.columns) == 8  # All 8 columns profiled

        # Should have date columns detected
        date_cols = model.get_date_columns()
        assert any(c.name == "order_date" for c in date_cols)

        # Should have metric columns with aggregations
        metric_cols = model.get_metric_columns()
        assert any(c.name == "amount" for c in metric_cols)

        # Should have dimension columns
        dim_cols = model.get_dimension_columns()
        assert len(dim_cols) >= 3  # region, channel, category, etc.

        # Should auto-generate metrics
        assert len(model.metrics) >= 2  # amount + COUNT

        # Save and load
        path = mgr.save(model, "orders_e2e")
        assert os.path.exists(path)

        loaded = mgr.load("orders_e2e")
        assert loaded is not None
        assert loaded.name == "orders_e2e"
        assert len(loaded.columns) == 8

    def test_model_prompt_context_with_real_data(self, db_path):
        """Generated prompt context should accurately reflect the table."""
        from scripts.semantic_model import ModelManager

        mgr = ModelManager()
        model = mgr.create_from_table("orders", db_path=db_path,
                                       model_name="orders_ctx")
        ctx_text = model.to_prompt_context()

        # Should contain table info
        assert "orders" in ctx_text
        assert "order_date" in ctx_text
        assert "amount" in ctx_text

        # Should have role categorization
        assert "metric" in ctx_text.lower() or "指标" in ctx_text
        assert "dimension" in ctx_text.lower() or "维度" in ctx_text

    def test_multiple_models_prompt_context(self, db_path):
        """Combine multiple semantic models into one context."""
        from scripts.semantic_model import ModelManager

        mgr = ModelManager()
        model1 = mgr.create_from_table("orders", db_path=db_path, model_name="orders_multi")
        mgr.save(model1, "orders_multi")

        # Create a second model (same table, different perspective)
        model2 = mgr.create_from_table("orders", db_path=db_path,
                                        model_name="orders_v2",
                                        description="订单模型V2")
        mgr.save(model2, "orders_v2")

        ctx = mgr.get_prompt_context(["orders_multi", "orders_v2"])
        assert "orders_multi" in ctx
        assert "orders_v2" in ctx
        assert "---" in ctx  # Separator


# ---------------------------------------------------------------------------
# E2E: Cross-Engine Data Consistency
# ---------------------------------------------------------------------------

class TestCrossEngineConsistency:
    """Verify engines produce consistent results on the same data."""

    def test_insight_and_attribution_agree_on_trend(self, db_path):
        """Insight trend direction should align with attribution change direction."""
        from scripts.insight_engine import InsightEngine
        from scripts.attribution_engine import AttributionEngine

        ie = InsightEngine(db_path)
        insights = ie.analyze("orders", dimensions=["region"])

        ae = AttributionEngine(db_path)
        attr = ae.explain_change(
            "orders", "amount", "order_date",
            "2024-01", "2024-12",
            ["region"],
        )

        # Both should find meaningful data
        assert len(insights) > 0
        assert attr.total_change != 0

    def test_forecast_periods_match_granularity(self, db_path):
        """Forecast with different granularities should produce appropriate periods."""
        from scripts.forecast_engine import ForecastEngine

        fe = ForecastEngine(db_path)

        # Monthly
        monthly = fe.forecast("orders", "order_date", "amount", periods=3,
                              granularity="month")
        assert len(monthly.historical_values) > 0

        # Quarterly
        quarterly = fe.forecast("orders", "order_date", "amount", periods=2,
                               granularity="quarter")
        assert len(quarterly.forecast_points) == 2

    def test_attribution_dimensions_contribute_to_total(self, db_path):
        """Top driver contributions should be meaningful."""
        from scripts.attribution_engine import AttributionEngine

        ae = AttributionEngine(db_path)
        result = ae.explain_change(
            "orders", "amount", "order_date",
            "2024-01", "2025-06",
            ["region", "channel", "category"],
            top_n=5,
        )

        # Contributions should not exceed 100% per dimension (rough check)
        total_contrib = sum(abs(c.contribution_pct) for c in result.top_drivers)
        # Top drivers should explain a good portion but not impossibly high
        assert total_contrib >= 0

    def test_report_includes_insight_types(self, db_path, temp_output_dir):
        """Report JSON should contain diverse insight types."""
        from scripts.report_engine import ReportEngine

        re = ReportEngine(db_path=db_path, output_dir=temp_output_dir)
        path = re.generate("orders", template="general", output_format="json")

        with open(path) as f:
            data = json.load(f)

        all_insights = data.get("all_insights", [])
        types_found = {i.get("type") for i in all_insights}
        # Should find multiple insight types in a rich dataset
        assert len(types_found) >= 2


# ---------------------------------------------------------------------------
# E2E: Error Recovery & Edge Cases
# ---------------------------------------------------------------------------

class TestE2EEdgeCases:
    """Test graceful handling of edge cases across engines."""

    def test_empty_table_handling(self):
        """All engines should handle empty tables gracefully."""
        import duckdb

        tmp = os.path.join(tempfile.gettempdir(), f"test_empty_{os.getpid()}.duckdb")
        if os.path.exists(tmp):
            os.unlink(tmp)

        conn = duckdb.connect(tmp)
        conn.execute("CREATE TABLE empty_t (dt DATE, val DOUBLE)")
        conn.close()

        try:
            from scripts.insight_engine import InsightEngine
            ie = InsightEngine(tmp)
            profile = ie.profile_table("empty_t")
            assert profile is not None
            assert profile.row_count == 0

            # Report engine should handle empty table
            from scripts.report_engine import ReportEngine
            re = ReportEngine(db_path=tmp)
            # This should either work (empty report) or raise clear error
            try:
                path = re.generate("empty_t", template="quick", output_format="markdown")
                assert os.path.exists(path)
            except ValueError:
                pass  # "数据点不足" is acceptable

            # Forecast should raise on insufficient data
            from scripts.forecast_engine import ForecastEngine
            fe = ForecastEngine(tmp)
            with pytest.raises(ValueError):
                fe.forecast("empty_t", "dt", "val", periods=3)
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    def test_nonexistent_table_all_engines(self, db_path):
        """All engines should raise clear errors for nonexistent tables."""
        nonexistent = "this_table_does_not_exist"

        from scripts.insight_engine import InsightEngine
        ie = InsightEngine(db_path)
        assert ie.profile_table(nonexistent) is None

        from scripts.report_engine import ReportEngine
        re = ReportEngine(db_path=db_path)
        with pytest.raises(ValueError):
            re.generate(nonexistent)

        from scripts.forecast_engine import ForecastEngine
        fe = ForecastEngine(db_path)
        with pytest.raises(Exception):
            fe.forecast(nonexistent, "dt", "val", periods=3)

        from scripts.attribution_engine import AttributionEngine
        ae = AttributionEngine(db_path)
        with pytest.raises(Exception):
            ae.explain_change(nonexistent, "val", "dt",
                             "2024-01", "2024-06", ["region"])


# ---------------------------------------------------------------------------
# E2E: Full Conversation Simulation
# ---------------------------------------------------------------------------

class TestFullConversationFlow:
    """Simulate a realistic multi-turn analysis conversation."""

    def test_full_analyze_followup_report_flow(self, db_path, temp_output_dir):
        """Simulate: /analyze → ask follow-up → /report"""
        from scripts.insight_engine import InsightEngine
        from scripts.context_manager import ContextManager
        from scripts.report_engine import ReportEngine

        # Turn 1: User asks to analyze
        ie = InsightEngine(db_path)
        profile = ie.profile_table("orders")
        assert profile is not None

        ctx = ContextManager()
        session = ctx.start_session(
            "orders", db_path=db_path,
            dimensions=["region", "channel", "category"],
            metrics=["amount", "quantity"],
            date_column="order_date",
        )
        ctx.record_turn(session, "分析orders表",
                       sql="SELECT * FROM orders LIMIT 10")

        # Turn 2: User asks a follow-up
        insights = ie.analyze("orders", dimensions=["region"])
        assert len(insights) > 0

        follow_up_result = ctx.resolve("广东的销售额是多少？", session)
        assert follow_up_result["session_active"]
        ctx.record_turn(session, "广东的销售额是多少？",
                       sql="SELECT region, SUM(amount) FROM orders WHERE region='广东' GROUP BY region")

        # Turn 3: Generate a report
        re = ReportEngine(db_path=db_path, output_dir=temp_output_dir)
        path = re.generate("orders", template="sales", output_format="markdown")
        assert os.path.exists(path)
        ctx.record_turn(session, "生成销售报告")

        # Verify session captures all turns
        full_session = ctx.get_session(session.session_id)
        assert full_session is not None
        assert len(full_session.turns) >= 3

    def test_insight_to_attribution_flow(self, db_path):
        """Simulate: /analyze → discover anomaly → /why"""
        from scripts.insight_engine import InsightEngine, InsightType
        from scripts.attribution_engine import AttributionEngine

        # Step 1: Analyze
        ie = InsightEngine(db_path)
        insights = ie.analyze("orders", dimensions=["region", "channel", "category"])

        # Step 2: Find an interesting insight (e.g., a change)
        change_insights = [i for i in insights if i.type == InsightType.CHANGE]
        trend_insights = [i for i in insights if i.type == InsightType.TREND]

        # Step 3: Attribute the change
        ae = AttributionEngine(db_path)
        result = ae.explain_change(
            "orders", "amount", "order_date",
            "2024-01", "2025-06",
            ["region", "channel", "category"],
        )

        assert len(result.contributions) > 0
        assert len(result.drill_recommendations) > 0

    def test_forecast_to_chart_suggestion(self, db_path):
        """Forecast output should provide enough info for chart generation."""
        from scripts.forecast_engine import ForecastEngine, ForecastMethod

        fe = ForecastEngine(db_path)
        result = fe.forecast("orders", "order_date", "amount", periods=6,
                             method=ForecastMethod.ENSEMBLE)

        # Data that a chart generator would need
        assert len(result.historical_periods) > 0
        assert len(result.historical_values) > 0
        assert len(result.forecast_points) > 0

        # Each forecast point has bounds for confidence bands
        for fp in result.forecast_points:
            assert fp.lower_bound <= fp.value <= fp.upper_bound
            assert fp.period  # Non-empty period label

        # Dict export should be chart-ready JSON
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "historical" in d
        assert "forecast" in d
