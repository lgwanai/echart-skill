"""
Build Agent context files from 356 ECharts official examples.
Each output .md contains: title, category, meta, option code, related template, debug patterns.
Output: references/examples/
"""
import json, os, re, sys

SRC = os.path.expanduser("~/workspace/echarts-examples")
OUT = os.path.abspath("references/examples")
TPL_DIR = os.path.abspath("references/templates")
DEBUG_LOG = os.path.abspath("docs/CHART_DEBUG_LOG.md")
os.makedirs(OUT, exist_ok=True)

# ── Load debug patterns ──
debug_patterns = ""
if os.path.exists(DEBUG_LOG):
    with open(DEBUG_LOG) as f:
        debug_patterns = f.read()

# ── Template catalog ──
template_catalog = {}
if os.path.exists(TPL_DIR):
    for root, dirs, files in os.walk(TPL_DIR):
        for f in files:
            if f.endswith('.html'):
                path = os.path.join(root, f)
                with open(path) as tf:
                    content = tf.read()
                # Extract category from comment
                cat_match = re.search(r'Chart Type:\s*(.+?)(?:\(|$)', content)
                cat = cat_match.group(1).strip() if cat_match else ""
                data_match = re.search(r'Data Format:\s*(.+)', content)
                fmt = data_match.group(1).strip() if data_match else ""
                template_catalog[os.path.relpath(path, TPL_DIR)] = {
                    "category": cat, "data_format": fmt
                }

# ── Map template to example categories ──
def find_template(category):
    """Find the best matching template for an example category."""
    cat_lower = category.lower()
    for tpl_path, info in template_catalog.items():
        tpl_cat = info["category"].lower()
        # Direct match
        if cat_lower == tpl_cat:
            return tpl_path, info
        # Substring match
        if cat_lower in tpl_cat or tpl_cat in cat_lower:
            return tpl_path, info
    return "", {}

# ── Find relevant debug patterns by keyword ──
def find_debug_section(category):
    """Extract relevant debug log sections for this category."""
    if not debug_patterns:
        return ""
    keywords = category.lower().split()
    # Find sections marked as ## #N — ...
    sections = re.split(r'\n## #(\d+)\b', debug_patterns)
    relevant = []
    for i in range(1, len(sections), 2):
        num = sections[i]
        content = sections[i+1] if i+1 < len(sections) else ""
        for kw in keywords:
            if kw in content.lower():
                relevant.append(f"## #{num}\n{content[:500]}...")
                break
    return "\n\n".join(relevant[:3])

# ── Process all examples ──
count = 0
for dname in sorted(os.listdir(SRC)):
    dpath = os.path.join(SRC, dname)
    if not os.path.isdir(dpath) or dname.startswith('.'):
        continue

    js_path = os.path.join(dpath, "main.js")
    meta_path = os.path.join(dpath, "meta.json")

    if not os.path.exists(js_path):
        continue

    # Read meta
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)

    category = meta.get("category", dname.split("-")[0])
    title_cn = meta.get("title_cn", meta.get("title_en", dname))
    title_en = meta.get("title_en", dname)

    # Read main.js
    with open(js_path) as f:
        js_code = f.read()

    # Extract option code (after header comment)
    option_code = re.sub(r'/\*.*?\*/', '', js_code, flags=re.DOTALL).strip()

    # Find matching template
    tpl_path, tpl_info = find_template(category)

    # Find relevant debug patterns
    debug_section = find_debug_section(category)

    # Build markdown
    md = f"""# {title_cn} / {title_en}

**Category:** `{category}`
**Example dir:** `{dname}`
**Difficulty:** {meta.get('difficulty', 'N/A')}

## Template Match
{f'- **{tpl_path}** — {tpl_info.get("category","")}' if tpl_path else '⚠️ No matching template — use knowledge base'}

## Option Code
```javascript
{option_code[:3000]}
```

{f'## Relevant Debug Patterns\n{debug_section}' if debug_section else ''}

## Key Points
- This is an official ECharts example from `{dname}/main.js`
- Template data format: `{tpl_info.get("data_format","N/A")}`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
"""

    out_path = os.path.join(OUT, f"{dname}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)

    count += 1
    if count % 50 == 0:
        print(f"  ... {count} examples processed")

print(f"\n{'='*60}")
print(f"  Generated {count} Agent context files")
print(f"  Output: {OUT}")
print(f"{'='*60}")
