"""
Procedural Shonisaurus popularis (Late Triassic shastasaurid ichthyosaur) for the map
(Swim style).

A giant of about 15 m from the Late Triassic of Nevada, and a very different animal
from the later dolphin-shaped ichthyosaurs: a long, deep, rotund, almost whale-like
trunk, a long, narrow rostrum with a smooth (toothless) tip, a relatively small eye
with its sclerotic ring, four long, narrow flippers of nearly equal size (fore and
hind), only a small, low dorsal fin (its presence is uncertain), and a long tail with
just a gentle tail bend ending in a modest crescent fluke whose lower, bone-supported
lobe is the larger.

Built with the shared ichthyosaur recipe (nh_ichthyosaur.py): lofted body, flipper,
dorsal and fluke slabs fused into one seamless surface (nh_model.MeshBuilder.fuse),
then repainted with countershading (dark brown-grey back, warm grey flanks, pale
belly) and blotchy mottling. Colours are speculative. Crisp eyes, sclerotic plates and
nostrils on top.

Usage:
  blender --background --python tools/blender/shonisaurus_popularis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ShonisaurusPopularis.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 2 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402

SPEC = ich.IchthyosaurSpec(
    name="ShonisaurusPopularis",
    voxel=0.015, max_tris=20000,
    snout_len=0.31, snout_r=0.040, snout_tip_r=0.007,
    eye_r=0.034, head_h=0.090, head_w=0.078,
    body_h=0.205, belly_k=1.22, body_w=0.190, y_max=-0.12, rear_k=0.88,
    y_ped=0.70, ped_h=0.032, ped_w=0.022,
    tail_bend=12.0, y_bend=0.58,
    fore=(-0.40, 0.36, 0.085), fore_shape=0.12, fore_droop=34.0, fore_sweep=40.0,
    hind=(0.14, 0.33, 0.080), hind_shape=0.12, hind_droop=36.0, hind_sweep=44.0,
    dorsal=(0.04, 0.065, 0.26), dorsal_rake=0.55,
    fluke_up=0.16, fluke_down=0.24, fluke_sweep=0.19, fluke_chord=0.09, fluke_lunate=0.06,
    back=(0.23, 0.18, 0.13), flank=(0.50, 0.42, 0.33), belly=(0.87, 0.81, 0.70),
    fin=(0.17, 0.13, 0.10), mottle=(0.33, 0.26, 0.19), mottle_k=0.55,
    shade_line=-0.30, ring=(0.74, 0.68, 0.54), ring_plates=12,
)


def build():
    return ich.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "ShonisaurusPopularis", background=(0.05, 0.18, 0.24),
           views=((35, 25), (-90, 4), (90, 4), (30, 62), (180, -40)))
