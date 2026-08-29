"""Repair deterministic data-embedding failures in generated chart HTML.

Usage:
    python scripts/repair_chart_html.py dashboard.html --in-place
    python scripts/repair_chart_html.py dashboard.html --output repaired.html

The in-place mode writes ``<file>.bak`` before changing the source.
"""

import argparse
import json
import re
import shutil
from pathlib import Path


JSON_PARSE = re.compile(r"\bJSON\s*\.\s*parse\s*\(")


def _mask_js_strings_and_comments(script):
    chars = list(script)
    index = 0
    state = "code"
    quote = None
    escape = False
    while index < len(chars):
        char = chars[index]
        next_char = chars[index + 1] if index + 1 < len(chars) else ""
        if state == "line_comment":
            if char in "\r\n":
                state = "code"
            else:
                chars[index] = " "
        elif state == "block_comment":
            chars[index] = " "
            if char == "*" and next_char == "/":
                chars[index + 1] = " "
                index += 1
                state = "code"
        elif state == "string":
            chars[index] = " "
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                state = "code"
                quote = None
        elif char == "/" and next_char == "/":
            chars[index] = chars[index + 1] = " "
            index += 1
            state = "line_comment"
        elif char == "/" and next_char == "*":
            chars[index] = chars[index + 1] = " "
            index += 1
            state = "block_comment"
        elif char in ("'", '"', "`"):
            chars[index] = " "
            state = "string"
            quote = char
        index += 1
    return "".join(chars)


def _extract_json_literal(text, start):
    opener = text[start]
    closer = "}" if opener == "{" else "]"
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""


def _as_safe_js_string(value):
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def repair_content(content):
    """Quote strict JSON object/array literals passed directly to JSON.parse."""
    edits = []
    masked_content = _mask_js_strings_and_comments(content)
    for match in JSON_PARSE.finditer(masked_content):
        argument_start = match.end()
        while argument_start < len(content) and content[argument_start].isspace():
            argument_start += 1
        if argument_start >= len(content) or content[argument_start] not in "{[":
            continue
        raw_literal = _extract_json_literal(content, argument_start)
        if not raw_literal:
            continue
        try:
            json.loads(raw_literal)
        except json.JSONDecodeError:
            continue
        edits.append(
            (
                argument_start,
                argument_start + len(raw_literal),
                _as_safe_js_string(raw_literal),
            )
        )

    for start, end, replacement in reversed(edits):
        content = content[:start] + replacement + content[end:]
    return content, len(edits)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--in-place", action="store_true")
    destination.add_argument("--output", type=Path)
    args = parser.parse_args()

    original = args.html.read_text(encoding="utf-8")
    repaired, count = repair_content(original)
    if not count:
        print(f"No repairable JSON.parse object/array literal found in {args.html}")
        return 0

    if args.in_place:
        backup = Path(str(args.html) + ".bak")
        suffix = 1
        while backup.exists():
            backup = Path(f"{args.html}.bak.{suffix}")
            suffix += 1
        shutil.copy2(args.html, backup)
        destination_path = args.html
        backup_note = f"; backup: {backup}"
    else:
        destination_path = args.output
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        backup_note = ""
    destination_path.write_text(repaired, encoding="utf-8")
    print(f"Repaired {count} invalid JSON.parse call(s): {destination_path}{backup_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
