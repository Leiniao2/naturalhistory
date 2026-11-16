"""
Procedural Anthracoblattina ensifera (Late Carboniferous roachoid, Phyloblattidae) for map colonies.

A female roachoid with the long sword-like external ovipositor that gave the
species its name ("sword-bearer"): a laterally flattened, slightly upcurved
blade of two valves sticking far out behind the wing tips, pale toward the
point. Otherwise a slender, long-winged cockroach-like insect (nh_roachoid.py):
a trapezoidal pronotum, narrower in front with a squarish hind margin, dark
chestnut with a narrow pale rim; narrow, elongate-oval tegmina about three
times as long as wide, plain reddish brown, with a long
subcostal field reaching about two-thirds of the wing and a comb of many
radial branches running to the front margin, a forked media, a cubitus fanning
to the inner margin and the arched claval furrow. Long antennae, spiny legs,
short cerci flanking the ovipositor base.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/anthracoblattina_ensifera.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Anthracoblattina.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_roachoid as rc  # noqa: E402
from nh_roachoid import Vein  # noqa: E402

SPEC = rc.Spec(
    name="Anthracoblattina",
    wing_y0=-0.19, wing_len=0.88, wing_w=0.275, wing_cx=0.40, wing_narrow=0.45, wing_tip=1.8,
    wing_apex=-0.04, wing_droop=0.05,
    veins=[
        Vein((0.04, 0.82), 18, 4, -62, 6, 0.20, 0.85, bow=0.02, width=0.0040),     # Sc: long field
        Vein((0.04, 0.66), 80, 6, 24, 70, 0.35, 0.92, bow=0.01, width=0.0045),     # R: many branches
        Vein((0.04, 0.50), 108, 2, 88, 98, 0.55, 0.80, width=0.0040),              # M
        Vein((0.06, 0.38), 166, 3, 120, 150, 0.35, 0.80, bow=-0.03, width=0.0038),  # CuA
        Vein((0.02, 0.32), 196, bow=-0.10, width=0.0042),                          # CuP
        Vein((0.03, 0.22), 212, 2, 203, 222, 0.0, 0.0, bow=-0.05, width=0.0026),   # A
    ],
    wing_col=(0.50, 0.26, 0.12), wing_base_col=(0.32, 0.15, 0.07), vein_col=(0.20, 0.09, 0.04),
    pron_y=-0.30, pron_rx=0.185, pron_ry=0.140, pron_front=2.2, pron_hind=3.6, pron_taper=0.22,
    pron_col=(0.26, 0.12, 0.06), pron_rim=(0.62, 0.42, 0.24), pron_rim_at=0.84,
    body_col=(0.24, 0.12, 0.06), body_band_col=(0.45, 0.28, 0.14), abd_len=0.62, body_rx=0.14,
    antenna_len=0.66,
    legs=((-0.24, (0.19, -0.06), (0.24, -0.17)),
          (-0.13, (0.23, 0.02), (0.35, 0.07)),
          (-0.02, (0.24, 0.14), (0.35, 0.36))),
    leg_col=(0.46, 0.25, 0.12), leg_dark=(0.22, 0.11, 0.05),
    cerci_len=0.14, cerci_spread=1.4,
    ovipositor=0.62, ovi_lift=0.05, ovi_col=(0.34, 0.17, 0.07), ovi_tip_col=(0.72, 0.50, 0.26),
)


if __name__ == "__main__":
    nh.run(lambda: rc.build(SPEC), "Anthracoblattina", ground=(0.30, 0.26, 0.18),
           views=((35, 30), (0, 80), (-90, 10)))
