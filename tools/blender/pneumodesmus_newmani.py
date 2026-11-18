"""
Procedural Pneumodesmus newmani (Silurian millipede from the Cowie Formation near
Stonehaven, Scotland, about 1 cm long, dated to around 425 million years ago) for map
colonies (Ground style).

One of the oldest known land animals and the oldest with direct evidence of breathing
air: a small millipede whose body rings carry the openings of its breathing tubes
(spiracles). A short head with antennae, then a row of domed body rings with flat side
keels (paranota) and a pair of tiny bumps on each ring, two pairs of short legs under
each ring. Dark chocolate-brown rings with pale orange keel edges. Built with
nh_arthropleura.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pneumodesmus_newmani.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PneumodesmusNewmani.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_arthropleura as ap  # noqa: E402

SPEC = ap.Spec(
    name="PneumodesmusNewmani",
    segments=14,
    length=1.5,
    half_width=0.13,
    dome=0.07,
    axial=0.62,
    paranota_droop=0.015,
    lobe_sweep=0.55,
    clearance=0.04,
    cols=12,
    rows=4,
    nodes=1,
    node_size=0.014,
    leg_sides=4,
    leg_reach=0.05,
    antenna=0.18,
    bend=0.12,
    axis_col=(0.24, 0.14, 0.08),
    para_col=(0.36, 0.20, 0.10),
    edge_col=(0.86, 0.52, 0.20),
    groove_col=(0.08, 0.05, 0.03),
    node_col=(0.10, 0.06, 0.04),
    leg_col=(0.52, 0.36, 0.22),
    leg_tip_col=(0.30, 0.20, 0.12),
)


if __name__ == "__main__":
    nh.run(lambda: ap.build(SPEC), SPEC.name, ground=(0.24, 0.22, 0.14), views=((35, 30), (0, 75), (-90, 10)))
