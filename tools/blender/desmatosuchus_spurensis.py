"""
Procedural Desmatosuchus spurensis (Late Triassic aetosaur, ~4.5 m) for map colonies.

A heavily armoured plant-eating crocodile-line archosaur from Texas, Arizona and New
Mexico, about 220 million years ago: a broad, low body completely covered in rows of
rectangular bony plates, a small head with a blunt, shovel-like, upturned snout for
rooting, short sturdy legs and a long armoured tail. Its signature weapon is the pair
of huge, curved horn-like spikes at the shoulders, flanked by shorter spikes on the neck
and smaller ones along the flanks. Built with the shared Triassic tetrapod recipe
(nh_tri_tetrapod.py). Painted khaki-brown with darker plates and pale spikes
(speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/desmatosuchus_spurensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Desmatosuchus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

PLATE = (0.26, 0.20, 0.13)
PLATE_RIM = (0.40, 0.32, 0.20)
SPIKE = (0.30, 0.24, 0.17)
SPIKE_TIP = (0.82, 0.76, 0.62)


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.245, 0.026, 0.018),
    (-0.965, 0.252, 0.034, 0.030),
    (-0.89, 0.272, 0.040, 0.046),
    (-0.81, 0.290, 0.050, 0.056),
    (-0.745, 0.300, 0.052, 0.054),
    (-0.68, 0.302, 0.064, 0.056),
    (-0.58, 0.312, 0.104, 0.076),
    (-0.46, 0.322, 0.152, 0.096),
    (-0.30, 0.330, 0.176, 0.106),
    (-0.10, 0.335, 0.180, 0.106),
    (0.08, 0.330, 0.166, 0.096),
    (0.22, 0.315, 0.116, 0.076),
    (0.40, 0.290, 0.076, 0.056, sway(0.40)),
    (0.60, 0.250, 0.048, 0.038, sway(0.60)),
    (0.80, 0.212, 0.026, 0.022, sway(0.80)),
    (0.98, 0.180, 0.004, 0.004, sway(0.98)),
]

FORE = tt.Limb(pts=[(0.12, -0.45, 0.27), (0.165, -0.43, 0.15), (0.158, -0.47, 0.045), (0.158, -0.485, 0.013)],
               radii=[0.052, 0.040, 0.031, 0.026], toes=5, toe_len=0.03, toe_r=0.011, toe_spread=60,
               stride=10, claw_len=0.014)
HIND = tt.Limb(pts=[(0.12, 0.08, 0.28), (0.165, 0.02, 0.16), (0.158, 0.10, 0.05), (0.158, 0.07, 0.013)],
               radii=[0.062, 0.046, 0.033, 0.027], toes=4, toe_len=0.045, toe_r=0.012, toe_spread=50,
               stride=-10, claw_len=0.016)

# paramedian + lateral plate rows: (x offset as fraction of body half width)
PLATES = [dict(xs=(x, -x), y0=-0.66, y1=0.96, step=0.052, size=0.030, wide=w, taper=0.55, shrink=0.35,
               follow=sway, col=PLATE, keel_col=PLATE_RIM, height=0.6)
          for x, w in ((0.035, 1.15), (0.10, 1.05))]


def spikes(mb, surf, spec):
    def col(co, n, base, ln):
        return nh.lerp(SPIKE, SPIKE_TIP, nh.smoothstep(0.2, 1.0, (co - base).length / ln))
    # (y, height on the side as fraction, length, radius, up, back)
    rows = [(-0.665, 0.5, 0.07, 0.016, 0.5, 0.3), (-0.61, 0.45, 0.11, 0.020, 0.35, 0.4),
            (-0.545, 0.35, 0.28, 0.030, 0.12, 0.45)]
    y = -0.44
    while y < 0.75:
        rows.append((y, 0.2, 0.045 * (1.0 - 0.5 * max(0.0, y) / 0.75), 0.014, 0.1, 0.4))
        y += 0.075
    for y, hz, ln, r, up, back in rows:
        for sx in (1, -1):
            zc = tt.Vector((0, 0, 0))
            # find the body centre height at y from the spec axis
            zs = [row[1] for row in AXIS if abs(row[0] - y) < 0.12] or [0.3]
            z = sum(zs) / len(zs) + hz * 0.08
            loc, n = surf.hit((sx * 2.0 + (sway(y) if y > 0.2 else 0), y, z), (-sx, 0, 0))
            if loc is None:
                continue
            d = Vector((sx, back, up))
            base = loc - Vector((sx, 0, 0)) * r * 0.4
            bend = Vector((0, 0.6, 0.15)) if ln > 0.2 else Vector((0, 0.3, 0))
            mb.add(tt.curved_spike(base, d, ln, r, bend=bend), lambda co, nn, b=base, l=ln: col(co, nn, b, l))
            del zc


def snout(co, n, c, spec):
    return nh.lerp(c, (0.55, 0.42, 0.30), 0.5 * nh.smoothstep(-0.94, -0.99, co.y))


SPEC = tt.TetrapodSpec(
    name="Desmatosuchus",
    axis=AXIS, power=2.6,
    blobs=[((0.11, 0.09, 0.26), (0.065, 0.12, 0.09), 20)],
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=10000,
    mouth=(-1.0, -0.83, 0.238, 0.268, 0.004),
    eyes=(-0.80, 0.312, 0.011, (0.70, 0.50, 0.15)),
    nostrils=(-0.985, 0.255),
    plates=PLATES,
    back=(0.30, 0.24, 0.16), flank=(0.55, 0.47, 0.32), belly=(0.80, 0.72, 0.54),
    paint_extra=snout,
    post=spikes,
)

if __name__ == "__main__":
    tt.run(SPEC)
