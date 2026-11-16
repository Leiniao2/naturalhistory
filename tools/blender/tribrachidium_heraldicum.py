"""
Procedural Tribrachidium heraldicum (Ediacaran trilobozoan) for the map, Fixed style.

A low, gently domed disc resting on the microbial mat, built on THREE-fold symmetry - a body
plan no living animal shares. From a small central boss three raised arms spiral out, all
curling the same way, each ending in a hook that turns back on itself; fine oblique bristle-
like striations cross the arms. Around the arms the disc dips into a shallow ring furrow,
then flares into a broad, frilly margin of short radial ribs whose scalloped edge rises and
falls. A sessile filter feeder. Muted pinkish ochre disc, paler arms, darker furrows.
The body is one polar heightfield over a flat base (like kimberella_quadrata.py).
Pivot at the base (z = 0), faces -Y, seen mostly from above.

Usage:
  blender --background --python tools/blender/tribrachidium_heraldicum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tribrachidium.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

R = 0.62               # disc radius
RIBS = 36              # radial ribs around the margin
SEGS = RIBS * 3        # segments around (three per rib; divisible by 3 for the symmetry)
MARGIN_R = 0.74        # where the arm field gives way to the ribbed margin (fraction of R)
DOME_H = 0.085         # dome height at the centre
ARM_H = 0.045          # arm ridge height
CURL = 2.1             # radians the arms turn between the centre and the hook
ARM_START, ARM_END = 0.09, 0.62   # arm radial extent (fraction of R) before the hook

DISC = (0.72, 0.54, 0.44)        # pinkish ochre
DISC_LIGHT = (0.82, 0.66, 0.54)
ARM = (0.90, 0.76, 0.62)         # pale raised arms
ARM_DARK = (0.66, 0.48, 0.38)    # striations across the arms
FURROW = (0.42, 0.29, 0.23)
RIB = (0.80, 0.62, 0.50)
RIB_DARK = (0.52, 0.37, 0.29)
BASE = (0.55, 0.42, 0.34)


def arm_path(k):
    """Polyline (x, y, w) of arm k: a spiral from the centre, then a tight hook."""
    pts = []
    th0 = -math.pi / 2 + k * math.tau / 3
    n = 22
    for i in range(n + 1):
        t = i / n
        r = (ARM_START + (ARM_END - ARM_START) * t) * R
        th = th0 + CURL * t ** 1.3
        pts.append((r * math.cos(th), r * math.sin(th), 0.034 + 0.018 * math.sin(math.pi * min(1.0, t * 1.3))))
    # the hook: the arm tip curls inward, back toward the centre
    r_end, th_end = ARM_END * R, th0 + CURL
    for i in range(1, 9):
        a = i / 8 * math.radians(150)
        rr = r_end - 0.08 * (1.0 - math.cos(a))
        th = th_end + 0.26 * math.sin(a) + 0.10 * a
        pts.append((rr * math.cos(th), rr * math.sin(th), 0.034 * (1.0 - 0.4 * i / 8)))
    return pts


ARMS = [arm_path(k) for k in range(3)]


def arm_field(x, y):
    """(ridge 0..1, position along the arm 0..1, distance) of the nearest arm."""
    best = (1e9, 0.0, 0.05)
    for pts in ARMS:
        n = len(pts) - 1
        for i in range(n):
            ax, ay, aw = pts[i]
            bx, by, bw = pts[i + 1]
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy or 1e-12
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
            d = math.hypot(x - ax - t * dx, y - ay - t * dy)
            if d < best[0]:
                best = (d, (i + t) / n, aw + (bw - aw) * t)
    d, pos, w = best
    return math.exp(-(d / w) ** 2), pos, d


def ring_radii():
    """Radial stations (fraction of R): dense enough through the arm field to carry the arms,
    then through the furrow and ribbed margin."""
    inner = [MARGIN_R * (i / 16) ** 0.9 for i in range(17)]
    return inner[:-1] + [MARGIN_R, 0.79, 0.85, 0.90, 0.945, 0.975, 1.0]


def rib_wave(theta):
    return math.cos(theta * RIBS)


def height(r, theta, x, y):
    """Top surface height at polar station r (fraction of R), angle theta."""
    h = DOME_H * (1.0 - min(1.0, r / 1.0) ** 2.0) ** 0.7 + 0.018
    ridge, pos, _ = arm_field(x, y)
    h += ARM_H * ridge * (1.0 - 0.4 * pos)
    h += 0.012 * math.exp(-(r / 0.10) ** 2)                      # small central boss
    h -= 0.014 * math.exp(-((r - MARGIN_R - 0.02) / 0.035) ** 2)   # ring furrow
    m = nh.smoothstep(MARGIN_R, MARGIN_R + 0.08, r)
    h += m * 0.010 * rib_wave(theta)                             # radial ribs
    h += 0.008 * rib_wave(theta * 0.5) * nh.smoothstep(0.9, 1.0, r)   # scalloped, ruffled edge
    return h


def top_color(r, theta, co):
    x, y = co.x, co.y
    c = nh.lerp(DISC_LIGHT, DISC, nh.smoothstep(0.0, MARGIN_R, r))
    ridge, pos, d = arm_field(x, y)
    # fine bristle-like striations across the arms
    stripe = 0.5 + 0.5 * math.cos(pos * 34.0 * math.pi)
    arm_c = nh.lerp(ARM, ARM_DARK, stripe * 0.45 * nh.smoothstep(0.05, 0.2, pos))
    c = nh.lerp(c, FURROW, math.exp(-((d - 0.06) / 0.025) ** 2) * 0.5 * (1.0 - ridge))  # arm edges
    c = nh.lerp(c, arm_c, nh.smoothstep(0.25, 0.75, ridge))
    c = nh.lerp(c, ARM, math.exp(-(r / 0.08) ** 2))                  # central boss
    c = nh.lerp(c, FURROW, math.exp(-((r - MARGIN_R - 0.02) / 0.03) ** 2) * 0.8)
    m = nh.smoothstep(MARGIN_R + 0.03, MARGIN_R + 0.08, r)
    rib = nh.lerp(RIB, RIB_DARK, (0.5 - 0.5 * rib_wave(theta)) * 0.75)
    c = nh.lerp(c, rib, m)
    k = 1.0 + 0.07 * noise.noise(co * 16.0)
    return tuple(min(1.0, a * k) for a in c)


def body():
    bm = bmesh.new()
    vcol = {}
    rings = []
    for i, r in enumerate(ring_radii()):
        if i == 0:
            co = Vector((0.0, 0.0, 0.0))
            co.z = height(0.0, 0.0, 0.0, 0.0)
            v = bm.verts.new(co)
            vcol[v] = top_color(0.0, 0.0, co)
            rings.append([v])
            continue
        ring = []
        for k in range(SEGS):
            th = -math.pi / 2 + k / SEGS * math.tau
            # the frilly edge scallops in and out
            rr = r * R * (1.0 + 0.012 * rib_wave(th * 0.5) * nh.smoothstep(0.93, 1.0, r))
            x, y = rr * math.cos(th), rr * math.sin(th)
            co = Vector((x, y, height(r, th, x, y)))
            v = bm.verts.new(co)
            vcol[v] = top_color(r, th, co)
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(SEGS):
            j = (k + 1) % SEGS
            if len(a) == 1:
                bm.faces.new([a[0], b[k], b[j]])
            else:
                bm.faces.new([a[k], b[k], b[j], a[j]])
    # flat base, tucked just inside the edge
    edge = rings[-1]
    base = []
    for k, ev in enumerate(edge):
        v = bm.verts.new((ev.co.x * 0.96, ev.co.y * 0.96, 0.0))
        vcol[v] = BASE
        base.append(v)
    for k in range(SEGS):
        j = (k + 1) % SEGS
        bm.faces.new([edge[k], base[k], base[j], edge[j]])
    bm.faces.new(list(reversed(base)))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def build():
    mb = nh.MeshBuilder()
    bm, vcol = body()
    nf.add_colored(mb, bm, vcol)
    obj = mb.to_object("Tribrachidium", roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Tribrachidium", ground=(0.50, 0.48, 0.38), background=(0.05, 0.14, 0.18),
           views=((30, 40), (0, 88), (-90, 10)))
