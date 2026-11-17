"""
Procedural Tetragraptus approximatus (Early Ordovician, Floian, planktonic graptolite;
its first appearance defines the base of the Floian Stage) for the map (Drift style).

A small floating colony of four slender stipes radiating from the sicula in two close
pairs ("approximate" pairs), held out horizontally like a flat cross. Each stipe is a
common canal along which inclined thecal tubes bud in a row, all opening on the same
(lower) side with dark apertures. A fine nema thread rises from the sicula. Pale amber,
modelled thick so it reads on the map (see didymograptellus_eobifidus.py).

Usage:
  blender --background --python tools/blender/tetragraptus_approximatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TetragraptusApproximatus.fbx (pivot at the colony centre)
"""

import math
import sys
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

AMBER = (0.82, 0.58, 0.28)
AMBER_PALE = (0.95, 0.80, 0.50)
AMBER_DARK = (0.44, 0.26, 0.10)
THREAD = (0.90, 0.82, 0.64)

STIPE_LEN = 0.85
THECAE = 10
# stipe directions (degrees): two close pairs, as in T. approximatus
ANGLES = (-25, 25, 155, 205)


def fusellar(co, n):
    band = 0.5 + 0.5 * math.sin((co.x + co.y) * 150.0)
    return nh.lerp(AMBER, AMBER_PALE, 0.2 + 0.45 * band)


def build():
    mb = nh.MeshBuilder()
    # sicula: short cone, aperture down
    mb.add(nh.tube([Vector((0, 0, 0.12)), Vector((0, 0, 0.0)), Vector((0, 0, -0.16))],
                   [0.012, 0.03, 0.045], sides=10), fusellar)
    mb.add(nh.tube([Vector((0, 0, -0.155)), Vector((0, 0, -0.17))], [0.05, 0.05], sides=10), AMBER_DARK)
    pts = [Vector((0.012 * math.sin(k * 0.8), 0.0, 0.12 + 0.35 * k / 6)) for k in range(7)]
    mb.add(nh.tube(pts, [0.006] * 6 + [0.0], sides=4, cap_start=False), THREAD)
    # crossing funicle joining the pairs
    for sx in (-1, 1):
        mb.add(nh.tube([Vector((0, 0, -0.02)), Vector((sx * 0.08, 0, -0.02))], [0.02, 0.022], sides=6), fusellar)
    for deg in ANGLES:
        a = math.radians(deg)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        start = Vector((math.copysign(0.08, d.x), 0, -0.02))
        path = [start + d * (STIPE_LEN * k / 6) + Vector((0, 0, -0.04 * (k / 6) ** 2)) for k in range(7)]
        mb.add(nh.tube(path, [0.02 + 0.006 * k / 6 for k in range(7)], sides=6), fusellar)
        down = Vector((0, 0, -1))
        for k in range(THECAE):
            t = (k + 0.3) / THECAE
            base = start + d * (STIPE_LEN * t) + Vector((0, 0, -0.04 * t * t))
            g = 0.8 + 0.3 * t
            p1 = base + d * 0.04 * g + down * 0.02 * g
            ap = base + d * 0.09 * g + down * 0.055 * g
            mb.add(nh.tube([base, p1, ap], [0.02 * g, 0.024 * g, 0.027 * g], sides=6,
                           cap_start=False, cap_end=False), fusellar)
            ld = (ap - p1).normalized()
            mb.add(nh.tube([ap - ld * 0.004, ap + ld * 0.006], [0.028 * g, 0.032 * g], sides=6,
                           cap_start=True, cap_end=False), AMBER_DARK)
    obj = mb.to_object("TetragraptusApproximatus", roughness=0.35)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "TetragraptusApproximatus", views=((30, 35), (0, 85), (90, 10)))
