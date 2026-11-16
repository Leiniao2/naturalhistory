"""
Procedural Progonoblattina clarkii (a large Late Carboniferous roachoid) for map colonies.

A big roachoid (nh_roachoid.py) whose long, broad tegmina dwarf a small,
transversely oval pronotum: the wings run far beyond the abdomen to a blunt
apex, amber-ochre and paler than the other roachoids, darker at the base, with
a dense, fine venation (the species is told apart by its many vein branches
reaching the margin): a long subcosta and radius with many combed branches,
and a strongly S-curved (sigmoidal) media and anterior cubitus whose branches
fork again near the margin, plus the arched claval furrow and anal veins. The
pronotum is buff with a dark central bar and pale rim. Slender legs, long
antennae, short cerci hidden under the wing tips.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/progonoblattina_clarkii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Progonoblattina.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_roachoid as rc  # noqa: E402
from nh_roachoid import Vein  # noqa: E402

SPEC = rc.Spec(
    name="Progonoblattina",
    wing_y0=-0.20, wing_len=1.00, wing_w=0.30, wing_cx=0.40, wing_narrow=0.35, wing_tip=2.5,
    wing_apex=0.03, wing_droop=0.055, wing_spread=2.0,
    veins=[
        Vein((0.03, 0.84), 10, 5, -64, -4, 0.15, 0.85, bow=0.02, width=0.0036),    # Sc
        Vein((0.03, 0.68), 78, 6, 16, 68, 0.35, 0.92, bow=0.01, width=0.0040, twig=3.5),   # R
        Vein((0.03, 0.53), 106, 3, 86, 98, 0.50, 0.85, sigmoid=0.035, width=0.0036, twig=3.0),  # M
        Vein((0.05, 0.41), 166, 4, 118, 154, 0.30, 0.85, bow=-0.02, sigmoid=0.03, width=0.0034,
             twig=3.5),                                                            # CuA
        Vein((0.02, 0.33), 194, bow=-0.10, width=0.0038),                          # CuP
        Vein((0.03, 0.22), 214, 3, 202, 228, 0.0, 0.0, bow=-0.05, width=0.0024),   # A
    ],
    vein_scale=0.85,
    wing_col=(0.66, 0.48, 0.24), wing_base_col=(0.40, 0.26, 0.12), vein_col=(0.30, 0.18, 0.08),
    decals=[("region", 0.0, 0.17, 0.0, 1.0, (0.55, 0.38, 0.18)), ("region", 0.0, 0.09, 0.0, 1.0, (0.42, 0.27, 0.12))],
    pron_y=-0.29, pron_rx=0.180, pron_ry=0.115, pron_dome=0.034, pron_front=2.0, pron_hind=2.4,
    pron_col=(0.55, 0.40, 0.22), pron_rim=(0.78, 0.66, 0.46), pron_rim_at=0.80,
    pron_mark="bar", pron_mark_col=(0.24, 0.14, 0.07),
    body_col=(0.30, 0.20, 0.10), abd_len=0.58, body_rx=0.14,
    antenna_len=0.70, antenna_curl=0.16,
    legs=((-0.24, (0.19, -0.06), (0.25, -0.17)),
          (-0.13, (0.23, 0.03), (0.35, 0.09)),
          (-0.02, (0.24, 0.16), (0.36, 0.40))),
    leg_col=(0.50, 0.34, 0.18), leg_dark=(0.26, 0.16, 0.08), leg_thick=0.9,
    cerci_len=0.16,
)


if __name__ == "__main__":
    nh.run(lambda: rc.build(SPEC), "Progonoblattina", ground=(0.30, 0.26, 0.18),
           views=((35, 30), (0, 80), (-90, 10)))
