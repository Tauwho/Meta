"""Branded assets: the typographic cover template and a paste-ready HTML export.

Same template every story (see config/visual.md), so the feed look stays consistent.
"""

from __future__ import annotations

from pathlib import Path

from . import config, store


def _font(candidates: list[str], size: int):
    from PIL import ImageFont

    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def _wrap(draw, text: str, font, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _luminance(rgb: tuple[int, int, int]) -> float:
    return (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255


def render_cover(title: str, label: str, background: str, out: Path) -> Path:
    from PIL import Image, ImageDraw

    v = config.settings()["visual"]
    w, h = v["cover_size"]
    pal = v["palette"]
    bg = _hex(background)
    fg = _hex(pal["paper"]) if _luminance(bg) < 0.5 else _hex(pal["ink"])
    accent = _hex(pal["accent"])

    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    margin = int(w * 0.08)
    text_w = w - 2 * margin

    # Largest title size that fits in 4 lines.
    for size in range(96, 39, -4):
        font = _font(v["fonts"]["display"], size)
        lines = _wrap(d, title, font, text_w)
        if len(lines) <= 4:
            break
    line_h = int(size * 1.18)
    block_h = line_h * len(lines)
    y = (h - block_h) // 2 + int(h * 0.04)

    label_font = _font(v["fonts"]["label"], 28)
    d.text((margin, y - 90), label.upper(), font=label_font, fill=fg)
    d.rectangle([margin, y - 40, margin + 120, y - 34], fill=accent)
    for line in lines:
        d.text((margin, y), line, font=font, fill=fg)
        y += line_h

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def cover(story: store.Story, meta: dict | None = None) -> Path:
    v = config.settings()["visual"]
    title = (meta or {}).get("title") or story.idea.get("title", story.id)
    niche = story.idea.get("niche", "")
    bg = v.get("niche_colors", {}).get(niche, v["palette"]["paper"])
    return render_cover(title, niche or "Essay", bg, story.path("package/cover.png"))


def export_html(story: store.Story, source: str = "package/final.md") -> Path:
    """Render markdown to HTML; open it in a browser, select all, paste into the Medium editor."""
    import markdown

    md = story.read(source) if story.path(source).exists() else story.read("package/story.md")
    body = markdown.markdown(md, extensions=["fenced_code", "tables"])
    html = (
        "<!doctype html><meta charset='utf-8'><title>paste into Medium</title>"
        "<body style='max-width:700px;margin:40px auto;font-family:Georgia,serif;line-height:1.6'>"
        f"{body}</body>"
    )
    out = story.path(Path(source).with_suffix(".html").as_posix())
    out.write_text(html, encoding="utf-8")
    return out
