from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_dashboard_expert_library_exists_and_is_dashboard_specific():
    index = read_doc("workflow_specs/dashboard_expert_library/INDEX.md")
    template = read_doc("workflow_specs/dashboard_expert_library/DASHBOARD_EXPERT_TEMPLATE.md")

    assert "This library is dedicated to dashboards" in index
    assert "Do not use report experts as the primary dashboard planning source" in index
    assert "Mandatory Dashboard Expert Loop" in index
    assert "Interaction Model" in template
    assert "Validation Checklist" in template


def test_dashboard_workflow_uses_dashboard_expert_library():
    workflow = read_doc("workflow_specs/dashboard_workflow.md")
    skill = read_doc("SKILL.md")
    readme = read_doc("README.md")

    assert "workflow_specs/dashboard_expert_library/INDEX.md" in workflow
    assert "general_business_dashboard.md" in workflow
    assert "workflow_specs/dashboard_expert_library/INDEX.md" in skill
    assert "workflow_specs/dashboard_expert_library/DASHBOARD_EXPERT_TEMPLATE.md" in skill
    assert "workflow_specs/dashboard_expert_library/INDEX.md" in readme
    assert "workflow_specs/dashboard_expert_library/DASHBOARD_EXPERT_TEMPLATE.md" in readme


def test_sales_dashboard_expert_requires_city_map_and_depth():
    expert = read_doc("workflow_specs/dashboard_expert_library/sales_ecommerce_dashboard.md")

    assert "City sales/volume map" in expert
    assert "workflow_specs/dashboard_modules/city_sales_map.md" in expert
    assert "references/examples/geo-map-scatter.md" in expert
    assert "At least 6 analytical modules" in expert
    assert "does not invent an industry such as white liquor" in expert
