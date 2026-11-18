"""
Procedural Smilosuchus gregorii (Late Triassic phytosaur, ~7 m) for map colonies.

One of the largest phytosaurs, from the Chinle Formation of Arizona about 225 million
years ago: a huge crocodile-like ambush predator of rivers and lakes. Phytosaurs differ
from true crocodiles in having their nostrils high on a mound just in front of the eyes
rather than at the snout tip; Smilosuchus also had a long, deep, crested snout lined with
big teeth. Low, sprawling, heavily armoured body with several rows of thick bony scutes,
short legs and a long, deep, side-flattened swimming tail. Built with the shared
Triassic tetrapod recipe (nh_tri_tetrapod.py). Painted dark olive with a paler snout
crest and a cream belly (speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/smilosuchus_gregorii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Smilosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.15) / 0.85)
    return 0.12 * s * s


AXIS = [
    (-1.00, 0.150, 0.026, 0.026),
    (-0.96, 0.152, 0.034, 0.034),
    (-0.90, 0.150, 0.026, 0.030),
    (-0.80, 0.152, 0.026, 0.034),
    (-0.70, 0.156, 0.030, 0.038),
    (-0.62, 0.164, 0.044, 0.046),
    (-0.56, 0.174, 0.062, 0.054),
    (-0.50, 0.180, 0.074, 0.058),
    (-0.44, 0.178, 0.072, 0.056),
    (-0.38, 0.176, 0.090, 0.068),
    (-0.25, 0.180, 0.130, 0.084),
    (-0.08, 0.184, 0.140, 0.088),
    (0.08, 0.182, 0.124, 0.080),
    (0.20, 0.172, 0.080, 0.066),
    (0.38, 0.160, 0.044, 0.060, sway(0.38)),
    (0.58, 0.150, 0.026, 0.046, sway(0.58)),
    (0.80, 0.140, 0.012, 0.028, sway(0.80)),
    (1.00, 0.135, 0.002, 0.004, sway(1.00)),
]

# rostral crest along the top of the snout and the raised nostril mound before the eyes
CREST = [(-0.97, 0.170, 0.012, 0.010), (-0.90, 0.185, 0.016, 0.022), (-0.80, 0.192, 0.016, 0.028),
         (-0.70, 0.192, 0.016, 0.026), (-0.62, 0.200, 0.020, 0.028), (-0.585, 0.212, 0.020, 0.020),
         (-0.56, 0.205, 0.010, 0.006)]

FORE = tt.Limb(pts=[(0.10, -0.32, 0.17), (0.17, -0.31, 0.12), (0.18, -0.34, 0.035), (0.185, -0.355, 0.012)],
               radii=[0.040, 0.032, 0.026, 0.022], toes=5, toe_len=0.035, toe_r=0.010, toe_spread=70,
               toe_yaw=20, stride=10, claw_len=0.014)
HIND = tt.Limb(pts=[(0.10, 0.10, 0.17), (0.18, 0.06, 0.12), (0.19, 0.12, 0.035), (0.195, 0.10, 0.012)],
               radii=[0.050, 0.040, 0.030, 0.024], toes=4, toe_len=0.05, toe_r=0.011, toe_spread=60,
               toe_yaw=20, stride=-10, claw_len=0.016)

PLATE = (0.16, 0.17, 0.11)
PLATE_RIM = (0.30, 0.30, 0.20)


def crest_tint(co, n, c, spec):
    if co.y < -0.56 and co.z > 0.19:
        c = nh.lerp(c, (0.55, 0.50, 0.34), 0.55 * nh.smoothstep(0.19, 0.21, co.z))
    return c


def nostrils(mb, surf, spec):
    for sx in (1, -1):
        loc, n = surf.hit((sx * 0.010, -0.595, 1.0), (0, 0, -1))
        if loc is not None:
            mb.add(nh.ellipsoid(loc, (0.006, 0.010, 0.005), subdivisions=1), tt.PUPIL)


SPEC = tt.TetrapodSpec(
    name="Smilosuchus",
    axis=AXIS, power=2.4,
    lofts=[(CREST, 2.0)],
    blobs=[((0.10, 0.10, 0.16), (0.06, 0.10, 0.07), 15),
           ((0.0, -0.75, 0.128), (0.024, 0.24, 0.020), 2)],      # lower jaw
    limbs=[FORE, HIND],
    voxel=0.0085, max_tris=12500,
    mouth=(-1.0, -0.47, 0.142, 0.160, 0.005),
    teeth=(20, 0.024, 0.0055, -0.99, -0.52), lower_teeth=True,
    eyes=(-0.505, 0.218, 0.013, (0.85, 0.65, 0.15), 0.05),
    plates=[dict(xs=(x, -x), y0=-0.40, y1=0.92, step=0.05, size=0.022, wide=1.1, taper=0.55, shrink=0.35,
                 follow=sway, col=PLATE, keel_col=PLATE_RIM, height=1.0)
            for x in (0.022, 0.065, 0.105)],
    back=(0.20, 0.22, 0.14), flank=(0.38, 0.38, 0.25), belly=(0.80, 0.76, 0.58),
    pattern=("bands", (0.12, 0.13, 0.08), 22.0, 0.5, -0.4, 1.0),
    paint_extra=crest_tint,
    post=nostrils,
)

if __name__ == "__main__":
    tt.run(SPEC)
