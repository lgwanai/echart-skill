"""Tests for the Semantic Model module."""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.semantic_model import (
    ColumnRole,
    JoinType,
    AggFunction,
    ColumnDef,
    MetricDef,
    Relationship,
    SemanticModel,
    ModelManager,
)


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def make_column(name="销售额", role=ColumnRole.METRIC, **kwargs):
    defaults = {
        "name": name,
        "role": role,
        "description": f"{name}的描述",
        "dtype": "DOUBLE",
        "aliases": kwargs.pop("aliases", []),
        "unit": kwargs.pop("unit", "元"),
        "agg_default": kwargs.pop("agg_default", AggFunction.SUM),
        "is_nullable": True,
        "format": kwargs.pop("format", "currency"),
    }
    defaults.update(kwargs)
    return ColumnDef(**defaults)


def make_metric(name="总销售额", **kwargs):
    defaults = {
        "name": name,
        "description": f"{name}的说明",
        "sql_expr": "SUM(amount)",
        "unit": "元",
        "format": "currency",
        "depends_on": ["amount"],
        "category": "销售",
    }
    defaults.update(kwargs)
    return MetricDef(**defaults)


def make_relationship(name="订单-产品", **kwargs):
    defaults = {
        "name": name,
        "target_model": "products",
        "join_type": JoinType.LEFT,
        "condition": "orders.product_id = products.id",
        "description": "关联产品信息",
    }
    defaults.update(kwargs)
    return Relationship(**defaults)


def make_model(name="orders", table="orders", **kwargs):
    defaults = {
        "name": name,
        "table": table,
        "description": "订单业务模型",
        "columns": [make_column("amount"), make_column("region", role=ColumnRole.DIMENSION, unit="", agg_default=None, format="")],
        "metrics": [make_metric("总销售额")],
        "relationships": [],
        "synonyms": ["订单", "order"],
    }
    defaults.update(kwargs)
    return SemanticModel(**defaults)


# ---------------------------------------------------------------------------
# ColumnDef tests
# ---------------------------------------------------------------------------

class TestColumnDef:
    def test_basic_column(self):
        col = ColumnDef(name="amount", role=ColumnRole.METRIC, dtype="DOUBLE")
        assert col.name == "amount"
        assert col.role == ColumnRole.METRIC
        assert col.dtype == "DOUBLE"

    def test_column_with_aliases(self):
        col = ColumnDef(name="金额", role=ColumnRole.METRIC,
                       aliases=["销售额", "收入", "revenue"])
        assert "销售额" in col.aliases
        assert "revenue" in col.aliases

    def test_column_with_aggregation(self):
        col = ColumnDef(name="price", role=ColumnRole.METRIC,
                       agg_default=AggFunction.AVG)
        assert col.agg_default == AggFunction.AVG

    def test_column_defaults(self):
        col = ColumnDef(name="text_col")
        assert col.role == ColumnRole.UNKNOWN
        assert col.description == ""
        assert col.aliases == []


# ---------------------------------------------------------------------------
# MetricDef tests
# ---------------------------------------------------------------------------

class TestMetricDef:
    def test_basic_metric(self):
        m = MetricDef(name="总销售额", sql_expr="SUM(amount)")
        assert m.name == "总销售额"
        assert m.sql_expr == "SUM(amount)"

    def test_metric_with_dependencies(self):
        m = MetricDef(name="客单价", sql_expr="SUM(amount)/COUNT(DISTINCT user_id)",
                     depends_on=["amount", "user_id"])
        assert "amount" in m.depends_on
        assert "user_id" in m.depends_on

    def test_metric_defaults(self):
        m = MetricDef(name="test")
        assert m.description == ""
        assert m.sql_expr == ""
        assert m.unit == ""


# ---------------------------------------------------------------------------
# Relationship tests
# ---------------------------------------------------------------------------

class TestRelationship:
    def test_basic_relationship(self):
        r = Relationship(name="订单-产品", target_model="products",
                        condition="o.product_id = p.id")
        assert r.target_model == "products"
        assert r.join_type == JoinType.LEFT  # default

    def test_inner_join(self):
        r = Relationship(name="必须关联", target_model="users",
                        join_type=JoinType.INNER,
                        condition="o.user_id = u.id")
        assert r.join_type == JoinType.INNER


