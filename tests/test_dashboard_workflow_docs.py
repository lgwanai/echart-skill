from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_dashboard_workflow_requires_city_sales_map_module_from_markdown():
    workflow = read_doc("workflow_specs/dashboard_workflow.md")

    assert "workflow_specs/dashboard_modules/city_sales_map.md" in workflow
    assert "metadata" in workflow.lower()
    assert "references/examples/geo-map-scatter.md" in workflow
    assert "Dashboard charts are not written from memory" in workflow
    assert "blocking failure" in workflow


def test_dashboard_workflow_prevents_invented_titles_and_shallow_dashboards():
    workflow = read_doc("workflow_specs/dashboard_workflow.md")
    skill = read_doc("SKILL.md")
    readme = read_doc("README.md")

    assert "Do not invent a product, brand, or industry label" in workflow
    assert "white liquor" in workflow
    assert "Minimum depth for business dashboards" in workflow
    assert "at least 6 analytical modules" in workflow
    assert "白酒分析" in skill
    assert "至少包含 6 个分析模块" in readme


def test_city_sales_map_module_uses_chart_recipes_and_fallback():
    module = read_doc("workflow_specs/dashboard_modules/city_sales_map.md")

    assert "Do not implement this as a fixed Python renderer" in module
    assert "references/examples/geo-map-scatter.md" in module
    assert "references/examples/bar-simple.md" in module
    assert "销量" in module
    assert "effectScatter" in module
    assert "blocking requirement" in module
    assert "china.js" in module
    assert "地图坐标待补充" in module


def test_sales_and_general_experts_reference_city_map_module():
    sales = read_doc("workflow_specs/expert_library/sales_ecommerce.md")
    general = read_doc("workflow_specs/expert_library/general_management.md")

    assert "workflow_specs/dashboard_modules/city_sales_map.md" in sales
    assert "workflow_specs/dashboard_modules/city_sales_map.md" in general
