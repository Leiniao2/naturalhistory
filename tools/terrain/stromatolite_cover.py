"""
Paints the stromatolite floor covers for the under layer (UnderSeabedStromatolite and
UnderLakebedStromatolite in Assets/Textures/Terrain): a field of domed, layered microbial mounds
seen from above, crowded together like cabbage heads, over the plain seabed / lakebed texture.
Each mound shows its growth laminae as rings, is lit from the north-west and has dark crevices
around it; tops carry a thin green-brown film of living mat. Wraps seamlessly (distances are
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


def paint(base, palette, seed, count):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    height = np.zeros((N, N), np.float32)
    ring = np.zeros((N, N), np.float32)        # 0 at a mound's centre, 1 at its rim
    tone = np.zeros((N, N), np.float32)
    inside = np.zeros((N, N), bool)
    wobble = wrapped_noise(rng, 16) * 2 - 1

    # big mounds first, then smaller ones filling the gaps between them
    radii = np.sort(rng.uniform(14, 52, count))[::-1]
    for r in radii:
        cx, cy = rng.uniform(0, N, 2)
        dx = (xx - cx + N / 2) % N - N / 2      # round the tile, so it wraps
        dy = (yy - cy + N / 2) % N - N / 2
        d = np.sqrt(dx * dx + dy * dy) * (1 + 0.12 * wobble)
        h = np.sqrt(np.clip(1 - (d / r) ** 2, 0, 1)) * r * 0.55
        top = h > height
        height = np.where(top, h, height)
        ring = np.where(top, d / r, ring)
        tone = np.where(top, rng.uniform(-1, 1), tone)
        inside |= h > 0

    grain = wrapped_noise(rng, 64) * 2 - 1
    # light from the north-west, from the height map's slope
    gy, gx = np.gradient(height)
    shade = np.clip(1 + (-gx - gy) * 0.16, 0.45, 1.4)
    # growth laminae: rings that waver a little
    fine = wrapped_noise(rng, 128) * 2 - 1
    lam = 0.5 + 0.5 * np.sin((ring * 4.5 + grain * 0.8 + fine * 0.25) * np.pi * 2)
    lam *= np.clip(ring * 1.4, 0, 1)                                   # laminae show on the flanks, not the crown
    stone = palette["stone"][None, None, :] * (1 + 0.1 * tone[..., None]) * (0.95 + 0.12 * lam[..., None] + 0.08 * fine[..., None])
    film = np.clip(1 - ring * 1.3, 0, 1)[..., None] * 0.6            # living mat on the tops
    stone = stone * (1 - film) + palette["film"][None, None, :] * film
    stone *= shade[..., None] * (0.94 + 0.08 * grain[..., None])
    # crevices: darker the lower the floor between the mounds
    edge = np.clip(height / 9.0, 0, 1)[..., None] ** 0.7
    floor = base * palette["floor_dark"]
    out = np.where(inside[..., None], stone * (0.55 + 0.45 * edge) + floor * (1 - edge) * 0.45, floor)
    return out.astype(np.float32)


COVERS = {
    "UnderSeabedStromatolite": dict(base="UnderSeabed", seed=11, count=95, palette=dict(
        stone=np.array([0.58, 0.53, 0.44], np.float32),
        film=np.array([0.38, 0.42, 0.28], np.float32),
        floor_dark=0.62)),
    "UnderLakebedStromatolite": dict(base="UnderLakebed", seed=23, count=85, palette=dict(
        stone=np.array([0.55, 0.52, 0.45], np.float32),
        film=np.array([0.33, 0.41, 0.27], np.float32),
        floor_dark=0.6)),
}

for name, c in COVERS.items():
    save(name, paint(load(c["base"]), c["palette"], c["seed"], c["count"]))
    print("wrote", name)
