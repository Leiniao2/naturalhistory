"""
Recolours the backdrops of the species portraits (Assets/Resources/Portraits/<id>.jpg) so they
are told apart at a glance, without painting them again:

  - The three founding protists and the protists of their lines each get the line's colour:
    Amorphea (Thecamonas) red, Diaphoretickes (Telonema) green, Excavata (Malawimonas) blue.
    These cells are mostly translucent, so they turn with the water; colours of their own stay.
  - Every other water-only species whose backdrop is the usual teal water gets one of several
    water colours (cobalt, indigo, violet dusk, emerald, or kept teal), chosen per species.
    Only the teal band moves, more towards the edges than the centre, so the animal keeps its colours.
  - Portraits with another backdrop (land, blood, gut) are left as they are.

Run with Blender's Python (it has numpy and reads/writes JPEG):
    blender --background --python tools/portraits/recolor.py -- [--only id,id] [--preview sheet.png] [--dry]
Works from the originals in tools/portraits/raw when present (so running it again doesn't
compound), else from the current portraits. The colours live in palette.py; make_prompts.py asks new paintings for the same ones.
"""

import json
import math
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import LINES, aquatic, line_of, water_for  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
PORTRAITS = os.path.join(ROOT, "Assets", "Resources", "Portraits")
RAW = os.path.join(HERE, "raw")
SPECIES = os.path.join(ROOT, "Assets", "Resources", "Data", "species.json")
EVOLUTION = os.path.join(ROOT, "Assets", "Resources", "Data", "evolution.json")
SIZE = 512

TEAL = (150.0, 215.0)  # backdrop hues counted as the usual teal water


def load_species():
    data = json.load(open(SPECIES, encoding="utf-8"))
    species = data["species"] if isinstance(data, dict) else data
    return {s["id"]: s for s in species}


def load_links():
    data = json.load(open(EVOLUTION, encoding="utf-8"))
    return data["links"] if isinstance(data, dict) else data


# ---------- image IO (Blender) ----------

