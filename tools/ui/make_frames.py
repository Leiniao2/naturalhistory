"""Menu frame textures for GameMenusStyle.uss: 9-slice panel / HUD / button frames and the
title divider, drawn at 2x (the stylesheet uses -unity-slice-scale: 0.5). Pure Python, no deps.

    python3 tools/ui/make_frames.py            # writes Assets/Resources/UI/Frames/*.png
    python3 tools/ui/make_frames.py --preview  # also writes a preview sheet to /tmp/nh_frames.png
"""
import math, os, struct, sys, zlib

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "Assets", "Resources", "UI", "Frames")
SS = 4  # supersamples per axis

BRASS_LIGHT = (232, 204, 136)
BRASS       = (190, 154, 88)
BRASS_DARK  = (104, 80, 42)
RIM         = (6, 9, 7)


def png(path, w, h, px):
    raw = b"".join(b"\x00" + bytes(px[y * w * 4:(y + 1) * w * 4]) for y in range(h))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def render(w, h, shade):
    """shade(x, y) -> premultiplied-free (r, g, b, a) in 0..1, averaged over SS x SS samples."""
    px = []
    for y in range(h):
        for x in range(w):
            r = g = b = a = 0.0
            for j in range(SS):
                for i in range(SS):
                    cr, cg, cb, ca = shade(x + (i + 0.5) / SS, y + (j + 0.5) / SS)
                    r += cr * ca; g += cg * ca; b += cb * ca; a += ca
            n = SS * SS
            if a > 0: r, g, b = r / a, g / a, b / a
            px += [round(min(1, r) * 255), round(min(1, g) * 255), round(min(1, b) * 255), round(a / n * 255)]
    return px


def over(dst, col, a):
    """Composite colour col (0..255 rgb) with alpha a over dst (r, g, b, a in 0..1)."""
    if a <= 0: return dst
    r, g, b, da = dst
    oa = a + da * (1 - a)
    if oa <= 0: return (0, 0, 0, 0)
    f = lambda c, d: (c / 255 * a + d * da * (1 - a)) / oa
    return (f(col[0], r), f(col[1], g), f(col[2], b), oa)


def lerp(c0, c1, t):
    t = max(0.0, min(1.0, t))
    return tuple(a + (b - a) * t for a, b in zip(c0, c1))


def box(x, y, w, h, inset, r):
    """Signed distance to a rounded rectangle inset from the texture edges."""
    hx, hy = w / 2 - inset, h / 2 - inset
    qx, qy = abs(x - w / 2) - hx + r, abs(y - h / 2) - hy + r
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r


def chamfer(x, y, w, h, inset, c):
    hx, hy = w / 2 - inset, h / 2 - inset
    ax, ay = abs(x - w / 2), abs(y - h / 2)
    return max(ax - hx, ay - hy, (ax + ay - (hx + hy - c)) / math.sqrt(2))


def edge_dist(x, y, w, h):
    return min(x, y, w - x, h - y)


# ---------- big modal panels: dark rim, brass bevel line, inner line with cut corners and corner diamonds ----------

def panel(fill=(24, 33, 27), fill_a=0.975, S=128):
    def shade(x, y):
        c = (0, 0, 0, 0)
        d0 = box(x, y, S, S, 0.5, 15)
        c = over(c, RIM, 0.85 * min(1, max(0, 0.5 - d0)))
        d1 = box(x, y, S, S, 3, 13)
        if d1 < 0.5:
            vig = min(1, edge_dist(x, y, S, S) / 26)
            c = over(c, lerp(tuple(v * 0.62 for v in fill), fill, vig ** 0.7), fill_a * min(1, 0.5 - d1))
        # outer brass line, bevelled: light outside, dark inside
        d2 = box(x, y, S, S, 7, 9)
        if abs(d2) < 2.2:
            col = lerp(BRASS_LIGHT, BRASS_DARK, (2.2 - d2) / 4.4)
            c = over(c, col, min(1, 2.2 - abs(d2)))
        # inner thin line: rectangle with concave quarter-circle corners
        ins, R = 15, 9
        dr = box(x, y, S, S, ins, 0)
        cx = ins if x < S / 2 else S - ins
        cy = ins if y < S / 2 else S - ins
        dc = math.hypot(x - cx, y - cy) - R
        d3 = max(dr, -dc)
        c = over(c, BRASS, 0.75 * min(1, max(0, 0.9 - abs(d3))))
        # corner diamond with a dark pip
        dd = abs(x - cx) + abs(y - cy)
        if dd < 8.5:
            c = over(c, BRASS_DARK, min(1, 8.5 - dd))
            c = over(c, lerp(BRASS_LIGHT, BRASS, (y - cy + 7) / 14), min(1, 7 - dd))
            c = over(c, RIM, 0.8 * min(1, max(0, 2.2 - math.hypot(x - cx, y - cy))))
        return c
    return S, S, render(S, S, shade)


