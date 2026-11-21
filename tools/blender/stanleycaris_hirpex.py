"""
Procedural Stanleycaris hirpex (Burgess Shale hurdiid radiodont, small).

A small radiodont with a short rounded head carapace, two large stalked lateral eyes
and a big third (median) eye on top of the head; frontal limbs with long, forward-
hooked spines like a rake of claws; a slim trunk of swimming flaps ending in a tail fan.
Reddish with dark bands. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Stanleycaris.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_b2_cambrian_kit as ck  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.66, 0.24, 0.16)
RIM = (0.92, 0.62, 0.44)
BODY = (0.74, 0.36, 0.24)
DARK = (0.38, 0.12, 0.08)
BELLY = (0.92, 0.72, 0.58)
FLAP = (0.82, 0.46, 0.32)
SPINE = (0.96, 0.90, 0.78)
EYE = (0.02, 0.02, 0.02)


def build():
    mb = nh.MeshBuilder()
    ck.radiodont_trunk(mb, -0.08, 0.75, 11, 0.1, BODY, DARK, BELLY, FLAP, flap_len=0.15, fan=3, fan_len=0.2, fan_col=DARK)
    mb.add(nh.uv_ellipsoid((0, -0.2, 0.0), (0.12, 0.16, 0.08), segments=14, rings=8), BELLY)
    h = nh.uv_ellipsoid((0, 0, 0), (0.12, 0.14, 0.05), segments=18, rings=8)
    for v in h.verts:
        if v.co.z < 0:
            v.co.z *= 0.3
    nh.transform(h, Matrix.Translation((0, -0.24, 0.07)))
    mb.add(h, lambda co, n: nh.lerp(SHELL, RIM, nh.smoothstep(0.08, 0.12, abs(co.x))))
    # big median eye on top
    mb.add(nh.ellipsoid((0, -0.14, 0.12), (0.045, 0.045, 0.04), subdivisions=3), EYE)
    mb.add(nh.ellipsoid((0.012, -0.165, 0.15), (0.01, 0.01, 0.01), subdivisions=1), (0.9, 0.9, 0.9))
    for s in (-1, 1):
        ck.stalked_eye(mb, (s * 0.09, -0.16, 0.05), (s * 0.22, -0.2, 0.08), 0.05, DARK, EYE)
        ck.frontal_limb(mb, s, (s * 0.05, -0.36, -0.02), 0.2, 0.14, 0.028, DARK, SPINE, n=6,
                        spine_len=0.12, comb=0, hook=0.8)
    return ec.centre(mb.to_object("Stanleycaris", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Stanleycaris")
