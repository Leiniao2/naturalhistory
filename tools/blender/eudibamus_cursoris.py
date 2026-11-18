"""
Procedural Eudibamus cursoris (Early Permian bolosaurid, ~25 cm) running, for map colonies.

The oldest known two-legged runner, from the Bromacker quarry of Germany: a small, slender
plant-eating reptile with a short, deep head, long hind legs (far longer than the arms) and
long feet that ran upright on its toes, short forelimbs held clear of the ground and a very
long, whip-like tail as a counterbalance. Shown sprinting on its hind legs.
Light sandy-brown with a darker stripe along the back and a pale belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/eudibamus_cursoris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eudibamus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402


def paint(co, n, c):
    return nh.lerp(c, (0.30, 0.20, 0.12), 0.7 * nh.smoothstep(0.03, 0.015, abs(co.x)) * nh.smoothstep(0.4, 0.8, n.z))


SPEC = pt.Spec(
    name="Eudibamus",
    torso=[   # body pitched up toward the shoulders, the tail held out behind
        (-0.30, 0.50, 0.04, 0.04),
        (-0.24, 0.48, 0.065, 0.065),
        (-0.12, 0.45, 0.08, 0.075),
        (0.00, 0.42, 0.08, 0.075),
        (0.10, 0.40, 0.065, 0.06),
        (0.30, 0.38, 0.03, 0.03),
        (0.60, 0.36, 0.016, 0.016),
        (0.95, 0.33, 0.006, 0.006),
        (1.05, 0.32, 0.0, 0.0),
    ],
    head=[
        (-0.29, 0.53, 0.045, 0.05),
        (-0.36, 0.54, 0.045, 0.05),
        (-0.43, 0.525, 0.035, 0.04),
        (-0.48, 0.51, 0.02, 0.026),
        (-0.495, 0.505, 0.0, 0.0),
    ],
    fore=pt.Limb(y=-0.20, z=0.44, x=0.06, upper=0.07, lower=0.07, sprawl=0.3, r=0.015, grounded=False,
                 foot=(0.012, 0.016, 0.006), toe_len=0.02, toe_r=0.004, claw=0.6),
    hind=pt.Limb(y=0.06, z=0.40, x=0.07, upper=0.18, lower=0.21, sprawl=0.1, swing=-0.06, r=0.032,
                 muscle=1.3, foot=(0.018, 0.06, 0.010), toe_len=0.05, toe_r=0.006, toe_fan=40, toe_yaw=0),
    eye=(0.04, -0.38, 0.555, 0.014), nostril=(0.012, -0.49, 0.52),
    back=(0.56, 0.42, 0.26), flank=(0.70, 0.56, 0.36), belly=(0.90, 0.84, 0.70), mark=(0.30, 0.20, 0.12),
    pattern="none", paint=paint, voxel=0.004, max_tris=7000, drop=0.08,
    preview=dict(views=((35, 22), (-90, 6), (25, 65))),
)

if __name__ == "__main__":
    pt.main(SPEC)
