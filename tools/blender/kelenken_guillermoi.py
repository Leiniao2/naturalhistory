"""
Procedural Kelenken guillermoi (Middle Miocene of Patagonia) for map colonies:
the terror bird with the largest known bird skull, about 71 cm long.

A tall, long-legged flightless predator with an enormous, narrow, hooked beak
on a stout neck, a deep body with tiny wings and long, slender lower legs that
suggest a fast runner. Shown dark brown with a barred, paler neck and belly
(a reconstruction choice). Built with nh_neo_bigbird.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kelenken_guillermoi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/KelenkenGuillermoi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_bigbird as q  # noqa: E402

SPEC = q.Spec(
    name="KelenkenGuillermoi",
    hip=1.15, body=(0.22, 0.42, 0.27), body_tilt=14, leg_r=0.052,
    neck=((0, -0.30, 0.22), (0, -0.36, 0.58), (0, -0.46, 0.86)), neck_r=(0.12, 0.09, 0.08),
    head_r=0.14, beak_len=0.50, beak_h=0.30, hook=1.0, wing=0.22, tail=0.20,
    feather=(0.30, 0.22, 0.15), dark=(0.14, 0.10, 0.07), pale=(0.66, 0.58, 0.46),
    head_col=(0.42, 0.34, 0.25), beak_col=(0.72, 0.58, 0.32), leg_col=(0.50, 0.44, 0.30), stride=0.34,
)

if __name__ == "__main__":
    q.main(SPEC)
