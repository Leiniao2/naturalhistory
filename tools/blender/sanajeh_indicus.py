"""
Procedural Sanajeh indicus (Late Cretaceous snake, Lameta Formation, Gujarat, India) for
map colonies. Built on nh_pal_snake.py.

A stout, 3.5-metre primitive snake (related to the madtsoiids) with a broad,
blunt, relatively rigid head - it could not gape as wide as modern snakes - and a thick
body tapering to a short tail. It was found coiled around a sauropod egg beside a
hatchling. Pattern: dark olive-brown with rusty saddles, darker flank spots and a cream
belly (colours conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sanajeh_indicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sanajeh.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_snake as sn  # noqa: E402

SPEC = sn.Spec(
    name="Sanajeh",
    length=2.4, girth=0.085, head_len=0.15, head_w=0.08, neck=0.7, tail=0.14,
    base=(0.34, 0.30, 0.18), saddle=(0.52, 0.26, 0.12), belly=(0.86, 0.80, 0.62),
    saddles=16, saddle_w=0.4, side_spots=0.55, head_col=(0.28, 0.24, 0.15),
)

if __name__ == "__main__":
    sn.main(SPEC, ground=(0.62, 0.52, 0.36))
