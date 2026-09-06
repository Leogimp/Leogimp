import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

FONT = r"C:\Users\local\AppData\Local\Temp\arrayfont\Array_Complete\Fonts\WEB\fonts\Array-Bold.ttf"
NAME_SIZE = 40.0
W, H = 760.0, 196.0
MARGIN = 12.0  # baked transparent side padding (~3% total gap between cards)

projects = {
    "flurren": {
        "name": "Flurren",
        "desc": "Agentic AI mesh that plugs into the CLI tools you already use.",
    },
    "yoana": {
        "name": "Yoana",
        "desc": "E-commerce website for a farm - fresh produce online.",
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
    scale = NAME_SIZE / upm
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
    return "\n".join(paths), x


def wrap(text, limit=48):
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


def card(name, desc):
    name_paths, name_w = shape_name(name)
    name_x = round((W - name_w) / 2, 1)
    lines = wrap(desc)
    cx = W / 2

    texts, ty = [], 88.0
    for line in lines:
        texts.append(f'<text x="{cx}" y="{ty}" class="d" text-anchor="middle">{line}</text>')
        ty += 22

    btn_w, btn_h = 128.0, 36.0
    btn_y = 148.0  # fixed: buttons always on the same level

    inner = name_paths  # already newline-joined by shape_name()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.bd{{fill:none;stroke:#30363d;stroke-width:1.5}}
.d{{font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-size:15px;fill:#c9d1d9}}
.bt{{font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:1px;fill:#000000}}
@media (prefers-color-scheme:light){{
.bd{{stroke:#d0d7de}}.d{{fill:#57606a}}
}}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" class="bd"/>
<g transform="translate({name_x} 52)" class="n">{inner}</g>
{chr(10).join(texts)}
<rect x="{round((W - btn_w) / 2, 1)}" y="{btn_y}" width="{btn_w}" height="{btn_h}" rx="{btn_h / 2}" fill="#ffffff" stroke="#d0d7de"/>
<text x="{cx}" y="{btn_y + btn_h / 2 + 4.5}" class="bt" text-anchor="middle">VISIT &#8594;</text>
</svg>
'''


for slug, p in projects.items():
    path = f"assets/card-{slug}.svg"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(card(p["name"], p["desc"]))
    print(path)
