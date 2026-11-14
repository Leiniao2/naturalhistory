"""
Procedural water bear (tardigrade) for colony instancing: a plump, barrel-shaped body of
four trunk segments behind a rounded head, with a tubular mouth cone, two dark eyespots,
four pairs of stubby legs (the last pair pointing backwards) each ending in four dark,
hooked claws. Translucent-looking tan-pink cuticle with soft segment creases and a darker
gut showing through the back.

Drift style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/water_bear.py -- [--render out.png]
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

CUTICLE = (0.86, 0.70, 0.58)    # pale tan-pink
BELLY = (0.95, 0.84, 0.74)
CREASE = (0.66, 0.48, 0.40)
GUT = (0.52, 0.42, 0.24)        # olive-brown gut contents seen through the back
MOUTH = (0.92, 0.62, 0.58)
CLAW = (0.18, 0.12, 0.08)
EYE = (0.06, 0.04, 0.04)

# (y, half-width, half-height) of the head and trunk segments, front (-Y) to back
SEGMENTS = [(-0.62, 0.22, 0.21), (-0.33, 0.30, 0.28), (-0.02, 0.33, 0.31),
            (0.30, 0.32, 0.30), (0.58, 0.25, 0.24)]
LEG_Y = [-0.33, -0.02, 0.30]


def arch(y):
    """Body midline height: the back humps up slightly over the middle."""
    return 0.04 * math.cos(y * 1.6)


def leg(y, side, back=False):
    """Stubby conical leg from the flank down to a foot; returns (shell, foot point, axis)."""
    s = 1 if side > 0 else -1
    if back:
        pts = [Vector((s * 0.1, 0.6, arch(0.6) - 0.05)), Vector((s * 0.15, 0.76, -0.12)),
               Vector((s * 0.17, 0.84, -0.2))]
    else:
        pts = [Vector((s * 0.14, y, arch(y) - 0.08)), Vector((s * 0.29, y - 0.02, -0.2)),
               Vector((s * 0.32, y - 0.03, -0.32))]
    bm = nh.tube(pts, [0.13, 0.11, 0.09], sides=10)
    return bm, pts[-1], (pts[-1] - pts[-2]).normalized()


def claws(foot, axis, side):
    """Four hooked claws fanned around the end of a leg."""
    out = []
    ref = Vector((0, -1, 0)) if abs(axis.y) < 0.8 else Vector((0, 0, -1))
    fwd = (ref - axis * ref.dot(axis)).normalized()
    lat = axis.cross(fwd).normalized()
    for k in range(4):
        a = (k - 1.5) * 0.45
        spread = fwd * math.cos(a) + lat * math.sin(a)
        p0 = foot - axis * 0.07 + spread * 0.03
        p1 = foot + axis * 0.0 + spread * 0.06
        p2 = p1 + spread * 0.06 + axis * 0.025
        out.append(nh.tube([p0, p1, p2], [0.022, 0.016, 0.0], sides=5))
    return out


def build():
    mb = nh.MeshBuilder()
    for y, w, h in SEGMENTS:
        mb.add(nh.ellipsoid((0, y, arch(y)), (w, 0.25, h), subdivisions=3), CUTICLE)
    mb.add(nh.ellipsoid((0, 0.0, arch(0) - 0.02), (0.29, 0.62, 0.26), subdivisions=3), CUTICLE)
    # mouth cone poking out of the front of the head
    mb.add(nh.tube([(0, -0.7, -0.03), (0, -0.86, -0.06), (0, -0.93, -0.07)], [0.12, 0.1, 0.085], sides=10),
           MOUTH)
    feet = []
    for y in LEG_Y:
        for side in (-1, 1):
            bm, foot, axis = leg(y, side)
            mb.add(bm, CUTICLE)
            feet.append((foot, axis, side))
    for side in (-1, 1):
        bm, foot, axis = leg(0, side, back=True)
        mb.add(bm, CUTICLE)
        feet.append((foot, axis, side))

    body = mb.fuse(voxel=0.05, smooth=8, smooth_factor=0.5)

    # cuticle: annular creases between segments and fine wrinkles
    seg_ys = [(SEGMENTS[i][0] + SEGMENTS[i + 1][0]) / 2 for i in range(len(SEGMENTS) - 1)]

    def crease(co):
        if co.z < -0.15 and abs(co.x) > 0.1:  # not on the legs
            return 0.0
        return max(math.exp(-((co.y - sy) / 0.05) ** 2) for sy in seg_ys)

    for v in body.verts:
        c = crease(v.co)
        v.co += v.normal * (-0.03 * c + 0.006 * noise.noise(v.co * 30))

    def color(co, n):
        c = nh.lerp(BELLY, CUTICLE, nh.smoothstep(-0.25, 0.05, co.z))
        # gut contents glow through the upper flanks and back
        gut = nh.smoothstep(0.45, 0.15, math.hypot(co.x * 1.2, co.y * 0.75))
        gut *= nh.smoothstep(-0.05, 0.2, co.z) * (0.75 + 0.25 * noise.noise(co * 6))
        c = nh.lerp(c, GUT, 0.6 * gut)
        c = nh.lerp(c, CREASE, 0.7 * crease(co))
        if co.y < -0.74 and abs(co.x) < 0.14:
            c = nh.lerp(c, MOUTH, nh.smoothstep(-0.74, -0.84, co.y))
        k = 0.94 + 0.1 * noise.noise(co * 25)
        return tuple(min(1.0, x * k) for x in c)

    out = nh.MeshBuilder()
    out.add(body, color)
    # dark mouth opening and eyespots
    out.add(nh.ellipsoid((0, -0.915, -0.07), (0.04, 0.02, 0.04), subdivisions=1), EYE)
    for s in (-1, 1):
        out.add(nh.ellipsoid((s * 0.135, -0.755, 0.11), (0.026, 0.026, 0.026), subdivisions=1), EYE)
    for foot, axis, side in feet:
        for bm in claws(foot, axis, side):
            out.add(bm, CLAW, smooth=False)
    obj = out.to_object("WaterBear", roughness=0.35)
    # centre the pivot on the body
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj


if __name__ == "__main__":
    nh.run(build, "WaterBear", views=((35, 25), (-90, 8), (150, 30)))
