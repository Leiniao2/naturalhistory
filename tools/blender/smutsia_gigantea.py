"""
Procedural giant ground pangolin (Smutsia gigantea, rainforests and savannas of
equatorial Africa) for map colonies: the largest pangolin, about 1.4-1.8 m long
including the tail and up to 33 kg.

A long, spindle-shaped body that tapers to a small, narrow, pointed head at one end
and into a very long, broad, thick tail at the other, the back, flanks, limbs and
tail all covered in large, overlapping, pointed keratin scales like a pine cone
(laid here as rows of separate crisp plates, rear edges lifted). Short, stout legs:
the forefeet carry three huge curved digging claws, folded under so it walks on
its knuckles; the hind feet are broad and flat. Brown-olive scales with paler
edges over grey-pink skin on the face and belly. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/smutsia_gigantea.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SmutsiaGigantea.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

SCALE = (0.42, 0.34, 0.20)
SCALE_EDGE = (0.62, 0.52, 0.34)
SKIN = (0.55, 0.45, 0.40)
EYE = (0.05, 0.04, 0.03)
CLAW = (0.25, 0.21, 0.16)

# body axis: (y, z, radius) from snout tip to tail tip
AXIS = [(-0.86, 0.225, 0.014), (-0.81, 0.24, 0.038), (-0.73, 0.27, 0.068), (-0.62, 0.30, 0.10), (-0.48, 0.33, 0.15),
        (-0.30, 0.355, 0.19), (-0.10, 0.36, 0.20), (0.10, 0.35, 0.19), (0.26, 0.32, 0.155), (0.42, 0.27, 0.13),
        (0.60, 0.20, 0.105), (0.78, 0.13, 0.08), (0.92, 0.08, 0.05), (1.02, 0.055, 0.02)]


def axis_at(y):
    for (y0, z0, r0), (y1, z1, r1) in zip(AXIS, AXIS[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return z0 + (z1 - z0) * t, r0 + (r1 - r0) * t
    return AXIS[-1][1], AXIS[-1][2]


def build():
    b = nh.MeshBuilder()
    b.add(nh.tube([(0, y, z) for y, z, _r in AXIS], [r for _y, _z, r in AXIS], sides=18, scale_xy=(1.0, 0.92)), SKIN)
    claws = []
    for (x, y, st, front) in ((-0.13, -0.32, -0.04, True), (0.13, -0.32, 0.05, True), (-0.14, 0.14, 0.04, False),
                              (0.14, 0.14, -0.04, False)):
        top = Vector((x * 0.8, y, 0.30))
        foot = Vector((x * 1.1, y + st, 0.0))
        b.add(nh.tube([tuple(top), tuple(top.lerp(foot, 0.55)), tuple(foot + Vector((0, 0, 0.04)))],
                      [0.075, 0.055, 0.045] if front else [0.09, 0.065, 0.05], sides=12), SKIN)
        if front:
            # knuckle-walking: the hand rests on the backs of the folded digits, claws curled under
            b.add(nh.ellipsoid(tuple(foot + Vector((0, -0.02, 0.03))), (0.05, 0.05, 0.035)), SKIN)
            for a in (-0.35, 0.0, 0.35):
                claws.append((foot + Vector((math.sin(a) * 0.03, -0.045, 0.035)), True))
        else:
            b.add(nh.ellipsoid(tuple(foot + Vector((0, -0.03, 0.02))), (0.055, 0.08, 0.025)), SKIN)
            for a in (-0.6, -0.3, 0.0, 0.3, 0.6):
                claws.append((foot + Vector((math.sin(a) * 0.045, -0.10 + abs(a) * 0.03, 0.012)), False))
    fused = b.fuse(voxel=0.012, smooth=4, smooth_factor=0.5, max_tris=9000)
    fused.normal_update()
    tree = BVHTree.FromBMesh(fused)
    mb = nh.MeshBuilder()
    mb.add(fused)
    # scale plates: rows along the body, from behind the head to the tail tip; each covers the top and
    # sides (and the whole tail, which is scaled underneath too)
    y = -0.72
    row = 0
    while y < 0.98:
        za, ra = axis_at(y)
        n_round = max(6, int(ra * 60))
        sweep = math.radians(125 if y < 0.30 else 175)
        for k in range(n_round + 1):
            a = -sweep + 2 * sweep * (k + 0.5 * (row % 2)) / n_round
            if abs(a) > sweep:
                continue
            d = Vector((math.sin(a), 0, math.cos(a)))
            o = Vector((0, y, za))
            loc, nrm, _i, _dist = tree.ray_cast(o + d * 0.5, -d)
            if loc is None:
                continue
            w = ra * 2 * sweep / n_round * 0.62 + 0.012
            ln = w * 1.25
            fwd = Vector((0, 1, 0))
            fwd = (fwd - nrm * fwd.dot(nrm)).normalized()
            side = nrm.cross(fwd).normalized()
            tilt = 0.25
            up = (nrm * math.cos(tilt) - fwd * math.sin(tilt)).normalized()
            fwd2 = side.cross(up).normalized() * -1
            rot = Matrix((side, fwd2 if fwd2.dot(fwd) > 0 else -fwd2, up)).transposed()
            c = loc + up * (ln * 0.10) + fwd * ln * 0.25

            def pointed(v):
                return 1.0 - 0.25 * max(0.0, v.y) ** 2

            plate = nh.ellipsoid((0, 0, 0), (w, ln, max(0.008, w * 0.18)), subdivisions=2, deform=pointed,
                                 rotation=rot)
            nh.transform(plate, Matrix.Translation(c))
            shade = 0.5 + 0.5 * noise.noise(c * 13.0)

            def col(co, n, c=c, rot=rot, ln=ln, shade=shade):
                lv = rot.transposed() @ (co - c)
                return nh.lerp(nh.lerp(SCALE, (0.34, 0.28, 0.17), shade * 0.6), SCALE_EDGE, nh.smoothstep(0.35, 0.95, lv.y / ln))

            mb.add(plate, col)
        y += ra * 0.42 + 0.025
        row += 1
    # head: eyes, nostril
    for sx in (-1, 1):
        nh.eye(mb, (sx * 0.05, -0.745, 0.285), (sx, -0.2, 0.35), 0.011, SKIN)
    for p, front in claws:
        if front:
            # big curved claws folded back under the wrist
            mb.add(nh.tube([tuple(p), tuple(p + Vector((0, -0.04, -0.02))), tuple(p + Vector((0, -0.03, -0.035))),
                            tuple(p + Vector((0, 0.0, -0.035)))], [0.014, 0.012, 0.008, 0.0], sides=6), CLAW)
        else:
            mb.add(nh.tube([tuple(p), tuple(p + Vector((0, -0.03, -0.008)))], [0.009, 0.0], sides=5), CLAW)
    obj = mb.to_object("SmutsiaGigantea")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "SmutsiaGigantea", ground=(0.40, 0.42, 0.28), views=((35, 25), (-90, 5), (0, 10)))
