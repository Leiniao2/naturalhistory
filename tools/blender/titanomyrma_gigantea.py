"""
Procedural Titanomyrma gigantea (Germany, early-middle Eocene, ~49-47 Ma) for map colonies:
the largest ant known, its winged queens about 6 cm long with a 15 cm wingspan,
as big as a hummingbird. Built with nh_ant.py.

Shown as a queen on the ground: a big head with strong mandibles, a deep thorax,
a one-node waist and a huge, long gaster, with her four smoky-brown wings folded
flat over the back and reaching past the tip of the gaster. No sting is shown.
Dark chestnut-brown, glossy. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/titanomyrma_gigantea.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TitanomyrmaGigantea.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ant  # noqa: E402
from mathutils import Vector  # noqa: E402

BROWN = (0.26, 0.15, 0.08)
DARK = (0.16, 0.09, 0.05)
LEG = (0.30, 0.18, 0.10)
WING = (0.46, 0.38, 0.28)

PARAMS = dict(
    base=0.14,
    head_w=0.12, head_l=0.12, head_h=0.085, head_pitch=10.0, head_z=0.085, neck=0.95,
    eye_r=0.034, eye_y=-0.12, mandible=1.15, mandible_teeth=5,
    scape=0.22, funiculus=0.30, fun_segs=11, club_segs=0, ant_r=0.011,
    meso_len=0.40, meso_h=0.17, meso_w=0.95, groove=0.12,
    meso_profile=((0.0, 0.50), (0.12, 0.90), (0.30, 1.00), (0.50, 0.98), (0.65, 0.86),
                  (0.80, 0.78), (0.92, 0.66), (1.0, 0.40)),
    waist="node", pet_h=0.055, pet_w=0.045,
    gaster_l=0.36, gaster_w=0.17, gaster_h=0.14, gaster_tilt=4.0, gaster_bands=5,
    sting=False,
    legs=1.25, knee_rise=0.10, leg_r=0.015,
    head_col=BROWN, meso_col=BROWN, gaster_col=DARK, leg_col=LEG, antenna_col=LEG,
    mandible_col=(0.20, 0.10, 0.05), gloss=0.4,
)


def wings(ant):
    """Fore and hind wings folded flat over the gaster, slightly spread, smoky brown."""
    c, r = ant.meso_point(0.42)
    top = c.z + r
    g_top = ant.gaster_c.z + ant.p["gaster_h"] + 0.012
    tip_y = ant.gaster_c.y + ant.p["gaster_l"] * 1.15
    for sx in (-1, 1):
        for (y0, length, width, spread, dz) in ((c.y, tip_y - c.y, 0.21, 0.06, 0.012),
                                                (c.y + 0.07, (tip_y - c.y) * 0.72, 0.15, 0.16, 0.0)):
            root = Vector((sx * 0.02, y0, top + dz))
            d = Vector((sx * spread, 1.0, 0)).normalized()
            side = Vector((d.y * sx, -d.x * sx, 0)) * sx
            outline = []
            n = 14
            for i in range(n + 1):
                t = i / n
                w = width * math.sin(math.pi * min(1.0, t * 1.08)) ** 0.7 * (0.55 + 0.45 * t)
                p = root + d * length * t + side * sx * w
                p.z = top + dz + (g_top - top) * nh.smoothstep(0.0, 0.5, t) - 0.45 * w  # drooping over the sides
                outline.append(tuple(p))
            for i in range(n - 1, 0, -1):
                t = i / n
                p = root + d * length * t - side * sx * width * 0.08
                p.z = top + dz + (g_top - top) * nh.smoothstep(0.0, 0.5, t)
                outline.append(tuple(p))
            ant.mb.add(nh.flat_panel(outline, 0.006), WING, smooth=False)


if __name__ == "__main__":
    nh_ant.run(PARAMS, "TitanomyrmaGigantea", extra=wings, roughness=0.5)
