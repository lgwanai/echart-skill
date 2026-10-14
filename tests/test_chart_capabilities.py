from pathlib import Path

from scripts.chart_capabilities import allowed_views, load_catalog, recommend_view
from scripts.reference_assets import get_asset


ROOT = Path(__file__).resolve().parents[1]


def test_catalog_relations_reference_known_views_and_existing_recipes():
    catalog = load_catalog()
    for relation in catalog["relations"].values():
        assert set(relation["allowed"]) <= set(catalog["views"])
        assert set(relation["preferred"]) <= set(relation["allowed"])
    for view in catalog["views"].values():
        if recipe := view.get("recipe"):
            assert get_asset(ROOT, recipe)['content'], recipe


def test_recommender_selects_line_for_time_series():
    result = recommend_view({
        "relation": "time",
        "roles": ["time", "metric"],
        "category_count": 12,
        "measure_count": 1,
    })

    assert result["selected"]["view"] == "line"
    assert result["table_mode"] == "source_toggle"


def test_recommender_rejects_pie_for_many_categories_and_uses_companion_table():
    result = recommend_view({
        "relation": "composition",
        "roles": ["category", "positive_metric", "metric", "series"],
        "category_count": 20,
        "measure_count": 2,
        "exact_lookup": True,
    })

    assert any(item["view"] == "pie" for item in result["rejected"])
    assert result["table_mode"] == "companion"


def test_analysis_plan_view_matrix_comes_from_catalog():
    assert "waterfall" in allowed_views("deviation")
    assert "pie" not in allowed_views("time")
