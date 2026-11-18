"""
Procedural low-poly Giardia duodenalis (G. lamblia) trophozoite, the gut parasite of giardiasis.

A flattened, pear- or teardrop-shaped cell: broad and rounded in front, tapering to a narrow tail,
domed on the back and flat underneath. Seen from above, its two oval nuclei sit side by side at
the front like a pair of eyes (each with a dark karyosome "pupil"), the paired axonemes run down
the midline like a nose and the two dark, curved median bodies below them make the mouth: the
famous Giardia "face". On the underside the large ventral adhesive (sucking) disc is a slightly
raised, concave oval rim; its outline also shows faintly through the back. Four pairs of
flagella (eight in all): anterior (crossing out at the front margins and sweeping back),
posterolateral, ventral, and two caudal ones trailing from the tail. Pale blue-grey. Colour is in
vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/giardia_duodenalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Giardia.fbx
About 1.6 units long including the trailing flagella, ~1.1 across. Faces -Y (broad front first),
back (dorsal) side up. Pivot at the centre of the bounds (Drift).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import nh_model as nh  # noqa: E402

FRONT = 0.40           # body half-length in front of its widest point
REAR = 0.56            # ... and behind it, to the tail tip
WIDTH = 0.34           # half-width at the widest
DORSAL = 0.11          # dome height on the back
VENTRAL = 0.045        # depth of the flat underside
BODY_TRIS = 900
DISC_C = (0.0, -0.10)  # ventral disc centre and radii
DISC_R = (0.25, 0.27)

BODY = (0.72, 0.80, 0.86)
BODY_EDGE = (0.80, 0.86, 0.90)
DISC_TINT = (0.62, 0.70, 0.78)
NUCLEUS = (0.42, 0.50, 0.64)
KARYO = (0.16, 0.20, 0.30)
MEDIAN = (0.26, 0.30, 0.40)
AXONEME = (0.52, 0.60, 0.70)
FLAG = (0.84, 0.89, 0.94)
DISC_RIM = (0.66, 0.74, 0.82)


def taper(s):
    """Width factor along the body, s = -1 (front) .. 1 (tail tip)."""
    return 1.0 if s < 0 else 1.0 - 0.62 * s ** 1.1


def surface(n):
    """Maps a unit-sphere direction to the body surface."""
    s = n.y
    y = s * (FRONT if s < 0 else REAR)
    x = n.x * WIDTH * taper(s)
    thin = 1.0 - 0.5 * max(0.0, s)
    z = n.z * (DORSAL if n.z > 0 else VENTRAL) * thin
    return Vector((x, y, z))


def decimate(bm, tris):
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = min(1.0, tris / sum(len(p.vertices) - 2 for p in mesh.polygons))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    out.normal_update()
    return out


def disc_d(co):
    return math.hypot((co.x - DISC_C[0]) / DISC_R[0], (co.y - DISC_C[1]) / DISC_R[1])


def make_body():
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        p = surface(n)
        if n.z < 0:
            # the sucking disc: a shallow concave dish inside a raised rim on the underside
            d = disc_d(p)
            p.z += 0.025 * (1 - nh.smoothstep(0.0, 0.85, d)) - 0.012 * math.exp(-((d - 1.0) / 0.12) ** 2)
        v.co = p
    bm = decimate(bm, BODY_TRIS)

    def color(co, nrm):
        c = nh.lerp(BODY, BODY_EDGE, nh.smoothstep(0.4, 0.95, 1.0 - abs(nrm.z)))
        c = tuple(k * (1.0 + 0.03 * noise.noise(co * 12.0)) for k in c)
        d = disc_d(co)
        if co.z < 0:
            c = nh.lerp(c, DISC_TINT, (1 - nh.smoothstep(0.9, 1.0, d)) * 0.6)
        else:  # the disc's outline showing faintly through the back
            c = nh.lerp(c, DISC_TINT, math.exp(-((d - 1.0) / 0.06) ** 2) * 0.55)
        return c

    return bm, color


def wavy(points, amp, waves, phase=0.0, axis=Vector((0, 0, 1))):
    """Densifies a polyline and adds a sideways sine wave that grows toward the tip."""
    pts = [Vector(p) for p in points]
    out = []
    n = 12
    for i in range(n + 1):
        u = i / n * (len(pts) - 1)
        k = min(int(u), len(pts) - 2)
        f = u - k
        # Catmull-Rom through the control points
        p0, p1, p2, p3 = pts[max(k - 1, 0)], pts[k], pts[k + 1], pts[min(k + 2, len(pts) - 1)]
        p = 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f
                   + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)
        t = i / n
        tan = (p2 - p1).normalized()
        side = tan.cross(axis).normalized()
        out.append(p + side * amp * math.sin(t * math.tau * waves + phase) * t)
    return out


def flagellum(mb, points, amp=0.03, waves=1.3, phase=0.0, axis=Vector((0, 0, 1))):
    pts = wavy(points, amp, waves, phase, axis)
    radii = [0.010] * (len(pts) - 3) + [0.008, 0.006, 0.0]
    mb.add(nh.tube(pts, radii, sides=5), FLAG)


def build():
    mb = nh.MeshBuilder()
    body, body_col = make_body()
    body.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(body)

    def top(x, y):
        hit = tree.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
        return hit[0].z if hit[0] is not None else 0.0

    mb.add(body, body_col)

    # the face: two oval nuclei (eyes) with karyosomes, axonemes (nose), median bodies (mouth)
    for sx in (-1, 1):
        x, y = sx * 0.115, -0.19
        z = top(x, y)
        nuc = nh.uv_ellipsoid((x, y, z - 0.02), (0.075, 0.10, 0.035), segments=14, rings=8)
        mb.add(nuc, NUCLEUS)
        mb.add(nh.ellipsoid((x + sx * 0.005, y + 0.01, top(x, y) + 0.008), (0.026, 0.03, 0.02),
                            subdivisions=2), KARYO)
        # axoneme running from between the eyes down the midline to the tail
        line = [(sx * 0.018, -0.14), (sx * 0.02, 0.05), (sx * 0.014, 0.25), (sx * 0.006, 0.44)]
        mb.add(nh.tube([(lx, ly, top(lx, ly) - 0.002) for lx, ly in line], [0.008, 0.008, 0.007, 0.004],
                       sides=4), AXONEME)
        # median body: a dark curved bar, the two together a smile below the nose
        bar = [(sx * (0.03 + 0.04 * k), 0.04 - 0.016 * k * k) for k in (0.0, 0.5, 1.0, 1.5, 2.0)]
        mb.add(nh.tube([(bx, by, top(bx, by) - 0.004) for bx, by in bar], [0.016, 0.021, 0.021, 0.017, 0.010],
                       sides=6), MEDIAN)

    # raised rim of the ventral disc, just proud of the underside
    ring = []
    for k in range(25):
        a = k / 24 * math.tau
        x, y = DISC_C[0] + math.cos(a) * DISC_R[0], DISC_C[1] + math.sin(a) * DISC_R[1]
        ring.append(Vector((x, y, -VENTRAL * 0.78)))
    mb.add(nh.tube(ring, [0.016] * len(ring), sides=5, cap_start=False, cap_end=False), DISC_RIM)

    # four pairs of flagella
    for sx in (-1, 1):
        # anterior: cross between the nuclei, leave the front margin and sweep out and back
        flagellum(mb, [(-sx * 0.03, -0.25, 0.02), (sx * 0.20, -0.33, 0.0), (sx * 0.38, -0.30, 0.0),
                       (sx * 0.55, -0.12, -0.01), (sx * 0.62, 0.10, -0.02)], amp=0.035, waves=1.2,
                  phase=sx)
        # posterolateral: leave the sides near the tail and trail back-outward
        flagellum(mb, [(sx * 0.10, 0.22, 0.0), (sx * 0.17, 0.33, 0.0), (sx * 0.30, 0.52, -0.01),
                       (sx * 0.40, 0.75, -0.02)], amp=0.03, waves=1.4, phase=1 + sx)
        # ventral: from the underside behind the disc, trailing below the tail
        flagellum(mb, [(sx * 0.03, 0.20, -0.03), (sx * 0.06, 0.34, -0.05), (sx * 0.14, 0.58, -0.07),
                       (sx * 0.22, 0.90, -0.08)], amp=0.03, waves=1.6, phase=2 * sx)
        # caudal: straight out of the tail tip
        flagellum(mb, [(sx * 0.008, 0.50, 0.0), (sx * 0.02, 0.62, 0.0), (sx * 0.05, 0.82, 0.0),
                       (sx * 0.07, 1.16, 0.0)], amp=0.025, waves=1.0, phase=sx)

    obj = mb.to_object("Giardia", roughness=0.45)
    # centre the bounds (flagella included) on the pivot
    vs = obj.data.vertices
    c = Vector([(max(v.co[i] for v in vs) + min(v.co[i] for v in vs)) / 2 for i in range(3)])
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "Giardia", views=((25, 45), (0, 88), (180, -60)))
