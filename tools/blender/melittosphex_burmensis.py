"""
Procedural Melittosphex burmensis (mid-Cretaceous bee-like wasp, Burmese amber, Myanmar), flying.

A tiny insect, about 3 mm long, preserved in roughly 99-million-year-old amber and described
in 2006 as the oldest bee-like fossil. It mixes wasp features (narrow hind legs, wing veins)
with bee ones: branched, feathery body hairs of the kind bees use to pick up pollen, so it
probably visited early flowers. Dark brown body, a fuzzy thorax, a slender waist, and two
pairs of clear wings raised in flight.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/melittosphex_burmensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Melittosphex.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402

BODY = (0.20, 0.13, 0.07)
HAIR = (0.62, 0.46, 0.26)
EYE = (0.06, 0.05, 0.04)
WING = (0.80, 0.80, 0.74)
VEIN = (0.35, 0.28, 0.20)
LEG = (0.28, 0.18, 0.10)


def fuzzy(base, light):
    def col(co, n):
        return nh.lerp(base, light, 0.5 + 0.5 * noise.noise(co * 40.0))
    return col


def wing(sx, root, length, width, sweep, lift):
    a = math.radians(sweep)
    d = Vector((sx * math.cos(a), math.sin(a), math.tan(math.radians(lift))))
    perp = Vector((-sx * math.sin(a) * 0.3, 1.0, 0.0)).normalized()
    lead, trail = [], []
    for i in range(10):
        t = i / 9
        p = Vector(root) + d * length * t
        w = width * math.sin(math.pi * min(1.0, 0.15 + t * 0.85)) ** 0.7
        lead.append(p)
        trail.append(p + perp * w)
    return cc.membrane(lead, trail, nv=3, thickness=0.006)


def wing_col(co, n):
    k = 0.5 + 0.5 * math.sin(co.x * 40.0 + co.y * 20.0)
    return nh.lerp(WING, VEIN, 0.4 * nh.smoothstep(0.85, 0.97, k))


def build():
    body = nh.MeshBuilder()
    body.add(nh.ellipsoid((0, -0.36, 0.02), (0.09, 0.07, 0.085), subdivisions=3), BODY)      # head
    body.add(nh.ellipsoid((0, -0.17, 0.04), (0.11, 0.15, 0.11), subdivisions=3), BODY)      # thorax
    body.add(cc.limb([(0, -0.03, 0.03), (0, 0.02, 0.02)], [0.03, 0.025]), BODY)               # waist
    body.add(nh.ellipsoid((0, 0.20, 0.0), (0.10, 0.20, 0.09), subdivisions=3), BODY)        # abdomen
    fused = body.fuse(voxel=0.012, smooth=4)
    fused = cc.sculpt(fused, cc.fuzz_disp(0.006, 45.0))

    def paint(co, n):
        c = BODY
        if -0.3 < co.y < -0.02:
            c = fuzzy(BODY, HAIR)(co, n)                      # hairy thorax
        if co.y > 0.05:
            band = 0.5 + 0.5 * math.sin((co.y - 0.05) * 38.0)
            c = nh.lerp(BODY, HAIR, 0.45 * nh.smoothstep(0.7, 0.9, band))
        return cc.mottle(c, co, 0.1, 30.0)
    mb = nh.MeshBuilder()
    mb.add(fused, paint)
    for sx in (1, -1):
        mb.add(nh.ellipsoid((sx * 0.07, -0.38, 0.03), (0.035, 0.05, 0.06), subdivisions=2), EYE)
        mb.add(nh.tube([(sx * 0.03, -0.42, 0.07), (sx * 0.08, -0.52, 0.14), (sx * 0.14, -0.64, 0.12)],
                       [0.008, 0.007, 0.005], sides=5), LEG)
        mb.add(wing(sx, (sx * 0.06, -0.22, 0.12), 0.55, 0.16, 18, 18), wing_col)
        mb.add(wing(sx, (sx * 0.06, -0.12, 0.10), 0.40, 0.11, 28, 12), wing_col)
        for k, (y, out, back) in enumerate(((-0.22, 0.20, -0.12), (-0.15, 0.24, 0.05), (-0.08, 0.26, 0.25))):
            hip = Vector((sx * 0.07, y, -0.04))
            knee = hip + Vector((sx * out * 0.6, back * 0.4, -0.06))
            foot = hip + Vector((sx * out, back, -0.16))
            mb.add(nh.tube([hip, knee, foot], [0.014, 0.011, 0.006], sides=5), LEG)
            if k == 2:      # branched hairs on the hind legs
                for j in range(5):
                    p = knee.lerp(foot, j / 5)
                    mb.add(cc.cone(p, p + Vector((sx * 0.03, 0.01, -0.01)), 0.004, sides=3), HAIR)
    obj = mb.to_object("Melittosphex", roughness=0.5)
    cc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Melittosphex", background=(0.22, 0.32, 0.20), views=((35, 25), (0, 80)), size=640)
