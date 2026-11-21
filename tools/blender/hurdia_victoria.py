"""
Procedural Hurdia victoria (Burgess Shale hurdiid radiodont, ~20 cm).

A long, pointed head carapace (the dorsal H-element) juts forward well beyond the head
like a prow, flanked by a pair of oval lateral plates; stalked eyes peep out behind
them. Under the front a pair of short frontal limbs bear long, comb-fringed spines.
Behind, a tapering trunk with swimming flaps, a tail fan of blades. Dark reddish brown
carapace with paler rims. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Hurdia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_b2_cambrian_kit as ck  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.50, 0.20, 0.14)
RIM = (0.84, 0.58, 0.42)
BODY = (0.62, 0.34, 0.24)
DARK = (0.36, 0.16, 0.12)
BELLY = (0.84, 0.64, 0.52)
FLAP = (0.70, 0.42, 0.30)
SPINE = (0.92, 0.82, 0.66)


def build():
    mb = nh.MeshBuilder()
    ck.radiodont_trunk(mb, -0.05, 0.75, 9, 0.12, BODY, DARK, BELLY, FLAP, flap_len=0.15, fan=3, fan_len=0.2, fan_col=DARK)
    mb.add(nh.uv_ellipsoid((0, -0.22, -0.02), (0.12, 0.2, 0.08), segments=14, rings=8), BELLY)
    # H-element: a long narrow pointed prow
    hl = 0.42
    h = nh.uv_ellipsoid((0, 0, 0), (0.13, hl, 0.06), segments=24, rings=10)
    for v in h.verts:
        u = -v.co.y / hl
        if u > 0:
            v.co.x *= 1 - 0.75 * u ** 1.4
            v.co.z += 0.06 * u * u
        if v.co.z < 0:
            v.co.z *= 0.3
    nh.transform(h, Matrix.Translation((0, -0.42, 0.06)))
    mb.add(h, lambda co, n: nh.lerp(SHELL, RIM, nh.smoothstep(0.08, 0.13, abs(co.x)) * 0.8))
    mb.add(ec.spike((0, -0.82, 0.12), (0, -0.92, 0.17), r=0.02, sides=5), SHELL)
    for s in (-1, 1):
        p = nh.uv_ellipsoid((0, 0, 0), (0.09, 0.2, 0.025), segments=14, rings=8)
        nh.transform(p, Matrix.Rotation(math.radians(s * 50), 4, "Y"))
        nh.transform(p, Matrix.Translation((s * 0.15, -0.25, 0.0)))
        mb.add(p, lambda co, n: nh.lerp(SHELL, RIM, 0.4))
        ck.stalked_eye(mb, (s * 0.1, -0.06, 0.03), (s * 0.2, -0.02, 0.06), 0.035, DARK)
        ck.frontal_limb(mb, s, (s * 0.06, -0.38, -0.06), 0.16, 0.18, 0.03, DARK, SPINE, n=6,
                        spine_len=0.13, comb=3)
    return ec.centre(mb.to_object("Hurdia", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Hurdia")
