"""
Procedural Elonichthys peltigerus (Late Carboniferous Mazon Creek of Illinois and Linton of
Ohio, a palaeoniscoid ray-finned fish about 15-20 cm long) for map colonies (Swim style).

A torpedo/spindle-shaped body armoured in thick, shiny rhombic ganoid scales (painted as a
fine diamond lattice of glossy scale rows), a large eye set far forward, a big oblique mouth
with small sharp teeth, a single dorsal fin set far back opposite the anal fin, and a
strongly heterocercal tail: the body sweeps up into the long upper lobe, with a shorter
lower lobe below. Dark olive back, bronze-gold flanks, silvery belly.
Built with nh_car_fish (paint wrapped with the scale lattice). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/elonichthys_peltigerus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Elonichthys.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
import nh_b2_carboniferous_fish as bf  # noqa: E402

def scaled_paint(sp):
    """Clean back/flank/belly gradient with a diamond lattice of ganoid scale rows (dark seams,
    glossy centres) over the body; the fins keep the plain fin colour."""

    def paint(co, n):
        h = max(cf.interp(sp.height, co.y), 1e-3)
        w = max(cf.interp(sp.width, co.y), 1e-3)
        z = co.z - cf.zmid(sp, co.y)
        up = z / h
        if abs(z) > h * 1.12 or abs(co.x) > w * 1.2:
            return sp.fin_col
        c = nh.lerp(sp.flank, sp.back, nh.smoothstep(0.15, 0.7, up))
        c = nh.lerp(c, sp.belly, nh.smoothstep(-0.15, -0.6, up))
        if co.y < -0.47:  # head: smooth enamelled bones, no scale rows
            return c
        p = 0.058
        u = ((co.y * 0.7 + z) / p) % 1.0
        v = ((co.y * 0.7 - z) / p) % 1.0
        seam = max(nh.smoothstep(0.14, 0.0, min(u, 1 - u)), nh.smoothstep(0.14, 0.0, min(v, 1 - v)))
        glow = max(0.0, 1.0 - 4.0 * ((u - 0.5) ** 2 + (v - 0.5) ** 2))
        c = tuple(min(1.0, ch * (1.0 + 0.22 * glow)) for ch in c)
        return nh.lerp(c, (c[0] * 0.40, c[1] * 0.36, c[2] * 0.28), 0.8 * seam)
    return paint


cf.make_paint = scaled_paint


def details(sp, tree):
    return bf.mouth_line(sp, tree, -0.60, -0.47, -0.012, -0.055, r=0.004)


SPEC = cf.Spec(
    name="Elonichthys",
    mid=[(-0.6, 0.0), (0.15, 0.0), (0.35, 0.03), (0.6, 0.15)],
    height=[(-0.6, 0.0), (-0.59, 0.04), (-0.5, 0.085), (-0.32, 0.125), (-0.1, 0.125), (0.12, 0.09),
            (0.30, 0.045), (0.42, 0.028), (0.6, 0.004)],
    width=[(-0.6, 0.0), (-0.59, 0.035), (-0.5, 0.06), (-0.32, 0.07), (-0.1, 0.065), (0.12, 0.045),
           (0.30, 0.025), (0.42, 0.016), (0.6, 0.003)],
    fins=[
        # heterocercal tail: long upper lobe along the upturned body, short lower lobe
        ("mid", [(0.36, 0.02), (0.50, 0.10), (0.68, 0.21), (0.64, 0.15), (0.55, 0.04), (0.51, -0.01),
                 (0.56, -0.12), (0.49, -0.12), (0.40, -0.04)]),
        # single dorsal far back, opposite the anal
        ("mid", [(0.08, 0.08), (0.14, 0.19), (0.19, 0.18), (0.24, 0.05)]),
        ("mid", [(0.08, -0.08), (0.14, -0.18), (0.20, -0.17), (0.25, -0.04)]),
        # pectorals and small pelvics
        ("pair", (0.055, -0.36, -0.08), [(0, 0, 0), (0.0, 0.06, 0.0), (0.10, 0.14, -0.04), (0.10, 0.09, -0.04)]),
        ("pair", (0.04, -0.02, -0.10), [(0, 0, 0), (0.0, 0.05, 0.0), (0.06, 0.09, -0.04), (0.05, 0.04, -0.04)]),
    ],
    fin_th=0.012,
    voxel=0.006, max_tris=9000,
    back=(0.20, 0.22, 0.12), flank=(0.66, 0.50, 0.22), belly=(0.86, 0.86, 0.82),
    fin_col=(0.30, 0.28, 0.16), pattern="none",
    eye=(-0.52, 0.03, 0.036), iris=(0.85, 0.70, 0.30), gills=0,
    teeth=9, tooth_len=0.012, mouth_y=(-0.585, -0.48), mouth_z=-0.035,
    extra=[details],
)

if __name__ == "__main__":
    cf.run(SPEC)
