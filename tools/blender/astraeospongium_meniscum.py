"""
Procedural Astraeospongium meniscum (a Silurian calcareous sponge, about 5-10 cm across,
common in the Silurian of Tennessee and also found in Europe) for map colonies (Fixed).

A thick, saucer- or meniscus-shaped sponge lying on the sea floor, its skeleton built
of large calcite spicules shaped like six-rayed stars (with a seventh and eighth ray
sticking up and down), packed loosely together so the star shapes cover the whole
surface. Water was drawn in through its pores and filtered for food. Two saucers on
a patch of pale reef mud, cream-grey with darker stars.
Fixed style: pivot on the sea floor, facing -Y.

Usage:
  blender --background --python tools/blender/astraeospongium_meniscum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AstraeospongiumMeniscum.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

NAME = "AstraeospongiumMeniscum"
SPONGE = (0.86, 0.82, 0.70)
SPONGE_DARK = (0.66, 0.60, 0.48)
STAR = (0.42, 0.36, 0.28)


def saucer(R, depth, thick, matrix, seed):
    """A meniscus: concave on top, convex below, with a rounded rim (polar grid)."""
    bm = bmesh.new()
    nr, na = 12, 48
    def top(r):
        return thick + depth * (r / R) ** 2
    def bot(r):
        return -thick * 0.4 + depth * 0.6 * (r / R) ** 2 - 0.0
    rings_t, rings_b = [], []
    for i in range(nr + 1):
        r = R * i / nr
        rt, rb = [], []
        for j in range(na):
            a = j / na * math.tau
            w = 1.0 + 0.04 * math.sin(a * 3 + seed)
            rt.append(bm.verts.new((r * w * math.cos(a), r * w * math.sin(a), top(r))))
            rb.append(bm.verts.new((r * w * math.cos(a), r * w * math.sin(a), bot(r))))
        rings_t.append(rt)
        rings_b.append(rb)
    for i in range(nr):
        for j in range(na):
            jj = (j + 1) % na
            bm.faces.new([rings_t[i][j], rings_t[i + 1][j], rings_t[i + 1][jj], rings_t[i][jj]])
            bm.faces.new([rings_b[i][j], rings_b[i][jj], rings_b[i + 1][jj], rings_b[i + 1][j]])
    for j in range(na):
        jj = (j + 1) % na
        bm.faces.new([rings_t[nr][j], rings_b[nr][j], rings_b[nr][jj], rings_t[nr][jj]])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    nh.transform(bm, matrix)
    return bm


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 1.0, ((0.48, 0.46, 0.40), (0.62, 0.60, 0.52)))
    rnd = random.Random(2)
    for x, y, R, tilt in ((-0.18, -0.10, 0.48, 6), (0.50, 0.38, 0.30, -10)):
        m = Matrix.Translation(Vector((x, y, 0.06))) @ Matrix.Rotation(math.radians(tilt), 4, "X")
        bm = saucer(R, R * 0.22, R * 0.14, m, rnd.random() * 6)
        mb.add(bm, lambda co, n: nh.lerp(SPONGE, SPONGE_DARK, 0.4 * nh.smoothstep(0.0, -0.8, n.z)))
        # six-rayed star spicules standing proud of the top surface on a jittered hex lattice
        cell = R * 0.21
        thick, depth = R * 0.14, R * 0.22
        for row in range(-6, 7):
            for col_ in range(-6, 7):
                px = (col_ + 0.5 * (row % 2)) * cell + rnd.uniform(-0.1, 0.1) * cell
                py = row * cell * 0.866 + rnd.uniform(-0.1, 0.1) * cell
                r = math.hypot(px, py)
                if r > R * 0.88:
                    continue
                z = thick + depth * (r / R) ** 2 + 0.006
                c = m @ Vector((px, py, z))
                up = (m.to_3x3() @ Vector((0, 0, 1))).normalized()
                rot = rnd.uniform(0, math.pi / 3)
                for k in range(6):
                    a = rot + k * math.pi / 3
                    d = m.to_3x3() @ Vector((math.cos(a), math.sin(a), 0.0))
                    mb.add(nh.tube([c, c + d * cell * 0.44], [cell * 0.07, 0.0], sides=4), STAR, smooth=False)
                mb.add(nh.tube([c, c + up * cell * 0.18], [cell * 0.07, 0.0], sides=4), STAR, smooth=False)
    obj = mb.to_object(NAME, roughness=0.75)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ec.VIEWS)
