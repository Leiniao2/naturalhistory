"""
Procedural Protostega gigas (Late Cretaceous protostegid sea turtle, Western Interior Seaway).

A 3-metre giant sea turtle with a reduced, leathery shell: a long, teardrop carapace of
skin over a light bony frame, ridged with five low lengthwise keels like a leatherback's,
very long wing-like front flippers, short rear paddles and a big head with a broad,
slightly hooked beak. Grey-brown with pale speckles, a cream belly and beak.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/protostega_gigas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Protostega.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

SHELL = (0.30, 0.27, 0.22)
RIDGE = (0.16, 0.14, 0.12)
SKIN = (0.42, 0.40, 0.36)
BELLY = (0.86, 0.82, 0.70)
SPECK = (0.80, 0.78, 0.70)
BEAK = (0.82, 0.76, 0.60)
KEELS = (0.0, 0.10, 0.20)


def paint(co, n):
    on_shell = co.z > 0.02 and abs(co.x) < 0.36 and -0.42 < co.y < 0.58
    if on_shell and n.z > 0.2:
        c = SHELL
        for rx in KEELS:
            c = nh.lerp(c, RIDGE, 0.8 * (1 - nh.smoothstep(0.006, 0.02, abs(abs(co.x) - rx))))
        c = nh.lerp(c, SPECK, 0.5 * cc.spots(co, 70.0, 0.06))
        return cc.mottle(c, co, 0.08)
    c = cc.countershade(n, BELLY, SKIN, SKIN)
    c = nh.lerp(c, SPECK, 0.4 * cc.spots(co, 60.0, 0.07) * nh.smoothstep(0.0, 0.5, n.z))
    return cc.mottle(c, co, 0.08)


def make():
    axis = [(0.70, -0.02, 0.0, 0.0), (0.64, -0.02, 0.025, 0.02), (0.52, -0.01, 0.08, 0.045),
            (0.25, 0.0, 0.16, 0.075), (-0.05, 0.0, 0.17, 0.08), (-0.32, 0.0, 0.10, 0.06),
            (-0.44, 0.01, 0.07, 0.055), (-0.55, 0.02, 0.08, 0.07), (-0.68, 0.015, 0.07, 0.06),
            (-0.77, 0.0, 0.04, 0.04), (-0.80, -0.02, 0.0, 0.0)]
    s = tp.Spec(name="Protostega", axis=axis, paint=paint, pivot="centre",
                eye=(0.065, -0.65, 0.045, 0.013), eye_col=(0.1, 0.08, 0.05),
                disp=cc.scales_disp(0.001, 40.0), voxel=0.012, max_tris=11000)
    # leathery teardrop carapace with five keels and a pointed rear
    s.blobs.append(((0, 0.05, 0.03), (0.36, 0.48, 0.11), False))
    s.blobs.append(((0, 0.50, 0.03), (0.12, 0.16, 0.06), False))
    for rx in KEELS:
        s.tubes.append(([(rx, -0.36, 0.08), (rx, 0.05, 0.14 - rx * 0.3), (rx, 0.55, 0.05)], [0.012, 0.016, 0.006], rx > 0))
    s.blobs.append(((0, 0.0, -0.03), (0.32, 0.42, 0.06), False))   # plastron
    s.limbs = [mr.flipper([(0.26, -0.22, -0.01), (0.60, -0.20, -0.01), (1.00, -0.08, 0.0), (1.30, 0.10, 0.0)],
                          [0.07, 0.08, 0.05, 0.01], flat=0.15),
               mr.flipper([(0.26, 0.40, -0.02), (0.40, 0.50, -0.03), (0.50, 0.58, -0.03)],
                          [0.06, 0.06, 0.02], flat=0.18)]

    def crisp(mb, s):
        mb.add(cc.curved_cone((0, -0.76, 0.0), (0, -0.82, -0.02), (0, -0.83, -0.05), 0.035, sides=8), BEAK)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Protostega")
