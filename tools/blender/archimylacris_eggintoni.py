"""
Procedural Archimylacris eggintoni (Late Carboniferous roachoid from the Coseley
ironstone nodules, British Coal Measures) for map colonies.

A stocky, broad roachoid (nh_roachoid.py), so it reads differently from the
slimmer Nova Scotian A. acadica: a big semicircular pronotum with a near
straight hind margin, almost black-brown with a pale rim and a darker central
disc; short, broad tegmina (about 2.7 times as long as wide) with a blunt
rounded apex that only just covers the abdomen, almost black-brown with a
broad pale cream costal field (a plausible colouring, not known from the
fossil), a strongly branched subcosta, pectinate radius, forked media, a
cubitus fanning to the inner margin and the arched claval furrow. Robust, long spiny legs, long antennae
and longer beaded cerci.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/archimylacris_eggintoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArchimylacrisEggintoni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_roachoid as rc  # noqa: E402
from nh_roachoid import Vein  # noqa: E402

PALE = (0.74, 0.62, 0.42)

SPEC = rc.Spec(
    name="ArchimylacrisEggintoni",
    wing_y0=-0.19, wing_len=0.66, wing_w=0.245, wing_cx=0.40, wing_narrow=0.30, wing_tip=2.6,
    wing_droop=0.050,
    veins=[
        Vein((0.04, 0.84), -14, 4, -62, -22, 0.15, 0.80, bow=0.03, width=0.0042),   # Sc
        Vein((0.04, 0.68), 70, 4, 6, 54, 0.40, 0.90, bow=0.02, width=0.0046),       # R
        Vein((0.04, 0.52), 102, 2, 82, 92, 0.55, 0.80, width=0.0042),               # M
        Vein((0.06, 0.40), 160, 3, 118, 144, 0.30, 0.80, bow=-0.03, width=0.0040),  # CuA
        Vein((0.02, 0.33), 198, bow=-0.12, width=0.0044),                           # CuP
        Vein((0.03, 0.22), 216, 2, 206, 228, 0.0, 0.0, bow=-0.05, width=0.0028),    # A
    ],
    decals=[("region", 0.03, 0.62, 0.80, 1.0, PALE)],
    wing_col=(0.26, 0.15, 0.08), wing_base_col=(0.18, 0.10, 0.05), vein_col=(0.10, 0.06, 0.03),
    pron_y=-0.31, pron_rx=0.225, pron_ry=0.165, pron_dome=0.046, pron_front=2.0, pron_hind=4.0,
    pron_taper=-0.06, pron_col=(0.16, 0.10, 0.06), pron_rim=(0.66, 0.54, 0.36), pron_rim_at=0.78,
    pron_mark="disc", pron_mark_col=(0.08, 0.05, 0.03),
    body_col=(0.18, 0.11, 0.06), abd_len=0.72, body_rx=0.16,
    antenna_len=0.60, antenna_curl=0.26,
    legs=((-0.26, (0.22, -0.07), (0.28, -0.19)),
          (-0.15, (0.27, 0.02), (0.41, 0.06)),
          (-0.04, (0.28, 0.13), (0.42, 0.34))),
    leg_col=(0.36, 0.22, 0.12), leg_dark=(0.15, 0.09, 0.05), leg_thick=1.15, spines=4,
    cerci_len=0.26, cerci_spread=1.0,
)


if __name__ == "__main__":
    nh.run(lambda: rc.build(SPEC), "ArchimylacrisEggintoni", ground=(0.30, 0.26, 0.18),
           views=((35, 30), (0, 80), (-90, 10)))
