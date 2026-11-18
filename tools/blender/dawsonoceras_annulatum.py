"""
Procedural Dawsonoceras annulatum (mid-Silurian orthocerid nautiloid of Gotland and the
Wenlock Limestone of England and North America) for map colonies (Swim style).

A straight, slowly tapering conch, a few tens of centimetres long, ringed along its whole
length by strong, rounded transverse ridges (annulations) - its name means "ringed" -
crossed by fine longitudinal threads, with the chambered phragmocone behind a body
chamber at the wide end. Colours are speculative: a cream shell banded brown in the
furrows between the rings, darker on the back. The animal peers out of the aperture:
a head with two big eyes and ten grasping arms (see nh_orthocone.py).

Usage:
  blender --background --python tools/blender/dawsonoceras_annulatum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DawsonocerasAnnulatum.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

CREAM = (0.90, 0.82, 0.66)
BELLY = (0.95, 0.90, 0.80)
FURROW = (0.42, 0.26, 0.14)
BACK_TINT = (0.62, 0.46, 0.30)
FLESH = (0.58, 0.30, 0.26)
FLESH_LIGHT = (0.86, 0.60, 0.50)

LENGTH = 1.6
R_AP = 0.12
R_APEX = 0.025
SPACING = 0.75        # annulation spacing in local shell radii
G = (R_AP - R_APEX) / LENGTH


def phase(y):
    r = max(R_AP - G * y, R_APEX)
    return -math.log(r / R_AP) / (SPACING * G) if y > 0 else 0.0


def ring(y):
    """1 on the crest of an annulation, 0 in the furrow."""
    return 0.5 + 0.5 * math.cos(math.tau * phase(y) + 1.0)


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.55, 0.45, math.sin(a))
    col = nh.lerp(BELLY, CREAM, dorsal)
    col = nh.lerp(col, BACK_TINT, 0.35 * dorsal)
    y = s * LENGTH
    furrow = 1.0 - nh.smoothstep(0.15, 0.55, ring(y))
    col = nh.lerp(col, FURROW, furrow * (0.35 + 0.5 * dorsal) * nh.smoothstep(0.0, 0.03, s))
    # fine longitudinal threads
    col = tuple(x * (0.94 + 0.06 * math.cos(a * 36)) for x in col)
    col = nh.lerp(col, (0.60, 0.48, 0.38), nh.smoothstep(0.8, 1.0, s) * 0.5)
    return tuple(min(1.0, x) for x in col)


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=260, sides=18, body_frac=0.24,
                     septum_spacing=0.6, siphuncle=0.0, sinus=0.15, growth=0.0, bulge=0.0)
    # sculpt the annulations: push the outer surface out on each ring crest
    for v in bm.verts:
        y = v.co.y
        if y < 0.03:
            continue
        k = 1.0 + 0.11 * ring(y) ** 1.5 * nh.smoothstep(0.03, 0.10, y)
        v.co.x *= k
        v.co.z *= k
    mb.add(bm, None)
    oc.soft_body(mb, 0.0, r * 0.98, FLESH, FLESH_LIGHT, arms=10, arm_len=2.4, arm_r=0.13,
                 eye_r=0.26, spot=(0.46, 0.20, 0.16))
    obj = mb.to_object("DawsonocerasAnnulatum", roughness=0.45)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "DawsonocerasAnnulatum", views=((35, 25), (-90, 8), (20, 10), (0, 90)))
