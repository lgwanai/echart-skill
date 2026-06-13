"""
Build all 356 ECharts official examples as self-contained HTML files.

Reads each example's main.js (ECharts option definition) from the
echarts-examples repository, wraps it in a self-contained HTML with
inline ECharts library, and outputs to examples/all_356/.

Source: /Users/wuliang/workspace/echarts-examples/
Output: examples/all_356/
"""
import json, os, re, sys, shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SRC  = os.path.expanduser("~/workspace/echarts-examples")
OUT  = os.path.abspath("examples/all_356")
EJS  = "assets/echarts/echarts.min.js"  # ECharts lib

if not os.path.isdir(SRC):
    print(f"ERROR: {SRC} not found")
    sys.exit(1)

os.makedirs(OUT, exist_ok=True)

# Load inline ECharts
with open(EJS, "rb") as f:
    ECHARTS_JS = f.read().decode("utf-8", errors="replace")

# Load all example directories
dirs = sorted(
    d for d in os.listdir(SRC)
    if os.path.isdir(os.path.join(SRC, d)) and not d.startswith(".")
)
print(f"Found {len(dirs)} example directories")

# HTML template
TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>
<body>
<div id="main" style="width:100vw;height:100vh;"></div>
<script>
{echarts_js}
</script>
<script>
(function() {{
    var chart = echarts.init(document.getElementById('main'));
    var option;
    {option_js}
    if (typeof option !== 'undefined' && option) chart.setOption(option);
    window.addEventListener('resize', function() {{ chart.resize(); }});
}})();
</script>
</body>
</html>"""

results = []
for i, dname in enumerate(dirs):
    dpath = os.path.join(SRC, dname)
    js_path = os.path.join(dpath, "main.js")
    meta_path = os.path.join(dpath, "meta.json")

    if not os.path.isfile(js_path):
        results.append(("⏭️", dname, "no main.js"))
        continue

    with open(js_path) as f:
        js = f.read()

    # Remove comments
    js_clean = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
    js_clean = re.sub(r'//.*$', '', js_clean, flags=re.MULTILINE)

    # Extract option/var option/let option/const option = {...};
    # Also handle `myChart.setOption({...})` and `app.config = {...}`
    m = None
    for pat in [
        r'(?:var\s+|let\s+|const\s+)?option\s*=\s*(\{.*?\n\})\s*;',
        r'(?:var\s+|let\s+|const\s+)?option\s*=\s*(\{.*?\})\s*;',
        r'\.setOption\s*\(\s*(\{.*?\n\})\s*\)',
        r'\.setOption\s*\(\s*(\{.*?\})\s*\)',
    ]:
        candidates = list(re.finditer(pat, js_clean, re.DOTALL))
        if candidates:
            # Take the LAST match (usually the final option)
            m = candidates[-1]
            break

    if not m:
        # Try bracket-matching approach: find first { after 'option =' or 'setOption('
        for marker in ['option = {', 'option= {', 'setOption({', 'setOption( {']:
            idx = js_clean.find(marker)
            if idx >= 0:
                start = js_clean.index('{', idx)
                depth = 0
                end = start
                for j in range(start, len(js_clean)):
                    if js_clean[j] == '{': depth += 1
                    elif js_clean[j] == '}':
                        depth -= 1
                        if depth == 0:
                            end = j + 1
                            break
                if end > start:
                    option_str = js_clean[start:end]
                    m = True  # signal success
                    break

    if not m:
        # Fallback: embed entire JS (minus header comment) for complex examples
        js_body = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL).strip()
        if js_body:
            option_str = None
            raw_js = js_body
        else:
            results.append(("❌", dname, "option not found, no JS body"))
            continue
    else:
        raw_js = None
        if m is not True:
            option_str = m.group(1)
        # else: option_str already set by bracket matching

    # Read meta for title
    title = dname
    if os.path.isfile(meta_path):
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            title = meta.get("title_cn", meta.get("title_en", dname))
        except json.JSONDecodeError:
            pass

    # Build HTML
    if raw_js:
        # Complex example: embed entire JS as-is
        option_block = raw_js
    else:
        option_block = f"option = {option_str};"

    html = TEMPLATE.format(
        title=f"{title} ({dname})",
        echarts_js=ECHARTS_JS,
        option_js=option_block,
    )

    out_path = os.path.join(OUT, f"{dname}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    results.append(("✅", dname, title))

    if (i + 1) % 50 == 0:
        print(f"  ... {i+1}/{len(dirs)}")

# Summary
ok  = sum(1 for r in results if r[0] == "✅")
sk  = sum(1 for r in results if r[0] == "⏭️")
bad = sum(1 for r in results if r[0] == "❌")
print(f"\n{'═'*60}")
print(f"  Results: {ok} passed, {bad} failed, {sk} skipped ({len(results)} total)")
print(f"{'═'*60}")

if bad:
    for s, n, t in results:
        if s == "❌":
            print(f"  ❌ {n}: {t}")

with open(os.path.join(OUT, "_summary.json"), "w") as f:
    json.dump([{"status": s, "dir": n, "title": t} for s, n, t in results], f, ensure_ascii=False, indent=2)

# Copy index
with open(os.path.join(OUT, "_INDEX.html"), "w") as f:
    f.write("""<!DOCTYPE html><html><head><meta charset="utf-8"><title>ECharts 356 Examples</title>
<style>body{font-family:system-ui;max-width:900px;margin:2rem auto;background:#0f172a;color:#e2e8f0}
a{color:#60a5fa;text-decoration:none}a:hover{text-decoration:underline}
li{margin:3px 0}.cat{margin-top:20px;color:#f59e0b}</style></head><body>
<h1>ECharts 356 Official Examples</h1>
""")
    cats = {}
    for s, n, t in results:
        if s != "✅": continue
        cat = n.split("-")[0]
        cats.setdefault(cat, []).append((n, t))
    for cat in sorted(cats):
        f.write(f'<h2 class="cat">{cat} ({len(cats[cat])})</h2><ul>')
        for n, t in cats[cat]:
            f.write(f'<li><a href="{n}.html">{t}</a> <small>({n})</small></li>')
        f.write('</ul>')
    f.write(f'<hr><p>Total: {ok} examples</p></body></html>')

print(f"Output: {OUT}")
print(f"Index:  {OUT}/_INDEX.html")
