"""
Procedural Trinucleus fimbriatus (Ordovician trinucleid trilobite, Wales / Welsh
Borderland) for map colonies.

Type species of Trinucleus: blind, with a broad, gently sloping fringe carrying
several evenly spaced concentric rows of pits, a strongly inflated pear-shaped
glabella, no eye tubercles, six thoracic segments, a small triangular pygidium
and long, fairly robust genal spines reaching well behind the tail.
Warm brown. Body built by nh_trinucleus.

Usage:
  blender --background --python tools/blender/trinucleus_fimbriatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TrinucleusFimbriatus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_trinucleus  # noqa: E402

PARAMS = dict(
    name="TrinucleusFimbriatus",
    ceph_w=0.44, ceph_l=0.44, fringe_w=0.12, fringe_w_side=0.10,
    pit_rows=(0.15, 0.38, 0.61, 0.84),   # four even rows on a broad flat fringe
    pits_per_row=34,
    fringe_slope=0.018,
    glabella_h=0.10, glabella_w=0.12, cheek_h=0.055,
    spine_len=0.92, spine_r=0.028, spine_spread=0.10,
)

if __name__ == "__main__":
    nh_trinucleus.run(PARAMS)
