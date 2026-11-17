"""
Procedural Mucrospirifer mucronatus (Middle Devonian spiriferid brachiopod, Hamilton Group,
New York, ~385 million years ago) for the map, Fixed style.

A "butterfly shell" much wider than long, about 4-6 cm across: the straight hinge line is
drawn out into long, pointed ears (mucronate), the lateral margins curving in behind them.
Strong rounded radial costae run out from the beak over both flanks, interlocking at the
zig-zag commissure; the dorsal valve carries a smooth, raised median fold and the deeper
ventral valve the matching sulcus, so the front of the commissure arches up in the middle.
Fine concentric growth lamellae, a small incurved ventral beak over a low triangular
interarea with its dark delthyrium. Tan-grey calcite. Three shells lie ventral valve down
on a patch of dark Hamilton mud, gaping slightly as in life; the widest-open one shows the
pale paired spiralia (the coiled supports of the feeding lophophore) whose cones point out
into the ears. Shared spiriferid code lives in nh_brachiopod.py.

Usage:
  blender --background --python tools/blender/mucrospirifer_mucronatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mucrospirifer.fbx

Faces -Y (the anterior commissure of the middle shell); pivot at the base of the mud patch (z = 0).
"""

import math
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_brachiopod as br  # noqa: E402

NAME = "Mucrospirifer"
MUD = ((0.26, 0.26, 0.24), (0.40, 0.39, 0.35))   # dark grey Hamilton mud
SPEC = br.SpiriferSpec(
    width=1.0, length=0.40, body_w=0.56, ear_from=0.95, ear_exp=2.2,
    dorsal_h=0.09, ventral_h=0.15, fold_w=0.26, fold_h=0.06, uplift=0.09,
    ribs=11, rib_amp=0.013, growth_lines=12, thick=0.012, n_theta=68, n_r=10,
    beak=0.05, interarea=0.05,
    shell=(0.72, 0.64, 0.51), shell_dark=(0.48, 0.43, 0.35), inside=(0.22, 0.19, 0.15),
    spiralia_col=(0.90, 0.86, 0.76),
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
