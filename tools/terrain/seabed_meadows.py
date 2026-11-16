"""Paints the seabed / lakebed 'meadow' floor textures (Assets/Textures/Terrain/Under{Kind}{Meadow}.png):
seagrass blades, brown kelp fronds, mixed red and green seaweed, freshwater waterweed whorls, over
the plain under-layer floor. Strokes are drawn wrapped round the edges, so the textures tile seamlessly.
Needs numpy and Pillow.  Run: python3 tools/terrain/seabed_meadows.py
"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "Assets", "Textures", "Terrain")
N = 512

def base(name):
    return Image.open(os.path.join(TEX, name + ".png")).convert("RGB").resize((N, N))

def clumps(rng, cells=6, keep=0.6):
    # low-frequency mask (0..1) that wraps: where the meadow grows thick
    g = np.array([[rng.random() for _ in range(cells)] for _ in range(cells)])
    img = Image.fromarray((g * 255).astype(np.uint8)).resize((N, N), Image.BICUBIC)
    a = np.asarray(img.filter(ImageFilter.GaussianBlur(18))).astype(float) / 255
    return np.clip((a - (1 - keep)) / keep * 1.6, 0, 1)

def wrapped(draw_fn, img):
    d = ImageDraw.Draw(img, "RGBA")
    def at(fn):
        for ox in (-N, 0, N):
            for oy in (-N, 0, N):
                fn(d, ox, oy)
    return at

def strokes(img, rng, mask, count, length, width, colors, curve=0.4, shadow=0.35):
    at = wrapped(None, img)
    for _ in range(count):
        x, y = rng.random() * N, rng.random() * N
        if rng.random() > mask[int(y) % N, int(x) % N]: continue
        L = rng.uniform(*length); w = rng.uniform(*width)
        a = rng.uniform(0, math.tau); bend = rng.uniform(-curve, curve)
        pts = []
        for k in range(6):
            t = k / 5
            ang = a + bend * t
            pts.append((x + math.cos(ang) * L * t, y + math.sin(ang) * L * t))
        c = colors[rng.randrange(len(colors))]
        c = tuple(int(max(0, min(255, v * rng.uniform(0.85, 1.15)))) for v in c)
        def blade(d, ox, oy, pts=pts, c=c, w=w):
            sh = [(px + ox + 2, py + oy + 2) for px, py in pts]
            d.line(sh, fill=(0, 0, 0, int(255 * shadow * 0.5)), width=max(1, int(w + 1)))
            d.line([(px + ox, py + oy) for px, py in pts], fill=c + (235,), width=max(1, int(w)))
        at(blade)

def fronds(img, rng, mask, count, size, colors, widthk=(0.18, 0.3)):
    at = wrapped(None, img)
    for _ in range(count):
        x, y = rng.random() * N, rng.random() * N
        if rng.random() > mask[int(y) % N, int(x) % N]: continue
        L = rng.uniform(*size); W = L * rng.uniform(*widthk); a = rng.uniform(0, math.tau)
        c = colors[rng.randrange(len(colors))]
        c = tuple(int(max(0, min(255, v * rng.uniform(0.85, 1.12)))) for v in c)
        # a blade as a polygon: leaf-shaped, with a darker midrib
        poly = []
        for k in range(12):
            t = k / 11
            off = math.sin(t * math.pi) * W * (1 if k < 12 else -1)
            poly.append((t * L, off))
        poly += [(t * L, -math.sin(t * math.pi) * W) for t in [k / 11 for k in range(11, -1, -1)]]
        ca, sa = math.cos(a), math.sin(a)
        P = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in poly]
        mid = [(x + t * L * ca, y + t * L * sa) for t in (0, 1)]
        def leaf(d, ox, oy, P=P, mid=mid, c=c):
            d.polygon([(px + ox + 3, py + oy + 3) for px, py in P], fill=(0, 0, 0, 60))
            d.polygon([(px + ox, py + oy) for px, py in P], fill=c + (240,))
            d.line([(px + ox, py + oy) for px, py in mid], fill=tuple(int(v * 0.7) for v in c) + (200,), width=2)
        at(leaf)

def whorls(img, rng, mask, count, r, colors):
    at = wrapped(None, img)
    for _ in range(count):
        x, y = rng.random() * N, rng.random() * N
        if rng.random() > mask[int(y) % N, int(x) % N]: continue
        R = rng.uniform(*r); arms = rng.randint(6, 9); rot = rng.uniform(0, math.tau)
        c = colors[rng.randrange(len(colors))]
        c = tuple(int(max(0, min(255, v * rng.uniform(0.85, 1.15)))) for v in c)
        def star(d, ox, oy, x=x, y=y, R=R, arms=arms, rot=rot, c=c):
            for k in range(arms):
                a = rot + k * math.tau / arms
                d.line([(x + ox, y + oy), (x + ox + math.cos(a) * R, y + oy + math.sin(a) * R)], fill=c + (230,), width=2)
            d.ellipse([x + ox - 2, y + oy - 2, x + ox + 2, y + oy + 2], fill=tuple(int(v * 0.8) for v in c) + (255,))
        at(star)

def save(img, name):
    img.save(os.path.join(TEX, name + ".png"))
    print("wrote", name)

rng = random.Random(7)
# Seagrass meadow: dense, thin green blades in thick clumps over sand
img = base("UnderSeabed"); m = clumps(rng, 6, 0.75)
strokes(img, rng, m, 9000, (16, 40), (2, 3.5), [(70, 130, 55), (90, 150, 60), (60, 115, 50), (110, 160, 70)])
save(img, "UnderSeabedSeagrassMeadow")
# Kelp bed: broad olive-brown fronds lying in the current, holdfasts between
img = base("UnderSeabed"); m = clumps(rng, 5, 0.8)
fronds(img, rng, m, 1300, (60, 120), [(92, 82, 38), (80, 72, 34), (108, 92, 44), (70, 66, 32)], widthk=(0.1, 0.16))
save(img, "UnderSeabedKelpBed")
# Seaweed meadow: a mix of small red, green and brown fronds and turf
img = base("UnderSeabed"); m = clumps(rng, 7, 0.7)
fronds(img, rng, m, 1400, (14, 30), [(170, 70, 70), (190, 95, 85), (80, 140, 60), (130, 110, 50), (150, 60, 90)])
strokes(img, rng, m, 3000, (6, 14), (1.5, 2.5), [(100, 150, 70), (160, 80, 80)], curve=1.0)
save(img, "UnderSeabedSeaweedMeadow")
# Waterweed meadow (lakebed): feathery green whorls of stoneworts and waterweed over mud
img = base("UnderLakebed"); m = clumps(rng, 6, 0.75)
whorls(img, rng, m, 5000, (6, 13), [(85, 135, 62), (70, 118, 55), (100, 148, 70)])
save(img, "UnderLakebedWaterweedMeadow")