# ---------------------------------------------------------------------------
# SemanticModel tests — serialization
# ---------------------------------------------------------------------------

class TestSemanticModelSerialization:
    """Round-trip serialization tests."""

    def test_to_dict_basic(self):
        model = make_model()
        d = model.to_dict()
        assert d["name"] == "orders"
        assert d["table"] == "orders"
        assert isinstance(d["columns"], list)
        assert isinstance(d["metrics"], list)

    def test_to_dict_columns(self):
        model = make_model()
        d = model.to_dict()
        col = d["columns"][0]
        assert "name" in col
        assert "role" in col
        assert "dtype" in col
        # Role should be serialized as string
        assert isinstance(col["role"], str)

    def test_to_dict_metrics(self):
        model = make_model()
        d = model.to_dict()
        metric = d["metrics"][0]
        assert "name" in metric
        assert "sql_expr" in metric

    def test_to_dict_relationships(self):
        model = make_model(relationships=[make_relationship()])
        d = model.to_dict()
        assert len(d["relationships"]) == 1
        assert d["relationships"][0]["join_type"] == "LEFT JOIN"

    def test_from_dict_roundtrip(self):
        original = make_model(relationships=[make_relationship()])
        d = original.to_dict()
        restored = SemanticModel.from_dict(d)
        assert restored.name == original.name
        assert restored.table == original.table
        assert len(restored.columns) == len(original.columns)
        assert len(restored.metrics) == len(original.metrics)
        assert len(restored.relationships) == len(original.relationships)

    def test_from_dict_preserves_agg_function(self):
        model = make_model(columns=[make_column(agg_default=AggFunction.AVG)])
        d = model.to_dict()
        restored = SemanticModel.from_dict(d)
        assert restored.columns[0].agg_default == AggFunction.AVG

    def test_from_dict_preserves_join_type(self):
        model = make_model(relationships=[make_relationship(join_type=JoinType.INNER)])
        d = model.to_dict()
        restored = SemanticModel.from_dict(d)
        assert restored.relationships[0].join_type == JoinType.INNER

    def test_from_dict_no_role_defaults_to_unknown(self):
        d = {
            "name": "test", "table": "test",
            "columns": [{"name": "col1"}],
            "metrics": [], "relationships": [],
        }
        model = SemanticModel.from_dict(d)
        assert model.columns[0].role == ColumnRole.UNKNOWN

    def test_json_serializable(self):
        """Verify to_dict output is JSON-serializable."""
        model = make_model(relationships=[make_relationship()])
        d = model.to_dict()
        # Should not raise
        json_str = json.dumps(d, ensure_ascii=False)
        assert len(json_str) > 0
        # And back
        parsed = json.loads(json_str)
        assert parsed["name"] == "orders"


# ---------------------------------------------------------------------------
# SemanticModel tests — query helpers
# ---------------------------------------------------------------------------

class TestSemanticModelQueryHelpers:
    """Tests for column/metric lookup methods."""

    def test_get_column_by_name(self):
        model = make_model()
        col = model.get_column("amount")
        assert col is not None
        assert col.name == "amount"

    def test_get_column_by_alias(self):
        col = make_column("金额", aliases=["销售额", "revenue"])
        model = make_model(columns=[col])
        found = model.get_column("revenue")
        assert found is not None
        assert found.name == "金额"

    def test_get_column_not_found(self):
        model = make_model()
        assert model.get_column("nonexistent") is None

    def test_get_metric(self):
        model = make_model()
        m = model.get_metric("总销售额")
        assert m is not None
        assert m.sql_expr == "SUM(amount)"

    def test_get_metric_not_found(self):
        model = make_model()
        assert model.get_metric("不存在的指标") is None

    def test_get_metric_columns(self):
        model = make_model()
        metrics = model.get_metric_columns()
        assert len(metrics) >= 1
        assert all(c.role == ColumnRole.METRIC for c in metrics)

    def test_get_dimension_columns(self):
        model = make_model()
        dims = model.get_dimension_columns()
        assert len(dims) >= 1
        assert all(c.role == ColumnRole.DIMENSION for c in dims)

    def test_get_date_columns(self):
        date_col = make_column("order_date", role=ColumnRole.DATE, unit="", agg_default=None, format="date")
        model = make_model(columns=[date_col])
        dates = model.get_date_columns()
        assert len(dates) == 1
        assert dates[0].name == "order_date"

    def test_get_geo_columns(self):
        geo_col = make_column("province", role=ColumnRole.GEO, unit="", agg_default=None, format="")
        model = make_model(columns=[geo_col])
        geos = model.get_geo_columns()
        assert len(geos) == 1
        assert geos[0].name == "province"

    def test_resolve_metric_sql_defined_metric(self):
        model = make_model()
        sql = model.resolve_metric_sql("总销售额")
        assert sql == "SUM(amount)"

    def test_resolve_metric_sql_column_with_agg(self):
        model = make_model()
        sql = model.resolve_metric_sql("amount")
        assert "amount" in sql

    def test_resolve_metric_sql_dimension_column(self):
        model = make_model()
        sql = model.resolve_metric_sql("region")
        # Dimension columns should not get aggregation wrapper
        assert "(" not in sql
        assert "region" in sql

    def test_resolve_metric_sql_fallback(self):
        model = make_model()
        sql = model.resolve_metric_sql("raw_column")
        assert sql == "raw_column"


