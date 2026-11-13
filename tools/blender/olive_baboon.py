"""
Procedural low-poly olive baboon (Papio anubis) for map colonies.

A male walking on all fours: long arms and legs of similar length, a fuller
shoulder mane, a long dog-like dark muzzle under a heavy brow with close-set
eyes, olive-grey grizzled fur, dark hands and feet, the tail raised at the base
then "broken" and drooping, and a small pinkish-grey rump pad.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/olive_baboon.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OliveBaboon.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

FUR = (0.45, 0.42, 0.29)        # olive-grey
FUR_DARK = (0.30, 0.28, 0.19)
FUR_LIGHT = (0.66, 0.62, 0.46)  # grizzled tips
SKIN = (0.29, 0.27, 0.27)       # dark grey-charcoal bare skin: muzzle, face, hands, feet
SKIN_LIGHT = (0.42, 0.39, 0.37)
NOSE = (0.17, 0.16, 0.16)
MOUTH = (0.06, 0.05, 0.05)
EYE = (0.55, 0.36, 0.12)
PUPIL = (0.03, 0.02, 0.02)
PAD = (0.62, 0.48, 0.48)        # rump callosities

SEED = 5


def fur(darken=0.0, lighten=0.0):
    """Olive with a fine grizzled salt-and-pepper speckle; slightly darker underneath."""
    def color(co, n):
        c = nh.lerp(FUR, FUR_DARK, nh.smoothstep(-0.2, -0.9, n.z) * 0.5 + darken)
        c = nh.lerp(c, FUR_LIGHT, lighten)
        g = noise.noise(co * 61.0) + 0.5 * noise.noise(co * 137.0)  # fine grain, no large patches
        return nh.lerp(c, FUR_LIGHT if g > 0 else FUR_DARK, min(0.5, abs(g) * 0.6))
    return color


def lumpy(amount, freq=3.0):
    return lambda n: 1.0 + amount * noise.noise(n * freq + Vector((2.0, 7.0, 1.0)))


def body():
    # Shoulders higher and fuller than the narrow hips
    def deform(n):
        k = 1.0 + 0.10 * max(0.0, -n.y)
        if n.z < 0:
            k *= 1.0 - 0.15 * (-n.z) * (1.0 - abs(n.y))
        return k * lumpy(0.04, 5.0)(n)
    return nh.uv_ellipsoid((0, 0.04, 0.55), (0.17, 0.40, 0.19), segments=28, rings=16, deform=deform)


def hand(x, y, z_len=0.1):
    """Dark palm walking on its fingers, with knuckle bumps."""
    parts = [(nh.ellipsoid((x, y - 0.02, 0.03), (0.045, 0.065, 0.03), subdivisions=2), SKIN)]
    for t in (-1, 0, 1):
        parts.append((nh.ellipsoid((x + t * 0.022, y - 0.08, 0.022), (0.016, 0.022, 0.02), subdivisions=1), SKIN))
    return parts


def foot(x, y):
    """Long dark foot, heel back, toes forward."""
    parts = [(nh.ellipsoid((x, y - 0.04, 0.03), (0.045, 0.09, 0.03), subdivisions=2), SKIN)]
    for t in (-1, 0, 1):
        parts.append((nh.ellipsoid((x + t * 0.022, y - 0.13, 0.02), (0.016, 0.024, 0.018), subdivisions=1), SKIN))
    return parts


def arm(x, y, stride):
    # long straight arm, slightly bowed at the elbow, wrist bent so the hand lies flat
    pts = [(x, y, 0.62), (x * 1.08, y + 0.03, 0.36), (x * 1.08, y + stride, 0.12), (x * 1.08, y + stride - 0.01, 0.05)]
    parts = [(nh.ellipsoid((x * 0.95, y + 0.02, 0.54), (0.09, 0.12, 0.16), subdivisions=2), fur()),  # shoulder
             (nh.tube(pts, [0.088, 0.068, 0.052, 0.04], sides=9), fur(0.1))]
    parts += hand(x * 1.08, y + stride)
    return parts


def leg(x, y, stride):
    # thigh forward, knee bent, shin back to the ankle
    pts = [(x, y, 0.55), (x * 1.05, y - 0.10, 0.34), (x * 1.08, y + 0.06 + stride, 0.10), (x * 1.08, y + 0.07 + stride, 0.05)]
    parts = [(nh.ellipsoid((x * 0.9, y + 0.02, 0.48), (0.10, 0.16, 0.17), subdivisions=2), fur()),  # thigh
             (nh.tube(pts, [0.09, 0.062, 0.046, 0.038], sides=9), fur(0.1))]
    parts += foot(x * 1.08, y + 0.07 + stride)
    return parts


def mane(rng):
    """Fuller, shaggier fur over the shoulders and neck, flowing back over the forequarters."""
    col = fur(lighten=0.25)
    parts = [(nh.ellipsoid((0, -0.20, 0.66), (0.23, 0.31, 0.19), subdivisions=3, deform=lumpy(0.10, 4.0)), col)]
    for i in range(8):
        a = rng.uniform(-1.2, 1.2)
        p = (math.sin(a) * 0.18, rng.uniform(-0.40, -0.05), 0.62 + math.cos(a) * 0.1)
        r = rng.uniform(0.055, 0.08)
        parts.append((nh.ellipsoid(p, (r, r * 1.6, r), subdivisions=2, deform=lumpy(0.15, 5.0)), col))
    return parts


def snout(hy, hz):
    """Long, tapered, slightly boxy dog-like snout: broad at the base, flat on top, nose pad at the tip."""
    base = Vector((0, hy - 0.06, hz - 0.02))
    tip = Vector((0, hy - 0.285, hz - 0.10))
    radii = [0.076, 0.062, 0.047, 0.036]
    pts = [base.lerp(tip, t) for t in (0.0, 0.35, 0.7, 1.0)]
    bm = nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.92))
    axis = tip - base
    for v in bm.verts:
        t = max(0.0, min(1.0, (v.co - base).dot(axis) / axis.length_squared))
        a = base.lerp(tip, t)
        r = radii[0] + (radii[-1] - radii[0]) * t
        top = a.z + r * 0.62                       # flat top ridge
        if v.co.z > top:
            v.co.z = top
        side = v.co.x
        if abs(side) > r * 0.88:                   # squarer sides
            v.co.x = math.copysign(r * 0.88, side)

    def col(co, n):
        # charcoal skin fading into olive fur where it meets the face
        t = nh.smoothstep(base.y, base.y - 0.07, co.y)
        skin = nh.lerp(SKIN, SKIN_LIGHT, 0.35 * max(0.0, n.z))
        return nh.lerp(FUR_DARK, skin, t)

    parts = [(bm, col)]
    # nose pad at the very tip, overhanging the mouth
    parts.append((nh.ellipsoid((0, tip.y - 0.012, tip.z + 0.012), (0.042, 0.022, 0.034), subdivisions=2), NOSE))
    for s in (-1, 1):
        parts.append((nh.ellipsoid((s * 0.016, tip.y - 0.032, tip.z + 0.006), (0.011, 0.006, 0.009), subdivisions=1), MOUTH))
        # mouth line along each lower side of the snout, stopping short of the nose pad
        line = []
        for t in (0.1, 0.5, 0.88):
            r = radii[0] + (radii[-1] - radii[0]) * t
            line.append(base.lerp(tip, t) + Vector((s * r * 0.84, 0, -r * 0.5)))
        parts.append((nh.tube(line, [0.005, 0.005, 0.004], sides=4), MOUTH))
    # lower jaw, recessed under the nose pad
    parts.append((nh.tube([(0, base.y, base.z - 0.04), (0, tip.y + 0.04, tip.z - 0.028)], [0.045, 0.022], sides=8,
                          scale_xy=(0.9, 0.6)), lambda co, n: nh.lerp(FUR_DARK, SKIN_LIGHT, nh.smoothstep(base.y, base.y - 0.07, co.y))))
    return parts


def head_parts():
    hy, hz = -0.56, 0.62
    parts = []
    # cranium, low and set forward of the shoulders
    parts.append((nh.uv_ellipsoid((0, hy, hz + 0.01), (0.115, 0.12, 0.11), segments=16, rings=10), fur(lighten=0.1)))
    # fluffy cheek fur framing the face
    for s in (-1, 1):
        parts.append((nh.ellipsoid((s * 0.085, hy - 0.03, hz - 0.03), (0.045, 0.06, 0.06), subdivisions=2,
                                   deform=lumpy(0.12, 4.0)), fur(lighten=0.15)))
    # dark bare skin around the eyes
    parts.append((nh.ellipsoid((0, hy - 0.10, hz + 0.008), (0.062, 0.03, 0.042), subdivisions=2),
                  lambda co, n: nh.lerp(SKIN, SKIN_LIGHT, 0.3 * max(0.0, n.z))))
    # furred heavy brow shading the eyes
    parts.append((nh.tube([(-0.07, hy - 0.10, hz + 0.048), (0, hy - 0.128, hz + 0.058), (0.07, hy - 0.10, hz + 0.048)],
                          [0.024, 0.03, 0.024], sides=8), fur()))
    parts += snout(hy, hz)
    # close-set amber eyes under the brow
    for s in (-1, 1):
        parts.append((nh.ellipsoid((s * 0.03, hy - 0.126, hz + 0.018), (0.016, 0.01, 0.013), subdivisions=2), EYE))
        parts.append((nh.ellipsoid((s * 0.03, hy - 0.134, hz + 0.018), (0.008, 0.005, 0.008), subdivisions=1), PUPIL))
        # small ears tucked into the fur
        parts.append((nh.ellipsoid((s * 0.10, hy + 0.04, hz + 0.05), (0.02, 0.03, 0.03), subdivisions=1), SKIN_LIGHT))
    return parts


def tail_parts():
    # raised at the base, sharply "broken", then hanging down
    pts = [(0, 0.40, 0.60), (0, 0.48, 0.70), (0, 0.55, 0.76), (0, 0.61, 0.74),
           (0, 0.65, 0.62), (0, 0.67, 0.46), (0, 0.66, 0.34)]
    parts = [(nh.tube(pts, [0.04, 0.035, 0.03, 0.028, 0.025, 0.022, 0.0], sides=8), fur(0.1))]
    # small pinkish-grey rump pads
    for s in (-1, 1):
        parts.append((nh.ellipsoid((s * 0.035, 0.435, 0.50), (0.04, 0.025, 0.05), subdivisions=2), PAD))
    return parts


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(body(), fur())
    # walking: left-front and right-hind forward
    for p in arm(-0.11, -0.28, -0.10) + arm(0.11, -0.28, 0.06) + leg(-0.11, 0.30, 0.06) + leg(0.11, 0.30, -0.08):
        mb.add(*p)
    mb.add(nh.tube([(0, -0.30, 0.62), (0, -0.48, 0.62)], [0.10, 0.08], sides=10), fur())  # neck
    for p in mane(rng) + head_parts() + tail_parts():
        mb.add(*p)
    obj = mb.to_object("OliveBaboon")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "OliveBaboon", ground=(0.55, 0.50, 0.30), views=((35, 25), (-90, 8), (20, 65)))
