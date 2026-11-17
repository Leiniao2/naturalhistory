"""
Procedural low-poly Sanctacaris uniformis (Burgess Shale stem chelicerate).

A broad, almost circular head shield with a pair of small eyes at the front;
under its front edge five pairs of stout, spiny grasping limbs reach forward
and up in a basket (the raptorial head limbs of an early chelicerate). Behind
the shield a segmented trunk of eleven tergites narrows to a broad, rounded
paddle-like telson. Short walking legs show beneath the shield. Sandy brown
with darker segment edges and reddish spines.
Faces -Y, pivot at the body centre (Swim, a bottom-hunting predator).

Usage:
  blender --background --python tools/blender/sanctacaris_uniformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sanctacaris.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

SHELL = (0.58, 0.46, 0.30)
SHELL_DARK = (0.36, 0.27, 0.17)
SHELL_LIGHT = (0.70, 0.58, 0.40)
LIMB = (0.64, 0.44, 0.28)
SPINE = (0.52, 0.24, 0.14)
TELSON = (0.56, 0.42, 0.26)
EYE = (0.05, 0.04, 0.04)


def build():
    mb = nh.MeshBuilder()
    # broad head shield, wider than long
    mb.add(ec.plate(-0.26, 0.40, 0.30, 0.09),
           lambda co, n: nh.lerp(SHELL_LIGHT, SHELL_DARK, nh.smoothstep(0.75, 1.0, math.hypot(co.x / 0.40, (co.y + 0.26) / 0.30))))
    # trunk: eleven tergites narrowing backwards
    for i in range(11):
        t = i / 10
        y = 0.08 + i * 0.062
        w = 0.27 - 0.17 * t
        mb.add(ec.plate(y, w, 0.052, 0.05 - 0.02 * t, z=0.005),
               lambda co, n, w=w: nh.lerp(SHELL, SHELL_DARK, nh.smoothstep(0.6, 1.0, abs(co.x) / w)))
        for s in (-1, 1):
            p = Vector((s * w * 0.95, y + 0.01, -0.005))
            mb.add(ec.spike(p - Vector((s * 0.03, 0, 0)), p + Vector((s * 0.02, 0.035, -0.005)), r=0.014, sides=4),
                   SHELL_DARK, smooth=False)
    # broad, rounded paddle telson
    mb.add(ec.plate(0.82, 0.12, 0.10, 0.02), TELSON)

    # five pairs of spiny grasping head limbs, reaching forward and up in a basket
    for i in range(5):
        for s in (-1, 1):
            # each limb sweeps out from under the shield, then bends forward and in at the tip
            base = Vector((s * (0.06 + 0.05 * i), -0.44 + 0.06 * i, -0.03))
            reach = 0.30 - 0.03 * i
            elbow = base + Vector((s * (0.08 + 0.04 * i), -reach * 0.45, 0.07))
            claw = elbow + Vector((s * 0.01, -reach * 0.40, 0.08))
            tip = claw + Vector((-s * (0.07 + 0.015 * i), -reach * 0.15, 0.02))
            mb.add(ec.jointed_leg([base, elbow, claw, tip], 0.026, 0.009, sides=6), LIMB)
            # a comb of inward-pointing spines along the outer podomeres
            for k in range(4):
                p = elbow.lerp(claw, (k + 0.5) / 4)
                inward = Vector((-s * 0.6, -0.3, 0.6)).normalized()
                mb.add(ec.spike(p, p + inward * 0.05, r=0.006, sides=4), SPINE, smooth=False)
            p = base.lerp(elbow, 0.6)
            mb.add(ec.spike(p, p + Vector((-s * 0.3, -0.2, 0.9)).normalized() * 0.05, r=0.006, sides=4), SPINE, smooth=False)

    # short walking legs under the shield
    for i in range(5):
        y = -0.18 + i * 0.07
        for s in (-1, 1):
            r = Vector((s * 0.08, y, -0.03))
            k = Vector((s * 0.24, y - 0.01, -0.05))
            f = Vector((s * 0.33, y + 0.03, -0.10))
            mb.add(ec.jointed_leg([r, k, f], 0.018, 0.007, sides=5), LIMB)

    # small eyes at the front of the shield
    for s in (-1, 1):
        mb.add(nh.ellipsoid((s * 0.10, -0.52, 0.06), (0.03, 0.03, 0.026), subdivisions=1), EYE)
    return ec.centre(mb.to_object("Sanctacaris", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Sanctacaris")
