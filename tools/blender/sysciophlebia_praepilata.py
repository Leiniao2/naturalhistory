"""
Procedural Sysciophlebia praepilata (latest Carboniferous spiloblattinid roachoid,
Commentry, France) for map colonies.

A small, neat roachoid (nh_roachoid.py) with the bold colour-patterned
forewings of its family, the Spiloblattinidae: each tegmen is pale cream with
dark chocolate longitudinal stripes following the vein fields (along the costal
field, between radius and media, along the cubitus and over the clavus), the
pale stripes left between them; the exact stripe layout is a plausible
stand-in for the species' real pattern. Short, fairly broad tegmina with a
rounded apex, a combed subcosta and radius, a forked media and cubitus and the
arched claval furrow. The pronotum is a broad, rounded shield, dark
chocolate with a wide cream rim. Dark body, banded legs, long antennae and
short cerci.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/sysciophlebia_praepilata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sysciophlebia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_roachoid as rc  # noqa: E402
from nh_roachoid import Vein  # noqa: E402

DARK = (0.17, 0.10, 0.05)


SPEC = rc.Spec(
    name="Sysciophlebia",
    wing_y0=-0.19, wing_len=0.64, wing_w=0.235, wing_cx=0.40, wing_narrow=0.38, wing_tip=2.0,
    wing_droop=0.045,
    veins=[
        Vein((0.04, 0.82), -10, 3, -55, -20, 0.25, 0.75, bow=0.03, width=0.0036),   # Sc
        Vein((0.04, 0.66), 70, 3, 10, 50, 0.45, 0.88, bow=0.02, width=0.0040),      # R
        Vein((0.04, 0.50), 100, 1, 84, 84, 0.65, 0.65, width=0.0036),               # M
        Vein((0.06, 0.38), 158, 2, 126, 144, 0.40, 0.75, bow=-0.03, width=0.0034),  # CuA
        Vein((0.02, 0.32), 196, bow=-0.10, width=0.0038),                           # CuP
        Vein((0.03, 0.22), 214, 2, 204, 226, 0.0, 0.0, bow=-0.05, width=0.0024),    # A
    ],
    decals=[  # dark longitudinal stripes in wing (u, v) space, so they follow the outline
        ("region", 0.05, 0.72, 0.84, 0.97, DARK),     # along the costal field
        ("region", 0.10, 0.98, 0.52, 0.66, DARK),     # between radius and media
        ("region", 0.30, 0.96, 0.18, 0.33, DARK),     # along the cubitus
        ("region", 0.04, 0.30, 0.04, 0.30, DARK),     # clavus
    ],
    wing_col=(0.82, 0.72, 0.50), wing_base_col=(0.60, 0.48, 0.30), vein_col=(0.30, 0.20, 0.10),
    pron_y=-0.31, pron_rx=0.200, pron_ry=0.150, pron_dome=0.040, pron_front=2.0, pron_hind=2.2,
    pron_col=(0.20, 0.12, 0.06), pron_rim=(0.86, 0.76, 0.54), pron_rim_at=0.72,
    body_col=(0.16, 0.10, 0.05), body_band_col=(0.55, 0.44, 0.28), abd_len=0.70, body_rx=0.15,
    antenna_len=0.58,
    leg_col=(0.62, 0.50, 0.32), leg_dark=(0.20, 0.13, 0.07), leg_thick=0.95,
    cerci_len=0.16,
)


if __name__ == "__main__":
    nh.run(lambda: rc.build(SPEC), "Sysciophlebia", ground=(0.30, 0.26, 0.18),
           views=((35, 30), (0, 80), (-90, 10)))
