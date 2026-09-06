import re
import sys

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

FONT = r"C:\Users\local\AppData\Local\Temp\arrayfont\Array_Complete\Fonts\WEB\fonts\Array-Bold.ttf"
FONT_SIZE = 46.0

projects = {
    "flurren": "Flurren",
    "yoana": "Yoana",
}


def banner(text: str) -> str:
    blob = hb.Blob.from_file_path(FONT)
    face = hb.Face(blob)
    font = hb.Font(face)
    upm = face.upem
    font.scale = (upm, upm)

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})

    tt = TTFont(FONT)
    glyph_set = tt.getGlyphSet()
    glyph_order = tt.getGlyphOrder()
    scale = FONT_SIZE / upm

    paths, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gname = glyph_order[info.codepoint]
        pen = SVGPathPen(glyph_set)
        tpen = TransformPen(pen, Transform(scale, 0, 0, -scale, x + pos.x_offset * scale, 0))
        glyph_set[gname].draw(tpen)
        d = pen.getCommands()
        if d:
            paths.append(f'<path d="{d}"/>')
        x += pos.x_advance * scale

    width = round(x + 8, 1)
    inner = "\n".join(paths)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="64" viewBox="0 0 {width} 64">\n'
            '<style>.t{fill:#ffffff}@media (prefers-color-scheme:light){.t{fill:#000000}}</style>\n'
            f'<g class="t" transform="translate(4 52)">{inner}</g>\n</svg>\n')


for slug, name in projects.items():
    path = f"assets/project-{slug}.svg"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(banner(name))
    print(path)
