"""
Procedural Smilodon gracilis (the earliest and smallest Smilodon species, North
America, latest Pliocene to middle Pleistocene, roughly jaguar-sized at ~55-100 kg)
for map colonies.

The same machairodont plan as S. populator in a smaller, lighter build: high
shoulders over a sloping back, a thick neck, strong forelimbs, short hind legs
and a short bobbed tail, but slimmer limbs and trunk and smaller paws. The short,
broad face carries long, laterally flattened upper canines that reach below the
chin, slightly slenderer than in the bigger species. Built with nh_sabretooth.py.
Coat: plain tawny-brown with a darker back line and a pale belly, throat and
muzzle (the real coat pattern is unknown; a plain coat is the conservative
choice).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/smilodon_gracilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SmilodonGracilis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_sabretooth as st  # noqa: E402

SPEC = st.Spec(
    name="SmilodonGracilis",
    withers=0.86, croup=0.74, length=1.0, girth=0.90,
    fore=0.98, hind=0.90, paw=0.86, neck=0.94, head=1.14,
    sabre=0.20, sabre_depth=0.026, sabre_flat=0.34,
    tail=((0, 0.0, 0.0), (0, 0.09, -0.04), (0, 0.15, -0.10)), tail_r=(0.05, 0.042, 0.032),
    coat=(0.64, 0.50, 0.33), coat_dark=(0.49, 0.37, 0.24), pale=(0.86, 0.80, 0.67),
    spots=0.0, tail_tip=0.3,
)


if __name__ == "__main__":
    st.main(SPEC, ground=(0.48, 0.47, 0.30))
