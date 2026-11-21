"""
Procedural Janassa bituminosa (Late Permian petalodont, a relative of ratfish) for map colonies.

A strange, skate-like cartilaginous fish of the Kupferschiefer sea: a broad, flattened
body with huge, wing-like pectoral fins spread out to the sides, a short, blunt head with
eyes on top, a mouth full of rows of crushing tooth plates for shellfish, small pelvic
fins and a slim whip-like tail. Sandy brown above with darker spots, pale below.
Built with nh_car_fish. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/janassa_bituminosa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Janassa.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_fish as cf  # noqa: E402

SPEC = cf.Spec(
    name="Janassa",
    mid=[(-0.6, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.57, 0.035), (-0.45, 0.060), (-0.20, 0.065), (0.05, 0.050), (0.20, 0.025),
            (0.40, 0.010), (0.6, 0.002)],
    width=[(-0.6, 0.0), (-0.57, 0.070), (-0.45, 0.120), (-0.20, 0.140), (0.05, 0.110), (0.20, 0.040),
           (0.40, 0.014), (0.6, 0.002)],
    fins=[
        ("pair", (0.10, -0.45, -0.01), [(0, 0, 0), (0.18, 0.02, 0.0), (0.30, 0.18, -0.01),
                                         (0.22, 0.34, -0.01), (0.06, 0.40, 0.0), (0.0, 0.32, 0.0)], 0.014),
        ("pair", (0.05, 0.12, -0.02), [(0, 0, 0), (0.09, 0.03, 0.0), (0.08, 0.12, -0.005), (0.0, 0.10, 0.0)]),
        ("mid", [(0.10, 0.04), (0.16, 0.075), (0.24, 0.025)]),
        ("mid", [(0.40, 0.0), (0.55, 0.02), (0.60, 0.0), (0.55, -0.01)]),
    ],
    fin_th=0.010,
    back=(0.42, 0.34, 0.22), flank=(0.54, 0.46, 0.32), belly=(0.86, 0.82, 0.72),
    fin_col=(0.46, 0.38, 0.25), pattern="spots", pattern_col=(0.24, 0.18, 0.11), pattern_scale=0.9,
    eye=(-0.47, 0.045, 0.016), iris=(0.80, 0.72, 0.40), gills=0,
    teeth=6, tooth_len=0.008, mouth_y=(-0.595, -0.55), mouth_z=-0.02,
    voxel=0.005, max_tris=6000,
)

if __name__ == "__main__":
    cf.run(SPEC)
