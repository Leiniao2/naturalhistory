"""
Procedural Brachiosaurus altithorax for map colonies.

The giraffe-like sauropod: long front legs and shorter hind legs, so the back
slopes steeply down from the high shoulders to the hips; a very long neck held
up at a steep angle with the small head high above the ground; a relatively
short, thick tail held clear of the ground. The skull has the broad blunt
snout and the arched nasal crest rising in front of the eyes, with the
nostrils at its base. Pillar-like legs end in elephantine feet: the front feet
with a single thumb claw, the hind feet with three claws.

Torso, neck and tail are one continuous loft; legs, shoulder and thigh
muscles, the head and its crest are fused with it into one surface, which is
then sculpted with pebbly scales, skin folds at the neck base and the knees, and
painted grey-green with a darker mottled back, a faint row of bands down the
neck and tail, and a pale belly and throat. Eyes, nostrils and claws are crisp
details.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/brachiosaurus_altithorax.py -- [--render out.png]
  (also renders out_head.png, a close-up of the head)

Output: Assets/Resources/Models/Species/Brachiosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

BACK = (0.30, 0.34, 0.26)       # grey-green
FLANK = (0.45, 0.47, 0.36)
BELLY = (0.78, 0.74, 0.60)      # pale cream
BAND = (0.21, 0.24, 0.18)
CREST = (0.55, 0.38, 0.26)      # warm flush on the nasal crest
CLAW = (0.18, 0.16, 0.13)
EYE = (0.75, 0.55, 0.15)
PUPIL = (0.03, 0.02, 0.02)

VOXEL = 0.011
BODY_TRIS = 21000


# ---------------------------------------------------------------- geometry helpers

def loft(sections, sides=20, ref=Vector((0, 0, 1))):
    """Skin elliptical rings along a path: (center, half width, half height) sections.
    Zero width closes the end in a point."""
    bm = bmesh.new()
    pts = [Vector(s[0]) for s in sections]
    rings = []
    for i, (c, ra, rb) in enumerate(sections):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = fwd.cross(ref).normalized()
        up = side.cross(fwd).normalized()
        if ra <= 1e-6:
            rings.append([bm.verts.new(Vector(c))])
            continue
        rings.append([bm.verts.new(Vector(c) + side * math.cos(k / sides * math.tau) * ra
                                   + up * math.sin(k / sides * math.tau) * rb) for k in range(sides)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[k], b[(k + 1) % sides]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
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


def smooth_loft(rows, steps=4, sides=20, ref=Vector((0, 0, 1))):
    """rows: (x, y, z, half width, half height), resampled smoothly."""
    pts = catmull(rows, steps)
    return loft([(p[:3], max(0.0, p[3]), max(0.0, p[4])) for p in pts], sides=sides, ref=ref)


def smooth_tube(points, radii, steps=4, sides=14, **kw):
    pts = catmull([(*p, r) for p, r in zip(points, radii)], steps)
    return nh.tube([p.xyz for p in pts], [max(0.0, p.w) for p in pts], sides=sides, **kw)


def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings)
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


class Parts(nh.MeshBuilder):
    def add(self, src, color=BACK, smooth=True):
        super().add(src, color, smooth)


# ---------------------------------------------------------------- anatomy

# tail tip -> hips -> high shoulders -> neck rising steeply -> back of the skull
SPINE = [
    (0, 1.66, 0.50, 0.0, 0.0),
    (0, 1.58, 0.52, 0.02, 0.022),
    (0, 1.40, 0.58, 0.05, 0.055),
    (0, 1.18, 0.66, 0.085, 0.09),
    (0, 0.94, 0.75, 0.13, 0.14),
    (0, 0.70, 0.84, 0.19, 0.20),
    (0, 0.45, 0.92, 0.25, 0.26),   # tail base
    (0, 0.25, 0.97, 0.30, 0.31),   # hips
    (0, 0.02, 1.04, 0.33, 0.35),
    (0, -0.20, 1.12, 0.34, 0.37),  # deep chest at the shoulders
    (0, -0.40, 1.26, 0.28, 0.30),
    (0, -0.53, 1.44, 0.19, 0.20),  # neck base
    (0, -0.63, 1.68, 0.13, 0.14),
    (0, -0.71, 1.94, 0.10, 0.105),
    (0, -0.78, 2.20, 0.085, 0.09),
    (0, -0.84, 2.44, 0.075, 0.08),
    (0, -0.89, 2.64, 0.068, 0.072),
    (0, -0.94, 2.78, 0.064, 0.068),
    (0, -1.00, 2.86, 0.06, 0.064),  # into the back of the skull
]

HEAD = Vector((0, -1.04, 2.88))      # back of the skull

LEGS = {  # name: (x, y, stride, top z, front)
    "lf": (-0.20, -0.22, -0.10, 1.12, True), "rf": (0.20, -0.22, 0.07, 1.12, True),
    "lh": (-0.21, 0.32, 0.06, 0.92, False), "rh": (0.21, 0.32, -0.09, 0.92, False),
}


def body(b):
    b.add(smooth_loft(SPINE, steps=4, sides=24))
    for s in (-1, 1):
        b.add(oriented((s * 0.19, -0.24, 1.08), (0.15, 0.24, 0.30), pitch=-12))  # shoulder blade + muscle
        b.add(oriented((s * 0.18, 0.32, 0.88), (0.16, 0.26, 0.30), pitch=8))     # thigh
        b.add(oriented((s * 0.09, 0.60, 0.84), (0.11, 0.30, 0.14), pitch=12))    # tail-base muscle
    b.add(oriented((0, 0.0, 0.80), (0.27, 0.42, 0.16)))                          # belly


def leg(b, name):
    x, y, stride, top, front = LEGS[name]
    if front:  # long straight column, elbow tucked back slightly
        pts = [(x * 0.95, y, top), (x, y + 0.03, 0.78), (x, y + stride * 0.5 + 0.03, 0.50),
               (x, y + stride * 0.9, 0.18), (x, y + stride, 0.06), (x, y + stride, 0.0)]
        radii = [0.14, 0.11, 0.09, 0.085, 0.09, 0.095]
    else:      # thick thigh, knee forward, shorter shin
        pts = [(x * 0.95, y, top), (x, y - 0.02, 0.65), (x, y + stride * 0.5 - 0.04, 0.42),
               (x, y + stride * 0.85, 0.18), (x, y + stride, 0.06), (x, y + stride, 0.0)]
        radii = [0.17, 0.14, 0.105, 0.095, 0.10, 0.105]
    b.add(smooth_tube(pts, radii, steps=3, sides=16))
    f = Vector((x, y + stride, 0.045))
    b.add(oriented(f + Vector((0, -0.015, 0)), (radii[-1] * 1.1, radii[-1] * 1.25, 0.045)))  # foot pad


HS = 1.35  # head scale


def hp(x, y, z):
    """Point on the head, relative to HEAD and scaled."""
    return HEAD + Vector((x, y, z)) * HS


def head(b):
    def part(off, radii, **kw):
        b.add(oriented(hp(*off), tuple(r * HS for r in radii), **kw))
    # skull: deep at the back, the snout longer, lower and narrower
    part((0, -0.03, 0.0), (0.07, 0.09, 0.068), pitch=8)
    part((0, -0.15, -0.035), (0.052, 0.10, 0.042), pitch=6)
    part((0, -0.225, -0.045), (0.046, 0.04, 0.036))
    # the tall arched nasal crest rising in front of and above the eyes
    part((0, -0.085, 0.065), (0.038, 0.06, 0.062), pitch=-30)
    # lower jaw and throat
    part((0, -0.13, -0.068), (0.048, 0.10, 0.026), pitch=6)
    part((0, 0.0, -0.04), (0.06, 0.07, 0.06))
    for s in (-1, 1):
        part((s * 0.05, -0.04, 0.005), (0.035, 0.045, 0.04))  # cheeks / brow


# ---------------------------------------------------------------- skin

KNEES = []


def displacement(co, n):
    d = 0.0014 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 45.0)))         # pebbly scales
    big = noise.voronoi(co * 14.0)[0]
    d += 0.003 * nh.smoothstep(0.0, 0.08, big[1] - big[0])                       # larger tubercles
    # folds at the neck base and around the knees/ankles
    if -0.62 < co.y < -0.38 and 1.1 < co.z < 1.55:
        d += 0.005 * math.sin((co.z - co.y * 0.6) * 90.0) * nh.smoothstep(0.2, 0.7, abs(n.x) + max(0.0, -n.z))
    for k in KNEES:
        r = (co - k).length
        if r < 0.13:
            d += 0.004 * math.sin(co.z * 120.0) * (1.0 - r / 0.13)
    return d


def sculpt(bm):
    bm.normal_update()
    offs = [(v, v.normal.copy() * displacement(v.co, v.normal)) for v in bm.verts]
    for v, o in offs:
        v.co += o
    bm.normal_update()


def skin(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.6, -0.1, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.0, 0.7, n.z))
    # pale throat along the underside of the neck
    if 1.3 < co.z < HEAD.z - 0.02 and co.y < -0.5:
        c = nh.lerp(c, BELLY, 0.7 * nh.smoothstep(0.4, 0.85, n.dot(Vector((0, -0.95, -0.3)))))
    # faint bands down the neck, back and tail
    t = co.z * 1.2 - co.y * 1.0
    band = 0.5 + 0.5 * math.sin(t * 22.0 + noise.noise(co * 3.0) * 2.0)
    c = nh.lerp(c, BAND, 0.45 * nh.smoothstep(0.7, 0.95, band) * nh.smoothstep(0.1, 0.7, n.z + 0.2))
    # dark mottling over the back
    m = noise.noise(co * 9.0)
    c = nh.lerp(c, BAND, 0.35 * nh.smoothstep(0.2, 0.6, m) * nh.smoothstep(0.2, 0.8, n.z))
    # warm flush on the crest
    r = (co - hp(0, -0.085, 0.10)).length
    if r < 0.12:
        c = nh.lerp(c, CREST, 0.7 * nh.smoothstep(0.11, 0.03, r))
    # nostril openings at the top of the crest
    for s in (-1, 1):
        if (co - hp(s * 0.025, -0.12, 0.10)).length < 0.018:
            c = PUPIL
    # darker lower legs
    c = nh.lerp(c, nh.lerp(FLANK, BAND, 0.5), 0.5 * nh.smoothstep(0.45, 0.1, co.z))
    cell = noise.cell(co * 45.0)
    return tuple(max(0.0, v * (0.92 + 0.12 * (1.0 - nh.smoothstep(0.2, 0.7, cell)))) for v in c)


# ---------------------------------------------------------------- details

def details(mb):
    for s in (-1, 1):
        e = hp(s * 0.066, -0.075, 0.03)
        mb.add(nh.ellipsoid(e, (0.018, 0.022, 0.017), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((s * 0.012, -0.005, 0)), (0.008, 0.01, 0.012), subdivisions=1), PUPIL)
    for name, (x, y, stride, top, front) in LEGS.items():
        f = Vector((x, y + stride, 0.0))
        if front:  # single big thumb claw on the inner side
            inner = -math.copysign(1, x)
            base = f + Vector((inner * 0.05, -0.07, 0.05))
            mb.add(nh.tube([base, base + Vector((inner * 0.02, -0.04, -0.03))], [0.016, 0.0], sides=6), CLAW)
        else:      # three claws on the hind foot, angled outward
            for k in range(3):
                a = math.radians(-10 + k * 22) * math.copysign(1, x)
                base = f + Vector((math.sin(a) * 0.07, -math.cos(a) * 0.08 - 0.01, 0.035))
                tip = base + Vector((math.sin(a) * 0.04, -math.cos(a) * 0.035, -0.03))
                mb.add(nh.tube([base, tip], [0.016, 0.0], sides=6), CLAW)


def build():
    KNEES.clear()
    b = Parts()
    body(b)
    for name, (x, y, stride, top, front) in LEGS.items():
        leg(b, name)
        KNEES.append(Vector((x, y + stride * 0.5, 0.48 if front else 0.42)))
    head(b)
    fused = b.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, BODY_TRIS)

    mb = nh.MeshBuilder()
    mb.add(fused, skin)
    details(mb)
    obj = mb.to_object("Brachiosaurus", roughness=0.75)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    """Extra close-up of the head (after nh.run has set up the scene)."""
    scene = bpy.context.scene
    cam = scene.camera
    target = hp(0, -0.08, 0.0)
    cam.location = target + Vector((0.55, -0.6, 0.2))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    out = Path(path)
    scene.render.filepath = str(out.with_name(f"{out.stem}_head.png"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, "Brachiosaurus", ground=(0.36, 0.44, 0.26), views=((35, 22), (-90, 6), (20, 60), (0, 8)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
