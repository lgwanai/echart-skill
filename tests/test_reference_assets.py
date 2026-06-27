from pathlib import Path

from scripts.reference_assets import (
    get_asset,
    list_assets,
    search_assets,
)


def test_search_and_get(tmp_path):
    root = tmp_path / "project"
    recipe_dir = root / "references" / "examples"
    recipe_dir.mkdir(parents=True)

    (recipe_dir / "line-simple.md").write_text(
        "# Simple Line Chart\n\n```js\nseries: [{ type: 'line' }]\n```",
        encoding="utf-8",
    )
    (recipe_dir / "bar-stack.md").write_text(
        "# Stacked Bar Chart\n\n```js\nseries: [{ type: 'bar', stack: 'x' }]\n```",
        encoding="utf-8",
    )

    rows = search_assets(root, "simple line", limit=3)
    assert rows[0]["path"] == "references/examples/line-simple.md"
    assert rows[0]["chart_type"] == "line"
    assert "score" in rows[0]

    asset = get_asset(root, "line-simple")
    assert "Simple Line Chart" in asset["content"]

    all_rows = list_assets(root, limit=10)
    assert len(all_rows) == 2

    bars = search_assets(root, "chart", chart_type="bar", limit=5)
    assert len(bars) == 1
    assert bars[0]["chart_type"] == "bar"

    assert search_assets(root, "", limit=3) == []


def test_get_asset_missing_file(tmp_path):
    root = tmp_path / "noproject"
    root.mkdir()
    try:
        get_asset(root, "nonexistent")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")


def test_list_filtered(tmp_path):
    root = tmp_path / "project"
    example_dir = root / "references" / "examples"
    example_dir.mkdir(parents=True)

    (example_dir / "bar-simple.md").write_text("# Bar\n\nbar", encoding="utf-8")
    (example_dir / "line-simple.md").write_text("# Line\n\nline", encoding="utf-8")

    bars = list_assets(root, chart_type="bar", limit=10)
    assert len(bars) == 1
    assert bars[0]["chart_type"] == "bar"

    lines = list_assets(root, chart_type="line", limit=10)
    assert len(lines) == 1
    assert lines[0]["chart_type"] == "line"
