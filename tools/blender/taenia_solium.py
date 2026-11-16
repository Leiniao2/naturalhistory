"""
Procedural low-poly pork tapeworm (Taenia solium) for colony instancing.

The ribbon-like strobila (a few metres and up to about a thousand proglottids in
life; here ~120) lies coiled in a flat spiral, widest and oldest segments on
the outside. Behind the slender neck the proglottids are tiny and much wider
than long, become squarish cream mature segments, then longer, warmer gravid
ones whose egg-filled, branched uterus shows darker down the midline. Each
proglottid is narrower at the front than the back, so the margins are finely
saw-toothed. The neck rears up from the centre of the coil so the (enlarged)
scolex is visible: a knob with four cup-shaped suckers and a rostellum armed
with a double crown of amber hooks. Pale ivory/cream vertex colours.

Drift style: pivot at the body centre.

Usage:
  blender --background --python tools/blender/taenia_solium.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PorkTapeworm.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_tapeworm as tw  # noqa: E402

SEED = 4
COUNT = 160
NECK_LEN, NECK_W = 0.22, 0.025
SCOLEX_R = 0.055
# (length, width) of the first, first mature and first gravid proglottid
START, MATURE, GRAVID = (0.008, 0.03), (0.06, 0.075), (0.11, 0.068)


def build():
    progs = tw.chain(COUNT, START, MATURE, GRAVID, mature_at=0.35, gravid_at=0.7, end_shrink=0.1)
    width, total = tw.width_lookup(progs, NECK_LEN, NECK_W)
    pts = tw.tangle_path(total, width, radius=0.6, curl=0.35, bias=0.14, seed=SEED)
    pts = tw.drape(pts, width, lambda s: max(width(s) * 0.13, 0.008))
    pts = tw.lift_front(pts, height=0.22, over=0.45)
    path = tw.Path(pts)

    mb = nh.MeshBuilder()
    mb.add(tw.strobila(path, progs, NECK_LEN, NECK_W, tw.taenia_paint(seed=SEED),
                       thickness=0.13, rings=(0.0, 0.94), sides=6, bank=0.15))
    p, t = path.at(0.0)
    for bm, c in tw.scolex_taenia(p - t * SCOLEX_R * 0.6, -t, SCOLEX_R, hooks=13):
        mb.add(bm, c)
    obj = mb.to_object("PorkTapeworm", roughness=0.45)
    tw.center_object(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "PorkTapeworm", views=((35, 45), (0, 85), (-60, 15)))
