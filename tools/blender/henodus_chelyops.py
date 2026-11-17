"""
Procedural Henodus chelyops (Late Triassic cyamodontoid placodont, ~1 m) for map colonies
(Swim style).

A strange, turtle-like placodont from the Carnian lagoon deposits of Tübingen, Germany,
about 230 million years ago, and probably a brackish-water animal. Its body was covered
by a very flat, almost rectangular shell wider than it was long, made of a mosaic of
small bony plates, with the limbs and short tail poking out at the edges. The head was
box-shaped with a broad, square-fronted, nearly toothless snout that may have carried
horny plates or baleen-like structures for straining or grazing food. Built with the
shared Triassic tetrapod recipe (nh_tri_tetrapod.py) plus a crisp flat carapace with a
painted plate mosaic. Painted olive-brown with pale seams (speculative). Faces -Y, pivot
at the body centre.

Usage:
  blender --background --python tools/blender/henodus_chelyops.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Henodus.fbx
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.40, 0.36, 0.22)
SHELL_DARK = (0.24, 0.21, 0.13)
SEAM = (0.66, 0.60, 0.44)
SC = Vector((0.0, -0.10, 0.0))
RX, RY = 0.58, 0.50

AXIS = [
    (-1.00, 0.000, 0.090, 0.030),
    (-0.96, 0.002, 0.100, 0.042),
    (-0.88, 0.005, 0.095, 0.048),
    (-0.80, 0.005, 0.082, 0.044),
    (-0.72, 0.000, 0.075, 0.042),
    (-0.58, 0.000, 0.110, 0.048),
    (-0.10, 0.000, 0.360, 0.062),
    (0.30, 0.000, 0.120, 0.040),
    (0.55, 0.000, 0.050, 0.034),
    (0.75, 0.000, 0.025, 0.020),
    (0.90, 0.000, 0.003, 0.003),
]

FORE = tt.Limb(pts=[(0.30, -0.42, -0.02), (0.46, -0.46, -0.03), (0.52, -0.48, -0.035)],
               radii=[0.040, 0.032, 0.026], paddle=(0.075, 0.040, 105, 0))
HIND = tt.Limb(pts=[(0.30, 0.22, -0.02), (0.46, 0.27, -0.03), (0.52, 0.30, -0.035)],
               radii=[0.040, 0.032, 0.026], paddle=(0.070, 0.038, 135, 0))

rng = random.Random(7)
CENTRES = [(rng.uniform(-RX, RX), rng.uniform(SC.y - RY, SC.y + RY)) for _ in range(140)]


def shell_col(co, n):
    c = nh.lerp(SHELL, SHELL_DARK, nh.smoothstep(-0.2, 0.6, noise.noise(co * 6.0)))
    if co.z < SC.z - 0.005:
        c = nh.lerp(c, (0.78, 0.72, 0.56), 0.6)
    return nh.lerp(c, SEAM, 0.6 * tt.voronoi_edge(co, CENTRES, 0.016))


def shell(mb, surf, spec):
    mb.add(tt.dome(SC, RX, RY, 0.085, 0.045, power=3.6, segments=110, rings=44,
                   ridge=lambda x, y: 0.012 * max(0.0, 1.0 - abs(x) / 0.1)), shell_col)


SPEC = tt.TetrapodSpec(
    name="Henodus",
    axis=AXIS, power=2.8,
    limbs=[FORE, HIND],
    voxel=0.010, max_tris=8000,
    pivot="centre",
    mouth=(-1.0, -0.86, -0.012, -0.006, 0.004), mouth_min_x=0.0,
    eyes=(-0.85, 0.040, 0.014, (0.70, 0.55, 0.20), 0.06),
    back=(0.32, 0.30, 0.20), flank=(0.48, 0.45, 0.32), belly=(0.80, 0.76, 0.60),
    pattern=("spots", (0.22, 0.20, 0.13), 22.0, 0.5),
    post=shell,
)

if __name__ == "__main__":
    tt.run(SPEC)
