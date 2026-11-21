"""
Procedural Dicynodon lacerticeps (Late Permian dicynodont, ~1.2 m) for map colonies.

The 'two dog-tooth' anomodont that names the whole group: a stout, barrel-bodied, short-
tailed plant eater with a short, high head ending in a sharp horny beak, and a single pair
of tusks pointing down from the upper jaw. Strong forelimbs held out to the side, hind
limbs more upright. Earthy brown with a darker beak and paler belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dicynodon_lacerticeps.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dicynodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402

BEAK = (0.18, 0.15, 0.11)


def paint(co, n, c):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.60, -0.64, co.y) * nh.smoothstep(0.29, 0.24, co.z))


SPEC = pt.Spec(
    name="Dicynodon",
    torso=[
        (-0.40, 0.23, 0.08, 0.08),
        (-0.30, 0.235, 0.14, 0.14),
        (-0.10, 0.245, 0.19, 0.17),
        (0.10, 0.245, 0.185, 0.165),
        (0.26, 0.23, 0.14, 0.13),
        (0.36, 0.20, 0.065, 0.065),
        (0.46, 0.165, 0.025, 0.025),
        (0.50, 0.155, 0.0, 0.0),
    ],
    head=[
        (-0.40, 0.29, 0.11, 0.10),
        (-0.49, 0.30, 0.105, 0.10),
        (-0.57, 0.28, 0.08, 0.085),
        (-0.635, 0.245, 0.05, 0.06),
        (-0.66, 0.225, 0.0, 0.0),
    ],
    fangs=[(0.05, -0.595, 0.23, 0.065, 0.014, -0.012)],
    fore=pt.Limb(y=-0.22, z=0.17, x=0.14, upper=0.12, lower=0.12, sprawl=0.85, r=0.048,
                 foot=(0.045, 0.048, 0.016), toe_len=0.032, toe_r=0.011, claw=1.4),
    hind=pt.Limb(y=0.22, z=0.18, x=0.12, upper=0.12, lower=0.13, sprawl=0.5, r=0.054,
                 foot=(0.042, 0.054, 0.016), toe_len=0.032, toe_r=0.011),
    eye=(0.085, -0.52, 0.34, 0.021), nostril=(0.035, -0.62, 0.30),
    back=(0.40, 0.31, 0.21), flank=(0.56, 0.45, 0.32), belly=(0.82, 0.75, 0.60), mark=(0.28, 0.21, 0.14),
    pattern="mottle", pattern_freq=8.0, pattern_amount=0.3, paint=paint,
    voxel=0.007, max_tris=9000,
)

if __name__ == "__main__":
    pt.main(SPEC)
