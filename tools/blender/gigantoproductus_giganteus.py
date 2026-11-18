"""
Procedural Gigantoproductus giganteus (Early Carboniferous, Visean, of Britain and Europe,
the largest brachiopod that ever lived, up to about 30 cm wide) for the map.

A productid lamp shell lying free on the sea floor: a huge, thick, strongly convex ventral
valve, much wider than long, with a straight hinge line drawn out into short ears, a broad
incurved beak at the back and fine radial ribs crossed by concentric growth wrinkles; the
flat to concave dorsal valve sits inside it like a lid, and the shell gapes slightly at the
front to feed. Three shells of different sizes half-sunk in pale lime mud, cream to buff.
Fixed style: faces -Y, pivot on the sea floor (z = 0).

Usage:
  blender --background --python tools/blender/gigantoproductus_giganteus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gigantoproductus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_brachiopod as br  # noqa: E402

NAME = "Gigantoproductus"
MUD = ((0.44, 0.42, 0.36), (0.60, 0.58, 0.50))     # pale lime mud
SHELL = (0.84, 0.70, 0.48)
SHELL_DARK = (0.50, 0.36, 0.22)
GAPE = (0.10, 0.08, 0.06)
LID = (0.74, 0.66, 0.50)


def ventral(w=0.5, l=0.36, h=0.22):
    """Convex ventral valve: a half-lens wider than long, highest toward the beak (+Y), with
    short ears along the straight hinge and an incurved umbo hanging over it."""
    bm = nh.uv_ellipsoid((0, 0, 0), (w, l, h), segments=40, rings=20)
    for v in bm.verts:
        x, y, z = v.co
        if z < 0:
            z = z * 0.08
        elif y < 0:
            z = z + h * 0.12 * (1 - z / h)  # thick front lip above the gape
        u = y / l                                   # -1 front .. +1 hinge
        if u > 0.55:                                # straight hinge with ears
            y = l * (0.55 + 0.45 * (u - 0.55) / 0.45 * 0.35)
            x = x * (1.0 + 0.55 * nh.smoothstep(0.55, 1.0, u))
        # umbo: highest point shifted back toward the hinge, beak curled over it
        z *= 1.0 + 0.25 * nh.smoothstep(-0.3, 0.7, u)
        v.co = Vector((x, y, z))
    beak = nh.uv_ellipsoid((0, l * 0.45, h * 0.95), (w * 0.28, l * 0.22, h * 0.32), 16, 10)
    return bm, beak


def shell_colour(w, l, h):
    def col(co, n):
        r = math.hypot(co.x / w, (co.y - l * 0.6) / (l * 1.6))
        a = math.atan2(co.x, -(co.y - l * 0.6))
        rib = 0.5 + 0.5 * math.cos(a * 46.0)
        growth = 0.5 + 0.5 * math.cos(r * 70.0)
        c = nh.lerp(SHELL, SHELL_DARK, 0.35 * rib + 0.5 * nh.smoothstep(0.8, 1.0, growth))
        if co.z < h * 0.22 and co.y < -l * 0.2 and n.z < 0.6:  # the dark gaping front commissure
            c = GAPE
        return c
    return col


# (x, y, yaw deg, scale)
SHELLS = ((0.0, -0.05, 0, 1.0), (-0.55, 0.42, 150, 0.7), (0.58, 0.36, -30, 0.6))


def build():
    mb = nh.MeshBuilder()
    height = br.seabed(mb, 1.05, MUD, seed=7, base=0.03, relief=0.012, n_r=12, n_a=48, oval=0.85)
    for x, y, yaw, k in SHELLS:
        w, l, h = 0.5 * k, 0.36 * k, 0.22 * k
        shell, beak = ventral(w, l, h)
        lid = nh.uv_ellipsoid((0, -l * 0.08, h * 0.08), (w * 0.86, l * 0.8, h * 0.05), 24, 8)
        m = (Matrix.Translation(Vector((x, y, height(x, y) + 0.01)))
             @ Matrix.Rotation(math.radians(yaw), 4, "Z"))
        for bm, c in ((shell, shell_colour(w, l, h)), (beak, SHELL), (lid, LID)):
            nh.transform(bm, m)
            mb.add(bm, (lambda co, n, c=c, m=m: c(m.inverted() @ co, n)) if callable(c) else c)
    return br.finish(mb, NAME, roughness=0.65)


if __name__ == "__main__":
    nh.run(build, NAME, ground=MUD[0], background=(0.05, 0.14, 0.18), views=br.VIEWS)
