"""
Procedural Poleumita discors (mid-Silurian euomphalid sea snail from the Wenlock reefs
of Dudley, England, and Gotland, Sweden, a few centimetres across) for map colonies
(Ground style).

A thick, low, almost disc-shaped shell: a nearly flat spire of three and a half angular
whorls, each with a strong keel round its shoulder studded with blunt nodes, fine spiral
cords and growth lines, a wide open umbilicus underneath, and a large angular aperture.
The animal creeps out of it on a broad foot with two head tentacles. Cream shell with
red-brown spiral bands; grey-orange foot. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/poleumita_discors.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PoleumitaDiscors.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

NAME = "PoleumitaDiscors"
SHELL = (0.86, 0.78, 0.62)
CORD = (0.64, 0.52, 0.38)
BAND = (0.58, 0.28, 0.16)
NODE = (0.94, 0.88, 0.74)
FOOT = (0.66, 0.54, 0.46)
FOOT_DARK = (0.46, 0.36, 0.30)

TURNS, W, SPIRE, SECTION, SIDES, STEPS = 3.5, 2.3, 0.12, 0.52, 16, 30
KEEL_A = 0.95          # angle of the shoulder keel on the whorl section (0 = outward, pi/2 = up)


def section_r(a):
    keel = 0.30 * math.exp(-((math.atan2(math.sin(a - KEEL_A), math.cos(a - KEEL_A))) / 0.28) ** 2)
    base = 0.12 * math.exp(-((math.atan2(math.sin(a + 0.7), math.cos(a + 0.7))) / 0.35) ** 2)   # basal angulation
    flat_top = -0.18 * math.exp(-((math.atan2(math.sin(a - 1.9), math.cos(a - 1.9))) / 0.5) ** 2)
    return 1.0 + keel + base + flat_top


def build():
    mb = nh.MeshBuilder()
    n = int(TURNS * STEPS)
    r_end = 0.3
    rings, cols = [], []
    keel_pts = []
    for i in range(n + 1):
        th = i / STEPS * math.tau
        R = r_end * W ** ((i - n) / STEPS)
        c = Vector((R * math.cos(th), R * math.sin(th), -SPIRE * R))
        rt = R * SECTION
        out = Vector((math.cos(th), math.sin(th), 0))
        up = Vector((0, 0, 1))
        ring, rc = [], []
        for j in range(SIDES):
            a = j / SIDES * math.tau
            p = c + (out * math.cos(a) + up * math.sin(a)) * rt * section_r(a)
            ring.append(p)
            s = 0.5 + 0.5 * math.cos(a * 9)
            col = nh.lerp(SHELL, CORD, 0.5 * nh.smoothstep(0.7, 1.0, s))
            if abs(math.sin(a) - 0.25) < 0.15 or abs(a - 2.2) < 0.15:
                col = nh.lerp(col, BAND, 0.75)
            g = 0.5 + 0.5 * math.sin(th * 18)
            rc.append(tuple(x * (0.92 + 0.08 * g) for x in col))
        rings.append(ring)
        cols.append(rc)
        if i % 5 == 0 and i > STEPS * 0.8:
            keel_pts.append((c + (out * math.cos(KEEL_A) + up * math.sin(KEEL_A)) * rt * section_r(KEEL_A),
                             out * math.cos(KEEL_A) + up * math.sin(KEEL_A), R))
    bm = bmesh.new()
    cl = bm.loops.layers.color.new("Col")
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    for i in range(n):
        for j in range(SIDES):
            jj = (j + 1) % SIDES
            f = bm.faces.new([vr[i][j], vr[i][jj], vr[i + 1][jj], vr[i + 1][j]])
            for lp, (ii, kk) in zip(f.loops, [(i, j), (i, jj), (i + 1, jj), (i + 1, j)]):
                c3 = cols[ii][kk]
                lp[cl] = (c3[0], c3[1], c3[2], 1.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ap = sum(rings[-1], Vector()) / SIDES
    ap_r = r_end * SECTION
    mb.add(bm, None)
    # dark aperture fill
    mb.add(nh.ellipsoid(tuple(ap + Vector((0, 0.03, 0))), (ap_r * 0.92, ap_r * 0.15, ap_r * 0.92), 2), (0.16, 0.11, 0.09))
    # blunt nodes along the shoulder keel
    for p, d, R in keel_pts:
        mb.add(nh.tube([p - d * 0.01, p + d * R * 0.16], [R * 0.06, 0.0], sides=6), NODE)
    # foot and head
    fz = ap.z - ap_r * 0.9
    mb.add(nh.ellipsoid((ap.x * 0.55, ap.y - 0.08, fz), (ap_r * 1.2, ap_r * 1.7, ap_r * 0.30), 2), FOOT)
    for sx in (-1, 1):
        b = Vector((ap.x * 0.55 + sx * ap_r * 0.45, ap.y - ap_r * 1.6, fz + ap_r * 0.3))
        mb.add(nh.tube([b, b + Vector((sx * 0.05, -0.14, 0.07))], [0.022, 0.0], sides=5), FOOT)
        mb.add(nh.ellipsoid(tuple(b + Vector((sx * 0.02, 0.0, 0.02))), (0.016,) * 3, 1), (0.05, 0.04, 0.04))
    obj = mb.to_object(NAME, roughness=0.5)
    nh.ground_to_zero(obj)
    vs = obj.data.vertices
    xs, ys = [v.co.x for v in vs], [v.co.y for v in vs]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    for v in vs:
        v.co.x -= cx
        v.co.y -= cy
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ec.VIEWS)
