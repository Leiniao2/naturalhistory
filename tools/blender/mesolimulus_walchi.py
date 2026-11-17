"""
Procedural Mesolimulus walchi (Late Jurassic horseshoe crab, Solnhofen) for map colonies.

A horseshoe crab very like the living Limulus, about 10-20 cm long including the tail:
a broad, domed, horseshoe-shaped head shield (prosoma) with a central ridge and two
crescent compound eyes, a hinged, hexagonal rear shield (opisthosoma) with a fringe of
movable spines along each side, and a long, spike-like tail (telson). Solnhofen is famous
for a Mesolimulus fossilised at the end of its own trackway. Olive-brown carapace, paler
margins. Faces -Y, pivot at the body centre (Swim, on the seabed).

Usage:
  blender --background --python tools/blender/mesolimulus_walchi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mesolimulus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

SHELL = (0.36, 0.30, 0.18)
RIM = (0.62, 0.54, 0.36)
DARK = (0.14, 0.12, 0.08)
EYE = (0.08, 0.07, 0.06)


def shell_col(cy, ry):
    def fn(co, n):
        r = math.hypot(co.x / 0.4, (co.y - cy) / ry)
        c = nh.lerp(SHELL, RIM, nh.smoothstep(0.75, 0.98, r))
        if abs(co.x) < 0.02:
            c = nh.lerp(c, DARK, 0.4)
        return c
    return fn


def dome(cy, rx, ry, h, front_round=True, cut_back=0.0):
    """Shallow dome: horseshoe outline from a superellipse, flat underside."""
    bm = nh.ellipsoid((0, cy, 0), (rx, ry, h), subdivisions=4,
                      deform=lambda v: 1.0)
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z *= 0.15
        # ridges: central keel and two lateral ridges
        x = abs(v.co.x)
        if v.co.z > 0:
            v.co.z += 0.012 * math.exp(-(x / 0.02) ** 2) + 0.008 * math.exp(-((x - rx * 0.45) / 0.02) ** 2)
    return bm


def build():
    mb = nh.MeshBuilder()
    # prosoma: broad horseshoe dome
    p = dome(-0.15, 0.4, 0.3, 0.12)
    for v in p.verts:  # flatten the back edge into a straight hinge
        if v.co.y > -0.02:
            v.co.y = -0.02 + (v.co.y + 0.02) * 0.25
    mb.add(p, shell_col(-0.15, 0.3))
    # opisthosoma: smaller hexagonal shield
    o = dome(0.12, 0.25, 0.16, 0.07)
    for v in o.verts:
        k = abs(v.co.x) / 0.25
        v.co.y -= 0.0 if v.co.y < 0.12 else (v.co.y - 0.12) * 0.4 * k
    mb.add(o, shell_col(0.12, 0.16))
    # marginal spines on the opisthosoma
    for i in range(6):
        y = 0.04 + i * 0.035
        for sx in (1, -1):
            x = 0.25 * math.sqrt(max(0.0, 1 - ((y - 0.12) / 0.16) ** 2)) * 0.95
            b = Vector((sx * x, y, 0.0))
            mb.add(kit.cone(b, b + Vector((sx * 0.05, 0.03, -0.004)), 0.01, sides=4), RIM, smooth=False)
    # telson
    mb.add(nh.tube([(0, 0.26, 0.01), (0, 0.5, 0.0), (0, 0.72, -0.02)], [0.025, 0.014, 0.0], sides=6), SHELL)
    # compound eyes
    for sx in (1, -1):
        mb.add(nh.ellipsoid((sx * 0.19, -0.18, 0.105), (0.02, 0.05, 0.012), subdivisions=2), EYE)
    # walking legs peeking out below
    for i in range(5):
        for sx in (1, -1):
            b = Vector((sx * 0.08, -0.2 + i * 0.05, -0.01))
            mb.add(nh.tube([b, b + Vector((sx * 0.16, -0.02, -0.03)), b + Vector((sx * 0.24, 0.0, -0.05))], [0.012, 0.009, 0.004], sides=5), (0.45, 0.36, 0.22))
    return kit.finish(mb, "Mesolimulus", pivot="center", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Mesolimulus", background=(0.04, 0.10, 0.13), views=((35, 35), (-90, 5), (0, 89)))
