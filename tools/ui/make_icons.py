"""
The game's UI icons (Assets/Resources/UI/Icons/<name>.png): simple line glyphs in one style, white
on a transparent background (RGBA), so the buttons' theme colours show through and the code can
tint them. Drawn on a 24-unit grid with one stroke width and round ends, like a minimal line-icon
set; antialiased by 4x4 supersampling.

python3 tools/ui/make_icons.py [out_dir] [--preview]
"""
import math, os, struct, sys, zlib

SIZE = 256          # pixels
UNIT = SIZE / 24.0  # the 24-unit design grid
STROKE = 1.9        # line width, in units
SS = 4              # supersamples per axis

def seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - dx * t, py - ay - dy * t)

class Icon:
    # stroke: line width in units (STROKE unless given); turn: degrees the whole glyph is turned
    # clockwise about the grid's centre; scale: its size about the centre (so a turned glyph fits)
    # tilt: the glyph laid back and seen from above at that many degrees (its height shrinks by
    # its sine, after the turn), for a lying-down look
    def __init__(self, stroke=STROKE, turn=0.0, scale=1.0, tilt=90.0):
        self.lines = []   # polylines (stroked)
        self.fills = []   # (kind, params): filled discs / ellipses
        self.stroke, self.turn, self.scale = stroke, math.radians(turn), scale
        self.squash = math.sin(math.radians(tilt))
    def poly(self, pts): self.lines.append(pts); return self
    def line(self, *pts): return self.poly(list(pts))
    def arc(self, cx, cy, r, a0, a1, n=48):
        return self.poly([(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                           cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)])
    def disc(self, cx, cy, r): self.fills.append(("e", cx, cy, r, r, 0.0)); return self
    def ellipse(self, cx, cy, rx, ry, rot=0.0): self.fills.append(("e", cx, cy, rx, ry, math.radians(rot))); return self
    def inside(self, x, y):
        if self.turn or self.scale != 1.0 or self.squash != 1.0: # back into the glyph's own frame
            c, s = math.cos(self.turn), math.sin(self.turn)
            dx, dy = (x - 12) / self.scale, (y - 12) / self.scale / self.squash
            x, y = 12 + dx * c + dy * s, 12 - dx * s + dy * c
        w = self.stroke / 2 / self.scale # (approximate where squashed: lines across get a little thinner)
        for pts in self.lines:
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                if seg(x, y, ax, ay, bx, by) <= w: return True
        for _, cx, cy, rx, ry, rot in self.fills:
            dx, dy = x - cx, y - cy
            c, s = math.cos(rot), math.sin(rot)
            u, v = dx * c + dy * s, -dx * s + dy * c
            if (u / rx) ** 2 + (v / ry) ** 2 <= 1: return True
        return False

def render(icon):
    rows = []
    for py in range(SIZE):
        row = bytearray()
        for px in range(SIZE):
            hit = 0
            for sy in range(SS):
                for sx in range(SS):
                    x = (px + (sx + 0.5) / SS) / UNIT
                    y = (py + (sy + 0.5) / SS) / UNIT
                    hit += icon.inside(x, y)
            row += bytes((255, 255, 255, round(255 * hit / (SS * SS))))
        rows.append(bytes(row))
    return rows

def write_png(path, rows):
    raw = b"".join(b"\x00" + r for r in rows)
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

def icons():
    out = {}
    # (the Evolution Tree button uses the evolve icon too, UiIcons.Tree)
    # a closed book set at a slant: the cover, its rounded spine and the page block at the foot
    b = Icon(stroke=1.4, turn=-35, scale=0.95)
    b.poly([(7, 19.5), (7, 5.5), (8.5, 4), (18, 4), (18, 17), (8.5, 17)])
    b.arc(8.5, 18.25, 1.25, 90, 270, 16)
    b.poly([(8.5, 19.5), (18, 19.5), (18, 17)])
    out["encyclopedia"] = b
    # revive: a circular arrow, its head pointing on round the circle
    r = Icon().arc(12, 12.5, 7.5, -20, 285)
    a1 = math.radians(285)
    ex, ey = 12 + 7.5 * math.cos(a1), 12.5 + 7.5 * math.sin(a1)
    tx, ty = -math.sin(a1), math.cos(a1)          # the way round (increasing angle)
    nx, ny = math.cos(a1), math.sin(a1)           # outward
    r.line((ex - tx * 3.4 + nx * 2.6, ey - ty * 3.4 + ny * 2.6), (ex + tx * 0.6, ey + ty * 0.6), (ex - tx * 3.4 - nx * 2.6, ey - ty * 3.4 - ny * 2.6))
    out["revive"] = r
    # evolve: a DNA double helix, one turn, with rungs across each half, turned 45 degrees
    d = Icon(turn=45, scale=0.95)
    def hx(y): return 12 + 4.6 * math.sin((y - 2.5) / 19 * 2 * math.pi)
    ys = [2.5 + i * 0.19 for i in range(101)]
    d.poly([(hx(y), y) for y in ys]).poly([(24 - hx(y), y) for y in ys])
    for y in (7.25, 16.75): # a rung across each half, at its widest, set in from the strands
        half = abs(hx(y) - 12) - 1.7
        if half > 0.6: d.line((12 - half, y), (12 + half, y))
    out["evolve"] = d
    # functions (body form): a nautilus shell, its logarithmic spiral with the chambers of the last
    # whorl (slightly bowed septa) and the aperture closing it, centred on the grid
    b_, R = 0.19, 9.0
    T = math.log(R / 0.7) / b_                    # from r = 0.7 out to R
    def nr(t): return R * math.exp(b_ * (t - T))
    def npt(t): return (nr(t) * math.cos(t), nr(t) * math.sin(t))
    spiral = [npt(T * i / 300) for i in range(301)]
    ox = 12 - (max(x for x, _ in spiral) + min(x for x, _ in spiral)) / 2
    oy = 12 - (max(y for _, y in spiral) + min(y for _, y in spiral)) / 2
    def at(q): return (q[0] + ox, q[1] + oy)
    f = Icon(stroke=1.6).poly([at(q) for q in spiral])
    f.line(at(npt(T)), at(npt(T - 2 * math.pi)))
    for k in range(1, 7):
        t = T - k * 2 * math.pi / 7
        tb = t - 0.18
        rb = (nr(tb) + nr(tb - 2 * math.pi)) / 2
        f.poly([at(npt(t)), at((rb * math.cos(tb), rb * math.sin(tb))), at(npt(t - 2 * math.pi))])
    out["functions"] = f
    # behaviors: a paw print
    p = Icon().ellipse(12, 15.5, 4.2, 3.4)
    for cx, cy, rot in ((6.6, 10.6, -20), (9.8, 7.0, -8), (14.2, 7.0, 8), (17.4, 10.6, 20)): p.ellipse(cx, cy, 1.55, 2.1, rot)
    out["behaviors"] = p
    # reproduce: a cell dividing in two, two overlapping rings
    out["reproduce"] = Icon().arc(8.8, 12, 5.0, 0, 360, 64).arc(15.2, 12, 5.0, 0, 360, 64)
    return out

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "..", "Assets", "Resources", "UI", "Icons")
    os.makedirs(out_dir, exist_ok=True)
    for name, icon in icons().items():
        write_png(os.path.join(out_dir, name + ".png"), render(icon))
        print("wrote", name)
