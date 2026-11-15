"""
Procedural Lystrosaurus murrayi (Permian-Triassic dicynodont, ~1 m) for map colonies.

A pig-sized, stocky plant-eater: a deep barrel body slung low between short, stout legs,
the forelimbs sprawling out to the sides with broad, clawed digging hands and the hind
limbs held more upright under the hips; a short thick neck and only a stub of a tail.
The head is short and high-domed with wide cheek arches behind the eyes; the snout is
bent steeply downward and ends in a squared-off horny beak (no front teeth), with the
two tusk-like upper canines - the only teeth - growing down from bony sheaths beside it.
The eyes sit high and well forward, the nostrils high on the snout just in front of them.
Body, legs, head, cheek arches, tusk sheaths and beak are fused into one seamless
surface and sculpted by displacement: wrinkled, hairless skin with folds across the neck
and over the elbows. Painted earthy grey-brown, darker over the back with faint mottling,
paler on the belly and throat; the beak is dark keratin.
Crisp details on top: ivory tusks, eyes, nostrils and blunt digging claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lystrosaurus_murrayi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lystrosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

NAME = "Lystrosaurus"

HIDE = (0.50, 0.43, 0.33)        # grey-brown
HIDE_DARK = (0.30, 0.26, 0.20)
BELLY = (0.72, 0.64, 0.52)
MOTTLE = (0.22, 0.19, 0.15)
BEAK = (0.13, 0.11, 0.09)
TUSK = (0.90, 0.86, 0.72)
CLAW = (0.16, 0.13, 0.10)
EYE = (0.26, 0.17, 0.08)
PUPIL = (0.02, 0.02, 0.02)


# ---------------------------------------------------------------- helpers

def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14, deform=None):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


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


# ---------------------------------------------------------------- anatomy

SNOUT_TIP = Vector((0.0, -0.735, 0.195))     # front-bottom corner of the beak
EYE_C = Vector((0.074, -0.600, 0.430))
TUSK_ROOT = Vector((0.064, -0.655, 0.255))
TUSK_TIP = Vector((0.068, -0.684, 0.170))
CLAWS = []      # (base, direction, radius)

# the head is built at 1:1, then enlarged a little about the back of the skull
HEAD_PIVOT = Vector((0.0, -0.46, 0.34))
HEAD = Matrix.Translation(HEAD_PIVOT) @ Matrix.Scale(1.12, 4) @ Matrix.Translation(-HEAD_PIVOT)
HEAD_INV = HEAD.inverted()


def H(bm):
    return nh.transform(bm, HEAD)


def limb(b, pts, radii, foot_c, foot_r, toes, s, toe_len, toe_r, yaw):
    b.add(nh.tube(pts, radii, sides=14), HIDE)
    for p, r in zip(pts[1:-1], radii[1:-1]):
        b.add(oriented(p, (r * 1.05, r * 1.05, r * 1.05), segments=12, rings=8), HIDE)   # joints
    b.add(oriented(foot_c, foot_r, yaw=yaw), HIDE)
    for k in range(toes):
        a = math.radians(-50 + 100 * k / (toes - 1) + yaw * -s)
        d = Vector((s * math.sin(a), -math.cos(a), 0.0))
        base = Vector(foot_c) + d * foot_r[1] * 0.6
        tip = base + d * toe_len + Vector((0, 0, -0.008))
        b.add(nh.tube([base, tip], [toe_r, toe_r * 0.8], sides=8), HIDE)
        CLAWS.append((tip - d * 0.004, d, toe_r * 0.75))


def body(b):
    # deep barrel trunk, slightly higher over the hips
    def barrel(n):
        return 1.0 + 0.08 * max(0.0, -n.z) + 0.05 * max(0.0, n.y) * max(0.0, n.z)
    b.add(oriented((0, 0.02, 0.265), (0.215, 0.36, 0.185), pitch=-3, segments=32, rings=22, deform=barrel), HIDE)
    b.add(oriented((0, -0.26, 0.262), (0.195, 0.19, 0.170)), HIDE)        # chest and shoulders
    b.add(oriented((0, 0.27, 0.270), (0.175, 0.17, 0.160)), HIDE)         # hips
    b.add(nh.tube([(0, 0.36, 0.28), (0, 0.46, 0.25), (0, 0.53, 0.20), (0, 0.56, 0.18)],
                  [0.085, 0.055, 0.025, 0.0], sides=14), HIDE)            # stub of a tail
    b.add(nh.tube([(0, -0.30, 0.30), (0, -0.42, 0.33), (0, -0.50, 0.35)], [0.15, 0.13, 0.11], sides=18), HIDE)  # neck
    b.add(oriented((0, -0.44, 0.24), (0.11, 0.09, 0.07)), HIDE)           # dewlap / throat


def head(b):
    # high domed cranium with a broad temporal region
    b.add(H(oriented((0, -0.535, 0.385), (0.105, 0.095, 0.085))), HIDE)
    b.add(H(oriented((0, -0.585, 0.415), (0.070, 0.060, 0.050))), HIDE)       # raised forehead between the eyes
    for sx in (1, -1):
        b.add(H(oriented((sx * 0.072, -0.520, 0.338), (0.042, 0.085, 0.042), yaw=sx * 8)), HIDE)   # cheek arches
        b.add(H(oriented((sx * 0.062, -0.600, 0.420), (0.032, 0.036, 0.030))), HIDE)              # orbit rims
        b.add(H(oriented(TUSK_ROOT * Vector((sx, 1, 1)) + Vector((-sx * 0.004, 0.006, 0.035)), (0.026, 0.030, 0.048),
                         pitch=-12)), HIDE)   # bony tusk sheath (caniniform process)
    # short, steeply down-turned snout ending in the squared beak
    b.add(H(nh.tube([(0, -0.59, 0.40), (0, -0.655, 0.37), (0, -0.705, 0.30), (0, -0.728, 0.225)],
                  [0.070, 0.064, 0.056, 0.044], sides=18, scale_xy=(0.95, 1.0))), HIDE)
    b.add(H(oriented((0, -0.715, 0.215), (0.045, 0.030, 0.035))), HIDE)       # upper beak edge
    # lower jaw and its beak (predentary), tucked inside the upper beak
    b.add(H(nh.tube([(0, -0.47, 0.275), (0, -0.57, 0.250), (0, -0.65, 0.228), (0, -0.70, 0.215)],
                  [0.075, 0.060, 0.045, 0.030], sides=14, scale_xy=(1.0, 0.7))), HIDE)


def limbs(b):
    for s in (-1, 1):
        # forelimb: sprawling, humerus out sideways, elbow bent, broad digging hand
        limb(b, [(s * 0.13, -0.27, 0.24), (s * 0.26, -0.29, 0.19), (s * 0.29, -0.32, 0.10),
                 (s * 0.29, -0.35, 0.035)], [0.075, 0.060, 0.050, 0.044],
             (s * 0.295, -0.375, 0.022), (0.052, 0.058, 0.022), 5, s, 0.030, 0.014, s * -8)
        # hind limb: more upright, under the hips
        limb(b, [(s * 0.12, 0.25, 0.25), (s * 0.21, 0.19, 0.15), (s * 0.22, 0.25, 0.08),
                 (s * 0.22, 0.24, 0.035)], [0.095, 0.068, 0.054, 0.046],
             (s * 0.225, 0.205, 0.022), (0.050, 0.064, 0.022), 5, s, 0.032, 0.014, s * -10)
        b.add(oriented((s * 0.15, 0.24, 0.24), (0.08, 0.12, 0.10), pitch=15), HIDE)   # thigh muscle
        b.add(oriented((s * 0.17, -0.27, 0.23), (0.08, 0.08, 0.08)), HIDE)            # shoulder


# ---------------------------------------------------------------- skin

def beak_mask(co):
    """1 on the horny beak (the down-turned snout tip and the lower beak)."""
    co = HEAD_INV @ Vector(co)
    if co.y > -0.62:
        return 0.0
    # distance along the snout from the tip
    d = (co - SNOUT_TIP).length
    up = nh.smoothstep(0.115, 0.085, d)
    return up * (1.0 - nh.smoothstep(0.13, 0.16, abs(co.x) + 0.0)) if abs(co.x) < 0.075 else 0.0


def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        # fine wrinkled skin
        d = 0.0014 * noise.noise(co * 70.0)
        d += 0.0012 * (1.0 - nh.smoothstep(0.0, 0.4, noise.cell(co * 45.0)))
        # neck folds
        if -0.48 < co.y < -0.30:
            d -= 0.0018 * nh.smoothstep(0.6, 0.95, 0.5 + 0.5 * math.sin(co.y * 105.0 + co.z * 20.0))
        # wrinkles over the elbows and knees
        if co.z < 0.22 and abs(co.x) > 0.17:
            d -= 0.002 * nh.smoothstep(0.6, 0.95, 0.5 + 0.5 * math.sin(co.z * 160.0))
        # beak: smooth horny surface with a rim ridge
        if beak_mask(co) > 0.5:
            d = 0.001 * noise.noise(co * 30.0)
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def paint(co, n):
    c = nh.lerp(BELLY, HIDE, nh.smoothstep(-0.6, -0.05, n.z))
    c = nh.lerp(c, HIDE_DARK, 0.6 * nh.smoothstep(0.35, 0.95, n.z))
    blot = noise.noise(Vector((co.x * 9.0, co.y * 9.0, co.z * 9.0)))
    c = nh.lerp(c, MOTTLE, 0.35 * nh.smoothstep(0.25, 0.55, blot) * nh.smoothstep(-0.1, 0.5, n.z))
    if co.z < 0.12:                      # feet and lower legs darker
        c = nh.lerp(HIDE_DARK, c, nh.smoothstep(0.02, 0.12, co.z))
    if co.y < -0.5:                       # face a touch paler, darker brow
        c = nh.lerp(c, HIDE_DARK, 0.25 * nh.smoothstep(0.4, 0.9, n.z))
    c = nh.lerp(c, BEAK, beak_mask(co))
    k = 1.0 + 0.08 * noise.noise(co * 25.0)
    return tuple(max(0.0, x * k) for x in c)


# ---------------------------------------------------------------- build / preview

def build():
    CLAWS.clear()
    b = nh.MeshBuilder()
    body(b)
    head(b)
    limbs(b)
    fused = b.fuse(voxel=0.0055, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 15000)

    mb = nh.MeshBuilder()
    mb.add(fused, paint)
    for sx in (1, -1):
        root = HEAD @ (TUSK_ROOT * Vector((sx, 1, 1)))
        tip = HEAD @ (TUSK_TIP * Vector((sx, 1, 1)))
        mid = root.lerp(tip, 0.5) + Vector((0, -0.006, 0))
        mb.add(nh.tube([root + Vector((0, 0.004, 0.02)), mid, tip], [0.021, 0.017, 0.0], sides=12),
               lambda co, n: nh.lerp(TUSK, (0.70, 0.62, 0.46), nh.smoothstep(0.21, 0.27, co.z)))
        e = EYE_C * Vector((sx, 1, 1))
        mb.add(H(nh.ellipsoid(e, (0.023, 0.025, 0.022), subdivisions=2)), EYE)
        mb.add(H(nh.ellipsoid(e + Vector((sx * 0.015, -0.009, 0.002)), (0.008, 0.010, 0.011), subdivisions=1)), PUPIL)
        mb.add(H(nh.ellipsoid((sx * 0.030, -0.668, 0.405), (0.009, 0.007, 0.006), subdivisions=1)), PUPIL)  # nostril
    for base, d, r in CLAWS:
        mb.add(nh.tube([base + Vector((0, 0, 0.004)), base + d * 0.018 + Vector((0, 0, -0.006))], [r, 0.0], sides=6),
               CLAW)
    obj = mb.to_object(NAME, roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head_c = Vector((0.0, -0.62, 0.30))
    out = Path(path)
    for i, off in enumerate((Vector((0.62, -0.62, 0.16)), Vector((-0.85, -0.10, 0.03)))):
        cam.location = head_c + off
        cam.rotation_euler = (head_c - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.42, 0.36, 0.26), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
