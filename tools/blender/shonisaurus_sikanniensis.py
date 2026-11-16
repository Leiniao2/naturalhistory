"""
Procedural Shonisaurus sikanniensis (Late Triassic shastasaurid ichthyosaur, reassigned
to Shastasaurus in 2011) for the map (Swim style).

The longest marine reptile known from a reasonably complete skeleton, about 21 m, from
the Pardonet Formation of British Columbia. Longer and more slender than S. popularis:
a very long, narrow, toothless rostrum, a deep chest that tapers into a long, slim
trunk and tail, a small eye with its sclerotic ring, four fairly short, narrow
flippers (the hind pair only a little smaller), no dorsal fin and a long tail with a
weak tail bend ending in a small crescent fluke.

Built with the shared ichthyosaur recipe (nh_ichthyosaur.py): lofted body, flipper and
fluke slabs fused into one seamless surface (nh_model.MeshBuilder.fuse), then
repainted with countershading (dark blue-slate back, a faint darker flank band, a
pale belly) and light mottling. Colours are speculative. Crisp eyes, sclerotic plates
and nostrils on top.

Usage:
  blender --background --python tools/blender/shonisaurus_sikanniensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ShonisaurusSikanniensis.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 2 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402

SPEC = ich.IchthyosaurSpec(
    name="ShonisaurusSikanniensis",
    voxel=0.014, max_tris=20000,
    snout_len=0.37, snout_r=0.034, snout_tip_r=0.006,
    eye_r=0.029, head_h=0.078, head_w=0.066,
    body_h=0.140, belly_k=1.30, body_w=0.125, y_max=-0.32, rear_k=0.74,
    y_ped=0.74, ped_h=0.033, ped_w=0.022,
    tail_bend=10.0, y_bend=0.62,
    fore=(-0.44, 0.27, 0.075), fore_shape=0.10, fore_droop=34.0, fore_sweep=42.0,
    hind=(0.08, 0.23, 0.065), hind_shape=0.10, hind_droop=36.0, hind_sweep=46.0,
    dorsal=None,
    fluke_up=0.13, fluke_down=0.20, fluke_sweep=0.16, fluke_chord=0.08, fluke_lunate=0.05,
    back=(0.11, 0.15, 0.20), flank=(0.33, 0.39, 0.45), belly=(0.84, 0.86, 0.85),
    fin=(0.09, 0.12, 0.16), mottle=(0.20, 0.25, 0.31), mottle_k=0.25,
    stripe=(0.16, 0.20, 0.26), shade_line=-0.25, ring=(0.72, 0.70, 0.60), ring_plates=12,
)


def build():
    return ich.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "ShonisaurusSikanniensis", background=(0.05, 0.18, 0.24),
           views=((35, 25), (-90, 4), (90, 4), (30, 62), (180, -40)))
