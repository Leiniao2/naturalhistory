"""
Procedural Lycosuchus vanderrieti (Middle Permian therocephalian, ~2 m) for map colonies.

A large early therocephalian, the top predator of the Karoo in the time of the
dinocephalians: a long, wolf-like body on fairly upright legs, a long, deep, narrow
snout and two pairs of long upper canines side by side (a replacement canine growing in
next to the working one). Dusky grey-brown with a dark back stripe and faint spots.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lycosuchus_vanderrieti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lycosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402

STRIPE = (0.16, 0.13, 0.11)


def paint(co, n, c):
    k = nh.smoothstep(0.03, 0.0, abs(co.x)) * nh.smoothstep(0.5, 0.9, n.z)
    return nh.lerp(c, STRIPE, 0.8 * k)


SPEC = pt.Spec(
    name="Lycosuchus",
    torso=[
        (-0.44, 0.42, 0.06, 0.07),
        (-0.36, 0.42, 0.105, 0.115),
        (-0.20, 0.415, 0.13, 0.135),
        (0.00, 0.415, 0.125, 0.13),
        (0.18, 0.41, 0.11, 0.115),
        (0.28, 0.40, 0.08, 0.08),
        (0.48, 0.32, 0.04, 0.04),
        (0.70, 0.22, 0.018, 0.018),
        (0.78, 0.19, 0.0, 0.0),
    ],
    head=[
        (-0.42, 0.46, 0.065, 0.072),
        (-0.53, 0.46, 0.062, 0.075),
        (-0.66, 0.44, 0.046, 0.064),
        (-0.78, 0.415, 0.034, 0.050),
        (-0.82, 0.41, 0.0, 0.0),
    ],
    jaw=[
        (-0.45, 0.365, 0.052, 0.026),
        (-0.66, 0.352, 0.036, 0.020),
        (-0.81, 0.356, 0.0, 0.0),
    ],
    teeth=[(-0.81, -0.77, 3, 0.02, 0.006, True), (-0.70, -0.52, 7, 0.011, 0.004, True)],
    fangs=[(0.030, -0.745, 0.375, 0.085, 0.010, 0.006), (0.033, -0.725, 0.375, 0.07, 0.009, 0.006)],
    fore=pt.Limb(y=-0.27, z=0.35, x=0.095, upper=0.17, lower=0.19, sprawl=0.3, r=0.045,
                 foot=(0.033, 0.048, 0.015), toe_len=0.04, toe_r=0.008),
    hind=pt.Limb(y=0.16, z=0.35, x=0.095, upper=0.18, lower=0.19, sprawl=0.25, r=0.052,
                 foot=(0.035, 0.055, 0.015), toe_len=0.042, toe_r=0.009),
    eye=(0.05, -0.60, 0.48, 0.017), nostril=(0.018, -0.81, 0.425),
    back=(0.30, 0.27, 0.23), flank=(0.48, 0.43, 0.36), belly=(0.80, 0.74, 0.64), mark=(0.22, 0.19, 0.16),
    pattern="spots", pattern_freq=30.0, pattern_amount=0.5, paint=paint,
    voxel=0.007, max_tris=10000, drop=0.02,
)

if __name__ == "__main__":
    pt.main(SPEC)
