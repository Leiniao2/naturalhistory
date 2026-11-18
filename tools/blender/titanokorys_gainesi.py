"""
Procedural Titanokorys gainesi (Burgess Shale hurdiid radiodont, ~50 cm).

Dominated by an enormous, flattened, oval head shield (the dorsal carapace) drawn out
into a short point at the front, with a pair of smaller lateral shields along its sides and
eyes peeping out at the rear corners. Behind it a short, tapering body with small swimming
flaps and a few setal blades; under the shield's front a pair of short frontal limbs bear
long, comb-like rakes of spines. Dark reddish brown shield with a paler rim. Swim style:
pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/titanokorys_gainesi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Titanokorys.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHIELD = (0.46, 0.22, 0.16)
RIM = (0.80, 0.56, 0.40)
BODY = (0.58, 0.32, 0.24)
DARK = (0.34, 0.16, 0.12)
BELLY = (0.80, 0.60, 0.50)
FLAP = (0.66, 0.40, 0.30)
RAKE = (0.92, 0.82, 0.66)
EYE = (0.04, 0.03, 0.03)


def shield_col(cx, hw, hl):
    def col(co, n):
        e = ((co.x - cx) / hw) ** 2 + ((co.y + 0.15) / hl) ** 2
        return nh.lerp(SHIELD, RIM, nh.smoothstep(0.7, 0.98, e))
    return col


def build():
    mb = nh.MeshBuilder()
    Y0, Y1, SEG = 0.12, 0.8, 9
    mb.add(ec.segmented_trunk(Y0, Y1, SEG, lambda t: 0.1 * (1 - 0.6 * t), flat=0.6, sides=10, tip=0.02),
           ec.banded(BODY, DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.5))
    for i in range(SEG):
        t = i / (SEG - 1)
        y = Y0 + (i + 0.5) * (Y1 - Y0) / SEG
        for s in (-1, 1):
            f = ec.paddle(0.13 * (1 - 0.5 * t) + 0.03, 0.04, n=10, taper=0.55, thickness=0.01)
            nh.transform(f, Matrix.Rotation(math.radians(-20), 4, "Z"))
            ec.mirror(f, s)
            nh.transform(f, Matrix.Translation((s * 0.08 * (1 - 0.5 * t), y, -0.02)))
            mb.add(f, FLAP, smooth=False)
    for s in (-1, 1):
        for k in range(3):
            b = ec.paddle(0.14, 0.02, n=8, taper=0.5, thickness=0.008)
            nh.transform(b, Matrix.Rotation(math.radians(70 + 12 * k), 4, "Z"))
            ec.mirror(b, s)
            nh.transform(b, Matrix.Translation((s * 0.015, Y1 - 0.02 + 0.015 * k, 0.01)))
            mb.add(b, RIM, smooth=False)
    # head core under the shield
    mb.add(nh.uv_ellipsoid((0, -0.25, -0.02), (0.13, 0.25, 0.07), segments=14, rings=8), BELLY)
    # giant dorsal shield: flat dome, pointed front
    hw, hl = 0.34, 0.62
    sh = nh.uv_ellipsoid((0, 0, 0), (hw, hl, 0.07), segments=32, rings=14)
    for v in sh.verts:
        if v.co.z < 0:
            v.co.z *= 0.25
        u = -v.co.y / hl
        if u > 0.4:
            v.co.x *= 1 - 0.6 * (u - 0.4) / 0.6
    nh.transform(sh, Matrix.Translation((0, -0.15, 0.06)))
    mb.add(sh, shield_col(0, hw, hl))
    for s in (-1, 1):
        lat = nh.uv_ellipsoid((0, 0, 0), (0.1, 0.32, 0.03), segments=14, rings=8)
        nh.transform(lat, Matrix.Rotation(math.radians(s * 55), 4, "Y"))
        nh.transform(lat, Matrix.Translation((s * 0.3, -0.12, -0.02)))
        mb.add(lat, lambda co, n: nh.lerp(SHIELD, RIM, 0.35))
        mb.add(nh.ellipsoid((s * 0.26, 0.38, 0.0), (0.035, 0.035, 0.03), subdivisions=2), EYE)
        # frontal limbs with long rakes
        b = Vector((s * 0.06, -0.5, -0.06))
        pts = kit.curve(b, b + Vector((s * 0.05, -0.1, -0.02)), b + Vector((0.0, -0.18, -0.1)), 5)
        mb.add(nh.tube(pts, [0.03, 0.026, 0.022, 0.018, 0.014, 0.01], sides=6), DARK)
        for k in range(1, 6):
            p = pts[k]
            mb.add(ec.spike(p, p + Vector((-s * 0.1, 0.03, -0.04)), r=0.006, sides=3), RAKE, smooth=False)
            for q in range(4):
                c = p.lerp(p + Vector((-s * 0.1, 0.03, -0.04)), 0.3 + q * 0.18)
                mb.add(ec.spike(c, c + Vector((0, 0.03, -0.015)), r=0.003, sides=3), RAKE, smooth=False)
    return ec.centre(mb.to_object("Titanokorys", roughness=0.4))


if __name__ == "__main__":
    ec.export(build, "Titanokorys")
