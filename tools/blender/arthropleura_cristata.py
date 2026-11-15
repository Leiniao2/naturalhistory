"""
Procedural Arthropleura cristata (a smaller Carboniferous Arthropleura, ~0.3-0.5 m) for map colonies.

Same body plan as A. armata (nh_arthropleura.py): a half-moon collum shield and
a long run of shingled tergites with flat, back-pointing paranota, two pairs of
short legs per ring, a small head with short antennae and stalked eyes. As the
name suggests it is modelled as the crested form: each tergite carries a sharp
transverse crest across its hind half plus a pair of longitudinal keels, so a
double dorsal ridge runs down the body, instead of A. armata's rows of nodes.
It is also proportionally a little narrower, with a higher axial ridge and
slightly fewer rings, and coloured a warmer reddish brown with pale crests.
A. cristata is known only from fragments, so these differences are plausible
rather than exact. Lighter than A. armata (fewer grid rows, three-sided legs).
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/arthropleura_cristata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArthropleuraCristata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_arthropleura as ap  # noqa: E402

SPEC = ap.Spec(
    name="ArthropleuraCristata",
    segments=26,
    length=1.7,
    half_width=0.17,
    dome=0.060,
    axial=0.46,
    lobe_sweep=1.0,
    cols=12,
    rows=4,
    nodes=0,
    crest=0.013,
    keels=0.014,
    leg_sides=3,
    leg_reach=0.045,
    antenna=0.10,
    bend=0.08,
    axis_col=(0.36, 0.15, 0.08),
    para_col=(0.50, 0.25, 0.12),
    edge_col=(0.70, 0.46, 0.26),
    groove_col=(0.14, 0.06, 0.03),
    crest_col=(0.64, 0.38, 0.18),
    leg_col=(0.52, 0.30, 0.16),
    leg_tip_col=(0.30, 0.16, 0.08),
)


if __name__ == "__main__":
    nh.run(lambda: ap.build(SPEC), "ArthropleuraCristata", ground=(0.24, 0.22, 0.14),
           views=((35, 30), (0, 75), (-90, 10)))
