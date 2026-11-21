"""
Procedural Naraoia compacta (Burgess Shale nektaspid, ~4 cm).

Two smooth, gently domed, unmineralised shields and no thorax: a semicircular head
shield and a larger oval trunk shield overlapping it, with a narrow hinge between.
Long, slender, curving antennae in front and the tips of many spiny legs showing under
the shield margins. Pale greyish tan with a faint darker midline. Faces -Y, pivot at the
body centre (Swim).

Output: Assets/Resources/Models/Species/Naraoia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_b2_cambrian_kit as ck  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHIELD = (0.70, 0.62, 0.48)
SHIELD_DARK = (0.52, 0.44, 0.32)
LEG = (0.62, 0.48, 0.32)


def col(cy):
    def c(co, n):
        mid = 1.0 - nh.smoothstep(0.02, 0.12, abs(co.x))
        return nh.lerp(SHIELD, SHIELD_DARK, 0.25 + 0.55 * mid)
    return c


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.plate(-0.3, 0.38, 0.22, 0.09, edge_droop=0.8), col(-0.3))
    mb.add(ec.plate(0.17, 0.4, 0.42, 0.11, z=0.01, edge_droop=0.8), col(0.17))
    mb.add(nh.uv_ellipsoid((0, 0.05, -0.02), (0.22, 0.5, 0.04), segments=14, rings=6), SHIELD_DARK)
    for s in (-1, 1):
        ck.antenna(mb, (s * 0.06, -0.48, -0.01), s, 0.5, 0.014, LEG, spread=0.7, droop=0.0, n=7)
    ck.legs_under(mb, -0.35, 0.45, 12, lambda t: 0.5 - 0.15 * t, LEG, z=-0.02, reach=0.1, drop=0.05, r=0.012)
    return ec.centre(mb.to_object("Naraoia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Naraoia")