# ---------------------------------------------------------------------------
# SemanticModel tests — prompt context
# ---------------------------------------------------------------------------

class TestSemanticModelPromptContext:
    """Tests for to_prompt_context()."""

    def test_prompt_context_contains_name(self):
        model = make_model()
        ctx = model.to_prompt_context()
        assert "orders" in ctx
        assert "业务模型" in ctx

    def test_prompt_context_contains_columns(self):
        model = make_model()
        ctx = model.to_prompt_context()
        assert "字段" in ctx
        assert "amount" in ctx
        assert "region" in ctx

    def test_prompt_context_contains_metrics(self):
        model = make_model()
        ctx = model.to_prompt_context()
        assert "业务指标" in ctx
        assert "总销售额" in ctx
        assert "SUM(amount)" in ctx

    def test_prompt_context_contains_relationships(self):
        model = make_model(relationships=[make_relationship()])
        ctx = model.to_prompt_context()
        assert "关联关系" in ctx
        assert "products" in ctx

    def test_prompt_context_no_relationships(self):
        model = make_model()
        ctx = model.to_prompt_context()
        assert "关联关系" not in ctx  # No relationships defined

    def test_prompt_context_is_string(self):
        model = make_model()
        ctx = model.to_prompt_context()
        assert isinstance(ctx, str)
        assert len(ctx) > 50


# ---------------------------------------------------------------------------
# ModelManager tests — file operations
# ---------------------------------------------------------------------------

class TestModelManagerFileOps:
    """Tests for save/load/delete/list."""

    @pytest.fixture
    def mgr(self):
        """Create a ModelManager with a temp directory."""
        tmpdir = tempfile.mkdtemp(prefix="semantic_test_")
        mgr = ModelManager(models_dir=tmpdir)
        yield mgr
        # Cleanup
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_save_and_load(self, mgr):
        model = make_model(name="test_model")
        path = mgr.save(model)
        assert os.path.exists(path)
        assert path.endswith(".json")

        loaded = mgr.load("test_model")
        assert loaded is not None
        assert loaded.name == "test_model"
        assert loaded.table == "orders"

    def test_save_with_custom_filename(self, mgr):
        model = make_model(name="original_name")
        path = mgr.save(model, filename="custom_filename")
        assert "custom_filename" in path

    def test_load_nonexistent(self, mgr):
        result = mgr.load("does_not_exist")
        assert result is None

    def test_delete(self, mgr):
        model = make_model(name="to_delete")
        mgr.save(model)
        assert mgr.delete("to_delete") is True
        assert mgr.load("to_delete") is None

    def test_delete_nonexistent(self, mgr):
        assert mgr.delete("never_saved") is False

    def test_list_models_empty(self, mgr):
        result = mgr.list_models()
        assert result == []

    def test_list_models(self, mgr):
        mgr.save(make_model(name="model_a"), "model_a")
        mgr.save(make_model(name="model_b"), "model_b")
        result = mgr.list_models()
        assert len(result) == 2
        names = [m["name"] for m in result]
        assert "model_a" in names
        assert "model_b" in names

    def test_list_models_returns_metadata(self, mgr):
        mgr.save(make_model(name="m1"), "m1")
        result = mgr.list_models()
        m = result[0]
        assert "name" in m
        assert "table" in m
        assert "columns" in m
        assert "metrics" in m
        assert "relationships" in m
        assert "description" in m

    def test_save_updates_timestamp(self, mgr):
        model = make_model(name="ts_test")
        mgr.save(model)
        cached = mgr.models["ts_test"]
        assert cached.updated_at is not None
        assert cached.updated_at != ""


