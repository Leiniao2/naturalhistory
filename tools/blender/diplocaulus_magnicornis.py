"""
Procedural Diplocaulus magnicornis (Early Permian nectridean lepospondyl, ~1 m) for map
colonies, swimming.

The "boomerang-headed" amphibian of the Texas red beds: a flattened, broad body with tiny
limbs and a short, flattened tail, and an extraordinary flat head whose back corners are
drawn out into long, swept-back horns, giving the skull its boomerang shape (it may have
worked as a hydrofoil). Small eyes on top of the head near the front. Mottled olive-brown
above, pale beneath. Built with nh_per_tetra. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/diplocaulus_magnicornis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Diplocaulus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402
from mathutils import Vector as V  # noqa: E402

HEAD = (0.36, 0.34, 0.22)


def fused(b, spec):
    # the boomerang: flattened lobes sweeping out and back from the back of the skull
    for sx in (1, -1):
        pts = [V((sx * 0.04, -0.52, 0.0)), V((sx * 0.13, -0.47, 0.0)), V((sx * 0.22, -0.40, -0.002)),
               V((sx * 0.30, -0.33, -0.004)), V((sx * 0.36, -0.27, -0.006))]
        rads = [0.075, 0.062, 0.045, 0.028, 0.010]
        for p, r in zip(pts, rads):
            b.add(pt.oriented(p, (r, r, r * 0.33), yaw=sx * 35), HEAD)
        for a, c, r0, r1 in zip(pts, pts[1:], rads, rads[1:]):
            for t in (0.33, 0.66):
                r = r0 + (r1 - r0) * t
                b.add(pt.oriented(a.lerp(c, t), (r, r, r * 0.33), yaw=sx * 35), HEAD)
    # tiny limbs
    for sx in (1, -1):
        for y, l in ((-0.36, 0.06), (0.06, 0.07)):
            p0 = V((sx * 0.07, y, -0.01))
            p1 = p0 + V((sx * l, l * 0.4, -0.01))
            b.add(pt.nh.tube([p0, p1], [0.014, 0.010], sides=8), spec.flank)
            b.add(pt.oriented(p1, (0.016, 0.018, 0.005)), spec.flank)


SPEC = pt.Spec(
    name="Diplocaulus",
    torso=[
        (-0.48, 0.0, 0.080, 0.032),
        (-0.40, 0.0, 0.100, 0.042),
        (-0.20, 0.0, 0.105, 0.045),
        (0.00, 0.0, 0.095, 0.042),
        (0.12, 0.0, 0.065, 0.034),
        (0.30, 0.0, 0.035, 0.030),
        (0.50, 0.0, 0.016, 0.022),
        (0.62, 0.0, 0.0, 0.0),
    ],
    torso_power=2.4,
    head=[
        (-0.50, 0.004, 0.095, 0.030),
        (-0.60, 0.004, 0.085, 0.026),
        (-0.68, 0.000, 0.060, 0.020),
        (-0.72, -0.002, 0.0, 0.0),
    ],
    head_power=3.0,
    eye=(0.035, -0.62, 0.022, 0.010), nostril=(0.02, -0.69, 0.012),
    back=(0.30, 0.30, 0.20), flank=(0.40, 0.38, 0.26), belly=(0.78, 0.74, 0.58), mark=(0.16, 0.16, 0.10),
    pattern="mottle", pattern_freq=10.0, pattern_amount=0.5,
    fused=fused, pivot="centre", voxel=0.0055, max_tris=6000,
)

if __name__ == "__main__":
    pt.main(SPEC)
