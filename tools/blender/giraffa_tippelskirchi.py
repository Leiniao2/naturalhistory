"""
Procedural Maasai giraffe (Giraffa tippelskirchi) bull for map colonies.

Pacing on long slender legs (both legs on one side swing together), with knobbly
knees, hocks and dark cloven hooves; a short, steeply sloping body with high
withers and a low croup; the very long neck carrying a short dark mane; a long
head with a tapering muzzle, a median forehead bump, two hair-tufted ossicones,
large sideways ears and dark eyes; and a thin tail ending in a black tassel.

The body is fused from overlapping parts into one seamless surface with a little
hair texture. The coat is painted per face (so the edges stay crisp and ragged)
from a domain-warped voronoi pattern: jagged, star- and vine-leaf-shaped dark
chocolate patches separated by irregular cream lines, the patches getting
smaller on the head and lower legs and fading out to cream just above the
hooves and on the belly. Ossicones, ears, eyes, hooves and the tail tassel are
crisp details.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/giraffa_tippelskirchi.py -- [--render out.png]
  (also renders out_head.png, a close-up of the head)

Output: Assets/Resources/Models/Species/MaasaiGiraffe.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

CREAM = (0.90, 0.80, 0.60)
CREAM_PALE = (0.95, 0.91, 0.80)    # belly, inner legs, lower legs
PATCH = (0.34, 0.18, 0.08)         # dark chocolate
PATCH_DARK = (0.20, 0.10, 0.05)
PATCH_WARM = (0.52, 0.30, 0.13)    # some patches are more chestnut
MANE = (0.30, 0.17, 0.08)
HOOF = (0.10, 0.08, 0.07)
TUFT = (0.06, 0.05, 0.04)
EYE = (0.03, 0.02, 0.02)
NOSE = (0.22, 0.15, 0.12)

VOXEL = 0.0075
BODY_TRIS = 22500


# ---------------------------------------------------------------- helpers

def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def catmull(points, steps):
    """Smooth Catmull-Rom resample of a polyline (any vector size)."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


def smooth_tube(points, radii, steps=4, sides=14, **kw):
    pts = catmull([(*p, r) for p, r in zip(points, radii)], steps)
    return nh.tube([p.xyz for p in pts], [max(0.0, p.w) for p in pts], sides=sides, **kw)


