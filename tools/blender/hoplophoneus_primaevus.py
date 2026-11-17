"""
Procedural Hoplophoneus primaevus (a nimravid "false sabre-tooth", North America,
early Oligocene, ~33-30 Ma) for map colonies. Built with nh_sabretooth.py.

Nimravids were cat-like carnivores that evolved sabre teeth independently of the
true cats. Hoplophoneus was leopard-sized but lower and longer-bodied, with short
powerful legs, a long tail, a short face, long flattened upper canines and a
bony flange on the lower jaw that sheathed them. Coat: tawny with faint dark spots
(unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/hoplophoneus_primaevus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HoplophoneusPrimaevus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_sabretooth as st  # noqa: E402

SPEC = st.Spec(
    name="HoplophoneusPrimaevus",
    withers=0.70, croup=0.68, length=1.18, girth=0.82,
    fore=0.95, hind=0.88, paw=0.85, neck=0.85, head=1.0,
    sabre=0.17, sabre_depth=0.022, sabre_flat=0.36,
    tail=((0, 0.0, 0.0), (0, 0.16, -0.07), (0, 0.32, -0.2), (0, 0.44, -0.38), (0, 0.5, -0.52)),
    tail_r=(0.045, 0.04, 0.036, 0.032, 0.028),
    coat=(0.62, 0.47, 0.30), coat_dark=(0.44, 0.32, 0.19), pale=(0.86, 0.79, 0.64),
    spot=(0.32, 0.23, 0.14), spots=0.35, tail_tip=0.5,
)


if __name__ == "__main__":
    st.main(SPEC, ground=(0.40, 0.44, 0.28))
