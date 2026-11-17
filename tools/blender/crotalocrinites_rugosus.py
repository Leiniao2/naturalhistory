"""
Procedural Crotalocrinites rugosus (mid-Silurian, Wenlock crinoid from Gotland, Sweden,
and the Wenlock Limestone of England) for map colonies (Fixed style).

A sea lily: a branching root holdfast on the sea floor, a stout stem of stacked
columnals, a small cup (calyx) and the genus' hallmark - arms that branch again and
again and are joined side by side into five broad, net-like, ruffled fans which spread
into a wide funnel (when closed they fold together like a rattle; Crotalocrinites means
"rattle crinoid"). Pale purplish-grey to buff. Faces -Y, pivot on the sea floor.

Usage:
  blender --background --python tools/blender/crotalocrinites_rugosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CrotalocrinitesRugosus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

NAME = "CrotalocrinitesRugosus"
STEM = (0.62, 0.55, 0.52)
STEM_DARK = (0.40, 0.34, 0.33)
CUP = (0.56, 0.46, 0.46)
FAN = (0.74, 0.62, 0.58)
FAN_DARK = (0.42, 0.32, 0.34)
EDGE = (0.86, 0.78, 0.68)

STEM_H = 0.95
CUP_Z = STEM_H + 0.06


def stem(mb):
    pts = [Vector((0.03 * math.sin(t * 2.3), 0.02 * math.sin(t * 1.7), STEM_H * t)) for t in [i / 10 for i in range(11)]]
    mb.add(nh.tube(pts, [0.035] * 11, sides=10),
           lambda co, n: STEM_DARK if math.cos(co.z * 160.0) > 0.6 else STEM)
    # root holdfast
    for k in range(6):
        a = k / 6 * math.tau + 0.3
        d = Vector((math.cos(a), math.sin(a), 0))
        mb.add(nh.tube([Vector((0, 0, 0.06)), d * 0.10 + Vector((0, 0, 0.015)), d * 0.20 + Vector((0, 0, 0.0))],
                       [0.03, 0.02, 0.0], sides=6), STEM_DARK)


def fan(mb, a0, a1):
    """One ruffled arm fan: a sheet from the cup rim spreading up and out over azimuths a0..a1,
    painted with a net of branching arm ridges."""
    bm = bmesh.new()
    nu, nv = 12, 8
    grid = []
    for i in range(nv + 1):
        v = i / nv
        row = []
        for j in range(nu + 1):
            u = j / nu
            a = a0 + (a1 - a0) * u
            r = 0.10 + 0.55 * v
            z = CUP_Z + 0.05 + 0.55 * v - 0.12 * v * v
            # ruffles: waves across the fan, growing outward
            wv = 0.05 * v * math.sin(u * math.pi * 6)
            row.append(bm.verts.new((math.cos(a) * (r + wv), math.sin(a) * (r + wv), z + wv * 0.6)))
        grid.append(row)
    for i in range(nv):
        for j in range(nu):
            bm.faces.new([grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]])
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, n):
        r = math.hypot(co.x, co.y)
        a = math.atan2(co.y, co.x)
        k = 0.5 + 0.5 * math.cos(a * 70.0 + r * 4.0)
        m = 0.5 + 0.5 * math.cos(r * 70.0)
        c = nh.lerp(FAN, FAN_DARK, 0.6 * nh.smoothstep(0.6, 0.9, max(k, m * 0.9)))
        c = nh.lerp(c, EDGE, nh.smoothstep(0.55, 0.66, r))
        return nh.lerp(c, FAN_DARK, 0.15 * (0.5 + 0.5 * noise.noise(co * 10.0)))
    mb.add(bm, col)


def build():
    mb = nh.MeshBuilder()
    stem(mb)
    mb.add(nh.uv_ellipsoid((0, 0, CUP_Z), (0.10, 0.10, 0.08), 14, 8,
                           deform=lambda n: 0.8 if n.z < 0 else 1.0),
           lambda co, n: CUP if math.cos(math.atan2(co.y, co.x) * 5) < 0.8 else STEM_DARK)
    for k in range(5):
        a = k / 5 * math.tau
        fan(mb, a - 0.58, a + 0.58)
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.30, 0.30, 0.27), background=(0.05, 0.14, 0.18), views=((30, 25), (0, 70), (-90, 5)))
