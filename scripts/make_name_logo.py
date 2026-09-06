import re

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

FONT = r"C:\Users\local\AppData\Local\Temp\arrayfont\Array_Complete\Fonts\WEB\fonts\Array-Bold.ttf"
TEXT = "Leo Gimpel"
FONT_SIZE = 46.0
LOGO_BOX = 58.0
GAP = 16.0
MARGIN = 6.0

blob = hb.Blob.from_file_path(FONT)
face = hb.Face(blob)
hbfont = hb.Font(face)
upm = face.upem
hbfont.scale = (upm, upm)

buf = hb.Buffer()
buf.add_str(TEXT)
buf.guess_segment_properties()
hb.shape(hbfont, buf, {"kern": True, "liga": True})

infos, positions = buf.glyph_infos, buf.glyph_positions
tt = TTFont(FONT)
glyph_set = tt.getGlyphSet()
glyph_order = tt.getGlyphOrder()
scale = FONT_SIZE / upm

paths = []
x_cursor = 0.0
for info, pos in zip(infos, positions):
    gname = glyph_order[info.codepoint]
    pen = SVGPathPen(glyph_set)
    tpen = TransformPen(pen, Transform(scale, 0, 0, -scale, x_cursor + pos.x_offset * scale, 0))
    glyph_set[gname].draw(tpen)
    d = pen.getCommands()
    if d:
        paths.append(f'<path transform="translate(0 71)" d="{d}"/>')
    x_cursor += (pos.x_advance) * scale

text_width = round(x_cursor, 1)
width = round(MARGIN * 2 + text_width + GAP + LOGO_BOX, 1)

d_blocks = "\n".join(paths)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="100" viewBox="0 0 {width} 100">
<style>
.t{{fill:#ffffff}}
@media (prefers-color-scheme:light){{.t{{fill:#000000}}}}
</style>
<g class="t">
{d_blocks}
</g>
<svg x="{round(MARGIN + text_width + GAP, 1)}" y="27" width="{LOGO_BOX}" height="{LOGO_BOX}" viewBox="0 0 4500 4500">LOGO_INNER</svg>
</svg>
'''

logo = open("logo.svg", encoding="utf-8").read()
logo_inner = re.sub(r"^\s*<svg[^>]*>", "", logo)
logo_inner = re.sub(r"</svg>\s*$", "", logo_inner)
svg = svg.replace("LOGO_INNER", logo_inner)

open("name-logo.svg", "w", encoding="utf-8", newline="\n").write(svg)
print(f"text width: {text_width}, total: {width}, glyphs: {len(paths)}")
