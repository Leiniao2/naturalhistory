"""
Procedural Trinucleus seticornis (= Tretaspis seticornis, late Ordovician
trinucleid trilobite of Scandinavia) for map colonies.

Compared with T. fimbriatus: a smaller, more domed shell; the fringe slopes
down as a steeper brim and is split by a raised ridge (the 'girder') into two
outer and two inner pit rows; small eye tubercles on the cheeks (no lenses)
and a median tubercle on the glabella; very long, slender genal spines
('seticornis' = bristle-horned). Cooler grey-olive. Body built by nh_trinucleus.

Usage:
  blender --background --python tools/blender/trinucleus_seticornis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TrinucleusSeticornis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_trinucleus  # noqa: E402

PARAMS = dict(
    name="TrinucleusSeticornis",
    shell=(0.44, 0.40, 0.31),
    shell_light=(0.66, 0.62, 0.50),
    axis=(0.36, 0.31, 0.22),
    groove=(0.18, 0.15, 0.10),
    pit=(0.09, 0.07, 0.05),
    fringe=(0.62, 0.58, 0.46),
    under=(0.36, 0.32, 0.25),
    ceph_w=0.40, ceph_l=0.42, fringe_w=0.11, fringe_w_side=0.08,
    thorax_w=0.25, thorax_w_back=0.20,
    pit_rows=(0.12, 0.32, 0.66, 0.86),   # E1, E2 | girder | I1, I2
    girder=0.49,
    pits_per_row=30,
    fringe_slope=0.03, fringe_droop=0.02,
    glabella_h=0.09, glabella_w=0.105, cheek_h=0.075,
    eye_tubercles=True, median_tubercle=True,
    spine_len=1.10, spine_r=0.021, spine_spread=0.16,
)

if __name__ == "__main__":
    nh_trinucleus.run(PARAMS)
