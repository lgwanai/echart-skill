"""Tests for Context Manager — conversational memory for Agent BI."""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.context_manager import (
    ContextManager,
    Session,
    Turn,
    TurnType,
    FollowUpIntent,
    TimeContext,
    AnalysisFocus,
    ReferenceResolver,
    IntentDetector,
)


class TestReferenceResolver:
    """Tests for natural language reference resolution."""

    def setup_method(self):
        self.resolver = ReferenceResolver()

    def test_resolve_last_month(self):
        tc = TimeContext(column="order_date")
        result = self.resolver.resolve_time("上个月的数据呢？", tc)
        assert result is not None
        assert "start_date" in result
        assert "end_date" in result
        assert result["resolved_type"] == "last_month"

    def test_resolve_last_year(self):
        tc = TimeContext(column="order_date")
        result = self.resolver.resolve_time("和去年同期比", tc)
        assert result is not None
        assert result["resolved_type"] == "last_year"

    def test_resolve_this_month(self):
        tc = TimeContext(column="order_date")
        result = self.resolver.resolve_time("本月的数据", tc)
        assert result is not None
        assert result["resolved_type"] in ("this_month", "this_year")

    def test_resolve_last_week(self):
        tc = TimeContext(column="order_date")
        result = self.resolver.resolve_time("上周怎么样", tc)
        assert result is not None
        assert result["resolved_type"] == "last_week"

    def test_resolve_last_n_days(self):
        tc = TimeContext(column="order_date")
        result = self.resolver.resolve_time("最近7天的数据", tc)
        assert result is not None
        assert result["resolved_type"] == "last_n_days"

    def test_no_time_reference(self):
        tc = TimeContext(column="order_date")
        result = self.resolver.resolve_time("帮我看看数据", tc)
        assert result is None

    def test_detect_comparison_yoy(self):
        assert self.resolver.detect_comparison("和去年同期比") == "yoy"
        assert self.resolver.detect_comparison("同比增长多少") == "yoy"

    def test_detect_comparison_mom(self):
        assert self.resolver.detect_comparison("环比变化") == "mom"
        assert self.resolver.detect_comparison("和上月比呢") == "mom"

    def test_detect_drill_intent(self):
        assert self.resolver.detect_drill_intent("深挖一下白酒品类") == "drill_down"
        assert self.resolver.detect_drill_intent("只看广东的数据") == "filter"
        assert self.resolver.detect_drill_intent("为什么下降了") == "explain"


class TestIntentDetector:
    """Tests for follow-up intent detection."""

    def setup_method(self):
        self.detector = IntentDetector()

    def test_new_topic_detection(self):
        session = Session()
        result = self.detector.detect("分析一下orders表", session)
        assert result["is_new_topic"] is True
        assert result["suggested_action"] == "start_new_analysis"

    def test_command_detection(self):
        session = Session()
        result = self.detector.detect("/chart bar 销售额", session)
        assert result["intent_type"] == TurnType.COMMAND
        assert result["suggested_action"] == "execute_command"

    def test_follow_up_with_active_session(self):
        session = Session(current_table="orders")
        session.time_context = TimeContext(column="order_date")
        result = self.detector.detect("上个月呢？", session)
        assert result["is_new_topic"] is False
        assert result["intent_type"] == TurnType.FOLLOW_UP

    def test_comparison_follow_up(self):
        session = Session(current_table="orders")
        session.time_context = TimeContext(column="交易时间")
        result = self.detector.detect("和去年同期比呢？", session)
        assert result["is_new_topic"] is False
        assert result["follow_up_intent"] == FollowUpIntent.COMPARE

    def test_drill_down_follow_up(self):
        session = Session(current_table="orders")
        result = self.detector.detect("深挖一下看看", session)
        assert result["is_new_topic"] is False
        assert result["follow_up_intent"] == FollowUpIntent.DRILL_DOWN

    def test_explain_follow_up(self):
        session = Session(current_table="orders")
        result = self.detector.detect("为什么销售额下降了", session)
        assert result["follow_up_intent"] == FollowUpIntent.EXPLAIN

    def test_short_follow_up(self):
        session = Session(current_table="orders")
        result = self.detector.detect("那广东呢？", session)
        assert result["is_new_topic"] is False
        assert result["follow_up_intent"] == FollowUpIntent.REFINE


