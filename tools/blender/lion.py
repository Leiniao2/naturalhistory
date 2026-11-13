"""
Procedural low-poly male lion (Panthera leo) for map colonies.

A lean, powerful tawny cat mid-stride: muscular shoulders and thighs tapering
into slim legs with round paws, a broad muzzle with a pale chin and dark nose,
small round ears, a big shaggy mane (golden-brown at the face to dark brown
behind) covering the neck and chest, and a long tail ending in a dark tuft.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lion.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lion.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

COAT = (0.78, 0.58, 0.31)       # tawny gold
COAT_DARK = (0.64, 0.45, 0.22)  # back line
BELLY = (0.90, 0.76, 0.52)      # pale underside, chin
MANE_LIGHT = (0.64, 0.38, 0.12)
MANE_DARK = (0.24, 0.11, 0.04)
NOSE = (0.22, 0.10, 0.07)
EYE = (0.05, 0.03, 0.01)
TUFT = (0.20, 0.10, 0.04)
PAW = (0.68, 0.46, 0.21)

SEED = 11


def coat(belly_z=None):
    """Tawny with a darker back line and a pale belly (normal pointing down)."""
    def color(co, n):
        c = nh.lerp(COAT, COAT_DARK, nh.smoothstep(0.55, 0.95, n.z))
        c = nh.lerp(c, BELLY, nh.smoothstep(-0.25, -0.75, n.z))
        return nh.lerp(c, COAT_DARK, 0.15 * max(0.0, noise.noise(co * 7.0)))
    return color


def body():
    # Deep chest, tucked waist, slightly raised rump
    def deform(n):
        k = 1.0
        if n.y < 0:
            k *= 1.0 + 0.12 * (-n.y)            # fuller chest
        if n.z < 0:
            k *= 1.0 - 0.18 * (-n.z) * (1.0 - abs(n.y)) ** 2  # waist tuck under the belly
        return k
    return nh.uv_ellipsoid((0, 0.02, 0.64), (0.22, 0.56, 0.23), segments=22, rings=14, deform=deform)


def leg(x, y, stride, front):
    """Muscular upper leg tapering to a slim wrist and a round paw. stride shifts the paw along y."""
    parts = []
    if front:
        pts = [(x, y - 0.02, 0.72), (x, y + 0.03, 0.46), (x * 1.02, y + stride * 0.5, 0.24),
               (x * 1.02, y + stride, 0.09)]
        radii = [0.125, 0.092, 0.064, 0.056]
        # shoulder blade muscle
        parts.append((nh.ellipsoid((x * 0.95, y + 0.02, 0.66), (0.10, 0.16, 0.20), subdivisions=2), coat()))
    else:
        pts = [(x, y, 0.66), (x, y - 0.10, 0.44), (x * 1.02, y + 0.10 + stride * 0.4, 0.24),
               (x * 1.02, y + stride + 0.04, 0.09)]
        radii = [0.14, 0.095, 0.06, 0.054]
        # thigh
        parts.append((nh.ellipsoid((x * 0.9, y + 0.02, 0.58), (0.12, 0.21, 0.22), subdivisions=2), coat()))
    parts.append((nh.tube(pts, radii, sides=10), coat()))
    px, py = pts[-1][0], pts[-1][1] - 0.035
    parts.append((nh.ellipsoid((px, py, 0.045), (0.07, 0.09, 0.048), subdivisions=2), PAW))
    # a hint of toes: three small bumps across the front of the paw
    for t in (-1, 0, 1):
        parts.append((nh.ellipsoid((px + t * 0.035, py - 0.07, 0.035), (0.024, 0.026, 0.026), subdivisions=1), PAW))
    return parts


def head_parts():
    hz, hy = 0.92, -0.86
    parts = []
    # skull: a little wider than tall, flat on top
    parts.append((nh.uv_ellipsoid((0, hy, hz), (0.16, 0.17, 0.15), segments=16, rings=10,
                                  deform=lambda n: 1.0 - 0.08 * max(0.0, n.z) ** 2), coat()))
    # broad muzzle with a pale lower half
    def muzzle_col(co, n):
        return nh.lerp(COAT, BELLY, nh.smoothstep(hz - 0.03, hz - 0.08, co.z))
    parts.append((nh.uv_ellipsoid((0, hy - 0.14, hz - 0.06), (0.11, 0.10, 0.075), segments=14, rings=8), muzzle_col))
    # whisker pads
    for s in (-1, 1):
        parts.append((nh.ellipsoid((s * 0.045, hy - 0.21, hz - 0.07), (0.05, 0.04, 0.04), subdivisions=2), BELLY))
    # pale chin
    parts.append((nh.ellipsoid((0, hy - 0.17, hz - 0.14), (0.06, 0.05, 0.035), subdivisions=2), BELLY))
    # nose: broad, dark, on top of the muzzle tip
    parts.append((nh.ellipsoid((0, hy - 0.235, hz - 0.025), (0.04, 0.025, 0.028), subdivisions=2), NOSE))
    # nose bridge
    parts.append((nh.tube([(0, hy - 0.06, hz + 0.06), (0, hy - 0.2, hz - 0.01)], [0.05, 0.035], sides=8), coat()))
    # eyes under a heavy brow
    for s in (-1, 1):
        parts.append((nh.ellipsoid((s * 0.075, hy - 0.135, hz + 0.035), (0.026, 0.016, 0.018), subdivisions=2), EYE))
        parts.append((nh.ellipsoid((s * 0.075, hy - 0.125, hz + 0.06), (0.045, 0.03, 0.018), subdivisions=1), coat()))
        # small round ears, just peeking over the mane
        ear = nh.ellipsoid((s * 0.115, hy + 0.02, hz + 0.16), (0.048, 0.024, 0.048), subdivisions=2)
        parts.append((ear, lambda co, n: MANE_DARK if n.y > 0 else COAT_DARK))
    return parts


def mane(rng):
    """Big lumpy shell around neck and chest plus loose tufts for a shaggy silhouette."""
    parts = []
    c = Vector((0, -0.60, 0.84))

    def mane_col(co, n):
        # golden around the face, darker toward the back and underside
        t = nh.smoothstep(-0.88, -0.62, co.y)
        col = nh.lerp(MANE_LIGHT, MANE_DARK, min(1.0, t * 0.85 + 0.3 * max(0.0, -n.z)))
        return nh.lerp(col, MANE_DARK, 0.25 * max(0.0, noise.noise(co * 11.0)))

    def lumpy(n):
        return 1.0 + 0.16 * noise.noise(n * 3.3 + Vector((5.0, 1.0, 2.0))) + 0.07 * noise.noise(n * 8.0)

    parts.append((nh.ellipsoid(tuple(c), (0.30, 0.30, 0.34), subdivisions=3, deform=lumpy), mane_col))
    # chest bib hanging between the front legs
    parts.append((nh.ellipsoid((0, -0.60, 0.58), (0.15, 0.16, 0.20), subdivisions=2, deform=lumpy), mane_col))
    # tufts around the edge of the face ruff and down the neck
    for i in range(26):
        a = rng.uniform(0, math.tau)
        el = rng.uniform(-0.9, 1.0)
        d = Vector((math.cos(a) * math.cos(el) * 0.29, rng.uniform(-0.12, 0.26), math.sin(el) * 0.34 + 0.02))
        if d.z < -0.2 and abs(d.x) < 0.1:
            continue
        p = c + d
        r = rng.uniform(0.055, 0.085)
        parts.append((nh.ellipsoid(tuple(p), (r, r * 1.3, r), subdivisions=2, deform=lumpy), mane_col))
    return parts


def tail():
    pts = [(0, 0.58, 0.72), (0, 0.76, 0.66), (0.03, 0.92, 0.50), (0.08, 1.02, 0.34), (0.14, 1.06, 0.24)]
    parts = [(nh.tube(pts, [0.05, 0.035, 0.03, 0.026, 0.022], sides=8), coat())]
    tuft = nh.ellipsoid((0.16, 1.07, 0.19), (0.045, 0.045, 0.07), subdivisions=2,
                        deform=lambda n: 1.0 + 0.15 * noise.noise(n * 4.0))
    parts.append((tuft, TUFT))
    return parts


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(body(), coat())
    # walking: left-front and right-hind forward
    for p in leg(-0.13, -0.40, -0.12, True) + leg(0.13, -0.40, 0.10, True) \
            + leg(-0.14, 0.42, 0.08, False) + leg(0.14, 0.42, -0.10, False):
        mb.add(*p)
    # neck under the mane
    mb.add(nh.tube([(0, -0.40, 0.70), (0, -0.62, 0.82), (0, -0.78, 0.90)], [0.17, 0.16, 0.13], sides=12), coat())
    for p in mane(rng) + head_parts() + tail():
        mb.add(*p)
    obj = mb.to_object("Lion")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Lion", ground=(0.55, 0.50, 0.30), views=((35, 25), (-90, 8), (20, 65)))
