"""
Procedural Edaphosaurus pogonias (Early Permian edaphosaurid synapsid, ~3 m) for map colonies.

The plant-eating sail-back: a broad barrel trunk on short sprawling legs, a long tapering
tail and a strikingly small, short, deep head. The tall rounded sail rises from the neck to
the hips on elongated neural spines that carry short sideways crossbars (the knobbed
"yardarms" that set it apart from Dimetrodon's smooth spines); the membrane is stretched
between them. Olive-brown with pale spotting over the flanks; the sail is buff with dark
spines.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/edaphosaurus_pogonias.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Edaphosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402
from mathutils import Vector as V  # noqa: E402

TORSO = [
    (-0.56, 0.31, 0.065, 0.075),
    (-0.46, 0.30, 0.12, 0.12),
    (-0.30, 0.29, 0.19, 0.16),
    (-0.10, 0.29, 0.22, 0.17),
    (0.10, 0.29, 0.20, 0.16),
    (0.25, 0.28, 0.13, 0.12),
    (0.40, 0.25, 0.08, 0.085),
    (0.65, 0.18, 0.05, 0.055),
    (0.90, 0.11, 0.03, 0.032),
    (1.10, 0.065, 0.013, 0.014),
    (1.18, 0.055, 0.0, 0.0),
]
HEAD = [
    (-0.52, 0.335, 0.072, 0.072),
    (-0.59, 0.335, 0.068, 0.066),
    (-0.66, 0.315, 0.052, 0.050),
    (-0.715, 0.295, 0.034, 0.034),
    (-0.74, 0.285, 0.0, 0.0),
]
DROP = 0.04   # sit the sprawler a little lower
TORSO = [(y, z - DROP, w, h) for y, z, w, h in TORSO]
HEAD = [(y, z - DROP, w, h) for y, z, w, h in HEAD]
Y0, Y1, N = -0.44, 0.22, 20
SPINE, SAIL, SAIL_TOP = (0.22, 0.16, 0.10), (0.72, 0.60, 0.40), (0.88, 0.80, 0.62)


def back_z(y):
    z, _w, hh, _x = pt.rows_at(TORSO, y)
    return z + hh


def sail_h(y):
    t = (y - Y0) / (Y1 - Y0)
    if t <= 0 or t >= 1:
        return 0.0
    return 0.50 * math.sin(math.pi * t ** 0.9) ** 0.85


def crisp(mb, spec):
    # membrane: outline along the back and over the spine tips
    top, low = [], []
    for i in range(41):
        y = Y0 + (Y1 - Y0) * i / 40
        top.append(V((0, y + 0.05 * sail_h(y), back_z(y) + sail_h(y) * 0.96)))
        low.append(V((0, y, back_z(y) - 0.03)))
    outline = low + top[::-1]

    def sail_col(co, n):
        h = max(sail_h(co.y), 0.02)
        t = (co.z - back_z(co.y)) / h
        return nh.lerp(nh.lerp(spec.back, SAIL, nh.smoothstep(0.0, 0.3, t)), SAIL_TOP, nh.smoothstep(0.8, 1.0, t))
    mb.add(pt.membrane(outline, 0.008), sail_col, smooth=False)
    # spines with paired crossbars
    for i in range(N):
        y = Y0 + 0.01 + (Y1 - Y0 - 0.02) * i / (N - 1)
        h = sail_h(y)
        base = V((0, y, back_z(y) - 0.03))
        tip = V((0, y + 0.05 * h, back_z(y) + h + 0.02))
        mb.add(nh.tube([base, tip], [0.009, 0.004], sides=6), SPINE)
        k = 1
        while k * 0.06 < h - 0.04:
            p = base.lerp(tip, (k * 0.06 + 0.03) / (h + 0.05))
            mb.add(nh.tube([p + V((-0.022, 0, 0)), p + V((0.022, 0, 0))], [0.004, 0.004], sides=5), SPINE)
            k += 1


SPEC = pt.Spec(
    name="Edaphosaurus",
    torso=TORSO, head=HEAD,
    fore=pt.Limb(y=-0.33, z=0.21, x=0.13, upper=0.17, lower=0.15, sprawl=0.85, r=0.05,
                 foot=(0.040, 0.050, 0.018), toe_len=0.035, toe_r=0.010),
    hind=pt.Limb(y=0.17, z=0.22, x=0.12, upper=0.19, lower=0.16, sprawl=0.8, r=0.06,
                 foot=(0.045, 0.060, 0.018), toe_len=0.045, toe_r=0.011),
    eye=(0.05, -0.62, 0.31, 0.016), nostril=(0.022, -0.72, 0.27),
    back=(0.30, 0.30, 0.18), flank=(0.42, 0.40, 0.26), belly=(0.76, 0.70, 0.52), mark=(0.80, 0.76, 0.58),
    pattern="spots", pattern_freq=26.0, pattern_amount=0.45,
    crisp=crisp, voxel=0.008, max_tris=11000,
)

if __name__ == "__main__":
    pt.main(SPEC)
