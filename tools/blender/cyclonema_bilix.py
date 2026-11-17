"""
Procedural Cyclonema bilix (Late Ordovician sea snail, very common in the Cincinnatian
of Ohio, Indiana and Kentucky; shell about 2 cm high) for the map (Fixed style).

A small turbiniform (top-shaped) gastropod: a few rounded whorls expanding quickly into
a large body whorl and a round aperture, the whole shell covered in fine raised spiral
cords crossed by growth lines. Three snails creep on a patch of mud, foot and
tentacles out. Buff shell with darker cords (colour conjectural). Built with
nh_ord_shells.py.

Usage:
  blender --background --python tools/blender/cyclonema_bilix.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CyclonemaBilix.fbx (pivot on the sea floor, z = 0)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402
import nh_ord_shells as sh  # noqa: E402

SNAILS = ((0.0, -0.05, 200, 1.0), (-0.55, 0.40, 120, 0.8), (0.55, 0.35, 300, 0.7))


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 1.0, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    for x, y, yaw, k in SNAILS:
        m = Matrix.Translation(Vector((x, y, 0.62 * k))) @ Matrix.Rotation(math.radians(yaw), 4, "Z") \
            @ Matrix.Scale(k, 4)
        sh.snail_shell(mb, turns=4.0, w=1.9, spire=1.5, section=0.66, cords=9,
                       shell=(0.80, 0.70, 0.52), cord=(0.52, 0.40, 0.26), matrix=m)
    obj = mb.to_object("CyclonemaBilix", roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "CyclonemaBilix", **ec.VIEWS)
