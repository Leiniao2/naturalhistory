"""
Procedural low-poly western rock lobster (Panulirus cygnus) for map colonies.

A spiny lobster with no big claws: a rounded, spiny cephalothorax ending in two
big forward-pointing horns over the eyes; a pair of very long, thick, spiny
second antennae sweeping forward and out well beyond the body length, plus a
pair of short forked antennules between them; five pairs of slender walking
legs; a six-segmented abdomen with down-curved side plates (pleura), each
segment banded and dotted with pale spots; and a tail fan of telson and two
pairs of uropods. Burgundy / purple-red shell with pale cream spots, orange-red
legs with pale bands, cream underside. Faces -Y, pivot at the body centre
(Swim style, like the other benthic marine animals on the opaque water tiles).

Usage:
  blender --background --python tools/blender/panulirus_cygnus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/WesternRockLobster.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

SHELL = (0.46, 0.08, 0.14)      # burgundy / purple-red
SHELL_LIGHT = (0.66, 0.16, 0.18)
SEAM = (0.26, 0.04, 0.08)
SPOT = (0.95, 0.86, 0.72)       # pale cream spots
UNDER = (0.93, 0.80, 0.64)
SPINE_TIP = (0.98, 0.78, 0.55)
ANTENNA = (0.58, 0.14, 0.14)
ANTENNA_TIP = (0.80, 0.40, 0.28)
LEG = (0.80, 0.30, 0.18)
LEG_BAND = (0.98, 0.84, 0.62)
TAIL = (0.62, 0.16, 0.16)
TAIL_EDGE = (0.98, 0.70, 0.40)
EYE = (0.04, 0.03, 0.03)

BODY_Z = 0.16           # height of the body axis above the feet
CEPH_FRONT = -0.46
CEPH_BACK = 0.0
ABD_SEGS = 6
ABD_BACK = 0.56


def axis_z(y):
    """Body axis height: level carapace, abdomen curving gently down toward the tail."""
    if y <= 0.0:
        return BODY_Z
    return BODY_Z - 0.10 * (y / ABD_BACK) ** 2


def mirror(bm, side):
    if side < 0:
        nh.transform(bm, Matrix.Scale(-1, 4, (1, 0, 0)))
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return bm


def shell_color(co, n):
    """Burgundy above with segment seams on the abdomen and scattered pale spots, cream below."""
    c = nh.lerp(SHELL, SHELL_LIGHT, 0.3 * (1.0 - abs(n.z)))
    if co.y > CEPH_BACK - 0.01:
        f = ((co.y - CEPH_BACK) / ((ABD_BACK - CEPH_BACK) / ABD_SEGS)) % 1.0
        c = nh.lerp(c, SEAM, 0.8 * (1.0 - nh.smoothstep(0.0, 0.14, f)))  # darker front edge of each tergite
    else:
        c = nh.lerp(c, SHELL_LIGHT, 0.25 * (0.5 + 0.5 * noise.noise(co * 18.0)))  # mottled carapace
    return nh.lerp(UNDER, c, nh.smoothstep(-0.7, -0.2, n.z))


def body():
    """Cephalothorax + abdomen as one tube with pinches between the abdominal segments."""
    pts, radii = [], []
    n_ceph = 12
    for i in range(n_ceph):
        y = CEPH_FRONT + (CEPH_BACK - CEPH_FRONT) * i / n_ceph
        t = (y - CEPH_FRONT) / (CEPH_BACK - CEPH_FRONT)
        r = 0.095 + 0.055 * math.sin(math.pi * min(1.0, 0.25 + t * 0.85)) ** 0.6
        pts.append((0, y, axis_z(y)))
        radii.append(r)
    seg = (ABD_BACK - CEPH_BACK) / ABD_SEGS
    for s in range(ABD_SEGS):
        for k, f in enumerate((0.0, 0.35, 0.7)):
            y = CEPH_BACK + seg * (s + f)
            t = (y - CEPH_BACK) / (ABD_BACK - CEPH_BACK)
            r = (0.13 - 0.04 * t) * (0.92 if k == 0 else 1.0)
            pts.append((0, y, axis_z(y)))
            radii.append(r)
    pts.append((0, ABD_BACK + 0.01, axis_z(ABD_BACK)))
    radii.append(0.06)
    radii[0] = 0.06
    return nh.tube(pts, radii, sides=14, scale_xy=(1.12, 0.74))


def cone(base, direction, length, radius, sides=4):
    d = Vector(direction).normalized()
    return nh.tube([Vector(base), Vector(base) + d * length], [radius, 0.0], sides=sides, cap_start=False)


def tip_color(base, direction, length, root):
    b, d = Vector(base), Vector(direction).normalized()
    return lambda co, n: nh.lerp(root, SPINE_TIP, nh.smoothstep(0.3, 1.0, (co - b).dot(d) / length))


def carapace_spines(mb):
    """Forward-pointing spines in loose rows over the cephalothorax."""
    for row in range(5):
        y = CEPH_FRONT + 0.08 + row * 0.08
        t = (y - CEPH_FRONT) / (CEPH_BACK - CEPH_FRONT)
        r = 0.095 + 0.055 * math.sin(math.pi * min(1.0, 0.25 + t * 0.85)) ** 0.6
        for a_deg in (-60, -30, 30, 60) if row % 2 == 0 else (-75, -45, -15, 15, 45, 75):
            a = math.radians(a_deg + 90)
            p = Vector((math.cos(a) * r * 1.12, y, axis_z(y) + math.sin(a) * r * 0.74))
            out = Vector((math.cos(a), 0, math.sin(a)))
            d = (out * 0.6 + Vector((0, -1.0, 0.25))).normalized()
            ln = 0.04 + 0.015 * (row == 0)
            mb.add(cone(p - out * 0.008, d, ln, 0.011), tip_color(p, d, ln, SHELL_LIGHT), smooth=False)


def horns(mb):
    """The two big supraorbital horns and the eyes beneath them."""
    for s in (-1, 1):
        base = Vector((s * 0.05, CEPH_FRONT + 0.07, BODY_Z + 0.07))
        d = Vector((s * 0.2, -1.0, 0.5))
        mb.add(cone(base, d, 0.17, 0.034, sides=6), tip_color(base, d, 0.17, SHELL))
        eb = Vector((s * 0.035, CEPH_FRONT + 0.03, BODY_Z + 0.02))
        et = eb + Vector((s * 0.035, -0.04, 0.0))
        mb.add(nh.tube([eb, et], [0.014, 0.012], sides=5), SHELL_LIGHT)
        mb.add(nh.ellipsoid(et + Vector((s * 0.008, -0.008, 0)), (0.019, 0.019, 0.019), subdivisions=1), EYE)


def antenna(mb, side):
    """Long, thick, spiny second antenna: stout spiny base, then a whip curving forward and out."""
    s = side
    pts = []
    n = 16
    base = Vector((s * 0.075, CEPH_FRONT + 0.03, BODY_Z - 0.0))
    for i in range(n + 1):
        t = i / n
        ang = math.radians(18 + 28 * t ** 1.2)          # sweeps outward along its length
        L = 1.15 * t
        x = s * (math.sin(ang) * L + 0.04 * t)
        y = -math.cos(ang) * L
        z = 0.10 * math.sin(t * math.pi * 0.8) - 0.10 * t ** 2
        pts.append(base + Vector((x, y, z)))
    radii = [0.05 * (1.0 - t) ** 1.1 + 0.004 for t in (i / n for i in range(n + 1))]
    radii[-1] = 0.0

    def color(co, nrm):
        t = (co - base).length / 1.15
        return nh.lerp(ANTENNA, ANTENNA_TIP, nh.smoothstep(0.2, 1.0, t))

    mb.add(nh.tube(pts, radii, sides=7), color)
    # spines along the thick basal half, pointing forward
    for i in range(1, 9):
        p = pts[i]
        fwd = (pts[i + 1] - pts[i - 1]).normalized()
        for a in (0.0, 2.1, 4.2):
            out = Vector((math.cos(a + i), 0, math.sin(a + i)))
            out = (out - fwd * out.dot(fwd)).normalized()
            d = (out + fwd * 1.3).normalized()
            ln = radii[i] * 1.2
            mb.add(cone(p + out * radii[i] * 0.7, d, ln, radii[i] * 0.3, sides=3),
                   tip_color(p, d, ln, ANTENNA), smooth=False)


def antennules(mb):
    """Short, forked first antennae between the big ones."""
    for s in (-1, 1):
        b = Vector((s * 0.02, CEPH_FRONT, BODY_Z - 0.02))
        m = b + Vector((s * 0.03, -0.16, 0.05))
        mb.add(nh.tube([b, b.lerp(m, 0.5), m], [0.012, 0.011, 0.009], sides=5), LEG)
        for k in (-1, 1):
            t = m + Vector((s * 0.04 + k * 0.025, -0.14, 0.03 + k * 0.02))
            mb.add(nh.tube([m, m.lerp(t, 0.5), t], [0.007, 0.005, 0.0], sides=4), ANTENNA_TIP)


def walking_leg(mb, i, side):
    """Slender jointed leg from the underside of the cephalothorax to the ground (z = 0)."""
    s = side
    y = -0.36 + i * 0.075
    deg = -35 + i * 22                                # front legs reach forward, back legs back
    a = math.radians(deg)
    out = Vector((s * math.cos(a), math.sin(a), 0))
    base = Vector((s * 0.08, y, BODY_Z - 0.07))
    reach = 0.36 - 0.02 * abs(i - 2)
    knee = base + out * reach * 0.45 + Vector((0, 0, 0.09))
    ankle = base + out * reach * 0.8 + Vector((0, 0, 0.0))
    tip = base + out * reach + Vector((0, 0, -base.z))
    pts = [base, knee, ankle, tip]
    r = 0.019
    for k, (p0, p1) in enumerate(zip(pts, pts[1:])):
        r0, r1 = r * (1.0 - 0.2 * k), (r * (1.0 - 0.2 * (k + 1)) if k < 2 else 0.0)

        def color(co, n, p0=p0, p1=p1):
            d = p1 - p0
            t = max(0.0, min(1.0, (co - p0).dot(d) / d.length_squared))
            return LEG_BAND if t > 0.8 or t < 0.08 else LEG
        mid = p0.lerp(p1, 0.5)
        mb.add(nh.tube([p0, mid, p1], [r0, (r0 + r1) / 2 + 0.002, r1], sides=5), color)


def pleuron(y, side, length):
    """Down-curved side plate of an abdominal segment, with a pointed rear corner."""
    pts = [(0, -0.035, 0), (length, -0.03, 0), (length * 1.1, 0.02, 0), (length * 0.6, 0.035, 0), (0, 0.035, 0)]
    bm = nh.flat_panel(pts, thickness=0.01)
    nh.transform(bm, Matrix.Rotation(math.radians(48), 4, "Y"))   # hang down the flank
    mirror(bm, side)
    t = (y - CEPH_BACK) / (ABD_BACK - CEPH_BACK)
    r = 0.13 - 0.04 * t
    nh.transform(bm, Matrix.Translation((side * r * 1.0, y, axis_z(y) - 0.005)))
    return bm


def tail_fan(mb):
    """Telson in the middle and two pairs of uropods, spread flat behind the abdomen."""
    y0 = ABD_BACK - 0.01
    z0 = axis_z(ABD_BACK) - 0.01
    tilt = Matrix.Rotation(math.radians(12), 4, "X")  # trailing edge dips a little

    def fan_color(co, n):
        return nh.lerp(TAIL, TAIL_EDGE, nh.smoothstep(y0 + 0.12, y0 + 0.21, co.y))
    telson = nh.flat_panel([(-0.05, 0, 0), (0.05, 0, 0), (0.07, 0.19, 0), (0.0, 0.21, 0), (-0.07, 0.19, 0)],
                           thickness=0.012)
    nh.transform(telson, tilt)
    nh.transform(telson, Matrix.Translation((0, y0, z0)))
    mb.add(telson, fan_color, smooth=False)
    for s in (-1, 1):
        for k, (yaw, ln) in enumerate(((16, 0.20), (36, 0.19))):
            pts = [(-0.025, 0, 0), (0.025, 0, 0), (0.065, ln * 0.75, 0), (0.0, ln, 0), (-0.055, ln * 0.8, 0)]
            bm = nh.flat_panel(pts, thickness=0.01)
            nh.transform(bm, tilt)
            nh.transform(bm, Matrix.Rotation(math.radians(-yaw), 4, "Z"))
            mirror(bm, s)
            nh.transform(bm, Matrix.Translation((s * 0.03, y0 - 0.005, z0 + 0.004 * k)))
            mb.add(bm, fan_color, smooth=False)


def abdomen_spots(mb):
    """Pale spots in transverse rows on each abdominal segment (small embedded decals)."""
    seg = (ABD_BACK - CEPH_BACK) / ABD_SEGS
    for sidx in range(ABD_SEGS):
        y = CEPH_BACK + seg * (sidx + 0.55)
        t = (y - CEPH_BACK) / (ABD_BACK - CEPH_BACK)
        r = 0.13 - 0.04 * t
        for a_deg, size in ((90, 0.75), (55, 1.0), (125, 1.0), (25, 0.85), (155, 0.85)):
            if a_deg == 90 and sidx % 2:
                continue
            a = math.radians(a_deg)
            p = Vector((math.cos(a) * r * 1.12, y, axis_z(y) + math.sin(a) * r * 0.74))
            spot = nh.uv_ellipsoid((0, 0, 0), (0.024 * size, 0.017 * size, 0.007), segments=6, rings=3)
            out = Vector((math.cos(a) / 1.12, 0, math.sin(a) / 0.74)).normalized()
            rot = out.to_track_quat("Z", "Y").to_matrix().to_4x4()
            nh.transform(spot, rot)
            nh.transform(spot, Matrix.Translation(p))
            mb.add(spot, SPOT)


def build():
    mb = nh.MeshBuilder()
    mb.add(body(), shell_color)
    carapace_spines(mb)
    horns(mb)
    for side in (-1, 1):
        antenna(mb, side)
        for i in range(5):
            walking_leg(mb, i, side)
    antennules(mb)
    seg = (ABD_BACK - CEPH_BACK) / ABD_SEGS
    for sidx in range(ABD_SEGS - 1):
        y = CEPH_BACK + seg * (sidx + 0.55)
        for side in (-1, 1):
            mb.add(pleuron(y, side, 0.05), shell_color, smooth=False)
    abdomen_spots(mb)
    tail_fan(mb)

    obj = mb.to_object("WesternRockLobster", roughness=0.4)
    # pivot at the body centre
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj


if __name__ == "__main__":
    nh.run(build, "WesternRockLobster", background=(0.05, 0.22, 0.30), views=((35, 30), (-90, 8), (0, 80)))
