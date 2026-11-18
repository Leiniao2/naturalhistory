"""
Procedural Typothorax coccinarum (Late Triassic aetosaur, ~3.5 m) for map colonies.

A plant-eating crocodile-line archosaur from New Mexico, Arizona and Texas, about 215
million years ago, and the widest, flattest aetosaur: its trunk was almost as broad as
it was long, roofed by a pancake-shaped carapace of many rows of interlocking bony
plates, edged by lateral plates carrying small backward-hooked spikes. A small head with
a blunt, upturned, pig-like snout for rooting, short sturdy sprawled legs and a long
armoured tail. Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py).
Painted sandy khaki with dark plate rows and pale spike tips (speculative). Faces -Y,
pivot on the ground.

Usage:
  blender --background --python tools/blender/typothorax_coccinarum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Typothorax.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

PLATE = (0.28, 0.22, 0.14)
PLATE_RIM = (0.50, 0.42, 0.28)
SPIKE = (0.32, 0.26, 0.18)
SPIKE_TIP = (0.85, 0.80, 0.66)


def sway(y):
    s = max(0.0, (y - 0.3) / 0.7)
    return 0.06 * s * s


AXIS = [
    (-1.00, 0.170, 0.026, 0.020),
    (-0.965, 0.178, 0.034, 0.030),
    (-0.90, 0.192, 0.040, 0.042),
    (-0.83, 0.206, 0.048, 0.050),
    (-0.77, 0.214, 0.050, 0.048),
    (-0.71, 0.214, 0.064, 0.050),
    (-0.62, 0.220, 0.140, 0.064),
    (-0.48, 0.228, 0.250, 0.080),
    (-0.30, 0.232, 0.300, 0.086),
    (-0.10, 0.232, 0.300, 0.086),
    (0.08, 0.228, 0.250, 0.078),
    (0.22, 0.220, 0.140, 0.064),
    (0.36, 0.205, 0.070, 0.048, sway(0.36)),
    (0.56, 0.180, 0.044, 0.034, sway(0.56)),
    (0.78, 0.155, 0.024, 0.020, sway(0.78)),
    (0.98, 0.135, 0.004, 0.004, sway(0.98)),
]

FORE = tt.Limb(pts=[(0.14, -0.50, 0.18), (0.21, -0.48, 0.11), (0.215, -0.52, 0.035), (0.22, -0.535, 0.012)],
               radii=[0.050, 0.040, 0.031, 0.026], toes=5, toe_len=0.03, toe_r=0.011, toe_spread=60,
               toe_yaw=15, stride=10, claw_len=0.014)
HIND = tt.Limb(pts=[(0.14, 0.10, 0.18), (0.22, 0.06, 0.11), (0.225, 0.12, 0.035), (0.23, 0.10, 0.012)],
               radii=[0.058, 0.045, 0.033, 0.027], toes=4, toe_len=0.04, toe_r=0.012, toe_spread=50,
               toe_yaw=15, stride=-10, claw_len=0.016)

# many paramedian plate rows across the broad carapace
PLATES = [dict(xs=(x, -x), y0=-0.66, y1=0.95, step=0.06, size=0.032, wide=1.2, taper=0.5, shrink=0.3,
               follow=sway, col=PLATE, keel_col=PLATE_RIM, height=0.5)
          for x in (0.032, 0.105, 0.180)]


def hw_at(y):
    for (y0, _z0, w0, _h0, *_), (y1, _z1, w1, _h1, *_) in zip(AXIS, AXIS[1:]):
        if y0 <= y <= y1:
            return w0 + (w1 - w0) * (y - y0) / (y1 - y0)
    return 0.0


def spikes(mb, surf, spec):
    y = -0.58
    while y < 0.70:
        w = hw_at(y)
        for sx in (1, -1):
            loc, n = surf.hit((sx * (w * 0.92) + (sway(y) if y > 0.3 else 0), y, 2.0), (0, 0, -1))
            if loc is None:
                continue
            ln = 0.030 if y < 0.25 else 0.022
            d = Vector((sx * 0.7, 0.6, 0.35))
            base = loc - Vector((0, 0, 0.004))
            mb.add(tt.curved_spike(base, d, ln, 0.010, bend=Vector((0, 0.6, 0))),
                   lambda co, nn, b=base, l=ln: nh.lerp(SPIKE, SPIKE_TIP, nh.smoothstep(0.2, 1.0, (co - b).length / l)))
        y += 0.06


def snout(co, n, c, spec):
    return nh.lerp(c, (0.58, 0.44, 0.32), 0.5 * nh.smoothstep(-0.94, -0.99, co.y))


SPEC = tt.TetrapodSpec(
    name="Typothorax",
    axis=AXIS, power=3.2,
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=8000,
    mouth=(-1.0, -0.85, 0.163, 0.190, 0.004),
    eyes=(-0.83, 0.232, 0.011, (0.70, 0.50, 0.15)),
    nostrils=(-0.985, 0.178),
    plates=PLATES,
    back=(0.36, 0.30, 0.20), flank=(0.60, 0.52, 0.36), belly=(0.82, 0.74, 0.56),
    paint_extra=snout,
    post=spikes,
)

if __name__ == "__main__":
    tt.run(SPEC)
