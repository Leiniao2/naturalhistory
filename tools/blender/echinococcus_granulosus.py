"""
Procedural low-poly dog tapeworm (Echinococcus granulosus) for colony instancing:
a tiny tapeworm, only 3-6 mm long, that lives in its thousands in the small
intestine of dogs and other canids (its larva, the hydatid cyst, grows in the
liver and lungs of sheep, cattle and people).

Unlike the metre-long Taenia, it has just three proglottids, so it's modelled
uncoiled, lying in a gentle curve: an (enlarged) scolex with four cup-shaped
suckers and a rostellum crowned by a double ring of amber hooks, a short neck,
a small immature proglottid, a squarish mature one with its genital pore on the
margin, and a big, swollen, egg-filled gravid proglottid making up about half
the worm, its uterus with side pouches showing darker inside. Pale ivory
vertex colours.

Drift style: pivot at the body centre.

Usage:
  blender --background --python tools/blender/echinococcus_granulosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Echinococcus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_tapeworm as tw  # noqa: E402

SEED = 2
NECK_LEN, NECK_W = 0.16, 0.13
SCOLEX_R = 0.12
# (length, width, stage): immature, mature, gravid
PROGS = [(0.14, 0.17, 0.3), (0.26, 0.22, 1.0), (0.78, 0.30, 2.0)]
PORE = (0.45, 0.33, 0.22)
UTERUS = (0.66, 0.52, 0.30)     # egg-packed uterus showing through


def width_profile(stage, u):
    if stage < 2.0:
        # short, slightly barrel-sided segments, narrower at the front
        return 0.86 + 0.14 * nh.smoothstep(0.0, 0.8, u) + 0.04 * math.sin(math.pi * u)
    # swollen, elongate-ovoid gravid proglottid, rounded at the end
    return (0.8 + 0.28 * math.sin(math.pi * min(u / 0.9, 1.0)) ** 0.8) * (1.0 - nh.smoothstep(0.86, 1.0, u) * 0.85)


def paint(i, prog, u, v, top):
    l, w, stage = prog
    c = nh.lerp(tw.IVORY, tw.CREAM, min(1.0, stage))
    if stage >= 2.0:
        c = tw.GRAVID
        if top != 0 and 0.08 < u < 0.9:
            # median uterus with lateral pouches packed with eggs
            stem = math.exp(-(v / 0.22) ** 2)
            pouch = math.exp(-((abs(v) - 0.45) / 0.22) ** 2) * (0.5 + 0.5 * math.cos(u * math.tau * 4))
            eggs = 0.75 + 0.25 * noise.noise(Vector((u * 12, v * 6, SEED)))
            c = nh.lerp(c, UTERUS, min(1.0, (0.9 * stem + 0.75 * pouch) * eggs))
    if u < 0.02:
        c = tuple(x * tw.GROOVE_SHADE for x in c)
    return c


def build():
    progs = PROGS
    total = NECK_LEN + sum(p[0] for p in progs)
    ctrl = [Vector((0.0, -0.05, 0.0)), Vector((0.05, 0.35, 0.0)), Vector((-0.02, 0.75, 0.0)),
            Vector((-0.12, 1.1, 0.0)), Vector((-0.1, 1.5, 0.0))]
    pts = tw.catmull_rom(ctrl, per_span=40)
    path = tw.Path(pts)
    assert path.length > total, (path.length, total)

    mb = nh.MeshBuilder()
    rings = lambda st: [k / 12 for k in range(13)] if st >= 2.0 else [0.0, 0.25, 0.5, 0.75, 0.96]
    mb.add(tw.strobila(path, progs, NECK_LEN, NECK_W, paint, thickness=0.42, sides=12, squareness=0.8,
                       stage_rings=rings, width_profile=width_profile, round_end=False, neck_rings=6))
    # genital pores on the margins of the mature and gravid proglottids (alternating sides)
    s = NECK_LEN
    for i, (l, w, stage) in enumerate(progs):
        if stage >= 1.0:
            u = 0.5 if stage < 2 else 0.3
            p, t = path.at(s + l * u)
            side = t.cross(Vector((0, 0, 1))).normalized() * (1 if i % 2 else -1)
            wf = width_profile(stage, u)
            mb.add(nh.ellipsoid(p + side * (w * wf * 0.5 - 0.012), (0.02, 0.02, 0.02), subdivisions=1), PORE)
        s += l
    p, t = path.at(0.0)
    for bm, c in tw.scolex_taenia(p - t * SCOLEX_R * 0.55, -t, SCOLEX_R, hooks=16, hook_size=1.1):
        mb.add(bm, c)
    obj = mb.to_object("Echinococcus", roughness=0.45)
    tw.center_object(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Echinococcus", views=((35, 35), (0, 85), (-70, 15)))
