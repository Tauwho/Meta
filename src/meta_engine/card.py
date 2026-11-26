"""Text cards: the post's hook drawn on a branded 4:5 gradient, for image posts."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350  # 4:5, the tallest ratio feeds show uncropped
MARGIN = 110
FONT_BOLD = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "DejaVuSans-Bold.ttf"]
FONT_REG = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "DejaVuSans.ttf"]

# (top colour, bottom colour, text colour): soft, warm palettes for the love niche
PALETTES = [
    ((255, 214, 224), (255, 170, 190), (74, 20, 40)),
    ((255, 228, 206), (255, 182, 159), (80, 34, 20)),
    ((236, 220, 255), (199, 170, 245), (45, 25, 80)),
    ((40, 24, 48), (110, 40, 80), (255, 236, 242)),
    ((255, 244, 214), (255, 205, 170), (70, 40, 20)),
]


def _font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    raise OSError("no usable font found (needs a font with Vietnamese glyphs, e.g. Segoe UI)")


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if draw.textlength(trial, font=font) <= width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    return lines


def render(text: str, handle: str, out: Path, seed: str = "") -> Path:
    """Draw `text` (shrinking the font until it fits) and save a PNG to `out`."""
    top, bottom, ink = PALETTES[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(PALETTES)]
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        row = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
        for x in range(W):
            px[x, y] = row
    draw = ImageDraw.Draw(img)

    box_w, box_h = W - 2 * MARGIN, H - 2 * MARGIN - 120
    for size in range(96, 39, -4):
        font = _font(FONT_BOLD, size)
        lines = _wrap(draw, text.strip(), font, box_w)
        line_h = int(size * 1.45)  # room for stacked Vietnamese diacritics
        if line_h * len(lines) <= box_h:
            break
    y = MARGIN + (box_h - line_h * len(lines)) // 2 + 60
    draw.text((MARGIN, y - int(size * 1.3)), "“", font=_font(FONT_BOLD, int(size * 1.6)), fill=ink)
    for line in lines:
        draw.text((MARGIN, y), line, font=font, fill=ink)
        y += line_h
    small = _font(FONT_REG, 38)
    draw.text((MARGIN, H - MARGIN - 20), f"@{handle}", font=small, fill=ink)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out
