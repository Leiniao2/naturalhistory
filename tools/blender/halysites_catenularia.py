"""
Procedural Halysites catenularia (Linnaeus, 1767), the classic Silurian chain coral (type
species of Halysites; neotype from Gotland, Sweden), for the map: a domed colony of palisade
walls, each a single row of elliptical corallites, meeting to enclose open windows (lacunae).

H. catenularia has subelliptical corallites about 2 mm long and lacunae of very variable size
and shape, often elongated and arranged in roughly parallel ranks, some several centimetres
long. Here: a fairly tall dome (the walls are highest in the middle) whose hexagonal lacuna
lattice has many walls removed along one direction, so the windows come out long and uneven,
with larger, more elliptical corallites than H. priscus (see halysites_priscus.py). Pale cream
walls, olive-green polyps with pale tips (colours are a guess). Built with nh_halysites.py.
Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/halysites_catenularia.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HalysitesCatenularia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_halysites as hl  # noqa: E402

COLONY = hl.Colony(
    name="HalysitesCatenularia",
    seed=17,
    radius=0.72,
    outline_noise=0.18,
    height=0.55,
    edge_height=0.13,
    dome_power=1.3,
    cell=0.31,
    jitter=0.30,
    corallite=0.086,
    width_ratio=0.62,      # subelliptical
    merge=0.7,
    merge_dir=0.0,
    max_merge=3,           # windows of one to three lattice cells
    polyp_frac=0.3,
    wall=(0.92, 0.87, 0.74),
    wall_dark=(0.64, 0.56, 0.43),
    rim=(0.97, 0.94, 0.84),
    calice=(0.28, 0.20, 0.12),
    polyp=(0.42, 0.52, 0.22),
    polyp_tip=(0.86, 0.90, 0.56),
)


def build():
    return hl.build_colony(COLONY)


if __name__ == "__main__":
    nh.run(build, "HalysitesCatenularia", ground=(0.75, 0.70, 0.55),
           views=((35, 30), (10, 70), (-90, 12)))
