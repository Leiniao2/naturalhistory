"""
Procedural Eospirifer radiatus (one of the first spiriferid brachiopods, shell about
3-4 cm wide, from the Silurian (Wenlock) of Britain, Gotland and North America) for
map colonies (Fixed).

An early "winged" lamp shell, but with only short, rounded wings: a moderately wide
hinge line, a rounded, transversely oval outline, a deep ventral valve with a curved
beak and a low triangular interarea, a smooth, broad fold and sulcus at the front, and
many fine, low radiating ribs (costellae) on the flanks - hence "radiatus". Inside, a
pair of spiral supports held its feeding tentacles. Three shells lying on grey reef mud,
one gaping to show its spiralia. Built with nh_brachiopod.spiriferid.
Fixed style: pivot on the sea floor, facing -Y.

Usage:
  blender --background --python tools/blender/eospirifer_radiatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EospiriferRadiatus.fbx
"""

import math
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_brachiopod as br  # noqa: E402

NAME = "EospiriferRadiatus"
MUD = ((0.40, 0.39, 0.35), (0.54, 0.52, 0.46))   # pale grey reef mud
SPEC = br.SpiriferSpec(
    width=0.82, length=0.52, body_w=0.86, ear_from=1.25, ear_exp=1.6,
    dorsal_h=0.11, ventral_h=0.18, fold_w=0.24, fold_h=0.05, uplift=0.08,
    ribs=22, rib_amp=0.006, growth_lines=9, thick=0.012, n_theta=64, n_r=9,
    beak=0.07, interarea=0.05,
    shell=(0.78, 0.70, 0.56), shell_dark=(0.54, 0.47, 0.37), inside=(0.24, 0.20, 0.16),
    spiralia_col=(0.92, 0.88, 0.78),
)

# (x, y, yaw deg, tilt deg about the hinge, gape deg, spiralia, scale, palette shift)
SHELLS = (
    (0.00, -0.12, 0, 4, 9, True, 1.0, 0.0),
    (-0.42, 0.36, 155, 6, 4, False, 0.88, 0.4),
    (0.55, 0.30, -35, -3, 3, False, 0.80, 0.8),
)
GREY = ((0.66, 0.64, 0.58), (0.45, 0.44, 0.40))   # greyer shells mixed in


def build():
    mb = nh.MeshBuilder()
    height = br.seabed(mb, 0.95, MUD, seed=11, base=0.03, relief=0.012, n_r=12, n_a=48, oval=0.8)
    for i, (x, y, yaw, tilt, gape, spir, k, grey) in enumerate(SHELLS):
        spec = replace(SPEC, width=SPEC.width * k, length=SPEC.length * k, dorsal_h=SPEC.dorsal_h * k,
                       ventral_h=SPEC.ventral_h * k, fold_h=SPEC.fold_h * k, uplift=SPEC.uplift * k,
                       rib_amp=SPEC.rib_amp * k, beak=SPEC.beak * k, interarea=SPEC.interarea * k,
                       shell=nh.lerp(SPEC.shell, GREY[0], grey), shell_dark=nh.lerp(SPEC.shell_dark, GREY[1], grey))
        parts = br.spiriferid(spec, seed=i + 1, gape=math.radians(gape), spiralia=spir)
        # shell centre sits a little in front of the beak; rest it on the mud, slightly sunk
        rot = Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(tilt), 4, "X")
        centre = Matrix.Translation(Vector((0, spec.length * 0.4, 0)))
        m = rot @ centre
        zmin = min((m @ v.co).z for bm, _c in parts for v in bm.verts)
        m = Matrix.Translation(Vector((x, y, height(x, y) - zmin - 0.025 * k))) @ m
        br.place(mb, parts, m)
    return br.finish(mb, NAME, roughness=0.65)


if __name__ == "__main__":
    nh.run(build, NAME, ground=MUD[0], background=(0.05, 0.14, 0.18), views=br.VIEWS)
