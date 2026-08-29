import json
import re

from scripts.repair_chart_html import repair_content


def test_repair_quotes_json_object_passed_to_json_parse():
    source = '<script>const DATA = JSON.parse({"items":[1,2,3]});</script>'

    repaired, count = repair_content(source)

    assert count == 1
    argument = re.search(r"JSON\.parse\((.+)\)", repaired).group(1)
    assert json.loads(json.loads(argument)) == {"items": [1, 2, 3]}


def test_repair_leaves_valid_json_string_embedding_unchanged():
    source = '<script>const DATA = JSON.parse("{\\\"items\\\":[1]}");</script>'

    repaired, count = repair_content(source)

    assert count == 0
    assert repaired == source


def test_repair_ignores_example_inside_javascript_string():
    source = '<script>const note = "Do not use JSON.parse({});";</script>'

    repaired, count = repair_content(source)

    assert count == 0
    assert repaired == source
