"""
Procedural Gonioceras anceps Hall, 1847 (Middle Ordovician actinocerid nautiloid of North
America) for map colonies (Swim style).

A straight nautiloid squashed flat: the conch is strongly depressed, several times wider than
high, with a gently arched back, a nearly flat belly and the two flanks meeting in sharp
keel-like edges, like a long, flattened spearhead. The chambers are short and very wide, the
siphuncle runs along the middle. It probably lay on the sea floor and waited for prey. Colours
are speculative: a mottled sand-and-olive back for camouflage on the bottom, a pale belly.
Built from nh_orthocone.conch() reshaped to the depressed cross-section; a low head with
upward-looking eyes and short arms.

Usage:
  blender --background --python tools/blender/gonioceras_anceps.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GoniocerasAnceps.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z).
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

SAND = (0.70, 0.62, 0.44)
OLIVE = (0.40, 0.38, 0.24)
BELLY = (0.88, 0.84, 0.72)
EDGE = (0.30, 0.26, 0.17)
SUTURE = (0.46, 0.40, 0.28)
FLESH = (0.52, 0.44, 0.32)
FLESH_LIGHT = (0.80, 0.72, 0.58)

LENGTH = 1.5
R_AP = 0.13
R_APEX = 0.014
WIDE = 2.6       # half-width / radius
TOP = 0.55       # back height / radius
FLAT = 0.18      # belly depth / radius


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.15, 0.15, math.sin(a))
    p = Vector((math.cos(a) * 3.0, s * 14.0, math.sin(a) * 3.0))
    m = nh.smoothstep(-0.1, 0.35, noise.noise(p))
    back = nh.lerp(SAND, OLIVE, m)
    col = nh.lerp(BELLY, back, dorsal)
    col = nh.lerp(col, EDGE, 0.7 * nh.smoothstep(0.75, 0.98, abs(math.cos(a))))
    col = tuple(x * (1.03 if info["ridge"] else 0.95) for x in col)
    col = nh.lerp(col, SUTURE, info["suture"] * 0.5)
    return col


def squash(bm, top=TOP, flat=FLAT, wide=WIDE, y_from=None):
    for v in bm.verts:
        if y_from is not None and v.co.y < y_from:
            continue
        x, z = v.co.x, v.co.z
        r = math.hypot(x, z)
        if r < 1e-6:
            continue
        a = math.atan2(z, x)
        c, s = math.cos(a), math.sin(a)
        # acute lateral edges: pull the flanks into a lens
        v.co.x = r * wide * math.copysign(abs(c) ** 0.7, c)
        v.co.z = r * (top if s > 0 else flat) * s * (0.6 + 0.4 * abs(s))


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=150, sides=32, body_frac=0.24,
                     septum_spacing=0.22, siphuncle=0.0, sinus=0.12, growth=0.008, bulge=0.12)
    squash(bm)
    mb.add(bm, None)
    head = nh.MeshBuilder()
    oc.soft_body(head, 0.0, r * 0.9, FLESH, FLESH_LIGHT, arms=10, arm_len=1.8, arm_r=0.14,
                 hood=False, eye_r=0.24, spot=(0.36, 0.30, 0.20), curl=0.5, spread=0.8, droop=0.05)
    hb = head.bm
    head.bm = None
    for v in hb.verts:
        v.co.x *= 1.9
        v.co.z *= 0.55
    hb_col = hb
    mb.add(hb_col, None)
    obj = mb.to_object("GoniocerasAnceps", roughness=0.55)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "GoniocerasAnceps", views=((35, 30), (-90, 8), (0, 90)))
