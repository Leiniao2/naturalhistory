"""
Procedural Hupehsuchus nanchangensis (Early Triassic hupehsuchian, ~1 m) for map colonies
(Swim style).

A strange early marine reptile from Hubei, China, about 248 million years ago, a close
relative of the ichthyosaurs. Its long, flattened, toothless snout had grooved jaw edges
and a loose, stretchy throat, and it is thought to have gulped and strained small prey
from the water much like a baleen whale. A spindle-shaped body roofed by a double layer
of bony plates along the back, paddle-like limbs and a long swimming tail. Built with
the shared Triassic tetrapod recipe (nh_tri_tetrapod.py) plus crisp dorsal plates and
a pale grooved jaw rim. Painted brown-grey with a pale belly (speculative). Faces -Y,
pivot at the body centre.

Usage:
  blender --background --python tools/blender/hupehsuchus_nanchangensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hupehsuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.25) / 0.75)
    return 0.10 * s * s


AXIS = [
    (-1.00, -0.004, 0.024, 0.008),
    (-0.94, -0.002, 0.034, 0.012),
    (-0.84, 0.000, 0.040, 0.018),
    (-0.74, 0.004, 0.044, 0.026),
    (-0.66, 0.008, 0.050, 0.038),
    (-0.58, 0.012, 0.050, 0.044),
    (-0.48, 0.016, 0.070, 0.062),
    (-0.32, 0.020, 0.100, 0.086),
    (-0.12, 0.020, 0.108, 0.092),
    (0.06, 0.016, 0.090, 0.078),
    (0.22, 0.010, 0.056, 0.054),
    (0.42, 0.004, 0.032, 0.040, sway(0.42)),
    (0.64, 0.000, 0.018, 0.028, sway(0.64)),
    (0.84, -0.002, 0.008, 0.016, sway(0.84)),
    (1.00, -0.002, 0.002, 0.003, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.07, -0.36, -0.04), (0.14, -0.36, -0.07), (0.18, -0.34, -0.08)],
               radii=[0.026, 0.021, 0.017], paddle=(0.070, 0.034, 125, -10))
HIND = tt.Limb(pts=[(0.06, 0.10, -0.03), (0.12, 0.14, -0.06), (0.15, 0.17, -0.065)],
               radii=[0.024, 0.019, 0.016], paddle=(0.055, 0.030, 145, -10))


def throat(co, n, c, spec):
    # pale grooved jaw rim and stretchy throat
    if co.y < -0.60:
        c = nh.lerp(c, (0.86, 0.80, 0.68), 0.5 * nh.smoothstep(0.1, -0.6, n.z))
    return c


SPEC = tt.TetrapodSpec(
    name="Hupehsuchus",
    axis=AXIS, power=2.4,
    blobs=[((0.0, -0.68, -0.030), (0.040, 0.13, 0.030), 4)],     # gular pouch
    limbs=[FORE, HIND],
    voxel=0.008, max_tris=9000,
    pivot="centre",
    mouth=(-1.0, -0.62, -0.004, 0.006, 0.004), mouth_min_x=0.2,
    eyes=(-0.62, 0.032, 0.014, (0.75, 0.60, 0.25)),
    nostrils=(-0.80, 0.014),
    plates=[dict(xs=(0.0,), y0=-0.52, y1=0.85, step=0.034, size=0.018, wide=1.6, taper=0.6, shrink=0.3,
                 follow=sway, col=(0.20, 0.17, 0.14), keel_col=(0.42, 0.36, 0.28), height=1.6),
            dict(xs=(0.034, -0.034), y0=-0.44, y1=0.25, step=0.040, size=0.014, kind="knob", height=0.6,
                 taper=0.4, col=(0.26, 0.22, 0.17))],
    back=(0.26, 0.24, 0.22), flank=(0.48, 0.45, 0.40), belly=(0.86, 0.84, 0.78),
    pattern=("mottle", (0.32, 0.29, 0.25), 9.0, 0.35),
    paint_extra=throat,
)

if __name__ == "__main__":
    tt.run(SPEC)
