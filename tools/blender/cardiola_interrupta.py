"""
Procedural Cardiola interrupta (a Silurian bivalve, about 2-4 cm across, from the
Wenlock-Ludlow of Europe and North Africa) for map colonies (Fixed).

A small, strongly inflated, rounded clam with prominent, inrolled beaks near the front
of the hinge, sculptured with strong radial ribs crossed by concentric growth furrows,
which cut the ribs into rows of beads - the "interrupted" ribs of its name. Common in
dark Silurian muds, where it may have lived attached by byssal threads. Three shells on
a patch of dark mud, beaks up. Fixed style: pivot on the sea floor, facing -Y.

Usage:
  blender --background --python tools/blender/cardiola_interrupta.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CardiolaInterrupta.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

NAME = "CardiolaInterrupta"
SHELL = (0.80, 0.72, 0.58)
RIB_DARK = (0.42, 0.34, 0.26)
BEAK = (0.60, 0.50, 0.38)
LINE = (0.16, 0.12, 0.10)

L, H, W = 0.36, 0.34, 0.20     # half-length, half-height, half-width over both valves
BEAK_Y, BEAK_Z = -0.08, 0.30


def shell(matrix):
    bm = nh.ellipsoid((0, 0, 0), (W, L, H), subdivisions=4)
    for v in bm.verts:
        dy, dz = v.co.y - BEAK_Y, v.co.z - BEAK_Z
        d = math.hypot(dy, dz)
        # beaks: pull the top front up and in
        bump = nh.smoothstep(0.22, 0.0, d)
        v.co.z += 0.07 * bump
        v.co.y -= 0.03 * bump
        # sculpture: radial ribs x concentric furrows (beaded)
        ang = math.atan2(dy, -dz)
        rib = 0.5 + 0.5 * math.cos(ang * 18.0)
        ring = 0.5 + 0.5 * math.cos(d * 32.0)
        k = (0.6 * rib + 0.4 * ring) * nh.smoothstep(0.08, 0.2, d)
        if abs(v.co.x) > 0.02:
            v.co.x *= 1.0 + 0.05 * k
    nh.transform(bm, matrix)

    inv = matrix.inverted()

    def col(co, n):
        p = inv @ co
        dy, dz = p.y - BEAK_Y, p.z - BEAK_Z
        d = math.hypot(dy, dz)
        ang = math.atan2(dy, -dz)
        rib = 0.5 + 0.5 * math.cos(ang * 18.0)
        ring = 0.5 + 0.5 * math.cos(d * 32.0)
        c = nh.lerp(SHELL, RIB_DARK, 0.75 * (1.0 - rib) * (0.5 + 0.5 * ring) + 0.25 * (1.0 - ring))
        c = nh.lerp(c, BEAK, 0.6 * nh.smoothstep(0.15, 0.0, d))
        return nh.lerp(c, LINE, nh.smoothstep(0.014, 0.006, abs(p.x)))
    return bm, col


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 0.95, ((0.22, 0.21, 0.19), (0.34, 0.32, 0.28)))
    for x, y, yaw, k in ((0.0, -0.15, 0, 1.0), (-0.48, 0.30, 70, 0.8), (0.46, 0.32, -50, 0.75)):
        m = Matrix.Translation(Vector((x, y, H * 0.75 * k))) @ Matrix.Rotation(math.radians(yaw), 4, "Z") \
            @ Matrix.Scale(k, 4)
        mb.add(*shell(m))
    obj = mb.to_object(NAME, roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ec.VIEWS)
