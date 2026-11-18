"""
Procedural Euchambersia mirabilis (Late Permian therocephalian, ~45 cm) for map colonies.

A small, possibly venomous therocephalian from the Karoo: a short, deep, broad-snouted skull
with a large, deep pit in front of each eye (thought to have housed a venom gland), long,
ridged upper canines, a low, lithe body on semi-erect limbs and a long tail. Shown in warning
colours - dark charcoal with ochre-yellow flank stripes and a dark-rimmed pit on the snout.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/euchambersia_mirabilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Euchambersia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402

PIT = (0.08, 0.04, 0.03)


def crisp(mb, spec):
    for sx in (1, -1):    # the deep maxillary fossa in front of each eye
        mb.add(pt.oriented((sx * 0.062, -0.635, 0.285), (0.012, 0.03, 0.022), yaw=sx * 15), PIT)


def paint(co, n, c):
    if co.y > -0.40 and abs(n.x) > 0.4:          # ochre stripes along the flanks
        v = abs(co.z - 0.25)
        k = nh.smoothstep(0.02, 0.005, abs(v - 0.035))
        c = nh.lerp(c, (0.86, 0.66, 0.18), 0.9 * k)
    return c


SPEC = pt.Spec(
    name="Euchambersia",
    torso=[
        (-0.42, 0.26, 0.06, 0.06),
        (-0.34, 0.26, 0.10, 0.09),
        (-0.18, 0.26, 0.12, 0.10),
        (0.00, 0.26, 0.115, 0.095),
        (0.16, 0.25, 0.10, 0.085),
        (0.28, 0.24, 0.07, 0.06),
        (0.50, 0.19, 0.04, 0.035),
        (0.80, 0.12, 0.02, 0.018),
        (1.00, 0.08, 0.006, 0.006),
        (1.04, 0.075, 0.0, 0.0),
    ],
    head=[
        (-0.42, 0.30, 0.075, 0.07),
        (-0.52, 0.30, 0.08, 0.075),
        (-0.60, 0.29, 0.07, 0.065),
        (-0.67, 0.27, 0.055, 0.05),
        (-0.71, 0.26, 0.035, 0.035),
        (-0.725, 0.255, 0.0, 0.0),
    ],
    jaw=[
        (-0.46, 0.225, 0.06, 0.024),
        (-0.62, 0.215, 0.045, 0.02),
        (-0.70, 0.215, 0.025, 0.015),
        (-0.72, 0.215, 0.0, 0.0),
    ],
    fangs=[(0.035, -0.665, 0.24, 0.075, 0.009, 0.006)],
    teeth=[(-0.72, -0.69, 2, 0.012, 0.004, True)],
    fore=pt.Limb(y=-0.28, z=0.22, x=0.10, upper=0.11, lower=0.12, sprawl=0.5, r=0.032,
                 foot=(0.026, 0.035, 0.010), toe_len=0.03, toe_r=0.0065),
    hind=pt.Limb(y=0.18, z=0.22, x=0.09, upper=0.12, lower=0.12, sprawl=0.4, r=0.038,
                 foot=(0.028, 0.040, 0.010), toe_len=0.032, toe_r=0.007),
    eye=(0.06, -0.57, 0.33, 0.016), nostril=(0.018, -0.72, 0.28),
    back=(0.12, 0.11, 0.10), flank=(0.22, 0.20, 0.17), belly=(0.70, 0.62, 0.40), mark=(0.06, 0.05, 0.05),
    pattern="none", paint=paint, crisp=crisp,
    voxel=0.005, max_tris=8000,
)

if __name__ == "__main__":
    pt.main(SPEC)
