"""
Procedural low-poly beef tapeworm (Taenia saginata) for colony instancing.

Longer than the pork tapeworm (commonly 4-10 m, around a thousand or more
proglottids; here ~210), so the ribbon lies in a bigger, denser tangle of
loops. Behind the slender neck the proglottids are tiny and wider than long,
become squarish mature segments, and the gravid ones at the end are long and
narrow (several times longer than wide), warmer in colour from the egg-filled
uterus. Margins are saw-toothed where each proglottid's front edge is narrower
than the back of the one before. The neck rears up out of the tangle so the
(enlarged) scolex shows: four cup-shaped suckers and NO rostellum or hooks
(the "unarmed" tapeworm), just a shallow apical dimple. Paler, whiter ivory
than T. solium.

Drift style: pivot at the body centre.

Usage:
  blender --background --python tools/blender/taenia_saginata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BeefTapeworm.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_tapeworm as tw  # noqa: E402

SEED = 9
COUNT = 210
NECK_LEN, NECK_W = 0.24, 0.024
SCOLEX_R = 0.05
# (length, width) of the first, first mature and first gravid proglottid
START, MATURE, GRAVID = (0.007, 0.026), (0.05, 0.068), (0.13, 0.05)
BODY = (0.96, 0.94, 0.86)
GRAVID_COL = (0.93, 0.88, 0.72)


def build():
    progs = tw.chain(COUNT, START, MATURE, GRAVID, mature_at=0.3, gravid_at=0.62, end_shrink=0.05)
    width, total = tw.width_lookup(progs, NECK_LEN, NECK_W)
    pts = tw.spiral_path(total, width, r0=0.1, gap=-0.004, seed=SEED)
    pts = tw.warp(pts, amount=0.16, freq=1.3, seed=SEED)
    pts = tw.drape(pts, width, lambda s: max(width(s) * 0.13, 0.008))
    pts = tw.lift_front(pts, height=0.24, over=0.5)
    path = tw.Path(pts)

    mb = nh.MeshBuilder()
    paint = tw.taenia_paint(seed=SEED, gravid=GRAVID_COL, cream=BODY)
    mb.add(tw.strobila(path, progs, NECK_LEN, NECK_W, paint, thickness=0.13, rings=(0.0, 0.94),
                       sides=6, bank=0.15))
    p, t = path.at(0.0)
    for bm, c in tw.scolex_taenia(p - t * SCOLEX_R * 0.6, -t, SCOLEX_R, hooks=0, color=BODY):
        mb.add(bm, c)
    obj = mb.to_object("BeefTapeworm", roughness=0.45)
    tw.center_object(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "BeefTapeworm", views=((35, 45), (0, 85), (-60, 15)))