class TestContextManager:
    """Tests for the full context manager."""

    @pytest.fixture
    def mgr(self, tmp_path):
        db_path = str(tmp_path / "test_sessions.db")
        return ContextManager(session_db=db_path)

    def test_start_session(self, mgr):
        session = mgr.start_session("test_table")
        assert session.current_table == "test_table"
        assert session.is_active()
        assert session.session_id in mgr.sessions

    def test_record_turn(self, mgr):
        session = mgr.start_session("test_table")
        turn = mgr.record_turn(
            session,
            "SELECT * FROM test_table LIMIT 10",
            sql="SELECT * FROM test_table LIMIT 10",
            result_summary="10 rows",
        )
        assert turn.user_input == "SELECT * FROM test_table LIMIT 10"
        assert len(session.turns) == 1
        assert session.last_query == "SELECT * FROM test_table LIMIT 10"

    def test_resolve_follow_up(self, mgr):
        session = mgr.start_session("test_table")
        session.time_context = TimeContext(column="dt")
        result = mgr.resolve("上个月呢？", session)
        assert result["is_follow_up"] is True
        assert result["time_range"] is not None
        assert "上个月" in result["time_range"]["label"] or "月" in str(result["time_range"])

    def test_resolve_new_topic_without_session(self, mgr):
        result = mgr.resolve("分析一下数据", None)
        assert result["session_active"] is False

    def test_get_prompt_context(self, mgr):
        session = mgr.start_session("orders", dimensions=["region", "category"])
        session.time_context = TimeContext(column="order_date", min_date="2024-01-01", max_date="2024-12-31")
        ctx = mgr.get_prompt_context(session)
        assert "orders" in ctx
        assert "region" in ctx
        assert "order_date" in ctx

    def test_session_persistence(self, mgr):
        session = mgr.start_session("test_persist")
        sid = session.session_id

        # Simulate new manager loading from same DB
        mgr2 = ContextManager(session_db=mgr.session_db)
        loaded = mgr2.get_session(sid)
        assert loaded is not None
        assert loaded.current_table == "test_persist"

    def test_multiple_turns(self, mgr):
        session = mgr.start_session("orders")
        mgr.record_turn(session, "查看销售额", result_summary="86 rows")
        mgr.record_turn(session, "只看广东的", result_summary="12 rows")
        mgr.record_turn(session, "按产品分类", result_summary="14 rows")
        assert len(session.turns) == 3
        assert session.get_last_turn().user_input == "按产品分类"

    def test_focus_management(self, mgr):
        session = mgr.start_session("orders")
        mgr.set_focus(session, dimensions=["channel"], metrics=["amount"])
        assert session.focus.dimensions == ["channel"]
        assert session.focus.metrics == ["amount"]

    def test_end_session(self, mgr):
        session = mgr.start_session("test_end")
        sid = session.session_id
        assert mgr.end_session(sid) is True
        assert sid not in mgr.sessions
        assert mgr.end_session(sid) is False  # Already gone

    def test_get_latest_session(self, mgr):
        s1 = mgr.start_session("first")
        s2 = mgr.start_session("second")
        latest = mgr.get_latest_session()
        assert latest.session_id == s2.session_id


class TestSessionModel:
    """Tests for Session data model."""

    def test_session_active(self):
        s = Session()
        assert s.is_active() is False
        s.current_table = "test"
        assert s.is_active() is True

    def test_session_to_dict(self):
        s = Session(current_table="test", current_db="test.duckdb")
        d = s.to_dict()
        assert d["current_table"] == "test"
        assert d["current_db"] == "test.duckdb"
        assert "turns" in d

    def test_turn_model(self):
        t = Turn(user_input="hello", intent=TurnType.QUERY)
        assert t.user_input == "hello"
        assert t.intent == TurnType.QUERY
        assert t.follow_up_intent is None

    def test_turn_with_follow_up(self):
        t = Turn(user_input="上个月呢", follow_up_intent=FollowUpIntent.REFINE)
        assert t.follow_up_intent == FollowUpIntent.REFINE
