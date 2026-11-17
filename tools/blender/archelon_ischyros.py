"""
Procedural Archelon ischyros (Late Cretaceous protostegid sea turtle, South Dakota).

The largest turtle known, about 4-4.6 metres long: a broad, low carapace that was not solid
bone but a frame of ribs covered by leathery skin (like today's leatherback), with low
ridges running along it, a big head with a strongly hooked beak, and huge front flippers
spanning some 4 metres. Dark slate-brown shell with paler ridges, grey skin with pale spots,
cream beak and underside. Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/archelon_ischyros.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Archelon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

SHELL = (0.20, 0.20, 0.18)
RIDGE = (0.50, 0.48, 0.42)
SKIN = (0.36, 0.38, 0.38)
BELLY = (0.84, 0.80, 0.70)
BEAK = (0.80, 0.74, 0.58)


def paint(co, n):
    on_shell = co.z > 0.02 and abs(co.x) < 0.42 and -0.48 < co.y < 0.5
    if on_shell and n.z > 0.2:
        c = SHELL
        for rx in (0.0, 0.14, 0.28):
            c = nh.lerp(c, RIDGE, 0.7 * (1 - nh.smoothstep(0.008, 0.025, abs(abs(co.x) - rx))))
        return cc.mottle(c, co, 0.1)
    c = cc.countershade(n, BELLY, SKIN, SKIN)
    c = nh.lerp(c, (0.70, 0.70, 0.66), 0.5 * cc.spots(co, 22.0, 0.15) * nh.smoothstep(0.0, 0.5, n.z))
    return cc.mottle(c, co, 0.08)


def make():
    axis = [(0.62, -0.02, 0.0, 0.0), (0.56, -0.02, 0.03, 0.025), (0.45, -0.01, 0.09, 0.05),
            (0.2, 0.0, 0.18, 0.08), (-0.1, 0.0, 0.18, 0.08), (-0.38, 0.0, 0.10, 0.06),
            (-0.50, 0.01, 0.07, 0.055), (-0.60, 0.02, 0.075, 0.065), (-0.72, 0.015, 0.06, 0.055),
            (-0.80, 0.0, 0.03, 0.035), (-0.83, -0.02, 0.0, 0.0)]
    s = tp.Spec(name="Archelon", axis=axis, paint=paint, pivot="centre",
                eye=(0.06, -0.69, 0.04, 0.013), eye_col=(0.1, 0.08, 0.05),
                disp=cc.scales_disp(0.001, 40.0), voxel=0.012, max_tris=11000)
    # carapace: broad low dome with three keels
    s.blobs.append(((0, 0.03, 0.03), (0.42, 0.50, 0.12), False))
    for rx in (0.0, 0.14, 0.28):
        s.tubes.append(([(rx, -0.40, 0.08), (rx, 0.0, 0.15 - rx * 0.25), (rx, 0.42, 0.06)], [0.018, 0.022, 0.01], rx > 0))
    s.blobs.append(((0, 0.0, -0.03), (0.38, 0.45, 0.07), False))   # plastron
    s.limbs = [mr.flipper([(0.30, -0.25, -0.01), (0.60, -0.22, -0.01), (0.95, -0.10, 0.0), (1.15, 0.05, 0.0)],
                          [0.08, 0.09, 0.06, 0.012], flat=0.16),
               mr.flipper([(0.30, 0.38, -0.02), (0.45, 0.48, -0.03), (0.55, 0.58, -0.03)],
                          [0.07, 0.07, 0.02], flat=0.18)]

    def crisp(mb, s):
        # hooked beak
        mb.add(cc.curved_cone((0, -0.78, 0.0), (0, -0.85, -0.03), (0, -0.86, -0.07), 0.03, sides=8), BEAK)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Archelon")