def read(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px


def resize(px, size):
    h, w = px.shape[:2]
    if h == size and w == size:
        return px
    # area-average down (originals are larger and square)
    ys = (np.arange(size + 1) * h / size).astype(int)
    xs = (np.arange(size + 1) * w / size).astype(int)
    out = np.zeros((size, size, 4), np.float32)
    cs = px.cumsum(0).cumsum(1)
    cs = np.pad(cs, ((1, 0), (1, 0), (0, 0)))
    for i in range(size):
        y0, y1 = ys[i], max(ys[i + 1], ys[i] + 1)
        row = cs[y1] - cs[y0]
        x0, x1 = xs[:-1], np.maximum(xs[1:], xs[:-1] + 1)
        out[i] = (row[x1] - row[x0]) / ((y1 - y0) * (x1 - x0))[:, None]
    return out


def write(path, px):
    h, w = px.shape[:2]
    img = bpy.data.images.new("out", w, h, alpha=False)
    img.pixels[:] = np.clip(px, 0, 1).ravel()
    img.filepath_raw = path
    img.file_format = "JPEG"
    img.save(quality=92)  # not save_render: that would apply the scene's view transform
    bpy.data.images.remove(img)


# ---------- colour ----------

def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return np.stack([h * 60.0, s, mx], -1)


def hsv_to_rgb(hsv):
    h, s, v = hsv[..., 0] % 360 / 60.0, hsv[..., 1], hsv[..., 2]
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    choices = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    out = np.zeros(h.shape + (3,), np.float32)
    for k, (a, b, c) in enumerate(choices):
        m = i == k
        out[m] = np.stack([a[m], b[m], c[m]], -1)
    return out


def circ_mean(hues, weights):
    a = np.radians(hues)
    return math.degrees(math.atan2((np.sin(a) * weights).sum(), (np.cos(a) * weights).sum())) % 360


def backdrop_hue(hsv):
    """Mean hue of the picture's border, weighted by saturation"""
    b = 48
    ring = np.concatenate([hsv[:b].reshape(-1, 3), hsv[-b:].reshape(-1, 3), hsv[:, :b].reshape(-1, 3), hsv[:, -b:].reshape(-1, 3)])
    return circ_mean(ring[:, 0], ring[:, 1] * ring[:, 2])


def hue_delta(a, b):
    return (b - a + 180) % 360 - 180


def recolor_line(rgb, hsv, target):
    """The backdrop's hues turned to `target`, the centre nearly as much (translucent protists
    take the water's colour; a cell with a colour of its own, a yellow slime mould, keeps it)"""
    sat = 0.92 if abs(hue_delta(target, 350)) < 30 else 1.0  # red reads as warm water, not blood
    return recolor_water(rgb, hsv, ("line", target, sat, 1.0), centre=0.8)


def recolor_water(rgb, hsv, water, centre=0.35):
    target, sat, val = water[1], water[2], water[3]
    src = backdrop_hue(hsv)
    shift = hue_delta(src, target)
    h, w = hsv.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / math.sqrt(2)
    radial = np.clip((r - 0.12) / 0.45, 0, 1) ** 0.8          # centre (the animal) moves less
    dist = np.abs(hue_delta(hsv[..., 0], src))
    band = np.clip(1 - (dist - 22) / 30, 0, 1)                # the backdrop's hues, softly
    band *= np.clip(hsv[..., 1] / 0.18, 0, 1)                 # not greys and whites
    k = band * (centre + (1 - centre) * radial)
    out = hsv.copy()
    out[..., 0] += shift * k
    out[..., 1] *= 1 + (sat - 1) * k
    out[..., 2] *= 1 + (val - 1) * k
    return hsv_to_rgb(out)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    preview = argv[argv.index("--preview") + 1] if "--preview" in argv else None
    dry = "--dry" in argv

    species = load_species()
    lines = line_of(species, load_links())
    report, sheet = [], []
    for name in sorted(os.listdir(PORTRAITS)):
        if not name.endswith(".jpg"):
            continue
        sid = name[:-4]
        if only and sid not in only:
            continue
        raw = next((os.path.join(RAW, sid + e) for e in (".jpg", ".jpeg", ".png", ".webp") if os.path.exists(os.path.join(RAW, sid + e))), None)
        px = resize(read(raw or os.path.join(PORTRAITS, name)), SIZE)
        rgb = px[..., :3]
        hsv = rgb_to_hsv(rgb)
        src = backdrop_hue(hsv)
        teal = TEAL[0] <= src <= TEAL[1]
        if sid in lines and teal:
            out, how = recolor_line(rgb, hsv, LINES[lines[sid]][0]), "line:" + lines[sid].split("_")[0]
        elif teal and aquatic(species.get(sid, {})):
            water = water_for(sid)
            if water[1] is None:
                report.append((sid, round(src), "teal kept"))
                continue
            out, how = recolor_water(rgb, hsv, water), "water:" + water[0]
        else:
            report.append((sid, round(src), "left"))
            continue
        report.append((sid, round(src), how))
        if preview and len(sheet) < 36:
            sheet.append((rgb, out))
        if not dry:
            write(os.path.join(PORTRAITS, name), np.concatenate([out, np.ones(out.shape[:2] + (1,), np.float32)], -1))

    counts = {}
    for _, _, how in report:
        counts[how.split(":")[0] if ":" in how else how] = counts.get(how.split(":")[0] if ":" in how else how, 0) + 1
    print("RECOLOR", json.dumps(counts))
    for r in report:
        if r[2].startswith("line"):
            print("RECOLOR", *r)
    if preview and sheet:
        t = 128
        cols = 6
        rows = math.ceil(len(sheet) / cols)
        img = np.zeros((rows * t, cols * 2 * t, 4), np.float32)
        img[..., 3] = 1
        for i, (a, b) in enumerate(sheet):
            y, x = (i // cols) * t, (i % cols) * 2 * t
            img[y:y + t, x:x + t, :3] = resize(np.concatenate([a, a[..., :1]], -1), t)[..., :3]
            img[y:y + t, x + t:x + 2 * t, :3] = resize(np.concatenate([b, b[..., :1]], -1), t)[..., :3]
        write_png(preview, img)


def write_png(path, px):
    h, w = px.shape[:2]
    img = bpy.data.images.new("sheet", w, h, alpha=False)
    img.pixels[:] = px.ravel()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


main()
