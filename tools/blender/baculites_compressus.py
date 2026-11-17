"""
Procedural Baculites compressus (Late Cretaceous heteromorph ammonite, Western Interior
Seaway), hovering.

A straight-shelled ammonite: after a tiny initial coil only millimetres across, the shell
grew as a long, slightly compressed, gently tapering rod up to about a metre long, marked by
low crescent-shaped ribs and intricately frilled ammonitic sutures between the chambers.
Fossils are so abundant in the Pierre Shale that they are used to date the rocks. Pale
nacreous tan shell with faint rusty ribs; the soft body with short arms peeks out of the
aperture. Pivot at the body centre, arms forward (-Y).

Usage:
  blender --background --python tools/blender/baculites_compressus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Baculites.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

SHELL = (0.82, 0.72, 0.56)
BELLY = (0.90, 0.84, 0.72)
RIB = (0.60, 0.42, 0.28)
SUTURE = (0.42, 0.30, 0.20)
FLESH = (0.66, 0.40, 0.32)
FLESH_LIGHT = (0.88, 0.70, 0.60)

LENGTH = 1.9
R_AP = 0.075
R_APEX = 0.012


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.6, 0.5, math.sin(a))
    col = nh.lerp(BELLY, SHELL, dorsal)
    # low crescent ribs, bowed forward on the flanks
    rib = 0.5 + 0.5 * math.sin(s * 90.0 + 1.6 * abs(math.cos(a)))
    col = nh.lerp(col, RIB, 0.35 * nh.smoothstep(0.6, 0.9, rib) * (1 - info["body"] * 0.3))
    # frilled ammonitic sutures on the phragmocone
    if not info["body"]:
        f = s * 34.0 + 0.10 * math.sin(a * 9.0) + 0.05 * math.sin(a * 23.0)
        d = abs(f - round(f))
        col = nh.lerp(col, SUTURE, 0.7 * (1 - nh.smoothstep(0.02, 0.06, d)))
    col = tuple(x * (1.03 if info["ridge"] else 0.95) for x in col)
    return tuple(min(1.0, x) for x in col)


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=140, sides=16, body_frac=0.30,
                     septum_spacing=0.9, siphuncle=-math.pi / 2, sinus=0.3, growth=0.01, bulge=0.02)
    mb.add(bm, None)
    oc.soft_body(mb, 0.0, r * 0.97, FLESH, FLESH_LIGHT, arms=10, arm_len=1.6, arm_r=0.11,
                 eye_r=0.22, spot=(0.5, 0.25, 0.2))
    obj = mb.to_object("Baculites", roughness=0.4)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Baculites", views=((35, 25), (-90, 8)), size=640)
