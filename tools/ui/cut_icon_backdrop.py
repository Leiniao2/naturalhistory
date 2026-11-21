"""
Makes the black surround of a painted round icon transparent, like the other icons in
Assets/Resources/UI/Icons (which come with an alpha channel). The black is flooded in from the
image's edges, so dark parts inside the medallion stay; its anti-aliased rim keeps its colour
with partial alpha.

Run with Blender's Python (it has numpy and reads/writes PNG):
    blender --background --python tools/ui/cut_icon_backdrop.py -- <in.png> <out.png> [<in> <out> ...]
Originals are kept in tools/ui/raw_icons.
"""

import sys
from collections import deque

import bpy
import numpy as np

DARK = 0.10   # brighter than this (max of r, g, b) is not background
SOFT = 0.16   # alpha ramps up over this much brightness above the background's


def read(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px


def write(path, px):
    h, w = px.shape[:2]
    img = bpy.data.images.new("out", w, h, alpha=True)
    img.alpha_mode = "STRAIGHT"
    img.pixels[:] = np.clip(px, 0, 1).ravel()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def cut(px):
    h, w = px.shape[:2]
    v = px[..., :3].max(-1)
    dark = v < DARK
    bg = np.zeros((h, w), bool)
    queue = deque()
    for y in range(h):
        for x in (0, w - 1):
            if dark[y, x] and not bg[y, x]:
                bg[y, x] = True
                queue.append((y, x))
    for x in range(w):
        for y in (0, h - 1):
            if dark[y, x] and not bg[y, x]:
                bg[y, x] = True
                queue.append((y, x))
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and dark[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True
                queue.append((ny, nx))

    # the rim: pixels next to the background fade in with their brightness
    edge = np.zeros((h, w), bool)
    edge[1:] |= bg[:-1]
    edge[:-1] |= bg[1:]
    edge[:, 1:] |= bg[:, :-1]
    edge[:, :-1] |= bg[:, 1:]
    edge &= ~bg
    out = px.copy()
    alpha = np.ones((h, w), np.float32)
    alpha[bg] = 0.0
    ramp = np.clip((v - DARK * 0.3) / SOFT, 0, 1)
    alpha[edge] = np.maximum(ramp[edge], 0.0)
    # un-mix the black from the rim's colour
    k = np.where(alpha > 0.02, 1.0 / np.maximum(alpha, 0.02), 1.0)
    out[..., :3] = np.where((edge & (alpha > 0.02))[..., None], np.clip(px[..., :3] * k[..., None], 0, 1), px[..., :3])
    out[..., :3][bg] = 0.0
    out[..., 3] = alpha
    return out


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for src, dst in zip(argv[0::2], argv[1::2]):
        px = cut(read(src))
        write(dst, px)
        print("CUT", dst, f"{(px[..., 3] == 0).mean():.0%} transparent")


main()
