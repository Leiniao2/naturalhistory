"""
Procedural low-poly Plasmodium falciparum, the deadliest malaria parasite, shown as its
tell-tale crescent (banana-shaped) gametocyte, the stage a mosquito picks up from the blood.

An elongated, curved sausage with blunt, rounded ends, its lilac-blue cytoplasm stained like a
Giemsa blood film, a diffuse pinkish-red nucleus in the middle and a cluster of dark brown-black
haemozoin (malaria pigment) granules gathered round it. It lies inside the faint remains of the
red blood cell it grew in: a pale pink, thin, shell-like membrane that hugs the convex side and
is stretched like a bow string across the concave side between the two tips (the "Laveran's
bib"), so it reads as "inside a red cell". Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/plasmodium_falciparum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PlasmodiumFalciparum.fbx
About 1.6 units tip to tip (red-cell remnant included). Long axis along Y, the concave side
toward +X. Pivot at the centre of the bounds (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 4
ARC_R = 0.95                  # radius of the crescent's bend
SPAN = math.radians(98)       # angle the crescent sweeps
RADIUS = 0.15                 # sausage radius
FLATTEN = 0.8                 # Z scale of the cross-section
CAP = 0.80                    # fraction of the half-length before the rounded end caps start
SAMPLES = 30
MEMBRANE_GAP = 0.05           # how far the red-cell membrane stands out round the convex side
BIB_BOW = 0.05                # how far the "bow string" bows out beyond the straight chord
PIGMENT = 16

CYTO = (0.58, 0.60, 0.86)
CYTO_END = (0.66, 0.68, 0.90)
NUCLEUS = (0.90, 0.40, 0.52)
HAEMOZOIN = [(0.16, 0.10, 0.06), (0.24, 0.14, 0.07), (0.10, 0.07, 0.05)]
RBC_SHEET = (0.97, 0.76, 0.80)
RBC_RIM = (0.92, 0.68, 0.72)


def axis(t):
    """Point on the crescent's centre line, t = 0 (one tip) .. 1 (the other). Bends toward +X."""
    a = (t - 0.5) * SPAN
    return Vector((ARC_R - ARC_R * math.cos(a), ARC_R * math.sin(a), 0.0))


def radius(t):
    s = abs(2 * t - 1)
    if s < CAP:
        return RADIUS * (1 - 0.10 * (s / CAP) ** 2)
    u = (s - CAP) / (1 - CAP)
    return RADIUS * 0.90 * math.sqrt(max(0.0, 1 - u * u))


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # the gametocyte: a curved, blunt-ended sausage, rings packed toward the rounded ends
    ts = [0.5 - 0.5 * math.cos(math.pi * k / SAMPLES) for k in range(SAMPLES + 1)]
    pts = [axis(t) for t in ts]
    radii = [radius(t) if 0 < k < SAMPLES else 0.0 for k, t in enumerate(ts)]
    mid = axis(0.5)

    def cyto_col(co, n):
        d = (co - mid).length
        c = nh.lerp(CYTO, CYTO_END, nh.smoothstep(0.3, 0.7, d))
        c = tuple(k * (1.0 + 0.05 * noise.noise(co * 14.0)) for k in c)
        # diffuse pinkish-red nucleus in the middle
        return nh.lerp(c, NUCLEUS, (1 - nh.smoothstep(0.10, 0.24, d)) * 0.95)

    mb.add(nh.tube(pts, radii, sides=14, scale_xy=(1.0, FLATTEN)), cyto_col)

    # haemozoin: dark pigment granules clustered round the nucleus, just poking through the top
    for i in range(PIGMENT):
        t = 0.5 + rng.uniform(-0.13, 0.13)
        if abs(t - 0.5) < 0.04:
            t += 0.06 if t > 0.5 else -0.06
        a = rng.uniform(-1.1, 1.1) + math.pi / 2       # round the upper half of the section
        c = axis(t)
        nrm = (c - Vector((ARC_R, 0, 0))).normalized()  # outward from the bend's centre (-X side)
        rad = radius(t)
        p = c - nrm * math.cos(a) * rad * 0.95 + Vector((0, 0, math.sin(a) * rad * FLATTEN * 0.95))
        r = rng.uniform(0.016, 0.026)
        mb.add(nh.ellipsoid(p, (r, r * rng.uniform(1.0, 1.6), r), subdivisions=1), rng.choice(HAEMOZOIN),
               smooth=False)

    # the red-cell remnant: a thin pink sheet in the mid-plane, standing just out round the convex
    # side and the ends, and stretched straight(ish) across the concave side between the tips
    outline = []
    n = 28
    for k in range(1, n):  # convex side, tip to tip
        t = k / n
        c = axis(t)
        nrm = (c - Vector((ARC_R, 0, 0))).normalized()
        outline.append(c + nrm * (radius(t) + MEMBRANE_GAP))
    # the membrane comes to a point just beyond each tip, and the bow string runs between them
    ends = [axis(1.0) + (axis(1.0) - axis(0.98)).normalized() * MEMBRANE_GAP,
            axis(0.0) + (axis(0.0) - axis(0.02)).normalized() * MEMBRANE_GAP]
    m = 18
    for k in range(m + 1):
        u = k / m
        p = ends[0] + (ends[1] - ends[0]) * u
        outline.append(p + Vector((BIB_BOW * math.sin(math.pi * u), 0, 0)))
    outline.reverse()  # counter-clockwise seen from above

    def sheet_col(co, n):
        return tuple(k * (1.0 + 0.03 * noise.noise(co * 6.0)) for k in RBC_SHEET)

    mb.add(nh.flat_panel([tuple(p) for p in outline], thickness=0.026), sheet_col, smooth=False)
    # a soft rounded rim all round the membrane's edge, thickest along the bow string
    rim = outline + [outline[0]]
    mb.add(nh.tube(rim, [0.017] * len(rim), sides=6, cap_start=False, cap_end=False), RBC_RIM)

    obj = mb.to_object("PlasmodiumFalciparum", roughness=0.45)
    vs = obj.data.vertices
    c = Vector([(max(v.co[i] for v in vs) + min(v.co[i] for v in vs)) / 2 for i in range(3)])
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "PlasmodiumFalciparum", views=((35, 40), (0, 88), (-90, 10)))