# ---------------------------------------------------------------------------
# ModelManager tests — prompt context
# ---------------------------------------------------------------------------

class TestModelManagerPromptContext:
    """Tests for get_prompt_context()."""

    @pytest.fixture
    def mgr(self):
        tmpdir = tempfile.mkdtemp(prefix="semantic_ctx_")
        mgr = ModelManager(models_dir=tmpdir)
        mgr.save(make_model(name="orders"), "orders")
        mgr.save(make_model(name="products", table="products",
                           columns=[make_column("price", unit="元")],
                           metrics=[make_metric("平均价格", sql_expr="AVG(price)")]),
                 "products")
        yield mgr
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_get_prompt_context_all(self, mgr):
        ctx = mgr.get_prompt_context()
        assert "orders" in ctx
        assert "products" in ctx
        assert "---" in ctx  # Separator between models

    def test_get_prompt_context_specific(self, mgr):
        ctx = mgr.get_prompt_context(["orders"])
        assert "orders" in ctx
        assert "products" not in ctx

    def test_get_prompt_context_empty_names(self, mgr):
        ctx = mgr.get_prompt_context([])
        # Empty list returns empty string (no models to query)
        assert ctx == ""

    def test_get_prompt_context_nonexistent_name(self, mgr):
        ctx = mgr.get_prompt_context(["nonexistent"])
        assert ctx == ""

    def test_get_prompt_context_no_models(self):
        tmpdir = tempfile.mkdtemp(prefix="empty_sem_")
        mgr = ModelManager(models_dir=tmpdir)
        ctx = mgr.get_prompt_context()
        assert ctx == ""
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# ColumnRole and AggFunction enums
# ---------------------------------------------------------------------------

class TestEnums:
    def test_column_role_values(self):
        assert ColumnRole.METRIC.value == "metric"
        assert ColumnRole.DIMENSION.value == "dimension"
        assert ColumnRole.DATE.value == "date"

    def test_join_type_values(self):
        assert JoinType.LEFT.value == "LEFT JOIN"
        assert JoinType.INNER.value == "INNER JOIN"

    def test_agg_function_values(self):
        assert AggFunction.SUM.value == "SUM"
        assert AggFunction.AVG.value == "AVG"
        assert AggFunction.COUNT.value == "COUNT"


# ---------------------------------------------------------------------------
# ModelManager — column builder helper tests
# ---------------------------------------------------------------------------

class TestModelManagerColumnBuilder:
    """Tests for _build_column_def and related helpers."""

    @pytest.fixture
    def mgr(self):
        return ModelManager()

    def test_is_ratio_metric_chinese(self, mgr):
        assert mgr._is_ratio_metric("转化率") is True
        assert mgr._is_ratio_metric("占比") is True

    def test_is_ratio_metric_english(self, mgr):
        assert mgr._is_ratio_metric("conversion_rate") is True
        assert mgr._is_ratio_metric("pct_change") is True

    def test_is_ratio_metric_false(self, mgr):
        assert mgr._is_ratio_metric("销售额") is False
        assert mgr._is_ratio_metric("quantity") is False

    def test_generate_aliases_金额(self, mgr):
        aliases = mgr._generate_aliases("金额", ColumnRole.METRIC)
        assert len(aliases) > 0
        assert "销售额" in aliases or "收入" in aliases or "revenue" in aliases

    def test_generate_aliases_unknown(self, mgr):
        aliases = mgr._generate_aliases("xyz_unknown_col", ColumnRole.UNKNOWN)
        assert aliases == []

    def test_generate_metric_name(self, mgr):
        col = make_column("金额", aliases=["销售额"])
        name = mgr._generate_metric_name(col, AggFunction.SUM)
        assert "总" in name
