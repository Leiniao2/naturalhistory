"""
Procedural Gigantospongia discoforma (Middle Permian giant sponge) for map colonies.

One of the largest sponges known from the Permian reefs of west Texas: a huge, thin,
plate-like disc held up off the reef on a short, thick stalk, its upper surface pocked
with many small exhalant openings (oscules) set in low radiating ridges, its rim gently
wavy. Pale ochre-cream with darker pores. Rubble and mud base.
Faces -Y, pivot on the sea floor (Fixed style).

Usage:
  blender --background --python tools/blender/gigantospongia_discoforma.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gigantospongia.fbx
"""

import math
import random
import sys
from pathlib import Path

import bmesh
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402
import nh_ord_echino as oe  # noqa: E402

TOP = (0.86, 0.74, 0.50)
RIDGE = (0.94, 0.86, 0.64)
PORE = (0.32, 0.22, 0.12)
UNDER = (0.66, 0.54, 0.36)
MUD = ((0.60, 0.56, 0.48), (0.70, 0.66, 0.56))
R = 0.85
H = 0.32          # height of the disc above the floor
TH = 0.05


def disc():
    bm = bmesh.new()
    nr, na = 22, 96
    rings_top, rings_bot = [], []
    for side in (1, -1):
        rows = []
        for i in range(nr + 1):
            t = i / nr
            row = []
            for j in range(na):
                a = j / na * math.tau
                rr = R * t * (1.0 + 0.05 * math.sin(a * 5 + 0.7) * t)
                wave = 0.035 * math.sin(a * 7) * t ** 2
                dish = 0.10 * t ** 2          # slightly saucer-shaped
                z = H + dish + wave + side * TH * 0.5 * (1.0 - 0.6 * t ** 4)
                row.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
            rows.append(row)
        (rings_top if side > 0 else rings_bot).extend(rows)
    for rows, flip in ((rings_top, False), (rings_bot, True)):
        for i in range(nr):
            for j in range(na):
                k = (j + 1) % na
                q = [rows[i][j], rows[i][k], rows[i + 1][k], rows[i + 1][j]]
                if flip:
                    q.reverse()
                try:
                    bm.faces.new(q)
                except ValueError:
                    pass
    # close the rim
    for j in range(na):
        k = (j + 1) % na
        bm.faces.new([rings_top[nr][j], rings_bot[nr][j], rings_bot[nr][k], rings_top[nr][k]])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def top_col(co, n):
    if n.z < 0.2:
        return UNDER
    a = math.atan2(co.y, co.x)
    r = math.hypot(co.x, co.y)
    ridge = 0.5 + 0.5 * math.cos(a * 36)
    c = nh.lerp(TOP, RIDGE, 0.6 * nh.smoothstep(0.6, 1.0, ridge) * nh.smoothstep(0.1, 0.3, r))
    # pores: cellular dots between ridges
    pore = nh.smoothstep(0.82, 0.92, 1.0 - noise.cell(Vector((co.x, co.y, 0)) * 26.0))
    c = nh.lerp(c, PORE, 0.85 * pore * nh.smoothstep(0.4, 0.0, ridge))
    k = 0.92 + 0.12 * noise.noise(co * 18.0)
    return tuple(x * k for x in c)


def build():
    rng = random.Random(3)
    mb = nh.MeshBuilder()
    oe.mud_patch(mb, 0.95, MUD, seed=7)
    nc.rubble(mb, rng, 0.55, 0.9, count=7, size=(0.05, 0.09))
    stalk = nh.tube([(0, 0, 0.0), (0.0, 0.0, H * 0.5), (0, 0, H + 0.02)], [0.16, 0.11, 0.14], sides=14)
    mb.add(stalk, lambda co, n: tuple(x * (0.9 + 0.15 * noise.noise(co * 20)) for x in UNDER))
    mb.add(disc(), top_col)
    return oe._finish(mb, "Gigantospongia", roughness=0.85)


if __name__ == "__main__":
    nh.run(build, "Gigantospongia", ground=(0.62, 0.58, 0.48), views=((30, 25), (10, 70), (-100, 12)))
