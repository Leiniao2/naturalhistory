"""
Imports the seabed cover textures (generated with Google Flow from the base Under* textures) into
Assets/Textures/Terrain as 512 x 512 PNGs that tile seamlessly.

The covers are the under layer's simple water plants painted into the floor instead of being
built as 3D props (HexGrid.Under / UnderMeshes): bacterial mats on the deep seabed, microbial mats,
coralline crusts and algal turf on the seabed and lakebed.

Generated images don't always wrap cleanly, so each is checked: if the jump across its edges is
clearly bigger than between neighbouring pixels inside it, it is cross-faded with a copy of itself
shifted by half a tile (whose edges come from the image's middle, so they wrap).

Run with Blender (it reads WebP):
  blender --background --python tools/terrain/seabed_covers.py -- <folder with the downloaded images>
"""

import os
import sys

import bpy
import numpy as np

NAMES = [
    "UnderDeepSeabedBacterialMat",
    "UnderSeabedMicrobialMat",
    "UnderSeabedCoralline",
    "UnderSeabedAlgalTurf",
    "UnderLakebedMicrobialMat",
    "UnderLakebedAlgalTurf",
]
N = 512
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Assets", "Textures", "Terrain")


def load(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
    bpy.data.images.remove(img)
    if (w, h) != (N, N):
        ys = (np.arange(N) * h / N).astype(int)
        xs = (np.arange(N) * w / N).astype(int)
        px = px[ys][:, xs]
    return px


def seam_ratio(px):
    """Mean colour jump across the wrap edges relative to the mean jump between neighbouring pixels."""
    inner = np.abs(np.diff(px, axis=1)).mean() + np.abs(np.diff(px, axis=0)).mean()
    edge = np.abs(px[:, 0] - px[:, -1]).mean() + np.abs(px[0] - px[-1]).mean()
    return edge / max(inner, 1e-6)


def make_seamless(px):
    shifted = np.roll(np.roll(px, N // 2, axis=0), N // 2, axis=1)
    t = np.linspace(0, 1, N)
    edge = np.minimum(t, 1 - t) * 2               # 0 at the edges, 1 in the middle
    w1 = np.clip(edge / 0.35, 0, 1)
    w1 = w1 * w1 * (3 - 2 * w1)
    w = np.minimum.outer(w1, w1)[..., None]       # the original away from the edges, the shifted copy at them
    return px * w + shifted * (1 - w)


def save(name, px):
    img = bpy.data.images.new(name, N, N, alpha=False)
    rgba = np.concatenate([np.clip(px, 0, 1), np.ones((N, N, 1), np.float32)], axis=2)
    img.pixels[:] = rgba.ravel()
    img.filepath_raw = os.path.abspath(os.path.join(OUT, name + ".png"))
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def main():
    src = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.expanduser("~/Downloads")
    for name in NAMES:
        path = next((os.path.join(src, name + ext) for ext in (".png", ".webp", ".jpg") if os.path.exists(os.path.join(src, name + ext))), None)
        if path is None:
            print("missing", name)
            continue
        px = load(path)
        before = seam_ratio(px)
        if before > 1.6:
            px = make_seamless(px)
        print(f"{name}: seam {before:.2f} -> {seam_ratio(px):.2f}")
        save(name, px)


main()
