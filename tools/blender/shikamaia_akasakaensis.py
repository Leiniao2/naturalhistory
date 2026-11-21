"""
Procedural Shikamaia akasakaensis (Middle Permian alatoconchid bivalve, up to ~1 m) for map colonies.

A giant, bizarre clam of the warm Tethyan reef lagoons, first found in the Akasaka
Limestone of Japan: the thick central part of the shell, with its beaks, is drawn out on
both sides into enormous, thin, flat 'wings', so the whole shell looks like a boomerang
lying on the sea floor, wings spread to stop it sinking into the soft lime mud. The
valves gape slightly along the edge to show the mantle. Cream-grey shell with concentric
growth bands, a darker commissure line and an olive-brown mantle edge. Mud patch base.
Faces -Y, pivot on the sea floor (Fixed style).

Usage:
  blender --background --python tools/blender/shikamaia_akasakaensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Shikamaia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, Matrix, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as oe  # noqa: E402

SHELL = (0.90, 0.84, 0.70)
BAND = (0.58, 0.48, 0.36)
UMBO = (0.74, 0.66, 0.52)
LIP = (0.30, 0.26, 0.20)
MANTLE = (0.46, 0.42, 0.22)
MUD = ((0.46, 0.44, 0.38), (0.56, 0.53, 0.46))

SPAN, DEPTH, THICK = 0.80, 0.27, 0.16
SWEEP = 0.28




def build_shell(scale, at, yaw):
    bm = nh.uv_ellipsoid((0, 0, 0), (1, 1, 1), segments=64, rings=24)
    for v in bm.verts:
        x, y, z = v.co
        t = abs(x)                                   # 0 centre .. 1 wing tip
        thick = THICK * (0.25 + 0.75 * math.exp(-(t / 0.22) ** 2))
        depth = DEPTH * (0.55 + 0.45 * math.exp(-(t / 0.3) ** 2)) * (1.0 - 0.35 * t ** 3)
        v.co = Vector((x * SPAN, y * depth + SWEEP * t ** 2 * SPAN * 0.5, z * thick * (1.0 if z > 0 else 0.45)))
    # colours: growth bands around the beaks (at the centre, slightly back), dark commissure
    beak = Vector((0, DEPTH * 0.55, 0))

    def col(co, n):
        d = math.hypot(co.x / SPAN, (co.y - beak.y) / (DEPTH * 1.2))
        c = nh.lerp(SHELL, BAND, nh.smoothstep(0.55, 0.9, 0.5 + 0.5 * math.sin(d * 46)))
        c = nh.lerp(c, UMBO, nh.smoothstep(0.18, 0.05, d))
        h = co.z
        c = nh.lerp(c, LIP, nh.smoothstep(0.012, 0.0, abs(h)))
        k = 0.92 + 0.12 * noise.noise(co * 25)
        return tuple(x * k for x in c)
    m = Matrix.Translation(Vector(at)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Scale(scale, 4)
    nh.transform(bm, Matrix.Translation(Vector((0, 0, THICK * 0.45))))
    nh.transform(bm, m)
    parts = [(bm, col)]
    # mantle showing in the gape along the front edge
    pts = []
    for i in range(25):
        u = -0.75 + 1.5 * i / 24
        t = abs(u)
        depth = DEPTH * (0.55 + 0.45 * math.exp(-(t / 0.3) ** 2)) * (1.0 - 0.35 * t ** 3)
        y = -depth + SWEEP * t ** 2 * SPAN * 0.5 + 0.004
        pts.append((m @ Vector((u * SPAN, y, THICK * 0.45, 1.0))).to_3d())
    parts.append((nh.tube(pts, [0.012 * scale] * len(pts), sides=6), MANTLE))
    return parts


def build():
    mb = nh.MeshBuilder()
    oe.mud_patch(mb, 0.95, MUD, seed=6)
    for bm, col in build_shell(1.0, (0.0, 0.18, 0.0), math.radians(0)):
        mb.add(bm, col)
    for bm, col in build_shell(0.55, (0.20, -0.42, 0.0), math.radians(160)):
        mb.add(bm, col)
    return oe._finish(mb, "Shikamaia", roughness=0.55)


if __name__ == "__main__":
    nh.run(build, "Shikamaia", ground=(0.62, 0.58, 0.48), views=((30, 30), (10, 75), (-100, 12)))
