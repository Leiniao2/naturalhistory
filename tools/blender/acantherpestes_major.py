"""
Procedural Acantherpestes major (Late Carboniferous of Mazon Creek, Illinois, a giant spiny
euphoberiid millipede up to about 30 cm long) for map colonies (Ground style).

A long, cylindrical millipede of 22 rounded body rings on a gently snaking line: every ring
carries a pair of long spines rising up and outwards, each forking near the tip into two
prongs (the very spiky silhouette of the euphoberiids), with smaller spines lower on the
sides; two pairs of short legs per ring underneath, a rounded head with short, clubbed
antennae and dark eye patches, and a blunt tail ring. Dark brown rings with paler hind
margins and pale spine tips. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/acantherpestes_major.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Acantherpestes.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Acantherpestes"
RING = (0.24, 0.15, 0.09)
RING_EDGE = (0.50, 0.36, 0.22)
SPINE = (0.30, 0.20, 0.12)
SPINE_TIP = (0.80, 0.68, 0.48)
LEG = (0.46, 0.34, 0.22)
HEAD = (0.20, 0.13, 0.08)
EYE = (0.04, 0.03, 0.03)

N = 22
L = 1.7
R = 0.065
Z = 0.085


def centre(t):
    """Body centre line, t = 0 head .. 1 tail: a gentle S in plan view."""
    y = -L / 2 + t * L
    x = 0.07 * math.sin(t * math.pi * 1.6 + 0.4)
    return Vector((x, y, Z))


def build():
    mb = nh.MeshBuilder()
    seg = L / (N + 1)
    for i in range(N):
        t = (i + 1.0) / (N + 1)
        c = centre(t)
        fwd = (centre(min(1, t + 0.01)) - centre(max(0, t - 0.01))).normalized()
        side = Vector((-fwd.y, fwd.x, 0)).normalized()
        taper = 1.0 - 0.35 * max(0.0, (t - 0.75) / 0.25)
        r = R * taper

        def ring_col(co, n, c=c, fwd=fwd):
            d = (co - c).dot(fwd)
            return RING_EDGE if d > seg * 0.32 else RING
        mb.add(nh.uv_ellipsoid(tuple(c), (r, seg * 0.62, r * 0.95), 12, 8), ring_col)
        # legs: two pairs per ring, short, splayed
        for sx in (-1, 1):
            for k in (-0.25, 0.25):
                root = c + side * sx * r * 0.55 + fwd * seg * k + Vector((0, 0, -r * 0.6))
                knee = root + side * sx * r * 0.55 + Vector((0, 0, 0.0))
                foot = knee + side * sx * r * 0.25 + Vector((0, 0, -knee.z + 0.004)) + fwd * (-0.01)
                mb.add(nh.tube([root, knee, foot], [0.010, 0.008, 0.004], sides=4), LEG)
        if i < 1:
            continue
        # big dorsal spine pair, forked near the tip
        for sx in (-1, 1):
            base = c + side * sx * r * 0.45 + Vector((0, 0, r * 0.75))
            d = (side * sx * 0.55 + Vector((0, 0, 1.0)) + fwd * 0.12).normalized()
            Ls = 0.20 * taper
            fork = base + d * Ls * 0.72

            def sc(co, n, b=base, Ls=Ls):
                return nh.lerp(SPINE, SPINE_TIP, min(1.0, ((co - b).length / Ls) ** 1.5))
            mb.add(nh.tube([base - d * 0.01, base.lerp(fork, 0.5), fork], [0.016, 0.011, 0.008], sides=5), sc)
            for prong in (-1, 1):
                pd = (d + fwd * 0.45 * prong).normalized()
                mb.add(nh.tube([fork, fork + pd * Ls * 0.35], [0.007, 0.0], sides=4), sc)
            # lower lateral spine
            base2 = c + side * sx * r * 0.95
            d2 = (side * sx + Vector((0, 0, 0.25)) + fwd * 0.15).normalized()
            mb.add(nh.tube([base2, base2 + d2 * 0.08 * taper], [0.010, 0.0], sides=4), sc)

    # head
    h = centre(0.0) + Vector((0, 0.02, -0.005))
    mb.add(nh.uv_ellipsoid(tuple(h), (R * 0.85, seg * 0.8, R * 0.8), 12, 8), HEAD)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid(tuple(h + Vector((sx * R * 0.6, -seg * 0.25, R * 0.25))), (0.016, 0.02, 0.014), 1), EYE)
        a0 = h + Vector((sx * R * 0.35, -seg * 0.6, R * 0.1))
        pts = [a0, a0 + Vector((sx * 0.04, -0.06, 0.03)), a0 + Vector((sx * 0.09, -0.11, 0.02))]
        mb.add(nh.tube(pts, [0.008, 0.007, 0.006], sides=4), LEG)
        mb.add(nh.ellipsoid(tuple(pts[-1]), (0.012, 0.012, 0.012), 1), LEG)
    # tail ring
    mb.add(nh.uv_ellipsoid(tuple(centre(1.0)), (R * 0.5, seg * 0.6, R * 0.5), 10, 6), RING)

    obj = mb.to_object(NAME, roughness=0.5)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.24, 0.22, 0.14), background=(0.20, 0.28, 0.18),
           views=((35, 30), (0, 75), (-90, 10)))
