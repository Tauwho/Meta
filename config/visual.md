# Visual style

One recognisable look across every story so a reader scrolling a feed knows it is you before reading the byline.

## Cover (featured image)

- **Default: generated typographic cover** (`medium cover <id>` → `package/cover.png`, 1400×788). Solid background from the palette, title in the display font, small series/niche label, thin accent rule. Same template every time; only the background colour rotates by niche.
- **Alternative: photo cover** via Medium's built-in Unsplash picker when a story is about a place or object. Rules: natural light, muted colours, no stock-photo handshakes or laptops-on-desks, no visible text, no faces looking at the camera. Credit is added automatically by Medium.
- Never mix both on one story. Never use AI-generated photoreal images of people.

## Palette

| Role | Hex |
|---|---|
| Ink (text on light) | `#1A1A1A` |
| Paper (light background) | `#F5F1EA` |
| Accent | `#C8553D` |
| Niche backgrounds | set per niche in `pipeline.yaml` → `visual.niche_colors` |

## Inline figures (diagrams, charts)

- Flat, 2D, white or paper background, ink lines, one accent colour for the thing that matters. No gradients, 3D or drop shadows.
- Same font family as the cover. Labels in sentence case.
- Width 1400px, PNG. Max 3 figures per story; each must explain something text alone explains worse.
- Alt text describes what the figure shows, not "diagram".
- Caption: `What it shows, in one sentence. Credit: Author` (or source).

## AI-generated illustrations (optional)

Only if a story genuinely needs an illustration. Use the fixed style suffix from `pipeline.yaml` → `visual.illustration_style` so every image matches, and caption it `Illustration generated with <tool>`.
