"""
Procedural Eoarthropleura devonica (Early-Middle Devonian arthropleurid myriapod, Germany
and New York) for map colonies (Ground style).

A small, early relative of the giant Carboniferous Arthropleura, a few centimetres long and
built the same way (nh_arthropleura.py): a short, very flat body of about a dozen rings,
each tergite spreading into broad, wing-like side lobes (paranota) whose corners point
back, so the outline is saw-toothed; a little head under a half-moon collum with short
antennae, and two pairs of short legs per ring. Proportionally broader and stubbier than
Arthropleura, with a pair of small tubercles on each tergite. Dark grey-brown with pale
lobe edges. Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/eoarthropleura_devonica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eoarthropleura.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_arthropleura as ap  # noqa: E402

SPEC = ap.Spec(
    name="Eoarthropleura",
    segments=13,
    length=1.25,
    half_width=0.25,
    dome=0.05,
    axial=0.36,
    lobe_sweep=1.25,
    cols=12,
    rows=4,
    nodes=1,
    node_size=0.018,
    leg_sides=3,
    leg_reach=0.04,
    antenna=0.13,
    bend=0.04,
    axis_col=(0.24, 0.20, 0.16),
    para_col=(0.38, 0.32, 0.24),
    edge_col=(0.72, 0.62, 0.44),
    groove_col=(0.10, 0.08, 0.06),
    node_col=(0.62, 0.52, 0.36),
    leg_col=(0.44, 0.36, 0.26),
    leg_tip_col=(0.24, 0.20, 0.14),
)


if __name__ == "__main__":
    nh.run(lambda: ap.build(SPEC), "Eoarthropleura", ground=(0.24, 0.22, 0.14),
           views=((35, 30), (0, 75), (-90, 10)))
