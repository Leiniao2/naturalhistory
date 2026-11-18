"""
Procedural Maclurites magnus Lesueur, 1818 (Middle Ordovician sea snail of North America, common
in the limestones of New York and the Lake Champlain region) for the map (Fixed style).

A big, heavy, low-spired snail several centimetres to over 8 cm across: its thick shell is coiled
almost flat, with a flat upper face and a broad, rounded body whorl, finely marked by growth
lines. Its trademark is the operculum, a very thick, horn-shaped calcareous lid on the back of the
foot that sealed the large aperture like a trapdoor; when closed it may have also anchored the
snail to the sea floor. Two snails rest on a patch of mud, one creeping with its foot and lid out,
one shut tight. Grey-buff shell, dark brown lid (colours conjectural). Built with nh_ord_shells.

Usage:
  blender --background --python tools/blender/maclurites_magnus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MacluritesMagnus.fbx (pivot on the sea floor, z = 0)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402
import nh_ord_shells as sh  # noqa: E402

TURNS = 3.4
W = 2.4
SPIRE = 0.06
SECTION = 0.62
SHELL = (0.70, 0.66, 0.56)
CORD = (0.50, 0.46, 0.38)
LID = (0.34, 0.22, 0.14)
LID_RIM = (0.62, 0.48, 0.32)
# (x, y, yaw, scale, lid open)
SNAILS = ((-0.15, -0.10, 210, 1.0, True), (0.55, 0.45, 40, 0.75, False))


def operculum(mb, m, open_):
    """Thick, horn-shaped lid: a cone whose flat face fits the aperture."""
    th = TURNS * math.tau
    R = 0.3
    ap = Vector((R * math.cos(th), R * math.sin(th), -SPIRE * R))
    tan = Vector((-math.sin(th), math.cos(th), 0.0))
    out = Vector((math.cos(th), math.sin(th), 0.0))
    up = Vector((0, 0, 1))
    r = R * SECTION * 0.98
    if open_:
        # swung up and back on top of the extended foot, flat face up
        centre = ap + tan * r * 0.9 + up * (-r * 0.35) + out * (-r * 0.2)
        axis = (up * 0.8 + tan * 0.6).normalized()
    else:
        centre = ap + tan * r * 0.05
        axis = tan
    pts = [centre + axis * (-r * 0.05), centre + axis * (r * 0.25), centre + axis * (r * 0.55),
           centre + axis * (r * 0.75)]
    bm = nh.tube(pts, [r, r * 0.92, r * 0.55, 0.0], sides=16)
    nh.transform(bm, m)
    c0 = m @ centre
    mb.add(bm, lambda co, n: nh.lerp(LID_RIM, LID, nh.smoothstep(r * 0.4, r * 0.9, (co - c0).length * 1.0 / max(m.to_scale().x, 1e-3))))


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 1.05, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    for x, y, yaw, k, open_ in SNAILS:
        m = Matrix.Translation(Vector((x, y, 0.2 * k))) @ Matrix.Rotation(math.radians(yaw), 4, "Z") \
            @ Matrix.Scale(k, 4)
        sh.snail_shell(mb, turns=TURNS, w=W, spire=SPIRE, section=SECTION, cords=3,
                       shell=SHELL, cord=CORD, foot=(0.62, 0.52, 0.42), matrix=m)
        operculum(mb, m, open_)
    obj = mb.to_object("MacluritesMagnus", roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "MacluritesMagnus", **ec.VIEWS)
