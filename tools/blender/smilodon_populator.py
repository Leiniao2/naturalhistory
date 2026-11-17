"""
Procedural Smilodon populator (Pleistocene South America, the largest sabre-toothed
cat, ~220-400 kg) for map colonies.

A massively built cat caught mid-stride: high, heavy shoulders over a sloping back
that falls to a lower croup, a deep chest, a thick muscular neck, very powerful
forelimbs with broad paws, comparatively short hind legs and a short bobbed tail.
The broad, short-faced head carries the long, laterally flattened upper canines
well below the chin, sheathed at the root by a tall upper lip. Built with
nh_sabretooth.py.
Coat: plain tawny-brown with a darker back line, pale belly, throat and muzzle,
and faint small spots on the flanks and legs. The coat pattern is unknown; the
faint spotting is a reconstruction choice.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/smilodon_populator.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SmilodonPopulator.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_sabretooth as st  # noqa: E402

SPEC = st.Spec(
    name="SmilodonPopulator",
    withers=0.90, croup=0.74, length=1.0, girth=1.08,
    fore=1.22, hind=1.08, paw=0.92, neck=1.12, head=1.22,
    sabre=0.21, sabre_depth=0.03, sabre_flat=0.34,
    tail=((0, 0.0, 0.0), (0, 0.09, -0.04), (0, 0.15, -0.10)), tail_r=(0.058, 0.048, 0.036),
    coat=(0.60, 0.46, 0.30), coat_dark=(0.45, 0.33, 0.21), pale=(0.84, 0.77, 0.64),
    spot=(0.44, 0.32, 0.20), spots=0.35, tail_tip=0.3,
)


if __name__ == "__main__":
    st.main(SPEC, ground=(0.50, 0.47, 0.30))
