"""
Procedural Arthropleura armata (giant Carboniferous myriapod, ~2 m) for map colonies.

The largest known land arthropod: a long, broad, flat millipede-like body of a
half-moon collum shield plus 30 shingled tergites, each with a raised axial
part and wide flat paranota (lateral lobes) whose corners point backwards,
giving a saw-toothed outline; two rows of dark tubercles (nodes) run along
every tergite. Two pairs of short legs per ring peek out beyond the paranota,
a small head with short antennae and little stalked eyes sits under the collum,
and a small anal plate closes the body. Chestnut brown with paler lobe edges;
the body curves gently as if walking. Built with nh_arthropleura.py, shared
with A. cristata (exact differences between the species are poorly known from
the fragmentary fossils, so A. armata is modelled as the broad, nodular form).
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/arthropleura_armata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArthropleuraArmata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_arthropleura as ap  # noqa: E402

SPEC = ap.Spec(
    name="ArthropleuraArmata",
    segments=30,
    length=1.9,
    half_width=0.22,
    dome=0.055,
    axial=0.42,
    lobe_sweep=0.85,
    cols=14,
    rows=4,
    nodes=3,
    node_size=0.017,
    leg_sides=4,
    bend=0.06,
)


if __name__ == "__main__":
    nh.run(lambda: ap.build(SPEC), "ArthropleuraArmata", ground=(0.24, 0.22, 0.14),
           views=((35, 30), (0, 75), (-90, 10)))
