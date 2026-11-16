"""
Paints the under layer's mat, turf and meadow floors as clumps on the plain floor
(UnderSeabedMicrobialMat, UnderLakebedMicrobialMat, UnderDeepSeabedBacterialMat, UnderSeabedAlgalTurf,
UnderLakebedAlgalTurf, UnderSeabedSeagrassMeadow, UnderSeabedKelpBed, UnderSeabedSeaweedMeadow,
UnderLakebedWaterweedMeadow -> ...Patches.png in Assets/Textures/Terrain): the bed's own floor texture at its own scale, with
patches of mat or turf here and there, see-through enough that the floor's ripples show under
them, a slightly darker lumpy rim round each, and bare floor between. The mat and turf look comes
from the full-cover textures (left as they are, the sources), repeated small inside the patches;
for meadows only their plants are taken (by colour: the bare floor showing between their blades
is left out), a little muted so the beds don't look busy.
Wraps seamlessly. 1024 x 1024, used at the plain floor's tiling (Materials/Under/*.mat).

Run with Blender (for numpy and PNG I/O):
  blender --background --python tools/terrain/mat_patches.py
"""

import os

import bpy
import numpy as np

N = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "Assets", "Textures", "Terrain")


def load(name):
    img = bpy.data.images.load(os.path.join(TEX, name + ".png"))
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
    bpy.data.images.remove(img)
    return px


def fit(px, repeats):
    """The texture repeated `repeats` times across an N x N image (nearest-neighbour box)."""
    h, w = px.shape[:2]
    t = (np.arange(N) * repeats * w / N).astype(int) % w
    s = (np.arange(N) * repeats * h / N).astype(int) % h
    return px[s][:, t]


def save(name, px):
    img = bpy.data.images.new(name, N, N, alpha=False)
    rgba = np.concatenate([np.clip(px, 0, 1), np.ones((N, N, 1), np.float32)], axis=2)
    img.pixels[:] = rgba.ravel()
    img.filepath_raw = os.path.join(TEX, name + ".png")
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def wrapped_noise(rng, cells):
    g = rng.random((cells, cells)).astype(np.float32)
    t = np.arange(N) * cells / N
    i = t.astype(int)
    f = t - i
    f = f * f * (3 - 2 * f)
    i1 = (i + 1) % cells
    rows = g[i][:, i] * (1 - f)[None, :] + g[i][:, i1] * f[None, :]
    rows1 = g[i1][:, i] * (1 - f)[None, :] + g[i1][:, i1] * f[None, :]
    return rows * (1 - f)[:, None] + rows1 * f[:, None]


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def clumps(rng, share, count, size, fuzz):
    """0..1 cover: round clumps, each a few blobs melted together (a metaball field), with lumpy
    outlines and bare floor between; scaled so about `share` of the image is covered."""
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    field = np.zeros((N, N), np.float32)
    lumps = wrapped_noise(rng, 24) * 0.6 + wrapped_noise(rng, 64) * 0.4 * (1 + fuzz) - 0.5
    for _ in range(count):
        c = rng.uniform(0, N, 2)
        for _ in range(rng.integers(2, 7)):
            r = float(np.exp(rng.uniform(np.log(size * 0.35), np.log(size))))
            cx, cy = (c + rng.normal(0, size * 0.7, 2)) % N
            dx = (xx - cx + N / 2) % N - N / 2      # round the tile, so it wraps
            dy = (yy - cy + N / 2) % N - N / 2
            field += np.exp(-(dx * dx + dy * dy) / (r * r))
    field *= 1 + 0.35 * lumps
    cut = np.quantile(field, 1 - share)
    return field, cut


def plants_only(cover, mute):
    """(cover, 0..1 mask of where it has plants rather than bare floor): by saturation"""
    mx, mn = cover.max(axis=2), cover.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    mask = smooth(0.15, 0.32, sat)
    grey = (cover @ np.array([0.3, 0.59, 0.11], np.float32))[..., None]
    return cover * (1 - mute) + grey * mute, mask


