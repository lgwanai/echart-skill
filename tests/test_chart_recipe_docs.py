from pathlib import Path

from scripts.reference_assets import get_asset


ROOT = Path(__file__).resolve().parents[1]


def test_mixed_line_bar_recipe_requires_dual_axis():
    asset = get_asset(ROOT, "mix-line-bar")
    content = asset["content"]

    assert "dual yAxis" in content
    assert "yAxisIndex: 0" in content
    assert "yAxisIndex: 1" in content
    assert "different magnitudes" in content


def test_skill_mentions_global_dual_axis_rule_for_mixed_charts():
    content = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "组合图双坐标硬规则" in content
    assert "yAxisIndex: 0" in content
    assert "yAxisIndex: 1" in content
