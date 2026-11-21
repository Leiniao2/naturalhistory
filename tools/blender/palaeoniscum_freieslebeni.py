"""
Procedural Palaeoniscum freieslebeni (Late Permian ray-finned fish, ~30 cm) for map colonies.

The classic fossil fish of the Kupferschiefer / Marl Slate sea: a spindle-shaped body
covered in shiny, diamond-shaped (ganoid) scales, a large eye far forward, a wide mouth
with small sharp teeth, a single dorsal fin facing the anal fin and a deeply forked,
strongly upturned tail. Dark steel-blue back, silvery flanks, rhombic scale lattice.
Built with nh_car_fish. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/palaeoniscum_freieslebeni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Palaeoniscum.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402

SPEC = cf.Spec(
    name="Palaeoniscum",
    mid=[(-0.6, 0.0), (0.2, 0.0), (0.38, 0.02), (0.6, 0.08)],
    height=[(-0.6, 0.0), (-0.57, 0.050), (-0.45, 0.090), (-0.20, 0.110), (0.05, 0.095), (0.25, 0.055),
            (0.38, 0.028), (0.6, 0.004)],
    width=[(-0.6, 0.0), (-0.57, 0.040), (-0.45, 0.062), (-0.20, 0.068), (0.05, 0.055), (0.25, 0.032),
           (0.38, 0.016), (0.6, 0.002)],
    fins=[
        ("mid", [(0.00, 0.085), (0.05, 0.175), (0.10, 0.165), (0.18, 0.065)]),      # dorsal
        ("mid", [(0.06, -0.080), (0.12, -0.155), (0.20, -0.140), (0.24, -0.050)]),  # anal
        ("mid", [(0.36, 0.035), (0.64, 0.17), (0.61, 0.12), (0.52, 0.03), (0.57, -0.11), (0.52, -0.12), (0.38, -0.01)]),
        ("pair", (0.05, -0.38, -0.06), [(0, 0, 0), (0.09, 0.14, -0.05), (0.04, 0.15, -0.04), (0.0, 0.05, 0.0)]),
        ("pair", (0.03, -0.08, -0.085), [(0, 0, 0), (0.05, 0.10, -0.04), (0.02, 0.10, -0.03)]),
    ],
    fin_th=0.008,
    back=(0.16, 0.22, 0.32), flank=(0.62, 0.66, 0.70), belly=(0.90, 0.90, 0.86),
    fin_col=(0.30, 0.34, 0.40), pattern="none",
    eye=(-0.50, 0.025, 0.025), iris=(0.85, 0.80, 0.55), gills=0,
    teeth=5, tooth_len=0.008, mouth_y=(-0.585, -0.50), mouth_z=-0.02,
    voxel=0.004, max_tris=14000,
)

_base_paint = cf.make_paint


def make_paint(sp):
    base = _base_paint(sp)

    def paint(co, n):
        c = base(co, n)
        h, w = max(cf.interp(sp.height, co.y), 1e-3), max(cf.interp(sp.width, co.y), 1e-3)
        if abs(co.z - cf.zmid(sp, co.y)) > h * 1.15 or abs(co.x) > w * 1.25 or co.y < -0.45:
            return c
        # rhombic ganoid scale lattice: two families of diagonal lines
        a = (co.y * 28 + co.z * 28) % 1.0
        b = (co.y * 28 - co.z * 28) % 1.0
        line = max(nh.smoothstep(0.80, 0.93, a), nh.smoothstep(0.80, 0.93, b))
        return nh.lerp(c, tuple(x * 0.55 for x in c), line)
    return paint


cf.make_paint = make_paint

if __name__ == "__main__":
    cf.run(SPEC)
