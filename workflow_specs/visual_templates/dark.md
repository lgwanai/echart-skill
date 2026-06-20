# Dark Visual Specification

Use this when the user requests dark mode or a monitoring/command-center dashboard.

## Tone

Formal, low-glare, operations-ready.

## Report Direction

- Dark paper on darker application background.
- Maintain strong contrast for headings and tables.
- Avoid neon-heavy styling.
- Use subtle borders and restrained shadows.
- Keep print output legible; reports may switch to white background in `@media print`.

Suggested palette:

- Page background: `#0b1220`
- Paper: `#111a2c`
- Muted surface: `#172033`
- Text: `#eef2f8`
- Muted text: `#b7c1d3`
- Accent: `#7aa2ff`
- Border: `#26344c`
- Warning: `#fbbf24`
- Critical: `#f87171`

## Dashboard Direction

- Prioritize scanability over decoration.
- Use bright colors only for status, threshold, or alerts.
- Ensure chart labels and grid lines remain readable.
- Keep interactive controls visible but quiet.

## CSS Contract

The Agent may write CSS directly into the generated HTML. Avoid external fonts,
remote images, external stylesheets, and one-note purple/blue gradients.
