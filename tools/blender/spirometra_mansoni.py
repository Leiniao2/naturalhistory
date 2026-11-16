"""
Procedural low-poly Spirometra mansoni for colony instancing: a pseudophyllidean
tapeworm of the small intestine of cats and dogs, whose plerocercoid larva (the
sparganum) lives in the muscles of frogs, snakes and other vertebrates.

The long ribbon (here ~110 proglottids) lies folded back and forth in loose
loops. All the proglottids are much wider than long; the mature and gravid ones
each carry the characteristic spirally coiled uterus as a dark brown rosette in
the middle of the upper face, so the folded ribbon is beaded with a line of dark
spots. The front end rears up: a slender neck and an elongate, spoon-shaped
scolex with a slit-like bothrium (sucking groove) along each flat face instead
of suckers and hooks. Pale ivory vertex colours.

Drift style: pivot at the body centre.

Usage:
  blender --background --python tools/blender/spirometra_mansoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Spirometra.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_tapeworm as tw  # noqa: E402

SEED = 6
COUNT = 110
NECK_LEN, NECK_W = 0.26, 0.03
SCOLEX_R = 0.042
# (length, width) of the first, first mature and first gravid proglottid: all wider than long
START, MATURE, GRAVID = (0.008, 0.035), (0.042, 0.12), (0.05, 0.13)

BODY = (0.95, 0.92, 0.80)
IMMATURE = (0.92, 0.90, 0.82)
ROSETTE = (0.22, 0.12, 0.07)     # egg-filled spiral uterus
ROSETTE_RIM = (0.55, 0.38, 0.24)

# flat ribbon cross-section with a vertex on the top midline for the rosette
SECTION = [(1.0, 0.0), (0.55, 0.92), (0.0, 1.0), (-0.55, 0.92), (-1.0, 0.0),
           (-0.55, -0.92), (0.55, -0.92)]


def paint(i, prog, u, v, top):
    l, w, stage = prog
    c = nh.lerp(IMMATURE, BODY, min(1.0, stage))
    if stage >= 0.8 and top > 0 and 0.2 < u < 0.8:
        k = min(1.0, (stage - 0.8) / 0.4)
        if abs(v) < 0.1:
            c = nh.lerp(c, ROSETTE, k)
        elif abs(v) < 0.6:
            c = nh.lerp(c, ROSETTE_RIM, 0.5 * k)
    if u < 0.02:
        c = tuple(x * tw.GROOVE_SHADE for x in c)
    jitter = 1.0 + 0.035 * noise.noise(Vector((i * 0.41, SEED, u)))
    return tuple(min(1.0, x * jitter) for x in c)


def build():
    progs = tw.chain(COUNT, START, MATURE, GRAVID, mature_at=0.3, gravid_at=0.6, end_shrink=0.05)
    width, total = tw.width_lookup(progs, NECK_LEN, NECK_W)
    pts = tw.meander_path(total, width, lane=0.6, gap=0.045, wiggle=0.025, seed=SEED)
    pts = tw.warp(pts, amount=0.12, freq=1.5, seed=SEED)
    pts = tw.drape(pts, width, lambda s: max(width(s) * 0.15, 0.008))
    pts = tw.lift_front(pts, height=0.2, over=0.4)
    path = tw.Path(pts)

    mb = nh.MeshBuilder()
    mb.add(tw.strobila(path, progs, NECK_LEN, NECK_W, paint, thickness=0.15, section=SECTION,
                       stage_rings=lambda st: (0.0, 0.5, 0.94) if st >= 0.8 else (0.0, 0.94),
                       front_narrow=0.9, bank=0.1))
    p, t = path.at(0.0)
    for bm, c in tw.scolex_bothria(p - t * SCOLEX_R * 0.2, -t, SCOLEX_R, length=3.0, color=BODY):
        mb.add(bm, c)
    obj = mb.to_object("Spirometra", roughness=0.45)
    tw.center_object(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Spirometra", views=((35, 45), (0, 85), (-60, 15)))
