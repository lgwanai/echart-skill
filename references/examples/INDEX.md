# Chart entry point

Read `references/chart_guide.md` first. Common charts are compiled from explicit
data mappings with `scripts/chart_builder.py`.

353 historical demos are preserved in `references/legacy_examples.zip`. Read one
on demand; do not extract or load the entire archive into model context:

```bash
python scripts/reference_assets.py list --limit 20
python scripts/reference_assets.py search "bar" --limit 3
python scripts/reference_assets.py get mix-line-bar
```

The API preserves virtual `references/examples/<name>.md` paths. Local custom
Markdown overrides archived examples. Historical demos are not quality-certified
templates; the chart guide supersedes their data-replacement instructions.
The portable package omits this optional archive; use the full package for
advanced examples. Common charts and all quality validators remain available.