def paint(floor, cover, seed, share, count, size, opacity, rim, fuzz, mask=None):
    rng = np.random.default_rng(seed)
    n, cut = clumps(rng, share, count, size, fuzz)
    edge = cut * (0.06 + 0.16 * fuzz)
    if fuzz >= 1: edge = cut * 0.5                        # turf: no outline at all, it thins out into the floor
    a = smooth(cut - edge, cut + edge, n)                 # 0 bare floor, 1 inside a clump
    core = smooth(cut, cut * 2.2, n)                      # thicker toward the middle
    alpha = a * (0.5 + 0.5 * core) * opacity
    if fuzz >= 1:
        # tufts: broken up by fine noise, so a clump is a scatter of tiny tufts rather than a disc
        tufts = smooth(0.35, 0.7, wrapped_noise(rng, 170) * 0.7 + wrapped_noise(rng, 340) * 0.3)
        alpha = alpha * (0.25 + 0.75 * tufts)
    if mask is not None: alpha = alpha * mask
    alpha = alpha[..., None]
    ring = a * (1 - smooth(cut + edge, cut + 4 * edge, n))
    if mask is not None: ring = ring * mask           # no outline round a meadow, only its plants
    ring = ring[..., None]
    # the floor's ripples show through: the cover takes the floor's light and dark
    lum = floor @ np.array([0.3, 0.59, 0.11], np.float32)
    shade = (lum / max(float(lum.mean()), 1e-4))[..., None]
    mat = cover * (0.7 + 0.3 * shade) * 1.08
    out = floor * (1 - alpha) + mat * alpha
    return (out * (1 - rim * ring)).astype(np.float32)


# name: (floor, cover repeats inside the image, share of floor covered, clumps, clump size (px),
#        opacity, rim darkening, outline fuzz)
COVERS = {
    "UnderSeabedMicrobialMat":     ("UnderSeabed",     8, 0.4,  26, 48, 0.72, 0.16, 0.3),
    "UnderLakebedMicrobialMat":    ("UnderLakebed",    8, 0.4,  26, 48, 0.72, 0.16, 0.3),
    "UnderDeepSeabedBacterialMat": ("UnderDeepSeabed", 8, 0.33, 24, 44, 0.7,  0.12, 0.3),
    "UnderSeabedAlgalTurf":        ("UnderSeabed",    12, 0.3, 110, 13, 0.6,  0.03, 1.0),
    "UnderLakebedAlgalTurf":       ("UnderLakebed",   12, 0.3, 110, 13, 0.6,  0.03, 1.0),
}

# meadows: (floor, cover repeats, share, clumps, clump size, opacity, rim, fuzz, mute)
MEADOWS = {
    "UnderSeabedSeagrassMeadow":   ("UnderSeabed",  2, 0.5,  22, 60, 0.95, 0.12, 0.6, 0.15),
    "UnderSeabedKelpBed":          ("UnderSeabed",  3, 0.55, 20, 64, 0.9, 0.14, 0.4, 0.15),
    "UnderSeabedSeaweedMeadow":    ("UnderSeabed",  2, 0.48, 26, 50, 0.95, 0.12, 0.8, 0.2),
    "UnderLakebedWaterweedMeadow": ("UnderLakebed", 3, 0.5,  22, 60, 0.85, 0.1, 0.6, 0.2),
}

for i, (name, (floor, cr, share, count, size, opacity, rim, fuzz)) in enumerate(COVERS.items()):
    out = paint(fit(load(floor), 1), fit(load(name), cr), 31 + 17 * i, share, count, size, opacity, rim, fuzz)
    save(name + "Patches", out)
    print("wrote", name + "Patches")

for i, (name, (floor, cr, share, count, size, opacity, rim, fuzz, mute)) in enumerate(MEADOWS.items()):
    cover, mask = plants_only(fit(load(name), cr), mute)
    out = paint(fit(load(floor), 1), cover, 131 + 17 * i, share, count, size, opacity, rim, fuzz, mask)
    save(name + "Patches", out)
    print("wrote", name + "Patches")
