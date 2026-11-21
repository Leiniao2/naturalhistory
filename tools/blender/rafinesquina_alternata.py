"""
Procedural Rafinesquina alternata (Late Ordovician strophomenid brachiopod, one of the
commonest fossils of the Cincinnati region) for map colonies (Fixed style).

A thin, broad, flat lamp shell: a D-shaped outline with a long straight hinge line at the
back (its widest part) and a rounded front margin; the lower valve gently convex, the upper
one nested inside it, so the whole shell is barely thicker than a coin. Covered in very
fine radiating ribs, alternately strong and weak (hence alternata), crossed by faint growth
lines. It lay loose on the soft sea floor, its wide, flat shell keeping it from sinking.
A large and a small shell on a patch of mud. Grey-tan. Pivot on the sea floor (z = 0),
facing -Y.

Usage:
  blender --background --python tools/blender/rafinesquina_alternata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/RafinesquinaAlternata.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "RafinesquinaAlternata"
SHELL = (0.74, 0.68, 0.57)
RIB = (0.58, 0.52, 0.42)
DARK = (0.40, 0.35, 0.28)


def shell(mb, cx, cy, scale, rot):
    H = 0.18   # hinge offset from the centre (towards +Y)

    def outline(a):
        ex, ey = 0.62, 0.50
        r = 1.0 / math.sqrt((math.cos(a) / ex) ** 2 + (math.sin(a) / ey) ** 2)
        if math.sin(a) > 1e-3:
            r = min(r, H / math.sin(a))
        return r

    beak = Vector((0, H, 0))

    def col(co, n):
        p = Vector(((co.x - cx), (co.y - cy), 0))
        p = Matrix.Rotation(-rot, 3, 'Z') @ p / scale
        d = (p - beak)
        ang = math.atan2(d.x, -d.y)
        rib = 0.5 + 0.5 * math.cos(ang * 70)
        rib2 = 0.5 + 0.5 * math.cos(ang * 140)
        c = nh.lerp(SHELL, RIB, 0.45 * nh.smoothstep(0.6, 1.0, rib) + 0.2 * nh.smoothstep(0.7, 1.0, rib2))
        g = 0.5 + 0.5 * math.sin(d.length * 70)
        c = nh.lerp(c, DARK, 0.18 * nh.smoothstep(0.85, 1.0, g))
        if n.z < -0.2:
            c = DARK
        return c

    m = Matrix.Translation((cx, cy, 0.035 * scale)) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Scale(scale, 4)
    frame = lambda u, v, w: (u, v, w)  # noqa: E731
    top = kit.valve(outline, 0.09, side=1, peak=(0.0, 0.35), power=0.6, frame=frame)
    bot = kit.valve(outline, 0.012, side=-1, peak=(0.0, 0.35), frame=frame)
    for bm in (top, bot):
        nh.transform(bm, m)
        mb.add(bm, col)
    # small beak at the hinge
    b = m @ Vector((0, H + 0.01, 0.03))
    mb.add(nh.ellipsoid(tuple(b), (0.05 * scale, 0.03 * scale, 0.025 * scale), 2), SHELL)


def build():
    mb = nh.MeshBuilder()
    kit.mud(mb, 0.95)
    shell(mb, -0.12, 0.05, 1.0, 0.0)
    shell(mb, 0.55, -0.45, 0.45, 0.9)
    return kit.finish_fixed(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
