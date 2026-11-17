"""
Procedural Platystrophia ponderosa (Late Ordovician orthide brachiopod, abundant in the
Cincinnatian of Ohio, Indiana and Kentucky; shell up to about 4-5 cm wide) for the map
(Fixed style).

A large, thick, strongly biconvex brachiopod: a straight hinge line a little wider than
the rounded body with short pointed ears, a few coarse, sharp-crested ribs on each flank,
a high median fold on the dorsal valve with a deep matching sulcus in the ventral one,
and a zig-zag commissure where the ribs interlock. Three shells lie on a patch of mud.
Grey-buff (colour conjectural). Built with nh_brachiopod.spiriferid (like
mucrospirifer_mucronatus.py), which handles strophic, ribbed, folded shells.

Usage:
  blender --background --python tools/blender/platystrophia_ponderosa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PlatystrophiaPonderosa.fbx (pivot on the sea floor, z = 0)
"""

import math
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_brachiopod as br  # noqa: E402

NAME = "PlatystrophiaPonderosa"
MUD = ((0.30, 0.29, 0.26), (0.44, 0.42, 0.37))
SPEC = br.SpiriferSpec(
    width=0.95, length=0.66, body_w=0.92, ear_from=1.25, ear_exp=1.6,
    dorsal_h=0.17, ventral_h=0.16, fold_w=0.30, fold_h=0.12, uplift=0.17,
    ribs=5, rib_amp=0.028, growth_lines=8, thick=0.014, n_theta=64, n_r=10,
    beak=0.07, interarea=0.05,
    shell=(0.74, 0.70, 0.60), shell_dark=(0.50, 0.47, 0.40), inside=(0.25, 0.22, 0.18),
)

SHELLS = (
    (0.00, -0.10, 10, 4, 6, 1.0),
    (-0.48, 0.38, 150, 6, 2, 0.82),
    (0.52, 0.34, -40, -3, 2, 0.75),
)


def build():
    mb = nh.MeshBuilder()
    height = br.seabed(mb, 0.95, MUD, seed=5, base=0.03, relief=0.012, n_r=12, n_a=48, oval=0.8)
    for i, (x, y, yaw, tilt, gape, k) in enumerate(SHELLS):
        spec = replace(SPEC, width=SPEC.width * k, length=SPEC.length * k, dorsal_h=SPEC.dorsal_h * k,
                       ventral_h=SPEC.ventral_h * k, fold_h=SPEC.fold_h * k, uplift=SPEC.uplift * k,
                       rib_amp=SPEC.rib_amp * k, beak=SPEC.beak * k, interarea=SPEC.interarea * k)
        parts = br.spiriferid(spec, seed=i + 1, gape=math.radians(gape), spiralia=False)
        rot = Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(tilt), 4, "X")
        m = rot @ Matrix.Translation(Vector((0, spec.length * 0.4, 0)))
        zmin = min((m @ v.co).z for bm, _c in parts for v in bm.verts)
        m = Matrix.Translation(Vector((x, y, height(x, y) - zmin - 0.025 * k))) @ m
        br.place(mb, parts, m)
    return br.finish(mb, NAME, roughness=0.65)


if __name__ == "__main__":
    nh.run(build, NAME, ground=MUD[0], background=(0.05, 0.14, 0.18), views=br.VIEWS)
