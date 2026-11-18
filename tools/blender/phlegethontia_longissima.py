"""
Procedural Phlegethontia longissima (Late Carboniferous of Mazon Creek, Illinois, a legless,
snake-like aistopod lepospondyl about 70 cm long) for map colonies (Ground style, slithering):
a small, pointed, lightly built head and an extremely long, thin, limbless body tapering to a
fine tail; dark brown above with pale crossbands and a cream belly. Pivot on the ground.
Built with nh_car_tetrapod, bent into an S-wave by nh_car_serpent. Faces -Y.

Usage:
  blender --background --python tools/blender/phlegethontia_longissima.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Phlegethontia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_car_serpent as sn  # noqa: E402

SPEC = tp.Spec(
    name="Phlegethontia",
    head_len=0.06, head_w=0.016, head_h=0.011, snout=0.35,
    neck_len=0.02, neck_r=0.012,
    trunk_len=1.05, trunk_r=0.014, trunk_h=0.95,
    tail_len=0.35, tail_r=0.011, tail_curve=0.25,
    leg_r=0.002, front=(0.004, 0.004), hind=(0.004, 0.004), foot=0.0, toes=0, body_z=0.0145,
    back=(0.24, 0.17, 0.10), flank=(0.38, 0.28, 0.17), belly=(0.86, 0.80, 0.62),
    pattern="bands", pattern_col=(0.85, 0.74, 0.46), pattern_scale=1.2,
    head_col=(0.28, 0.20, 0.12), iris=(0.80, 0.60, 0.15), eye_r=0.0055, eye_at=0.55, teeth=0,
    voxel=0.0035, max_tris=6000,
)

if __name__ == "__main__":
    sn.run(SPEC, amp=0.07, wavelength=0.5)
