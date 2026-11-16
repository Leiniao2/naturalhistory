"""
Paints the stromatolite floor covers for the under layer (UnderSeabedStromatolite, ...2 and ...3,
and the same for UnderLakebed, in Assets/Textures/Terrain): fields of microbial mounds seen from
above over the plain seabed / lakebed texture, in clumps with floor showing between them, of
every size from small knobs to broad heads. Three kinds, one per variant (HexGrid.Under picks a
variant per tile, so neighbouring tiles differ): round domes like cabbage heads; heads drawn
out along the current, like Shark Bay's; and clusters of slender columns among a few big domes.
In the colour of the 3D stromatolites standing on them (MapFeatureMeshes.Stromatolite), lit from
the north-west in a few flat steps like their facets, with dark crevices around each mound. Wraps seamlessly (distances are
measured round the tile). 512 x 512.

Run with Blender (for numpy and PNG I/O):
  blender --background --python tools/terrain/stromatolite_cover.py
"""

import os

import bpy
import numpy as np

N = 512
HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "Assets", "Textures", "Terrain")


def load(name):
    img = bpy.data.images.load(os.path.join(TEX, name + ".png"))
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
    bpy.data.images.remove(img)
    if (w, h) != (N, N):
        ys = (np.arange(N) * h / N).astype(int)
        xs = (np.arange(N) * w / N).astype(int)
        px = px[ys][:, xs]
    return px


def save(name, px):
    img = bpy.data.images.new(name, N, N, alpha=False)
    rgba = np.concatenate([np.clip(px, 0, 1), np.ones((N, N, 1), np.float32)], axis=2)
    img.pixels[:] = rgba.ravel()
    img.filepath_raw = os.path.join(TEX, name + ".png")
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def wrapped_noise(rng, cells):
    """Smooth value noise that tiles: random grid upsampled with periodic cubic interpolation."""
    g = rng.random((cells, cells)).astype(np.float32)
    t = np.arange(N) * cells / N
    i = t.astype(int)
    f = t - i
    f = f * f * (3 - 2 * f)
    i1 = (i + 1) % cells
    rows = g[i][:, i] * (1 - f)[None, :] + g[i][:, i1] * f[None, :]
    rows1 = g[i1][:, i] * (1 - f)[None, :] + g[i1][:, i1] * f[None, :]
    return rows * (1 - f)[:, None] + rows1 * f[:, None]


def mound(xx, yy, cx, cy, r, aspect, angle, flat, wobble):
    """Height of one mound (0 outside): a dome, stretched by `aspect` along `angle`; `flat` 0..1
    flattens its top into a table."""
    dx = (xx - cx + N / 2) % N - N / 2          # round the tile, so it wraps
    dy = (yy - cy + N / 2) % N - N / 2
    ca, sa = np.cos(angle), np.sin(angle)
    u = (dx * ca + dy * sa) / aspect
    v = -dx * sa + dy * ca
    d = np.sqrt(u * u + v * v) * (1 + 0.14 * wobble)
    h = np.sqrt(np.clip(1 - (d / r) ** 2, 0, 1))
    h = np.minimum(h * (1 + 1.5 * flat), 1)
    return h * r * 0.55, d / r


def paint(base, palette, seed, count, style):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    height = np.zeros((N, N), np.float32)
    ring = np.zeros((N, N), np.float32)        # 0 at a mound's centre, 1 at its rim
    tone = np.zeros((N, N), np.float32)
    inside = np.zeros((N, N), bool)
    wobble = wrapped_noise(rng, 16) * 2 - 1
    current = rng.uniform(0, np.pi)            # the way the water runs over this field

    # mounds gather in clumps, with bare floor between: each grows near a clump's centre
    clumps = rng.uniform(0, N, (max(count // 14, 6), 2))
    def where():
        c = clumps[rng.integers(len(clumps))]
        return (c + rng.normal(0, N * 0.09, 2)) % N

    # every size, small knobs far outnumbering broad heads (log-uniform radius)
    big, small = dict(dome=(34, 4), ridge=(30, 4), column=(30, 3))[style]
    mounds = []
    for _ in range(count):
        r = float(np.exp(rng.uniform(np.log(small), np.log(big))))
        cx, cy = where()
        if style == "ridge" and r > 7:
            mounds.append((r, cx, cy, rng.uniform(1.5, 2.6), current + rng.normal(0, 0.25), rng.uniform(0, 0.3)))
        elif style == "column" and r < 14:
            # a tight bundle of slender columns: small, flat-topped knobs close together
            for _ in range(rng.integers(3, 8)):
                o = rng.normal(0, r * 0.9, 2)
                mounds.append((rng.uniform(2.5, 5.5), cx + o[0], cy + o[1], 1.0, 0.0, rng.uniform(0.5, 1)))
        else:
            mounds.append((r, cx, cy, rng.uniform(1, 1.35), rng.uniform(0, np.pi), rng.uniform(0, 0.5) ** 2))
    # big mounds first, then smaller ones filling the gaps between them
    for r, cx, cy, aspect, angle, flat in sorted(mounds, key=lambda m: -m[0]):
        h, rr = mound(xx, yy, cx, cy, r, aspect, angle, flat, wobble)
        top = h > height
        height = np.where(top, h, height)
        ring = np.where(top, rr, ring)
        tone = np.where(top, rng.uniform(-1, 1), tone)
        inside |= h > 0

    grain = wrapped_noise(rng, 64) * 2 - 1
    # light from the north-west, stepped into a few flat levels like the 3D domes' facets
    gy, gx = np.gradient(height)
    shade = np.clip(1 + (-gx - gy) * 0.16, 0.55, 1.3)
    shade = np.round(shade * 6) / 6
    stone = palette["stone"][None, None, :] * (1 + 0.1 * tone[..., None]) * shade[..., None]
    stone *= 0.97 + 0.04 * grain[..., None]
    # crevices: the seabed between the mounds, darker the lower
    edge = np.clip(height / 9.0, 0, 1)[..., None] ** 0.7
    # the floor between them: the base texture's light and dark, in the stromatolites' own stone
    # colour (not its greenish tint)
    lum = (base @ np.array([0.3, 0.59, 0.11], np.float32))[..., None]
    floor = palette["stone"][None, None, :] * (lum / max(float(lum.mean()), 1e-4)) * palette["floor_dark"]
    out = np.where(inside[..., None], stone * (0.7 + 0.3 * edge) + floor * (1 - edge) * 0.3, floor)
    return out.astype(np.float32)


STYLES = [("", "dome", 0), ("2", "ridge", 1), ("3", "column", 2)]
COVERS = {
    "UnderSeabedStromatolite": dict(base="UnderSeabed", seed=11, count=300, palette=dict(
        stone=np.array([0.55, 0.50, 0.42], np.float32),  # MapFeatureMeshes.Stromatolite
        floor_dark=0.62)),
    "UnderLakebedStromatolite": dict(base="UnderLakebed", seed=23, count=270, palette=dict(
        stone=np.array([0.55, 0.50, 0.42], np.float32),
        floor_dark=0.6)),
}

for name, c in COVERS.items():
    base = load(c["base"])
    for suffix, style, k in STYLES:
        save(name + suffix, paint(base, c["palette"], c["seed"] + 101 * k, c["count"], style))
        print("wrote", name + suffix)
