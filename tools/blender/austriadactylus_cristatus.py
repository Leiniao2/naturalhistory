"""
Procedural Austriadactylus cristatus (Late Triassic pterosaur, Norian of the Austrian
Alps, wingspan ~1.2 m) for map colonies, flying with the wings spread.

One of the oldest pterosaurs: a long-tailed early form with a long, low skull topped by
a thin bony crest running along the snout, jaws with large fangs at the front and many
small multi-cusped teeth behind, a short neck, a compact furry body, long narrow wings
on the elongated fourth finger and a long stiff tail with a small vane. Built with the
Jurassic flier recipe (nh_jur_flyer.py, as rhamphorhynchus_muensteri.py) plus a crisp
head crest. Grey-brown pycnofibre coat, pale throat, brown membranes with a dark leading
edge, red crest and tail vane (speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/austriadactylus_cristatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Austriadactylus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import Vector  # noqa: E402

CREST = (0.78, 0.18, 0.10)
VANE = (0.72, 0.20, 0.12)
MEM = (0.46, 0.32, 0.22)
MEM_EDGE = (0.20, 0.14, 0.10)


def wing_color(co, n):
    k = nh.smoothstep(-0.02, 0.08, co.y + 0.13 - abs(co.x) * 0.14)
    return nh.lerp(MEM_EDGE, MEM, k)


def crest_col(co, n):
    return nh.lerp(CREST, (0.95, 0.70, 0.30), nh.smoothstep(0.045, 0.075, co.z))


def extras(spine):
    crisp = [(kit.blade([(0.58, 0.0), (0.66, 0.045), (0.75, 0.0), (0.66, -0.03)], 0.004), VANE),
             # thin crest along the top of the snout
             (kit.blade([(-0.50, 0.012), (-0.46, 0.040), (-0.40, 0.068), (-0.34, 0.074), (-0.29, 0.050),
                         (-0.27, 0.036), (-0.34, 0.032), (-0.42, 0.024), (-0.48, 0.012)], 0.004), crest_col)]
    for i in range(9):
        y = -0.36 - i * 0.015
        big = i >= 6
        ln = 0.020 if big else 0.010
        for sx in (1, -1):
            b = Vector((sx * 0.010, y, 0.016 - i * 0.0012))
            crisp.append((kit.cone(b, b + Vector((sx * 0.003, -0.006, -ln)), 0.0032 if big else 0.0024, sides=4), kit.TOOTH))
            b2 = Vector((sx * 0.008, y + 0.005, 0.003 - i * 0.0012))
            crisp.append((kit.cone(b2, b2 + Vector((sx * 0.003, -0.006, ln * 0.8)), 0.0024, sides=4), kit.TOOTH))
    return [], crisp


SPEC = fl.Spec(
    name="Austriadactylus",
    rows=[(0, 0.72, 0.0, 0, 0), (0, 0.58, 0.0, 0.005, 0.005), (0, 0.35, 0.0, 0.007, 0.007), (0, 0.15, 0.0, 0.02, 0.02),
          (0, 0.05, 0.0, 0.046, 0.042), (0, -0.05, 0.005, 0.05, 0.046), (0, -0.13, 0.012, 0.032, 0.032),
          (0, -0.19, 0.022, 0.021, 0.022), (0, -0.25, 0.030, 0.024, 0.026), (0, -0.30, 0.030, 0.026, 0.028),
          (0, -0.36, 0.018, 0.017, 0.018), (0, -0.43, 0.010, 0.011, 0.010), (0, -0.49, 0.005, 0.006, 0.005),
          (0, -0.515, 0.004, 0, 0)],
    paint=kit.paint(back=(0.34, 0.30, 0.26), flank=(0.50, 0.44, 0.38), belly=(0.86, 0.80, 0.70)),
    wing=[(0.03, -0.09), (0.2, -0.11), (0.31, -0.14), (0.58, -0.08), (0.86, 0.01), (0.58, 0.07), (0.30, 0.11), (0.12, 0.13), (0.03, 0.05)],
    wing_color=wing_color,
    arm=[(0.02, -0.08, 0.0), (0.2, -0.105, 0.0), (0.31, -0.135, 0.0), (0.58, -0.08, 0.0), (0.86, 0.01, 0.0)],
    arm_r=[0.018, 0.013, 0.011, 0.006, 0.002],
    legs=[(0.03, 0.04, -0.01), (0.08, 0.09, -0.015), (0.12, 0.13, -0.015)], leg_r=[0.013, 0.008, 0.005],
    eye=(0.021, -0.30, 0.042), eye_r=0.011,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "Austriadactylus", **fl.PREVIEW)
