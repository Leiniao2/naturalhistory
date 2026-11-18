"""
Procedural Isoxys auritus (early Cambrian swimming arthropod, Chengjiang, ~3 cm).

A thin, laterally flattened, two-halved (bivalved) carapace, its hinge line along the back
drawn out into a long, straight spine at the front and another at the back; a pair of big,
round, stalked eyes bulging out in front, a pair of spiny grasping frontal limbs curling
down beneath them, and a fringe of small swimming legs and a short tail fan peeking out
under the shell. Pale amber carapace with a darker hinge and margin. Swim style: pivot at
the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/isoxys_auritus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Isoxys.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.86, 0.70, 0.44)
MARGIN = (0.60, 0.42, 0.22)
HINGE = (0.46, 0.30, 0.14)
LEG = (0.92, 0.80, 0.62)
APP = (0.70, 0.44, 0.24)
EYE = (0.05, 0.04, 0.04)


def build():
    mb = nh.MeshBuilder()
    for s in (-1, 1):
        v = nh.uv_ellipsoid((0, 0, 0), (0.12, 0.36, 0.22), segments=20, rings=10)
        for p in v.verts:
            p.co.x = abs(p.co.x) * 0.8 + 0.008
        if s < 0:
            nh.transform(v, Matrix.Scale(-1, 4, (1, 0, 0)))
            bmesh.ops.reverse_faces(v, faces=v.faces)
        nh.transform(v, Matrix.Translation((0, 0, -0.05)))

        def col(co, n):
            e = (co.y / 0.36) ** 2 + ((co.z + 0.05) / 0.22) ** 2
            c = nh.lerp(SHELL, MARGIN, nh.smoothstep(0.75, 0.98, e))
            return nh.lerp(HINGE, c, nh.smoothstep(0.012, 0.03, abs(co.x)))
        mb.add(v, col)
    mb.add(ec.spike((0, -0.3, 0.13), (0, -0.62, 0.17), r=0.018, sides=6), HINGE)
    mb.add(ec.spike((0, 0.3, 0.13), (0, 0.66, 0.16), r=0.018, sides=6), HINGE)
    for s in (-1, 1):
        e0 = Vector((s * 0.03, -0.34, 0.0))
        e1 = e0 + Vector((s * 0.03, -0.08, 0.0))
        mb.add(nh.tube([e0, e1], [0.02, 0.018], sides=6), SHELL)
        mb.add(nh.ellipsoid(e1 + Vector((s * 0.02, -0.03, 0)), (0.055, 0.055, 0.055), subdivisions=3), EYE)
        b = Vector((s * 0.025, -0.3, -0.13))
        pts = kit.curve(b, b + Vector((s * 0.03, -0.16, -0.02)), b + Vector((0, -0.2, -0.12)), 5)
        mb.add(nh.tube(pts, [0.016, 0.014, 0.012, 0.01, 0.008, 0.0], sides=5), APP)
        for k in range(1, 5):
            p = pts[k]
            mb.add(ec.spike(p, p + Vector((-s * 0.015, 0.03, -0.035)), r=0.004, sides=3), LEG, smooth=False)
        for k in range(9):
            y = -0.22 + k * 0.05
            p0 = Vector((s * 0.02, y, -0.18))
            mb.add(ec.jointed_leg([p0, p0 + Vector((s * 0.02, 0.01, -0.05)), p0 + Vector((s * 0.01, 0.03, -0.09))],
                                  r0=0.007, r1=0.003, sides=4), LEG)
    for s in (-1, 1):
        f = ec.paddle(0.08, 0.025, n=8, taper=0.5, thickness=0.006)
        nh.transform(f, Matrix.Rotation(math.radians(70), 4, "Z"))
        ec.mirror(f, s)
        nh.transform(f, Matrix.Translation((s * 0.01, 0.34, -0.12)))
        mb.add(f, LEG, smooth=False)
    return ec.centre(mb.to_object("Isoxys", roughness=0.35))


if __name__ == "__main__":
    ec.export(build, "Isoxys")
