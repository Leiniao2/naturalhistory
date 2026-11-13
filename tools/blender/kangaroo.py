"""
Procedural low-poly red kangaroo (Osphranter rufus) for map colonies.

Resting upright stance: sitting back on huge hind legs and long feet, the thick
tail as a third support, small bent forearms held in front of a deep chest, a
small head with long upright ears and a long deer-like muzzle. Reddish-brown
back fading to a pale cream chest and belly, dark ear tips, paws and toes, pale
muzzle band. Faces -Y, pivot on the ground.

The torso, neck and head are one lofted shell so the body flows without creases.

Usage:
  blender --background --python tools/blender/kangaroo.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kangaroo.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

RED = (0.66, 0.30, 0.15)        # reddish-brown back
RED_DARK = (0.50, 0.21, 0.10)
CREAM = (0.93, 0.84, 0.70)      # chest / belly
DARK = (0.14, 0.09, 0.07)       # ear tips, paws, toes
NOSE = (0.08, 0.06, 0.06)
MUZZLE = (0.95, 0.90, 0.82)     # pale band across the muzzle
EYE = (0.03, 0.02, 0.02)


def resample(sections, steps=3):
    """Catmull-Rom interpolation of (center, rx, rd) sections for a smoother loft."""
    vals = [(Vector(c), rx, rd) for c, rx, rd in sections]
    out = []
    for i in range(len(vals) - 1):
        p0, p1 = vals[max(0, i - 1)], vals[i]
        p2, p3 = vals[i + 1], vals[min(len(vals) - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            w = (-0.5 * t ** 3 + t * t - 0.5 * t, 1.5 * t ** 3 - 2.5 * t * t + 1,
                 -1.5 * t ** 3 + 2 * t * t + 0.5 * t, 0.5 * t ** 3 - 0.5 * t * t)
            ps = (p0, p1, p2, p3)
            c = Vector((0, 0, 0))
            for wj, pj in zip(w, ps):
                c += pj[0] * wj
            out.append((c, sum(wj * pj[1] for wj, pj in zip(w, ps)), sum(wj * pj[2] for wj, pj in zip(w, ps))))
    out.append(vals[-1])
    return out


def loft(sections, sides=16):
    """Smooth shell through (center, half_width_x, half_depth) sections along a path in the
    YZ plane; width is along X, depth in the plane. Ends close to the first/last centres."""
    bm = bmesh.new()
    sections = resample(sections)
    pts = [Vector(c) for c, _, _ in sections]
    rings = []
    for i, (c, rx, rd) in enumerate(sections):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        fwd = (b - a).normalized()
        side = Vector((1, 0, 0))
        up = side.cross(fwd).normalized()
        ring = []
        for k in range(sides):
            t = k / sides * math.tau
            ring.append(bm.verts.new(pts[i] + side * math.cos(t) * rx + up * math.sin(t) * rd))
        rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([ra[k], ra[j], rb[j], rb[k]])
    for ring, end in ((rings[0], pts[0]), (rings[-1], pts[-1])):
        # rounded cap: a pole slightly beyond the last ring
        nb = (end - (pts[1] if ring is rings[0] else pts[-2])).normalized()
        r = (ring[0].co - end).length
        pole = bm.verts.new(end + nb * r * 0.6)
        for k in range(sides):
            bm.faces.new([ring[k], ring[(k + 1) % sides], pole])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def oriented(center, radii, pitch=0.0, yaw=0.0, segments=18, rings=12):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings)
    rot = Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(pitch), 4, "X")
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def fur(co, n):
    c = nh.lerp(RED, RED_DARK, nh.smoothstep(0.3, 0.95, n.y * 0.7 + n.z * 0.4))
    return nh.lerp(c, RED, 0.3 * max(0.0, noise.noise(co * 10.0)))


def body_color(co, n):
    c = fur(co, n)
    if co.z > 1.0:  # head
        if co.y < -0.335:
            return NOSE
        band = 0.7 * nh.smoothstep(0.014, 0.0, abs(co.y + 0.27)) * nh.smoothstep(-0.2, 0.3, n.z)
        c = nh.lerp(c, CREAM, nh.smoothstep(-0.2, -0.7, n.z))            # pale chin and lips
        return nh.lerp(c, MUZZLE, band)
    # cream chest and belly on the front of the body and throat
    front = nh.smoothstep(-0.15, -0.55, n.y) * nh.smoothstep(0.16, 0.30, co.z)
    return nh.lerp(c, CREAM, front)


def build():
    mb = nh.MeshBuilder()

    # One shell: hips -> belly -> chest -> neck -> head -> muzzle tip
    sections = [
        ((0, 0.10, 0.13), 0.10, 0.10),
        ((0, 0.08, 0.20), 0.165, 0.18),
        ((0, 0.05, 0.32), 0.200, 0.225),
        ((0, 0.02, 0.46), 0.190, 0.215),
        ((0, -0.01, 0.60), 0.160, 0.180),
        ((0, -0.035, 0.73), 0.125, 0.140),
        ((0, -0.055, 0.84), 0.095, 0.105),
        ((0, -0.07, 0.93), 0.072, 0.080),
        ((0, -0.085, 1.01), 0.066, 0.072),
        ((0, -0.105, 1.08), 0.074, 0.080),
        ((0, -0.135, 1.125), 0.080, 0.082),
        ((0, -0.18, 1.135), 0.072, 0.072),
        ((0, -0.235, 1.118), 0.056, 0.058),
        ((0, -0.29, 1.095), 0.042, 0.046),
        ((0, -0.335, 1.08), 0.030, 0.034),
    ]
    mb.add(loft(sections, sides=18), body_color)

    # Eyes, set high on the head
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.066, -0.165, 1.165), (0.014, 0.019, 0.017), subdivisions=2), EYE)

    # Ears: long, upright, flared, pale inner faces and dark tips
    def ear_color(co, n):
        c = nh.lerp(RED, CREAM, 0.85 * nh.smoothstep(-0.1, -0.5, n.y))
        return nh.lerp(c, DARK, nh.smoothstep(1.33, 1.37, co.z))
    for sx in (-1, 1):
        ear = nh.tube([(sx * 0.04, -0.10, 1.17), (sx * 0.058, -0.095, 1.22), (sx * 0.075, -0.088, 1.29),
                       (sx * 0.088, -0.08, 1.35), (sx * 0.092, -0.077, 1.385)],
                      [0.03, 0.045, 0.042, 0.024, 0.0], sides=12, scale_xy=(1.0, 0.38))
        mb.add(ear, ear_color)

    # Hind legs: big haunch merged into the hips, shin to a defined heel, long foot forward
    for sx in (-1, 1):
        x = sx * 0.135
        mb.add(oriented((x * 0.92, 0.0, 0.25), (0.11, 0.235, 0.165), pitch=-22), lambda co, n: nh.lerp(
            fur(co, n), CREAM, 0.6 * nh.smoothstep(-0.5, -0.9, n.z)))
        mb.add(nh.tube([(x, -0.14, 0.22), (x * 1.05, -0.06, 0.15), (x * 1.08, 0.08, 0.075), (x * 1.08, 0.15, 0.05)],
                       [0.07, 0.06, 0.045, 0.038], sides=12), fur)
        mb.add(nh.ellipsoid((x * 1.08, 0.165, 0.045), (0.036, 0.04, 0.04), subdivisions=2), RED_DARK)  # heel

        def foot_color(co, n):
            return nh.lerp(RED_DARK, DARK, nh.smoothstep(-0.14, -0.27, co.y))
        foot = nh.tube([(x * 1.08, 0.17, 0.035), (x * 1.06, 0.06, 0.032), (x * 1.02, -0.10, 0.03),
                        (x * 0.98, -0.24, 0.026), (x * 0.96, -0.31, 0.022), (x * 0.955, -0.335, 0.02)],
                       [0.036, 0.046, 0.046, 0.038, 0.026, 0.0], sides=12, scale_xy=(1.0, 0.62))
        mb.add(foot, foot_color)

    # Forearms: rounded, bent, held in front of the chest; small dark paws with fingers
    for sx in (-1, 1):
        arm = nh.tube([(sx * 0.07, -0.08, 0.82), (sx * 0.11, -0.13, 0.76), (sx * 0.125, -0.17, 0.69),
                       (sx * 0.105, -0.23, 0.655), (sx * 0.085, -0.27, 0.64)],
                      [0.05, 0.046, 0.036, 0.028, 0.022], sides=12)
        mb.add(arm, fur)
        mb.add(nh.ellipsoid((sx * 0.08, -0.285, 0.633), (0.026, 0.028, 0.022), subdivisions=2), DARK)
        for f in (-1, 0, 1):
            base = Vector((sx * 0.08 + f * 0.012, -0.30, 0.628))
            tip = base + Vector((f * 0.004, -0.012, -0.03))
            mb.add(nh.tube([base, (base + tip) / 2, tip], [0.008, 0.006, 0.0], sides=5), DARK)

    # Tail: thick at the base, tapering, resting on the ground in a gentle curve
    tail = nh.tube([(0, 0.14, 0.28), (0, 0.27, 0.17), (0.01, 0.42, 0.08), (0.035, 0.60, 0.04),
                    (0.07, 0.78, 0.032), (0.09, 0.93, 0.04), (0.095, 1.02, 0.055), (0.095, 1.05, 0.06)],
                   [0.115, 0.095, 0.072, 0.055, 0.042, 0.03, 0.016, 0.0], sides=14)
    mb.add(tail, lambda co, n: nh.lerp(fur(co, n), CREAM, 0.5 * nh.smoothstep(-0.4, -0.9, n.z)))

    obj = mb.to_object("Kangaroo")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Kangaroo", ground=(0.55, 0.42, 0.25), views=((35, 25), (-90, 8), (20, 65)))
