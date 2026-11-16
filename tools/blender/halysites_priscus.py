"""
Procedural Halysites priscus Klaamann, 1966 (a chain coral described from the earliest Silurian
Juuru Stage of Estonia, known from boreholes in central Estonia) for the map: a small, low
cushion of palisade walls, each a single row of corallites, enclosing open windows (lacunae).

Klaamann described it as a small corallum of rounded corallites (about 1.4-1.55 x 1.6-1.8 mm,
so smaller and less elongate than in H. catenularia) with rounded-polygonal lacunae and very
weak septal spines; he later (1979) treated it as a synonym of H. catenularia. Here: a small,
flat-topped cushion with an even net of small, roundish windows (no merged, elongated lacunae)
built from smaller, nearly round corallites, contrasting with the tall dome and long windows of
halysites_catenularia.py. Pale buff walls, rosy-orange polyps (colours are a guess). Built with
nh_halysites.py. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/halysites_priscus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HalysitesPriscus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_halysites as hl  # noqa: E402

COLONY = hl.Colony(
    name="HalysitesPriscus",
    seed=4,
    radius=0.56,
    outline_noise=0.10,
    height=0.26,
    edge_height=0.14,
    dome_power=3.0,        # flat-topped cushion
    cell=0.28,
    jitter=0.22,
    corallite=0.068,
    width_ratio=0.86,      # rounded corallites
    merge=0.0,             # small, evenly sized rounded-polygonal windows
    polyp_frac=0.45,
    wall=(0.90, 0.83, 0.68),
    wall_dark=(0.62, 0.53, 0.40),
    rim=(0.96, 0.91, 0.79),
    calice=(0.32, 0.19, 0.12),
    polyp=(0.88, 0.45, 0.32),
    polyp_tip=(1.0, 0.80, 0.62),
)


def build():
    return hl.build_colony(COLONY)


if __name__ == "__main__":
    nh.run(build, "HalysitesPriscus", ground=(0.75, 0.70, 0.55),
           views=((35, 30), (10, 70), (-90, 12)))
