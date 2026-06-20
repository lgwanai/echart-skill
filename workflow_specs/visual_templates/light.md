# Light Visual Specification

Use this as the default visual direction for Agent-authored reports and dashboards.

## Tone

Formal, enterprise, executive-review ready.

## Report Direction

- Paper-like canvas centered on a muted application background.
- Header should feel like a PDF cover: title, subtitle, date, scope, and optional confidence/assumption note.
- Use numbered sections.
- Use compact tables with strong header rows.
- Use conclusion cards only for material findings.
- Print styles should remove app background and shadows.

Suggested palette:

- Page background: `#e9edf5`
- Paper: `#ffffff`
- Text: `#172033`
- Muted text: `#667085`
- Accent: `#1f5eff`
- Border: `#d8dee9`
- Warning: `#b45309`
- Critical: `#c81e1e`

## Dashboard Direction

- Restrained header and toolbar.
- KPI cards should be compact and comparable.
- Charts should use consistent spacing and axis styling.
- Use blue as accent, not as the entire palette.
- Use green/yellow/red only for semantic status.

## CSS Contract

The Agent may write CSS directly into the generated HTML. Avoid external fonts,
remote images, external stylesheets, and generic decorative gradients.