def decimate(bm, max_tris):
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    n = sum(len(p.vertices) - 2 for p in mesh.polygons)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = min(1.0, max_tris / max(n, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    return out


class Parts(nh.MeshBuilder):
    def add(self, src, color=CREAM, smooth=True):
        super().add(src, color, smooth)


# ---------------------------------------------------------------- anatomy

LEGS = {  # name: (x, y, stride) — pacing: both left legs forward, both right legs back
    "lf": (-0.085, -0.25, -0.09), "lh": (-0.085, 0.27, -0.07),
    "rf": (0.085, -0.25, 0.07), "rh": (0.085, 0.27, 0.08),
}
HEAD = Vector((0, -0.66, 2.06))   # back of the skull
NECK = [(0, -0.22, 1.28), (0, -0.32, 1.48), (0, -0.43, 1.70), (0, -0.54, 1.90), (0, -0.62, 2.03)]
NECK_R = [0.14, 0.105, 0.08, 0.065, 0.058]


def torso(b):
    b.add(oriented((0, 0.02, 1.20), (0.16, 0.36, 0.18), pitch=-14, segments=24, rings=16))  # barrel, sloping
    b.add(oriented((0, -0.18, 1.20), (0.17, 0.20, 0.21)))                 # deep chest
    b.add(oriented((0, -0.20, 1.40), (0.07, 0.14, 0.08), pitch=-25))      # high withers
    b.add(oriented((0, 0.28, 1.10), (0.135, 0.14, 0.13)))                 # low croup
    for s in (-1, 1):
        b.add(oriented((s * 0.085, -0.24, 1.18), (0.07, 0.11, 0.17), pitch=-15))  # shoulder
        b.add(oriented((s * 0.085, 0.27, 1.02), (0.07, 0.12, 0.15), pitch=10))    # haunch
    b.add(smooth_tube(NECK, NECK_R, steps=4, sides=18))
    # short upright mane along the back of the neck
    mane = [(0, -0.18, 1.42), (0, -0.28, 1.58), (0, -0.39, 1.78), (0, -0.50, 1.96), (0, -0.58, 2.08)]
    b.add(smooth_tube(mane, [0.022, 0.024, 0.022, 0.02, 0.015], steps=4, sides=10, scale_xy=(0.5, 1.0)), MANE)


def leg(b, name):
    x, y, stride = LEGS[name]
    front = y < 0
    if front:
        pts = [(x, y, 1.15), (x, y + 0.01, 0.92), (x, y + stride * 0.4, 0.60), (x, y + stride * 0.6, 0.48),
               (x, y + stride * 0.9, 0.14), (x, y + stride, 0.05)]
        radii = [0.06, 0.045, 0.028, 0.03, 0.02, 0.019]
        knee = Vector((x, y + stride * 0.5, 0.54))
    else:
        pts = [(x, y, 1.05), (x, y - 0.04, 0.82), (x, y + 0.08 + stride * 0.4, 0.60),
               (x, y + 0.05 + stride * 0.7, 0.38), (x, y + stride * 0.9, 0.14), (x, y + stride, 0.05)]
        radii = [0.075, 0.055, 0.03, 0.026, 0.02, 0.019]
        knee = Vector((x, y + 0.085 + stride * 0.4, 0.60))   # hock
    b.add(smooth_tube(pts, radii, steps=4, sides=14))
    b.add(oriented(knee, (0.032, 0.034, 0.04)))                           # knobbly knee / hock
    b.add(oriented((x, y + stride * 0.95, 0.09), (0.024, 0.026, 0.03)))  # fetlock


def head(b):
    h = HEAD
    b.add(oriented(h + Vector((0, -0.03, 0.0)), (0.055, 0.07, 0.06), pitch=-30))           # skull
    b.add(smooth_tube([h + Vector((0, -0.04, -0.01)), h + Vector((0, -0.12, -0.06)),
                       h + Vector((0, -0.19, -0.10)), h + Vector((0, -0.215, -0.115))],
                      [0.05, 0.04, 0.032, 0.022], steps=3, sides=16))                       # long muzzle
    b.add(oriented(h + Vector((0, -0.20, -0.125)), (0.03, 0.03, 0.022)))                   # soft lips
    b.add(oriented(h + Vector((0, -0.09, 0.025)), (0.02, 0.03, 0.022), pitch=-30))         # median bump
    b.add(oriented(h + Vector((0, -0.05, -0.06)), (0.035, 0.06, 0.035), pitch=-30))        # jaw


def tail(b):
    pts = [(0, 0.40, 1.15), (0, 0.44, 1.02), (0, 0.45, 0.85), (0, 0.45, 0.72)]
    b.add(smooth_tube(pts, [0.018, 0.012, 0.009, 0.008], steps=3, sides=8))


# ---------------------------------------------------------------- coat

def patch_field(p):
    """(lineness 0..1, cell point) of the jagged patch pattern at p."""
    # patches are smaller on the head, neck top and lower legs
    scale = 10.5
    if p.z < 0.9:
        scale *= 1.0 + 0.9 * nh.smoothstep(0.9, 0.3, p.z)
    if p.z > 1.95:
        scale *= 1.5
    q = p * scale
    # domain warp: coarse lobes plus fine jagged teeth along the borders
    q = q + noise.noise_vector(q * 0.55) * 0.45 + noise.noise_vector(q * 2.6 + Vector((5, 1, 3))) * 0.16
    d, pts = noise.voronoi(q)
    gap = d[1] - d[0]
    width = 0.09 + 0.03 * noise.noise(q * 0.7 + Vector((2, 2, 2)))
    return 1.0 - nh.smoothstep(width * 0.85, width * 1.15, gap), pts[0]


def coat_color(p, n):
    line, cell = patch_field(p)
    # per-patch shade and a darker core
    v = noise.noise(cell * 0.37 + Vector((0.3, 0.7, 0.1)))
    c = nh.lerp(PATCH, PATCH_WARM, nh.smoothstep(0.1, 0.6, v))
    c = nh.lerp(c, PATCH_DARK, 0.35 * nh.smoothstep(0.0, -0.5, v))
    ground = CREAM
    # belly, inner legs and the lower legs fade to pale cream
    pale = max(nh.smoothstep(-0.4, -0.85, n.z) * nh.smoothstep(1.35, 1.0, p.z),
               nh.smoothstep(0.30, 0.15, p.z))
    if p.z < 0.95:
        inner = 0.0
        for x, y, stride in LEGS.values():
            if abs(p.y - y - stride * 0.5) < 0.12 and abs(p.x - x) < 0.07:
                inner = max(inner, nh.smoothstep(0.2, 0.7, -n.x * math.copysign(1, x)))
        pale = max(pale, 0.7 * inner)
    # muzzle is pale and plain
    if p.z > 1.9 and p.y < HEAD.y - 0.13:
        pale = max(pale, 0.7 * nh.smoothstep(HEAD.y - 0.13, HEAD.y - 0.17, p.y))
    ground = nh.lerp(ground, CREAM_PALE, pale * 0.8)
    patch = 1.0 - line
    c = nh.lerp(ground, c, patch * (1.0 - pale))
    return c


def paint_faces(bm):
    """Colour each face flat by its centre, so the patch borders stay crisp and ragged."""
    bm.normal_update()
    col = bm.loops.layers.color["Col"]
    for f in bm.faces:
        c = coat_color(f.calc_center_median(), f.normal)
        for l in f.loops:
            l[col] = (c[0], c[1], c[2], 1.0)
        f.smooth = True


def fur_displace(bm, amount=0.0018, freq=60.0):
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * noise.noise(v.co * freq) * amount


# ---------------------------------------------------------------- details

def ossicone(mb, s):
    base = HEAD + Vector((s * 0.03, 0.0, 0.04))
    top = base + Vector((s * 0.012, 0.008, 0.075))
    mb.add(smooth_tube([base, base.lerp(top, 0.5), top], [0.019, 0.016, 0.017], steps=2, sides=10), CREAM)
    mb.add(oriented(top + Vector((0, 0, 0.004)), (0.018, 0.018, 0.013), segments=10, rings=6), TUFT)  # hair tuft


def ear(mb, s):
    bm = nh.uv_ellipsoid((0, 0, 0), (0.05, 0.013, 0.018), segments=12, rings=8)
    for v in bm.verts:   # leaf shape: pointed at the tip
        t = (v.co.x + 0.05) / 0.1
        v.co.z *= 0.5 + 0.8 * math.sin(math.pi * min(1.0, t * 0.9 + 0.1))
        v.co.x += 0.05
    nh.transform(bm, Matrix.Rotation(math.radians(-15), 4, "Y") @ Matrix.Rotation(math.radians(20), 4, "Z"))
    if s < 0:
        nh.transform(bm, Matrix.Scale(-1, 4, Vector((1, 0, 0))))
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    nh.transform(bm, Matrix.Translation(HEAD + Vector((s * 0.05, 0.015, 0.02))))

    def color(co, n):
        return nh.lerp(CREAM, CREAM_PALE, nh.smoothstep(0.0, -0.7, n.y))
    mb.add(bm, color)


def details(mb):
    for s in (-1, 1):
        ossicone(mb, s)
        ear(mb, s)
        e = HEAD + Vector((s * 0.045, -0.075, -0.005))
        mb.add(oriented(e, (0.012, 0.016, 0.011), yaw=s * 20, segments=10, rings=6), EYE)
        mb.add(oriented(HEAD + Vector((s * 0.014, -0.222, -0.098)), (0.004, 0.008, 0.003), pitch=-30,
                        segments=8, rings=4), NOSE)
    for name, (x, y, stride) in LEGS.items():
        hy = y + stride
        for half in (-1, 1):  # cloven hooves
            hx = x + half * 0.0105
            mb.add(nh.tube([(hx, hy + 0.012, 0.05), (hx, hy + 0.002, 0.026), (hx, hy - 0.012, 0.006),
                            (hx + half * 0.002, hy - 0.026, 0.0)],
                           [0.0115, 0.0125, 0.012, 0.004], sides=8, scale_xy=(1.0, 0.8)), HOOF)
    # black tassel at the end of the tail
    base = Vector((0, 0.45, 0.74))
    for k in range(8):
        a = k / 8 * math.tau
        mb.add(nh.tube([base, base + Vector((math.cos(a) * 0.018, math.sin(a) * 0.012, -0.10 - 0.02 * (k % 2)))],
                       [0.008, 0.0], sides=4), TUFT)


def build():
    b = Parts()
    torso(b)
    for name in LEGS:
        leg(b, name)
    head(b)
    tail(b)
    fused = b.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    fur_displace(fused)
    fused = decimate(fused, BODY_TRIS)
    # keep the dark mane (tagged before fusing), repaint the rest of the coat
    col = fused.loops.layers.color["Col"]
    mane = {f for f in fused.faces if sum(l[col][0] for l in f.loops) / len(f.loops) < 0.5}
    paint_faces(fused)
    for f in mane:
        for l in f.loops:
            l[col] = (*MANE, 1.0)

    mb = nh.MeshBuilder()
    mb.add(fused)
    details(mb)
    obj = mb.to_object("MaasaiGiraffe", roughness=0.8)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    target = HEAD + Vector((0, -0.08, -0.03))
    cam.location = target + Vector((0.45, -0.5, 0.15))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    out = Path(path)
    scene.render.filepath = str(out.with_name(f"{out.stem}_head.png"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, "MaasaiGiraffe", ground=(0.55, 0.50, 0.30), views=((35, 22), (-90, 6), (20, 60), (0, 8)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
