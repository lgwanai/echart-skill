from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_mixed_line_bar_recipe_requires_dual_axis():
    content = read_doc("references/examples/mix-line-bar.md")

    assert "dual yAxis" in content
    assert "yAxisIndex: 0" in content
    assert "yAxisIndex: 1" in content
    assert "different magnitudes" in content


def test_mixed_line_bar_template_pins_series_to_separate_axes():
    content = read_doc("references/templates/mix/line-bar.html")

    assert "required dual yAxis" in content
    assert "yAxisIndex: 0" in content
    assert "yAxisIndex: 1" in content


def test_skill_mentions_global_dual_axis_rule_for_mixed_charts():
    content = read_doc("SKILL.md")

    assert "组合图双坐标硬规则" in content
    assert "yAxisIndex: 0" in content
    assert "yAxisIndex: 1" in content
