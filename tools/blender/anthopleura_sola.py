"""
Procedural low-poly sunburst anemone (Anthopleura sola) for the map.

A squat, olive column studded with rows of pale sticky warts (verrucae) on a
broad pedal disc, flaring at the top into a wide, slightly cupped oral disc:
green, with the radiating pink-lavender "sunburst" stripes that give the species
its name, and a pink-lipped mouth slit in the centre. Several rings of short,
tapering tentacles crowd the disc margin - the inner ones held up, the outer ones
splayed out and drooping - green at the base, banded pale, with pink-lavender tips.
Fixed style: pivot at the pedal disc (z = 0).

Usage:
  blender --background --python tools/blender/anthopleura_sola.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SunburstAnemone.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SEED = 7
COL_R = 0.30        # column radius at mid height
COL_H = 0.24        # column height (to the disc margin)
DISC_R = 0.42       # oral disc radius (to the tentacle ring)
STRIPES = 22        # radiating sunburst stripes on the oral disc
RINGS = ((42, 0.98, 0.12, 68), (36, 0.89, 0.13, 45), (30, 0.80, 0.12, 26), (20, 0.71, 0.10, 12))
# tentacle rings, outer to inner: (count, radius as a fraction of DISC_R, length, tip tilt from vertical in degrees)

COLUMN = (0.34, 0.40, 0.22)       # olive-green column
COLUMN_DARK = (0.22, 0.27, 0.15)
VERRUCA = (0.62, 0.66, 0.46)      # pale warts
DISC = (0.24, 0.55, 0.28)         # green oral disc
DISC_DARK = (0.14, 0.36, 0.18)
STRIPE = (0.86, 0.58, 0.84)       # pink-lavender sunburst rays
MOUTH = (0.92, 0.50, 0.62)
MOUTH_DARK = (0.35, 0.12, 0.18)
TENT_BASE = (0.30, 0.52, 0.30)
TENT_BAND = (0.78, 0.82, 0.70)
TENT_TIP = (0.88, 0.52, 0.86)     # pink-lavender tips
TENT_TIP_ALT = (0.95, 0.62, 0.72)


def column():
    """Squat column, slightly waisted, widening into the disc margin; warts in vertical rows."""
    n_t, n_z = 40, 12
    bm = bmesh.new()
    rings = []
    for i in range(n_z + 1):
        t = i / n_z
        z = COL_H * t
        # straight, slightly bulging column that flares smoothly out under the disc margin
        r = COL_R * (1.06 - 0.05 * math.sin(math.pi * t)) + (DISC_R * 1.0 - COL_R * 1.06) * nh.smoothstep(0.45, 1.0, t) ** 1.6
        if i == 0:
            r = COL_R * 1.14  # pedal disc
        ring = []
        for j in range(n_t):
            a = j / n_t * math.tau
            # verrucae: bumps in vertical rows, strongest on the upper column
            wart = max(0.0, math.cos(a * 20)) ** 6 * max(0.0, math.sin(t * math.pi * 6)) ** 4
            rr = r * (1.0 + 0.04 * wart * nh.smoothstep(0.1, 0.5, t) + 0.02 * noise.noise(Vector((a * 2, t * 3, 1.0))))
            ring.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, z)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for j in range(n_t):
            k = (j + 1) % n_t
            bm.faces.new([a[j], a[k], b[k], b[j]])
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        a = math.atan2(co.y, co.x)
        t = co.z / COL_H
        wart = max(0.0, math.cos(a * 20)) ** 6 * max(0.0, math.sin(t * math.pi * 6)) ** 4
        c = nh.lerp(COLUMN_DARK, COLUMN, nh.smoothstep(0.0, 0.6, t))
        return nh.lerp(c, VERRUCA, nh.smoothstep(0.2, 0.7, wart) * nh.smoothstep(0.1, 0.4, t))
    return bm, color


def disc_height(rf):
    """Oral disc surface height: cupped toward the mouth, rising to the margin."""
    return COL_H + 0.02 - 0.035 * (1.0 - rf * rf)


def oral_disc():
    n_r, n_t = 6, 132
    bm = bmesh.new()
    centre = bm.verts.new((0, 0, disc_height(0.0) - 0.01))
    rings = []
    for i in range(1, n_r + 1):
        rf = i / n_r
        ring = []
        for j in range(n_t):
            a = j / n_t * math.tau
            r = DISC_R * rf
            ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, disc_height(rf))))
        rings.append(ring)
    for j in range(n_t):
        bm.faces.new([centre, rings[0][j], rings[0][(j + 1) % n_t]])
    for a, b in zip(rings, rings[1:]):
        for j in range(n_t):
            k = (j + 1) % n_t
            bm.faces.new([a[j], a[k], b[k], b[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        rf = math.hypot(co.x, co.y) / DISC_R
        a = math.atan2(co.y, co.x)
        # mouth slit: an elongated pink oval with a dark centre
        mx, my = co.x / 0.075, co.y / 0.035
        m = math.hypot(mx, my)
        if m < 0.45:
            return MOUTH_DARK
        if m < 1.0:
            return MOUTH
        # radiating stripes, narrow near the mouth, widening outward, softly edged
        s = 0.5 + 0.5 * math.cos(a * STRIPES + 0.6 * math.sin(a * 3))
        width = 0.62 - 0.18 * rf
        ray = nh.smoothstep(width, width + 0.18, s) * nh.smoothstep(0.18, 0.35, rf)
        base = nh.lerp(DISC_DARK, DISC, nh.smoothstep(0.1, 0.8, rf))
        return nh.lerp(base, STRIPE, ray)
    return bm, color


def tentacle(rng, angle, rf, length, droop):
    """Short tapering tentacle rising from the disc and curving outward; returns (bm, color)."""
    r0 = DISC_R * rf
    base = Vector((math.cos(angle) * r0, math.sin(angle) * r0, disc_height(rf) - 0.01))
    out = Vector((math.cos(angle), math.sin(angle), 0.0))
    tilt0 = math.radians(droop * 0.35)
    tilt1 = math.radians(droop + rng.uniform(-8, 8))
    pts, radii = [], []
    p = base.copy()
    steps = 4
    rad = 0.022 * (0.85 + 0.3 * rng.random())
    seg = length * rng.uniform(0.85, 1.15) / steps
    for k in range(steps + 1):
        t = k / steps
        pts.append(p.copy())
        radii.append(rad * (1.0 - 0.5 * t))
        tilt = tilt0 + (tilt1 - tilt0) * t
        d = out * math.sin(tilt) + Vector((0, 0, math.cos(tilt)))
        p += d * (seg if k < steps else rad * 0.45)
    pts.append(p.copy())  # rounded, blunt tip
    radii.append(0.0)
    bm = nh.tube(pts, radii, sides=5)
    tip_col = TENT_TIP if rng.random() < 0.7 else TENT_TIP_ALT
    total = sum((b - a).length for a, b in zip(pts, pts[1:]))

    def color(co, n):
        t = min(1.0, (co - base).length / total)
        c = nh.lerp(TENT_BASE, TENT_BAND, nh.smoothstep(0.35, 0.55, t) * (1.0 - nh.smoothstep(0.6, 0.72, t)))
        return nh.lerp(c, tip_col, nh.smoothstep(0.6, 0.85, t))
    return bm, color


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(*column())
    mb.add(*oral_disc())
    for ring_i, (count, rf, length, droop) in enumerate(RINGS):
        offset = rng.random() * math.tau
        for k in range(count):
            a = offset + (k + 0.5 * (ring_i % 2)) / count * math.tau + rng.uniform(-0.03, 0.03)
            mb.add(*tentacle(rng, a, rf, length, droop))
    obj = mb.to_object("SunburstAnemone", roughness=0.4)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "SunburstAnemone", background=(0.04, 0.20, 0.30), ground=(0.42, 0.40, 0.36),
           views=((35, 30), (10, 75), (-90, 10)))
