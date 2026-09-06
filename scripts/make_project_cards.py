import re

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

FONT = r"C:\Users\local\AppData\Local\Temp\arrayfont\Array_Complete\Fonts\WEB\fonts\Array-Bold.ttf"
FONT_SIZE = 40.0
PAD = 14.0
CONTENT_W = 360.0

projects = {
    "flurren": {
        "name": "Flurren",
        "desc": "Agentic AI mesh that plugs into the CLI tools you already use.",
    },
    "yoana": {
        "name": "Yoana",
        "desc": "An e-commerce website for a farm, built for browsing and ordering fresh produce online.",
    },
}


def shape_name(text):
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
    return "\n".join(paths), x * 1.0


def wrap(text, limit=44):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) <= limit:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(slug, name, desc):
    name_paths, name_w = shape_name(name)
    total_w = CONTENT_W + PAD * 2
    name_x = round(PAD + (CONTENT_W - name_w) / 2, 1)
    desc_lines = wrap(desc)
    y = 46.0  # name baseline (keeps ~16px gap above the name)
    texts, ty = [], y + 34
    for line in desc_lines:
        texts.append(f'<text x="{PAD + CONTENT_W / 2}" y="{round(ty, 1)}" class="d" text-anchor="middle">{line}</text>')
        ty += 22

    btn_w, btn_h = 118.0, 34.0
    btn_x = round(PAD + (CONTENT_W - btn_w) / 2, 1)
    btn_y = round(ty + 10, 1)
    height = round(btn_y + btn_h + PAD, 1)

    inner = name_paths  # already newline-joined by shape_name()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{height}" viewBox="0 0 {total_w} {height}">
<style>
.d{{font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-size:15px;fill:#c9d1d9}}
.bt{{font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:1px;fill:#000000}}
@media (prefers-color-scheme:light){{.d{{fill:#57606a}}}}
</style>
<g transform="translate({name_x} {y})" class="n">{inner}</g>
{chr(10).join(texts)}
<rect x="{btn_x}" y="{btn_y}" width="{btn_w}" height="{btn_h}" rx="{btn_h / 2}" fill="#ffffff" stroke="#d0d7de"/>
<text x="{btn_x + btn_w / 2}" y="{btn_y + btn_h / 2 + 4.5}" class="bt" text-anchor="middle">VISIT &#8594;</text>
</svg>
'''


for slug, p in projects.items():
    path = f"assets/card-{slug}.svg"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(card(slug, p["name"], p["desc"]))
    print(path)