# ---------- HUD cards and info panels: thin rim, chamfered brass line, small corner studs ----------

def hud(fill=(22, 29, 25), fill_a=0.93, line=BRASS, line_w=1.2, S=64):
    def shade(x, y):
        c = (0, 0, 0, 0)
        d0 = box(x, y, S, S, 0.5, 8)
        c = over(c, RIM, 0.8 * min(1, max(0, 0.5 - d0)))
        d1 = box(x, y, S, S, 2, 7)
        if d1 < 0.5:
            vig = min(1, edge_dist(x, y, S, S) / 12)
            c = over(c, lerp(tuple(v * 0.7 for v in fill), fill, vig), fill_a * min(1, 0.5 - d1))
        d2 = chamfer(x, y, S, S, 4.5, 4)
        if abs(d2) < line_w + 1:
            col = lerp(tuple(min(255, v * 1.18) for v in line), tuple(v * 0.6 for v in line), (-d2 + line_w) / (2 * line_w))
            c = over(c, col, min(1, line_w + 0.5 - abs(d2)))
        cx = 9.5 if x < S / 2 else S - 9.5
        cy = 9.5 if y < S / 2 else S - 9.5
        dd = abs(x - cx) + abs(y - cy)
        c = over(c, line, 0.9 * min(1, max(0, 2.6 - dd)))
        return c
    return S, S, render(S, S, shade)


# ---------- buttons: vertical gradient, top sheen, brass edge ----------

def button(top, bottom, line=BRASS, line_a=0.9, W=64, H=64):
    def shade(x, y):
        c = (0, 0, 0, 0)
        d0 = box(x, y, W, H, 0.5, 9)
        c = over(c, RIM, 0.85 * min(1, max(0, 0.5 - d0)))
        d1 = box(x, y, W, H, 2, 8)
        if d1 < 0.5:
            t = (y - 2) / (H - 4)
            col = lerp(top, bottom, max(0.0, t) ** 0.9)
            c = over(c, col, min(1, 0.5 - d1))
            # sheen just under the top edge
            c = over(c, (255, 255, 255), 0.10 * max(0, 1 - abs(y - 5.5) / 2.2) * min(1, -d1 / 3))
        d2 = box(x, y, W, H, 3, 7)
        c = over(c, lerp(tuple(min(255, v * 1.15) for v in line), tuple(v * 0.7 for v in line), y / H),
                 line_a * min(1, max(0, 1.4 - abs(d2))))
        return c
    return W, H, render(W, H, shade)


# ---------- title divider: brass rule fading out both ways, diamond and pips in the middle ----------

