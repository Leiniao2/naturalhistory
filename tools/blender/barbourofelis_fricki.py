"""
Procedural Barbourofelis fricki (Late Miocene of North America, a barbourofelid
"false sabre-tooth", about lion-sized) for map colonies.

The most extreme sabre-tooth plan of all: a short, very robust, low-slung body
with massively muscled forelimbs, short hind legs and a short tail, a short,
deep skull and the longest, most blade-like upper canines relative to skull
size of any cat-like predator, sheathed at rest by a deep bony flange on the
lower jaw. Coat a plain dark tawny-brown with a darker back line and pale belly
(the real coat is unknown). Built with nh_sabretooth.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/barbourofelis_fricki.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BarbourofelisFricki.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_sabretooth as st  # noqa: E402

SPEC = st.Spec(
    name="BarbourofelisFricki",
    withers=0.76, croup=0.70, length=1.02, girth=1.06,
    fore=1.18, hind=1.02, paw=1.0, neck=1.05, head=1.16, muzzle=-0.01,
    sabre=0.27, sabre_depth=0.032, sabre_flat=0.30,
    tail=((0, 0.0, 0.0), (0, 0.08, -0.04), (0, 0.13, -0.09)), tail_r=(0.05, 0.042, 0.032),
    coat=(0.56, 0.42, 0.27), coat_dark=(0.38, 0.27, 0.16), pale=(0.82, 0.74, 0.60),
    spots=0.0, tail_tip=0.3,
)


if __name__ == "__main__":
    st.main(SPEC, ground=(0.48, 0.47, 0.30))
