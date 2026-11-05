#!/usr/bin/env python3
"""
build_card.py  ->  dark_mode.svg + light_mode.svg
Neofetch-style profile card: your photo as ASCII on the left, "about me" on the right.

Run locally:   pip install pillow  &&  python build_card.py
Needs:         me.jpg (the face crop used for the ASCII portrait)
The daily GitHub Action re-runs this, so the "Uptime" line stays current.
"""
import calendar
from datetime import date
from html import escape

from PIL import Image, ImageChops, ImageFilter, ImageOps

# ═══════════════════════ EDIT THIS SECTION ═══════════════════════
PHOTO = "me.jpg"
BIRTH = date(2007, 6, 26)     # drives the live "Uptime" line
COLS = 100                    # ASCII width. Higher = more detail, bigger file

# ("head", "text")           -> name line
# ("title", "Section name")  -> a section divider
# ("kv", "Key", "Value")     -> a line with dotted leader
# ("blank",)                 -> empty line
# Placeholder: {uptime}
INFO = [
    ("head", "Nirjala Sharma"),
    ("kv", "Uptime", "{uptime}"),
    ("kv", "Host", "India"),
    ("kv", "Kernel", "B.Tech CSE (AI/ML), Batch of 2028"),
    ("kv", "IDE", "VS Code, Android Studio, AntiGravity"),
    ("blank",),
    ("kv", "Languages.Code", "Python, Java, C++, C, TypeScript, SQL"),
    ("kv", "Languages.Human", "English, Hindi"),
    ("blank",),
    ("kv", "Interests.Tech", "ML systems, Digital Forensics, FastAPI + React"),
    ("kv", "Interests.Life", "Debate, Anchoring, Creative writing"),
    ("kv", "Currently", "Going deeper into MLOps + backend"),
    ("blank",),
    ("title", "Contact"),
    ("kv", "Email", "nirjalasharmawork@gmail.com"),
    ("kv", "LinkedIn", "nirjala-sharma-9b808a330"),
    ("kv", "Location", "Pune, India"),
]
# ═════════════════════════════════════════════════════════════════

LINE_W = 62                   # chars per info line (leader dots fill the gap)
ART_FS, ART_LH = 6, 7         # ASCII font size / line height
INFO_FS, INFO_LH = 13, 19
ART_X, INFO_X = 28, 440
RAMP = " .,:;i1tfLCG08@"       # light -> dense

THEMES = {
    "dark":  dict(bg="#0d1117", bar="#161b22", art="#8b949e", key="#ffa657",
                  dim="#484f58", val="#a5d6ff", text="#c9d1d9", head="#7ee787"),
    "light": dict(bg="#ffffff", bar="#f6f8fa", art="#57606a", key="#bc4c00",
                  dim="#afb8c1", val="#0550ae", text="#24292f", head="#1a7f37"),
}


def ascii_art(path, cols):
    im = Image.open(path).convert("L")
    im = ImageOps.autocontrast(im, cutoff=2)
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=300, threshold=2))   # crisp up a blurry photo
    im = Image.blend(im, ImageOps.equalize(im), 0.6)                               # spread tones so skin shading shows
    # darkness map: hair/eyes/shadows -> dense chars, bright wall -> empty
    dark = ImageOps.invert(im).point(lambda p: int(255 * (p / 255) ** 0.9))
    edges = ImageOps.autocontrast(im.filter(ImageFilter.GaussianBlur(1)).filter(ImageFilter.FIND_EDGES), cutoff=3)
    edges = edges.point(lambda p: int(p * 1.0))           # eyes, brows, nose, mouth, jaw
    im = ImageOps.invert(ImageChops.lighter(dark, edges))
    w, h = im.size
    rows = max(1, int(cols * h / w * 0.5))      # chars are ~2x taller than wide
    im = im.resize((cols, rows))
    px = im.load()
    lines = []
    for y in range(rows):
        row = ""
        for x in range(cols):
            v = 255 - px[x, y]   # dark areas (hair, eyes, shadows) = dense chars; light wall = empty
            row += RAMP[int(v / 255 * (len(RAMP) - 1))]
        lines.append(row.rstrip())
    return lines


def uptime(born):
    t = date.today()
    y, m, d = t.year - born.year, t.month - born.month, t.day - born.day
    if d < 0:
        m -= 1
        prev_month = t.month - 1 or 12
        prev_year = t.year if t.month > 1 else t.year - 1
        d += calendar.monthrange(prev_year, prev_month)[1]
    if m < 0:
        y -= 1
        m += 12
    return f"{y} years, {m} months, {d} days"


def build(theme_name, vals):
    c = THEMES[theme_name]
    art = ascii_art(PHOTO, COLS)
    height = max(len(art) * ART_LH, len(INFO) * INFO_LH) + 80
    width = 1000
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" rx="12" fill="{c["bg"]}"/>',
        f'<path d="M0 12a12 12 0 0 1 12-12h{width-24}a12 12 0 0 1 12 12v22H0z" fill="{c["bar"]}"/>',
        '<circle cx="22" cy="17" r="6" fill="#ff5f56"/><circle cx="42" cy="17" r="6" fill="#ffbd2e"/><circle cx="62" cy="17" r="6" fill="#27c93f"/>',
        f'<text x="{width//2}" y="22" fill="{c["dim"]}" font-size="12" text-anchor="middle" '
        f'font-family="ui-monospace,Consolas,monospace">Nirjala Sharma ~ README.md</text>',
        '<g font-family="ui-monospace,SFMono-Regular,Consolas,\'Liberation Mono\',Menlo,monospace" xml:space="preserve">',
    ]
    # ASCII portrait
    o.append(f'<g font-size="{ART_FS}" fill="{c["art"]}">')
    for i, line in enumerate(art):
        o.append(f'<text x="{ART_X}" y="{62 + i * ART_LH}">{escape(line)}</text>')
    o.append("</g>")
    # Info panel
    o.append(f'<g font-size="{INFO_FS}">')
    for i, item in enumerate(INFO):
        y = 62 + i * INFO_LH
        kind = item[0]
        if kind == "head":
            o.append(f'<text x="{INFO_X}" y="{y}" fill="{c["head"]}" font-weight="bold">{escape(item[1])}</text>')
        elif kind == "title":
            name = item[1]
            rule = "-" * (LINE_W - len(name) - 4)
            o.append(f'<text x="{INFO_X}" y="{y}" fill="{c["text"]}">- {escape(name)} '
                     f'<tspan fill="{c["dim"]}">{rule}-</tspan></text>')
        elif kind == "kv":
            key, val = item[1], item[2].format(**vals)
            dots = "." * max(2, LINE_W - len(key) - len(val) - 2)
            o.append(
                f'<text x="{INFO_X}" y="{y}"><tspan fill="{c["key"]}">{escape(key)}</tspan>'
                f'<tspan fill="{c["dim"]}">: {dots} </tspan><tspan fill="{c["val"]}">{escape(val)}</tspan></text>'
            )
    o.append("</g></g></svg>")
    with open(f"{theme_name}_mode.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print(f"wrote {theme_name}_mode.svg ({height}px tall)")


if __name__ == "__main__":
    vals = {"uptime": uptime(BIRTH)}
    for t in THEMES:
        build(t, vals)
