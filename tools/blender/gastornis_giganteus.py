"""
Procedural Gastornis giganteus (formerly Diatryma; North America, late Paleocene
to early Eocene, ~56-45 Ma) for map colonies. Built with nh_pal_bird.py.

A giant flightless bird about 2 m tall and up to ~175 kg, a relative of ducks and
geese. Its enormous, deep, parrot-like beak on a big head and thick neck was once
thought to kill small horses, but bite mechanics, the lack of a hooked tip and
calcium isotopes suggest it mostly cracked seeds, nuts and tough plants. Tiny
vestigial wings, stout legs and a short tail. Plumage: shaggy dark brown with a
paler neck (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/gastornis_giganteus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GastornisGiganteus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_bird as nb  # noqa: E402

SPEC = nb.Spec(
    name="GastornisGiganteus",
    body=(0.26, 0.42, 0.3), body_z=0.88, body_pitch=-12,
    neck_len=0.48, neck_r=0.13, neck_lean=18, head_r=0.17,
    beak_len=0.3, beak_h=0.32, beak_w=0.15, beak_hook=0.12,
    leg_len=0.62, leg_r=0.075, thigh_r=0.14, toe_len=0.13,
    wing=0.08, tail=0.1,
    plumage=(0.27, 0.21, 0.15), back=(0.20, 0.15, 0.11), head_col=(0.40, 0.33, 0.25),
    beak_col=(0.78, 0.70, 0.48), leg_col=(0.42, 0.37, 0.30), eye_r=0.022, shaggy=1.0,
    voxel=0.014, max_tris=12000,
)

if __name__ == "__main__":
    nb.main(SPEC)
