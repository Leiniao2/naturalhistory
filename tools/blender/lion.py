"""
Procedural male lion (Panthera leo) for map colonies, high-detail version.

The body is sculpted from overlapping anatomy (ribcage, loose belly skin, shoulder
blades, haunches, leg muscles, big toed paws, a head with brow ridge, cheekbones,
broad nose bridge, whisker pads and chin) fused into one seamless surface. The
mane is part of that surface, displaced into clumped locks that flow back and
down from the face, longer and darker toward the shoulders and chest; the tail
tuft gets the same treatment. Colour is painted procedurally afterwards, then
crisp eyes, nose leather and whiskers are added on top.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lion.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lion.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

COAT = (0.78, 0.58, 0.31)       # tawny gold
COAT_DARK = (0.62, 0.43, 0.21)  # back line, ear backs
PALE = (0.93, 0.83, 0.64)       # belly, inner legs, muzzle, chin
MANE_LIGHT = (0.72, 0.50, 0.21) # golden ruff around the face
MANE_DARK = (0.26, 0.13, 0.05)  # long dark locks behind and on the chest
TUFT = (0.18, 0.09, 0.04)
NOSE = (0.36, 0.17, 0.13)
EYE = (0.62, 0.42, 0.12)
PUPIL = (0.03, 0.02, 0.01)
LIP = (0.15, 0.08, 0.05)
WHISKER = (0.95, 0.93, 0.88)

# Region tags painted on the parts before fusing; fuse() carries them to the new surface
TAG_COAT = (1.0, 0.0, 0.0)
TAG_MANE = (0.0, 1.0, 0.0)
TAG_TUFT = (0.0, 0.0, 1.0)

VOXEL = 0.011
MAX_TRIS = 21000

FACE = Vector((0, -1.06, 0.95))  # where the mane's locks start flowing from


# ---------------------------------------------------------------- anatomy

def front_leg(b, x, stride):
    """Shoulder blade, triceps, forearm and a big paw; stride moves the paw along y."""
    s = math.copysign(1, x)
    # shoulder blade, raised a little above the back line
    b.add(nh.tube([(x * 0.85, -0.34, 0.93), (x * 1.05, -0.47, 0.62)], [0.075, 0.08], sides=12,
                  scale_xy=(0.55, 1.0)), TAG_COAT)
    b.add(nh.ellipsoid((x * 1.08, -0.47, 0.55), (0.09, 0.11, 0.14)), TAG_COAT)        # triceps
    b.add(nh.tube([(x * 1.08, -0.50, 0.62), (x, -0.42, 0.38)], [0.10, 0.08], sides=12), TAG_COAT)  # upper arm
    wrist = Vector((x, -0.46 + stride, 0.13))
    b.add(nh.tube([(x, -0.42, 0.40), (x, -0.44 + stride * 0.5, 0.26), tuple(wrist)], [0.08, 0.065, 0.05],
                  sides=12), TAG_COAT)                                                  # forearm
    b.add(nh.ellipsoid((x * 1.02, -0.43 + stride * 0.3, 0.32), (0.065, 0.07, 0.09)), TAG_COAT)  # forearm muscle
    paw(b, wrist + Vector((0, -0.03, 0)), big=True)


def hind_leg(b, x, stride):
    """Powerful haunch, gaskin, hock and paw."""
    b.add(nh.ellipsoid((x * 0.9, 0.42, 0.63), (0.115, 0.19, 0.22)), TAG_COAT)          # haunch
    b.add(nh.ellipsoid((x * 1.02, 0.36, 0.44), (0.10, 0.13, 0.15)), TAG_COAT)          # thigh muscle
    knee = Vector((x * 1.02, 0.30, 0.38))
    hock = Vector((x * 1.02, 0.55 + stride * 0.5, 0.21))
    ankle = Vector((x, 0.48 + stride, 0.10))
    b.add(nh.tube([tuple(knee), tuple(hock)], [0.085, 0.05], sides=12), TAG_COAT)      # gaskin
    b.add(nh.ellipsoid((x * 1.02, 0.43 + stride * 0.2, 0.31), (0.06, 0.09, 0.09)), TAG_COAT)  # calf
    b.add(nh.tube([tuple(hock), tuple(ankle)], [0.045, 0.043], sides=10), TAG_COAT)   # metatarsus
    paw(b, ankle + Vector((0, -0.05, 0)), big=False)


def paw(b, center, big):
    r = 0.085 if big else 0.075
    b.add(nh.ellipsoid((center.x, center.y, 0.055), (r, r * 1.15, 0.058)), TAG_COAT)
    # four toes in an arc across the front, slightly apart so the voxel surface keeps the gaps
    for i, a in enumerate((-0.75, -0.25, 0.25, 0.75)):
        tx = center.x + math.sin(a) * r * 1.05
        ty = center.y - math.cos(a) * r * 1.0 - 0.035
        b.add(nh.ellipsoid((tx, ty, 0.036), (0.03, 0.036, 0.036)), TAG_COAT)


def torso(b):
    b.add(nh.ellipsoid((0, -0.25, 0.68), (0.22, 0.36, 0.27), subdivisions=4), TAG_COAT)  # ribcage
    b.add(nh.ellipsoid((0, 0.12, 0.66), (0.18, 0.32, 0.20), subdivisions=4), TAG_COAT)   # loin, tucked
    b.add(nh.ellipsoid((0, 0.06, 0.50), (0.14, 0.27, 0.09)), TAG_COAT)                   # loose belly skin
    b.add(nh.ellipsoid((0, 0.42, 0.70), (0.19, 0.22, 0.20), subdivisions=4), TAG_COAT)   # croup
    b.add(nh.tube([(0, -0.40, 0.80), (0, -0.62, 0.92), (0, -0.82, 0.97)], [0.19, 0.17, 0.14], sides=14),
          TAG_COAT)                                                                     # neck


def head(b):
    b.add(nh.ellipsoid((0, -0.90, 0.99), (0.155, 0.165, 0.15), subdivisions=4), TAG_COAT)  # cranium
    b.add(nh.tube([(-0.10, -1.01, 1.035), (0, -1.045, 1.055), (0.10, -1.01, 1.035)], [0.032, 0.038, 0.032],
                  sides=10), TAG_COAT)                                                  # brow ridge
    for s in (-1, 1):
        b.add(nh.ellipsoid((s * 0.105, -0.98, 0.935), (0.07, 0.09, 0.065)), TAG_COAT)  # cheekbones
        b.add(nh.ellipsoid((s * 0.048, -1.115, 0.885), (0.058, 0.055, 0.052)), TAG_COAT)  # whisker pads
        b.add(nh.ellipsoid((s * 0.12, -0.86, 1.12), (0.055, 0.03, 0.055)), TAG_COAT)   # ears
    b.add(nh.tube([(0, -0.99, 1.045), (0, -1.08, 1.0), (0, -1.135, 0.955)], [0.06, 0.058, 0.05], sides=12,
                  scale_xy=(1.25, 0.8)), TAG_COAT)                                      # broad nose bridge
    b.add(nh.tube([(0, -0.92, 0.87), (0, -1.07, 0.84)], [0.075, 0.05], sides=12), TAG_COAT)  # lower jaw
    b.add(nh.ellipsoid((0, -1.085, 0.82), (0.05, 0.045, 0.035)), TAG_COAT)             # chin


def mane_volume(b):
    def shaggy(seed):
        return lambda n: 1.0 + 0.07 * noise.noise(n * 3.0 + Vector((seed, 0, 0))) + 0.03 * noise.noise(n * 7.0)
    b.add(nh.ellipsoid((0, -0.62, 0.92), (0.30, 0.27, 0.35), subdivisions=4, deform=shaggy(1)), TAG_MANE)  # ruff
    b.add(nh.ellipsoid((0, -0.45, 0.93), (0.23, 0.22, 0.17), deform=shaggy(2)), TAG_MANE)   # over the shoulders
    b.add(nh.ellipsoid((0, -0.62, 0.62), (0.17, 0.18, 0.25), deform=shaggy(3)), TAG_MANE)   # chest bib
    b.add(nh.ellipsoid((0, -0.58, 0.45), (0.11, 0.12, 0.12), deform=shaggy(4)), TAG_MANE)   # belly fringe start


def tail(b):
    pts = [(0, 0.56, 0.78), (0, 0.74, 0.74), (0.03, 0.92, 0.57), (0.09, 1.03, 0.38), (0.15, 1.08, 0.26)]
    b.add(nh.tube(pts, [0.055, 0.04, 0.033, 0.029, 0.026], sides=10), TAG_COAT)
    b.add(nh.ellipsoid((0.17, 1.10, 0.20), (0.05, 0.05, 0.075)), TAG_TUFT)


# ---------------------------------------------------------------- surface treatment

def vertex_tags(bm):
    """Per-vertex (coat, mane, tuft) weights from the fused colour layer."""
    col = bm.loops.layers.color["Col"]
    tags = {}
    for v in bm.verts:
        acc = Vector((0, 0, 0))
        for l in v.link_loops:
            c = l[col]
            acc += Vector((c[0], c[1], c[2]))
        s = max(acc.x + acc.y + acc.z, 1e-6)
        tags[v] = acc / s
    return tags


def lock_flow(p):
    """Direction the mane hair runs at p: away from the face, back and down."""
    away = p - FACE
    away.x *= 1.4
    return (away.normalized() * 0.7 + Vector((0, 0.55, -0.6))).normalized()


def lock_pattern(p, n):
    """0..1 clumped strand pattern: thin across the flow, long along it."""
    f = lock_flow(p)
    f = (f - n * f.dot(n)).normalized()  # keep it in the surface
    across = f.cross(n)
    u = p.dot(across) * 13.0
    w = p.dot(f) * 2.2
    clump = 0.5 + 0.5 * math.sin(u * 3.6 + 3.0 * noise.noise(Vector((u * 0.4, w, 1.7))))  # rows of locks
    fine = 0.5 + 0.5 * noise.noise(Vector((u * 2.4, w * 1.5, 9.3)))                       # strands within them
    return clump ** 1.3 * 0.8 + fine * 0.2, f


def mane_length(p):
    """How long the mane is at p: short ruff at the face, long behind the head and on the chest."""
    back = nh.smoothstep(-0.95, -0.55, p.y)
    chest = nh.smoothstep(0.85, 0.45, p.z) * nh.smoothstep(-0.35, -0.6, p.y)
    return 0.016 + 0.05 * max(back, chest)


def displace(bm, tags):
    bm.normal_update()
    moves = {}
    for v in bm.verts:
        t = tags[v]
        p, n = v.co.copy(), v.normal.copy()
        d = Vector((0, 0, 0))
        if t.y > 0.05:
            pat, f = lock_pattern(p, n)
            amt = mane_length(p) * t.y
            # locks puff outward and droop a little along their flow
            d += n * amt * (0.2 + 0.8 * pat) + f * amt * 0.5 * pat
            d += n * amt * 0.45 * noise.noise(p * 2.5)  # big shaggy clumps
        if t.z > 0.05:
            spike = 1.0 - abs(noise.noise(n * 9.0 + Vector((3, 1, 2))))
            d += n * 0.03 * t.z * spike ** 2
        if t.x > 0.5:
            d += n * 0.003 * noise.noise(p * 30.0)  # faint fur texture on the coat
        moves[v] = d
    for v, d in moves.items():
        v.co += d
    # relax the displaced hair so locks stay rounded instead of breaking into shards
    hair = [v for v in bm.verts if tags[v].y > 0.05 or tags[v].z > 0.05]
    for _ in range(3):
        bmesh.ops.smooth_vert(bm, verts=hair, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.normal_update()


def decimate(bm, max_tris):
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
    dec = obj.modifiers.new("dec", "DECIMATE")
    dec.ratio = min(1.0, max_tris / max(tris, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    return out


def paint(bm):
    """Final colours from the region tags (re-read after decimation) and position."""
    tags = vertex_tags(bm)
    bm.normal_update()
    col = bm.loops.layers.color["Col"]
    vcol = {}
    for v in bm.verts:
        t, p, n = tags[v], v.co, v.normal
        # coat: tawny, darker along the spine, pale underneath and on the inner legs
        c = nh.lerp(COAT, COAT_DARK, nh.smoothstep(0.6, 0.95, n.z) * nh.smoothstep(0.7, 0.85, p.z))
        under = nh.smoothstep(-0.2, -0.7, n.z)
        inner = nh.smoothstep(0.08, 0.02, abs(p.x)) * nh.smoothstep(0.55, 0.35, p.z) if p.z < 0.55 else 0.0
        c = nh.lerp(c, PALE, min(1.0, under * 0.9 + inner * 0.6))
        # muzzle, whisker pads and chin are pale; dark lip line under the whisker pads
        if p.y < -1.04:
            c = nh.lerp(c, PALE, nh.smoothstep(0.98, 0.9, p.z))
            if 0.84 < p.z < 0.865 and p.y < -1.07:
                c = nh.lerp(c, LIP, 0.8)
        # pale fur under the eyes
        if -1.06 < p.y < -1.0 and 0.94 < p.z < 0.975 and 0.04 < abs(p.x) < 0.11:
            c = nh.lerp(c, PALE, 0.6)
        # ear backs dark
        if p.z > 1.07 and abs(p.x) > 0.07 and p.y > -0.9 and n.y > 0.2:
            c = nh.lerp(c, MANE_DARK, 0.7)
        c = nh.lerp(c, COAT_DARK, 0.12 * max(0.0, noise.noise(p * 9.0)))
        # mane: golden at the face to dark behind, lighter on lock crests
        if t.y > 0.02:
            pat, _ = lock_pattern(p, n)
            depth = nh.smoothstep(-0.98, -0.5, p.y) * 0.8 + nh.smoothstep(0.85, 0.45, p.z) * 0.4
            m = nh.lerp(MANE_LIGHT, MANE_DARK, min(1.0, depth))
            m = nh.lerp(m, MANE_DARK, 0.35 * (1.0 - pat))
            m = nh.lerp(m, MANE_LIGHT, 0.25 * pat * pat)
            c = nh.lerp(c, m, nh.smoothstep(0.05, 0.6, t.y))
        if t.z > 0.02:
            c = nh.lerp(c, TUFT, nh.smoothstep(0.05, 0.5, t.z))
        vcol[v] = c
    for f in bm.faces:
        for l in f.loops:
            c = vcol[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)


def details(mb):
    for s in (-1, 1):
        # amber eyes set under the brow, with round pupils
        mb.add(nh.ellipsoid((s * 0.073, -1.042, 0.992), (0.036, 0.014, 0.024), subdivisions=2), LIP)  # dark rim
        mb.add(nh.ellipsoid((s * 0.073, -1.050, 0.992), (0.029, 0.013, 0.02), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((s * 0.073, -1.061, 0.992), (0.012, 0.005, 0.013), subdivisions=1), PUPIL)
        # whiskers fanning out from the pads
        for k in range(3):
            a = math.radians(-12 + k * 12)
            start = Vector((s * 0.07, -1.13, 0.885 + k * 0.012))
            end = start + Vector((s * math.cos(a) * 0.16, 0.03, math.sin(a) * 0.05))
            mb.add(nh.tube([tuple(start), tuple(end)], [0.0025, 0.0], sides=3), WHISKER)
    # nose leather: broad, flattened, on the end of the bridge
    mb.add(nh.ellipsoid((0, -1.156, 0.952), (0.05, 0.016, 0.026), subdivisions=2,
                        deform=lambda n: 1.0 - 0.35 * max(0.0, -n.z)), NOSE)


def build():
    b = nh.MeshBuilder()
    torso(b)
    # walking: left-front and right-hind forward
    front_leg(b, -0.14, -0.12)
    front_leg(b, 0.14, 0.10)
    hind_leg(b, -0.15, 0.08)
    hind_leg(b, 0.15, -0.10)
    head(b)
    mane_volume(b)
    tail(b)
    fused = b.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    tags = vertex_tags(fused)
    displace(fused, tags)
    fused = decimate(fused, MAX_TRIS)
    paint(fused)

    mb = nh.MeshBuilder()
    mb.add(fused)
    details(mb)
    obj = mb.to_object("Lion")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Lion", ground=(0.55, 0.50, 0.30), views=((35, 25), (-90, 8), (20, 65)))
