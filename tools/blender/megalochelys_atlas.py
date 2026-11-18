"""
Procedural Megalochelys atlas (Late Miocene to Pleistocene of India, Pakistan and
south-east Asia) for map colonies: the largest land tortoise known, with a shell
about 2-2.7 m long and a weight of perhaps a tonne or more.

A tall, domed tortoise carapace made of horny scutes (five vertebrals down the
middle, four costals each side and a ring of marginals over a slightly flared,
notched rim), each scute with concentric growth rings round a paler centre; a
flat plastron; massive elephantine pillar legs covered in heavy, overlapping
scales, the forelimbs held in front; a short thick tail; and a smallish head on a
thick, wrinkled neck that could be pulled back under the front of the shell.
Dark grey-brown shell, grey skin. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/megalochelys_atlas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MegalochelysAtlas.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.27, 0.24, 0.19)
SHELL_PALE = (0.44, 0.39, 0.29)
SEAM = (0.10, 0.09, 0.07)
SKIN = (0.40, 0.38, 0.34)
SKIN_DARK = (0.26, 0.25, 0.22)
PLASTRON = (0.55, 0.49, 0.36)
EYE = (0.06, 0.05, 0.03)
NAIL = (0.18, 0.16, 0.13)

SC = Vector((0, 0, 0.40))          # carapace centre (at the rim height)
RX, RY, RZ = 0.46, 0.62, 0.50

# scute centres as directions from SC (x, y, z on the unit dome)
def _dir(x, y, z):
    return Vector((x, y, z)).normalized()


CENTRES = [_dir(0, y, 1.0) for y in (-0.95, -0.45, 0.0, 0.45, 0.95)]                # vertebrals
CENTRES += [_dir(sx * 0.85, y, 0.75) for sx in (-1, 1) for y in (-0.75, -0.25, 0.25, 0.75)]   # costals
for k in range(24):
    a = k / 24 * math.tau
    CENTRES.append(_dir(math.cos(a), math.sin(a) * 1.0, 0.12))                         # marginals


def shell_dir(co):
    q = co - SC
    return Vector((q.x / RX, q.y / RY, max(q.z, 0.0) / RZ)).normalized()


def scute(co):
    d = shell_dir(co)
    ds = sorted((1 - d.dot(c), i) for i, c in enumerate(CENTRES))
    (d0, _i0), (d1, _i1) = ds[0], ds[1]
    edge = d1 - d0            # ~0 on a seam
    return d0, edge


def build():
    b = nh.MeshBuilder()

    def dome(v):
        k = 1.0
        if v.z < 0:
            k = 1.0 + 0.04 * (-v.z)
        return k

    shell = nh.ellipsoid(tuple(SC), (RX, RY, RZ), subdivisions=5, deform=dome)
    # keep only the upper dome (+ a little skirt): flatten the bottom into the plastron
    for v in shell.verts:
        if v.co.z < SC.z - 0.06:
            v.co.z = SC.z - 0.06 - (SC.z - 0.06 - v.co.z) * 0.25
    b.add(shell, SHELL)
    b.add(nh.ellipsoid((0, 0, SC.z - 0.08), (RX * 0.88, RY * 0.9, 0.09)), PLASTRON)
    # neck and head, stretched forward and slightly down
    n0 = Vector((0, -RY * 0.85, SC.z - 0.02))
    n1 = Vector((0, -RY - 0.18, SC.z + 0.02))
    b.add(nh.tube([tuple(n0), tuple(n0.lerp(n1, 0.5) + Vector((0, 0, 0.02))), tuple(n1)], [0.12, 0.10, 0.075], sides=14),
          SKIN)
    hc = n1 + Vector((0, -0.07, -0.01))
    b.add(nh.ellipsoid(tuple(hc), (0.075, 0.10, 0.07)), SKIN)
    b.add(nh.ellipsoid(tuple(hc + Vector((0, -0.07, -0.015))), (0.055, 0.06, 0.05)), SKIN)
    # legs: thick pillars, front legs in front, hind under the rear
    feet = []
    for (x, y, st) in ((-0.30, -0.36, -0.06), (0.30, -0.36, 0.05), (-0.30, 0.38, 0.04), (0.30, 0.38, -0.05)):
        top = Vector((x * 0.85, y, SC.z - 0.02))
        foot = Vector((x * 1.08, y + st, 0.0))
        b.add(nh.tube([tuple(top), tuple(top.lerp(foot, 0.5) + Vector((x * 0.08, 0, 0))), tuple(foot + Vector((0, 0, 0.06)))],
                      [0.11, 0.10, 0.095], sides=14), SKIN)
        b.add(nh.ellipsoid(tuple(foot + Vector((0, 0, 0.04))), (0.10, 0.11, 0.045)), SKIN)
        feet.append(foot)
    b.add(nh.tube([(0, RY * 0.85, SC.z - 0.05), (0, RY + 0.08, SC.z - 0.12), (0, RY + 0.13, SC.z - 0.20)],
                  [0.06, 0.04, 0.0], sides=10), SKIN)
    fused = b.fuse(voxel=0.014, smooth=3, smooth_factor=0.5, max_tris=14000)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    info = {}
    for v in fused.verts:
        q = v.co - SC
        on = (q.x / RX) ** 2 + (q.y / RY) ** 2 + (max(q.z, 0) / RZ) ** 2 > 0.82 and v.co.z > SC.z - 0.075
        if on:
            d0, edge = scute(v.co)
            v.co -= v.normal * 0.012 * (1 - nh.smoothstep(0.0, 0.02, edge))       # sunken seams
            info[v] = (d0, edge)
        elif v.co.z < SC.z - 0.06:
            # heavy scales on the legs, neck and head
            dist, _p = noise.voronoi(v.co * 30.0, distance_metric="DISTANCE")
            v.co += v.normal * 0.006 * nh.smoothstep(0.0, 0.3, dist[1] - dist[0])
            info[v] = (None, dist[1] - dist[0])
    fused.normal_update()
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            c = (c[0], c[1], c[2])
            v = l.vert
            if v in info:
                d0, e = info[v]
                if d0 is not None:
                    ring = 0.5 + 0.5 * math.cos(d0 * 140.0)
                    base = nh.lerp(SHELL_PALE, SHELL, nh.smoothstep(0.0, 0.025, d0))
                    base = nh.lerp(base, SEAM, 0.25 * nh.smoothstep(0.6, 0.95, ring) * nh.smoothstep(0.004, 0.02, d0))
                    c = nh.lerp(base, SEAM, 1 - nh.smoothstep(0.0, 0.015, e))
                else:
                    c = nh.lerp(SKIN_DARK, SKIN, nh.smoothstep(0.02, 0.25, e))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        nh.eye(mb, tuple(hc + Vector((sx * 0.06, -0.035, 0.022))), (sx, -0.3, 0.2), 0.014, SKIN)
    for foot in feet:
        for a in (-0.6, -0.2, 0.2, 0.6):
            p = foot + Vector((math.sin(a) * 0.085, -math.cos(a) * 0.09, 0.02))
            mb.add(nh.tube([tuple(p + Vector((0, 0.02, 0.005))), tuple(p + Vector((0, -0.025, -0.01)))], [0.016, 0.004],
                           sides=6), NAIL)
    obj = mb.to_object("MegalochelysAtlas")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "MegalochelysAtlas", ground=(0.45, 0.42, 0.30), views=((35, 25), (-90, 5), (0, 10)))
