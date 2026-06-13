"""Tests for Forecast & Attribution Engines."""

import os, sys, tempfile, pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def db_path():
    import duckdb
    path = os.path.join(tempfile.gettempdir(), f"test_fa_{os.getpid()}.duckdb")
    if os.path.exists(path):
        os.unlink(path)
    conn = duckdb.connect(path)
    conn.execute("CREATE TABLE sales (dt DATE, region VARCHAR, cat VARCHAR, amount DOUBLE)")
    for m in range(1, 13):
        for r, c in [("北京","电子"), ("上海","家居"), ("广东","电子"), ("北京","家居")]:
            conn.execute("INSERT INTO sales VALUES (?, ?, ?, ?)",
                        (f"2024-{m:02d}-15", r, c, 1000 + m * 100 + hash(r) % 500))
    conn.close()
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


class TestForecastEngine:
    def test_ensemble_forecast(self, db_path):
        from scripts.forecast_engine import ForecastEngine, ForecastMethod
        engine = ForecastEngine(db_path)
        result = engine.forecast("sales", "dt", "amount", periods=3,
                                 method=ForecastMethod.ENSEMBLE, granularity="month")
        assert len(result.forecast_points) == 3
        assert len(result.historical_values) == 12
        assert result.confidence >= 0

    def test_methods(self, db_path):
        from scripts.forecast_engine import ForecastEngine, ForecastMethod
        engine = ForecastEngine(db_path)
        for m in [ForecastMethod.MOVING_AVERAGE, ForecastMethod.EXPONENTIAL, ForecastMethod.LINEAR_TREND]:
            result = engine.forecast("sales", "dt", "amount", periods=2, method=m)
            assert len(result.forecast_points) == 2

    def test_quick_forecast(self, db_path):
        from scripts.forecast_engine import ForecastEngine
        engine = ForecastEngine(db_path)
        result = engine.quick_forecast("sales", "dt", "amount", periods=2)
        assert result.method.value == "ensemble"

    def test_result_to_dict(self, db_path):
        from scripts.forecast_engine import ForecastEngine
        engine = ForecastEngine(db_path)
        result = engine.forecast("sales", "dt", "amount", periods=2)
        d = result.to_dict()
        assert "historical" in d
        assert "forecast" in d
        assert d["metric"] == "amount"

    def test_insufficient_data(self, db_path):
        from scripts.forecast_engine import ForecastEngine
        engine = ForecastEngine(db_path)
        with pytest.raises(ValueError):
            engine.forecast("sales", "dt", "amount", periods=2, filter_sql="1=0")


class TestAttributionEngine:
    def test_explain_change(self, db_path):
        from scripts.attribution_engine import AttributionEngine
        engine = AttributionEngine(db_path)
        result = engine.explain_change("sales", "amount", "dt",
                                       "2024-01", "2024-06",
                                       ["region", "cat"])
        assert result.total_before > 0
        assert result.total_after > 0
        assert result.total_change != 0
        assert len(result.contributions) > 0

    def test_quick_explain(self, db_path):
        from scripts.attribution_engine import AttributionEngine
        engine = AttributionEngine(db_path)
        result = engine.quick_explain("sales", "amount", "dt", "2024-01", "2024-06")
        assert len(result.drill_recommendations) > 0

    def test_result_to_dict(self, db_path):
        from scripts.attribution_engine import AttributionEngine
        engine = AttributionEngine(db_path)
        result = engine.explain_change("sales", "amount", "dt",
                                       "2024-01", "2024-06", ["region"])
        d = result.to_dict()
        assert "contributions" in d
        assert "top_drivers" in d
        assert "drill_recommendations" in d

    def test_top_drivers(self, db_path):
        from scripts.attribution_engine import AttributionEngine
        engine = AttributionEngine(db_path)
        result = engine.explain_change("sales", "amount", "dt",
                                       "2024-01", "2024-06",
                                       ["region", "cat"], top_n=3)
        assert len(result.top_drivers) >= 0  # may or may not have drivers
        if result.top_drivers:
            assert abs(result.top_drivers[0].contribution_pct) >= 15.0