def divider(W=512, H=32):
    cy, cx = H / 2, W / 2
    def shade(x, y):
        c = (0, 0, 0, 0)
        u = abs(x - cx) / cx
        fade = max(0, 1 - u) ** 1.4
        c = over(c, BRASS, 0.85 * fade * min(1, max(0, 1.3 - abs(y - cy))))
        c = over(c, BRASS_DARK, 0.5 * fade * min(1, max(0, 1.0 - abs(y - cy - 4)) ) * (u > 0.06))
        c = over(c, BRASS_DARK, 0.5 * fade * min(1, max(0, 1.0 - abs(y - cy + 4)) ) * (u > 0.06))
        for px in (cx - 30, cx + 30):
            dd = abs(x - px) + abs(y - cy)
            c = over(c, BRASS_LIGHT, min(1, max(0, 4.2 - dd)))
        dd = abs(x - cx) * 0.8 + abs(y - cy)
        if dd < 12:
            c = over(c, RIM, min(1, 12 - dd))
            c = over(c, lerp(BRASS_LIGHT, BRASS_DARK, (y - cy + 10) / 20), min(1, 10.5 - dd))
            c = over(c, RIM, 0.75 * min(1, max(0, 4.5 - dd)))
            c = over(c, BRASS_LIGHT, min(1, max(0, 2.5 - dd)))
        return c
    return W, H, render(W, H, shade)


FRAMES = {
    "panel":                lambda: panel(),
    "hud":                  lambda: hud(),
    "hud-hover":            lambda: hud(fill=(40, 54, 42), fill_a=0.96, line=BRASS_LIGHT),
    "hud-gold":             lambda: hud(line=BRASS_LIGHT, line_w=1.9),
    "button":               lambda: button((66, 82, 64), (34, 44, 36)),
    "button-hover":         lambda: button((92, 114, 86), (48, 62, 48), line=BRASS_LIGHT, line_a=1),
    "button-primary":       lambda: button((86, 140, 82), (44, 84, 48), line=BRASS_LIGHT),
    "button-primary-hover": lambda: button((110, 168, 102), (58, 104, 60), line=BRASS_LIGHT, line_a=1),
    "button-gold":          lambda: button((176, 136, 52), (110, 78, 26), line=BRASS_LIGHT, line_a=1),
    "button-gold-hover":    lambda: button((204, 162, 70), (130, 94, 34), line=(250, 228, 170), line_a=1),
    "button-danger":        lambda: button((128, 60, 52), (76, 32, 28)),
    "button-danger-hover":  lambda: button((160, 76, 64), (96, 40, 34), line=BRASS_LIGHT, line_a=1),
    "divider":              lambda: divider(),
}


def nine(px, w, h, sl, tw, th):
    """Nearest-sample 9-slice of a texture to tw x th (preview only)."""
    def src(d, size, tsize):
        if d < sl: return d
        if d >= tsize - sl: return size - (tsize - d)
        return sl + (d - sl) * (size - 2 * sl) // max(1, tsize - 2 * sl)
    out = []
    for y in range(th):
        sy = src(y, h, th)
        for x in range(tw):
            i = (sy * w + src(x, w, tw)) * 4
            out.append(px[i:i + 4])
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    made = {}
    for name, make in FRAMES.items():
        w, h, px = make()
        made[name] = (w, h, px)
        png(os.path.join(OUT, name + ".png"), w, h, px)
        print("wrote", name, w, h)
    if "--preview" in sys.argv:
        PW, PH = 900, 700
        sheet = [[40, 60, 50, 255] for _ in range(PW * PH)]
        def blit(name, sl, x0, y0, tw, th):
            w, h, px = made[name]
            tile = nine(px, w, h, sl, tw, th) if sl else [px[i:i + 4] for i in range(0, len(px), 4)]
            for y in range(th):
                for x in range(tw):
                    s = tile[y * tw + x]; a = s[3] / 255; d = sheet[(y0 + y) * PW + x0 + x]
                    sheet[(y0 + y) * PW + x0 + x] = [round(s[k] * a + d[k] * (1 - a)) for k in range(3)] + [255]
        blit("panel", 40, 20, 20, 520, 420)
        blit("divider", 0, 24, 90, 512, 32)
        for i, n in enumerate(["button", "button-hover", "button-primary", "button-gold", "button-danger"]):
            blit(n, 26, 80, 150 + i * 56, 380, 48)
        blit("hud", 20, 570, 20, 300, 200)
        blit("hud-hover", 20, 570, 240, 300, 80)
        blit("hud-gold", 20, 570, 340, 300, 80)
        png(os.environ.get("NH_PREVIEW", "/tmp/nh_frames.png"), PW, PH, [v for p in sheet for v in p])
        print("preview written")
