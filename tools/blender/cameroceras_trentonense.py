"""
Procedural Cameroceras trentonense (Middle-Late Ordovician endocerid nautiloid) for map colonies.

A giant straight-shelled nautiloid, the largest animal of the Ordovician seas (the
conch probably reached several metres; the biggest claims are debated). Heavier and
stouter than Orthoceras: a long, thick, gently swelling conch with a blunt apex,
coarser growth lines and a few deeper growth halts, long chambers and the endocerids'
huge siphuncle running along the ventral side (a dark line on the belly). Colours are
speculative: an olive-brown shell with dark, wavy longitudinal flame stripes on the
back and a pale belly; the old apical end is faded and patched with encrusters. The
robust head has big eyes, a leathery Nautilus-like hood and a crown of two dozen
tentacles over the funnel (see nh_orthocone.py).

Usage:
  blender --background --python tools/blender/cameroceras_trentonense.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cameroceras.fbx
Pivot at the body centre, tentacles forward (-Y), back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

OLIVE = (0.72, 0.62, 0.42)
BELLY = (0.86, 0.80, 0.64)
STRIPE = (0.30, 0.20, 0.11)
FADED = (0.74, 0.70, 0.60)
ENCRUST = (0.86, 0.84, 0.76)
SUTURE = (0.42, 0.34, 0.22)
FLESH = (0.50, 0.30, 0.24)
FLESH_LIGHT = (0.80, 0.60, 0.48)
HOOD = (0.42, 0.28, 0.20)

LENGTH = 1.85
R_AP = 0.15
R_APEX = 0.045
HALTS = (0.12, 0.31, 0.52)   # growth halts (shallow constrictions with darker lines)


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.6, 0.5, math.sin(a))
    col = nh.lerp(BELLY, OLIVE, dorsal)
    # wavy longitudinal flame stripes over the back
    wave = a * 6.0 + 0.9 * math.sin(s * 26.0 + a * 2.0)
    stripe = nh.smoothstep(0.35, 0.8, math.sin(wave))
    col = nh.lerp(col, STRIPE, stripe * dorsal * (0.75 - 0.35 * s))
    # coarse growth lines and the growth halts
    col = tuple(x * (1.05 if info["ridge"] else 0.90) for x in col)
    for h in HALTS:
        col = nh.lerp(col, STRIPE, 0.6 * nh.smoothstep(0.012, 0.0, abs(s - h)))
    col = nh.lerp(col, SUTURE, info["suture"] * 0.35)
    # the old apical end: faded, with pale encrusting patches
    old = nh.smoothstep(0.55, 0.95, s)
    col = nh.lerp(col, FADED, old * 0.55)
    p = Vector((math.cos(a) * 2.0, s * 9.0, math.sin(a) * 2.0))
    col = nh.lerp(col, ENCRUST, nh.smoothstep(0.25, 0.45, noise.noise(p)) * old * 0.85)
    return tuple(min(1.0, x) for x in col)


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=190, sides=32, body_frac=0.24,
                     septum_spacing=0.6, siphuncle=-math.pi / 2, sinus=0.3,
                     growth=0.010, bulge=0.10)
    # shallow constrictions at the growth halts
    for v in bm.verts:
        s = v.co.y / LENGTH
        k = 1.0
        for h in HALTS:
            k -= 0.025 * nh.smoothstep(0.012, 0.0, abs(s - h))
        v.co.x *= k
        v.co.z *= k
    mb.add(bm, None)
    oc.soft_body(mb, 0.0, r * 0.98, FLESH, FLESH_LIGHT, arms=24, arm_len=1.7, arm_r=0.11,
                 hood=True, hood_col=HOOD, eye_r=0.24, spot=(0.36, 0.20, 0.15), curl=0.2,
                 spread=0.35, droop=0.45)
    obj = mb.to_object("Cameroceras", roughness=0.5)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Cameroceras", views=((35, 25), (-90, 8), (20, 10), (0, 90)))
