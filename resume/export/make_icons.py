#!/usr/bin/env python3
"""Render Font Awesome glyphs to tight PNG icons for the resume contact row.

Writes PNGs + aspects.json into resume/export/icons/. The icons are committed,
so you normally do not need to run this; it's here to regenerate if needed
(requires the `fontawesomefree` and `pillow` packages).
"""
import importlib.util
import json
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

ICONS_DIR = Path(__file__).resolve().parent / "icons"
ICONS_DIR.mkdir(parents=True, exist_ok=True)

spec = importlib.util.find_spec("fontawesomefree")
base = Path(spec.submodule_search_locations[0])
SOLID = next(base.glob("**/fa-solid-900.ttf"))
BRANDS = next(base.glob("**/fa-brands-400.ttf"))

GLYPHS = {
    "email": ("\uf0e0", SOLID),
    "phone": ("\uf095", SOLID),
    "github": ("\uf09b", BRANDS),
    "linkedin": ("\uf08c", BRANDS),
}

aspects = {}
SIZE = 240
for name, (char, fontpath) in GLYPHS.items():
    font = ImageFont.truetype(str(fontpath), SIZE)
    canvas = Image.new("RGBA", (SIZE * 2, SIZE * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    bbox = d.textbbox((0, 0), char, font=font)
    d.text((-bbox[0], -bbox[1]), char, font=font, fill=(17, 17, 17, 255))
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    canvas.crop((0, 0, w, h)).save(ICONS_DIR / f"{name}.png")
    aspects[name] = w / h

(ICONS_DIR / "aspects.json").write_text(json.dumps(aspects))
print("icons written to", ICONS_DIR, aspects)
