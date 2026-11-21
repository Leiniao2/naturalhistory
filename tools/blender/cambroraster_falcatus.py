"""
Procedural Cambroraster falcatus (Burgess Shale hurdiid radiodont, up to ~30 cm).

The head is covered by a huge, broad horseshoe-shaped carapace (wider than long, with
two blunt prongs trailing back at the sides and notches where the small eyes look
out). A short tapering trunk with small flaps sticks out behind; under the shield a pair
of frontal limbs bear rakes of long, inward-curving spines with fine combs.
Brown carapace with a pale rim. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Cambroraster.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_b2_cambrian_kit as ck  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.42, 0.28, 0.16)
RIM = (0.86, 0.70, 0.48)
BODY = (0.58, 0.40, 0.26)
DARK = (0.30, 0.18, 0.10)
BELLY = (0.82, 0.66, 0.50)
FLAP = (0.66, 0.48, 0.32)
SPINE = (0.94, 0.86, 0.70)


def build():
    mb = nh.MeshBuilder()
    ck.radiodont_trunk(mb, 0.1, 0.62, 7, 0.1, BODY, DARK, BELLY, FLAP, flap_len=0.1, fan=2, fan_len=0.12)
    mb.add(nh.uv_ellipsoid((0, -0.12, -0.03), (0.13, 0.22, 0.07), segments=14, rings=8), BELLY)
    # horseshoe shield: a broad flat dome, a deep notch cut out of the back
    W, L = 0.5, 0.42
    sh = nh.uv_ellipsoid((0, 0, 0), (W, L, 0.09), segments=40, rings=16)
    for v in sh.verts:
        x, y = v.co.x / W, v.co.y / L
        if v.co.z < 0:
            v.co.z *= 0.2
        # rear notch: pull the middle back edge forward -> horseshoe with two prongs
        if y > 0:
            k = math.exp(-(x / 0.45) ** 2) * y ** 1.5
            v.co.y -= 0.6 * L * k
            v.co.z -= 0.05 * k
        v.co.z -= 0.03 * x * x
    nh.transform(sh, Matrix.Translation((0, -0.12, 0.07)))
    def col(co, n):
        e = (co.x / W) ** 2 + ((co.y + 0.12) / L) ** 2
        return nh.lerp(SHELL, RIM, nh.smoothstep(0.65, 0.95, e))
    mb.add(sh, col)
    mb.add(nh.uv_ellipsoid((0, -0.2, 0.13), (0.08, 0.2, 0.03), segments=12, rings=6), nh.lerp(SHELL, DARK, 0.4))
    for s in (-1, 1):
        mb.add(nh.ellipsoid((s * 0.2, 0.05, 0.04), (0.03, 0.03, 0.025), subdivisions=2), (0.03, 0.03, 0.03))
        ck.frontal_limb(mb, s, (s * 0.07, -0.3, -0.04), 0.1, 0.12, 0.025, DARK, SPINE, n=7,
                        spine_len=0.13, comb=4)
    return ec.centre(mb.to_object("Cambroraster", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Cambroraster")
