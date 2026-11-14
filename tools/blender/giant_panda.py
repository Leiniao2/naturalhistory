"""
Procedural giant panda (Ailuropoda melanoleuca) for map colonies - detailed version.

One seamless body: torso with shoulder blades and hump, heavy forelimbs, rounded
haunches, neck, head with brow, cheek fluff, muzzle and ears, all built from
overlapping primitives and fused (voxel remesh + smoothing) into a single surface.
Fur is displacement along the normals (fine noise everywhere, clumpy tufts on the
cheeks, belly and backs of the legs); the mouth and philtrum are sculpted grooves.

Markings are painted procedurally on the fused surface: a signed "black field"
(saddle band, legs, haunches, ears, eye patches) whose zero line the vertices are
snapped onto, then each face is coloured by its centre, so the black/white edges
are clean lines. Crisp separate details on top: wet nose with nostrils, eyes with
glints, claws, paw pads, and the bamboo stalk held up to the mouth.

Usage:
  blender --background --python tools/blender/giant_panda.py -- [--render out.png]
  (also renders out_head.png, a close-up of the face)

Output: Assets/Resources/Models/Species/GiantPanda.fbx (faces -Y, pivot on the ground)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Euler, Matrix, Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

VOXEL = 0.014
BODY_TRIS = 15000   # fused body after decimation; details add ~3k

WHITE = (0.95, 0.94, 0.89)
WHITE_UNDER = (0.74, 0.72, 0.66)  # shaded, slightly dingy belly and inner legs
BLACK = (0.05, 0.05, 0.06)
BLACK_SHEEN = (0.13, 0.12, 0.13)  # tips of the black fur catch a little light
EAR_INNER = (0.30, 0.24, 0.24)
MOUTH = (0.12, 0.08, 0.08)
PAD = (0.22, 0.19, 0.19)
CLAW = (0.80, 0.76, 0.66)
NOSE = (0.025, 0.025, 0.03)
NOSE_SHINE = (0.30, 0.30, 0.33)
NOSTRIL = (0.0, 0.0, 0.0)
EYE = (0.12, 0.07, 0.05)
GLINT = (0.97, 0.97, 0.97)
BAMBOO = (0.38, 0.64, 0.20)
BAMBOO_NODE = (0.58, 0.72, 0.30)
LEAF = (0.22, 0.52, 0.14)

BODY_C = Vector((0.0, 0.04, 0.46))
BODY_R = (0.31, 0.46, 0.30)

SADDLE_HALF = 0.12
SADDLE_SLANT = 0.35

HEAD_C = Vector((0.02, -0.60, 0.60))
HEAD_TURN = 20   # degrees toward the raised paw (+X)
HEAD_DIP = 8     # degrees nose-down

# Limb skeletons: (points, radii). x < 0 is the panda's left.
FRONT_LEFT = ([(-0.12, -0.24, 0.56), (-0.18, -0.26, 0.40), (-0.185, -0.27, 0.27), (-0.175, -0.28, 0.15),
               (-0.17, -0.29, 0.07)],
              [0.13, 0.15, 0.125, 0.095, 0.088])
RAISED_RIGHT = ([(0.12, -0.25, 0.52), (0.20, -0.33, 0.38), (0.25, -0.42, 0.25), (0.25, -0.64, 0.38)],
                [0.13, 0.14, 0.11, 0.085])
HIND = [([(sx * 0.11, 0.31, 0.52), (sx * 0.19, 0.34, 0.36), (sx * 0.19, 0.34, 0.24), (sx * 0.19, 0.32, 0.14),
          (sx * 0.19, 0.30, 0.07)],
         [0.13, 0.16, 0.135, 0.10, 0.092]) for sx in (-1, 1)]
HAUNCHES = [(Vector((sx * 0.175, 0.31, 0.37)), Vector((0.135, 0.19, 0.18))) for sx in (-1, 1)]
PAWS = [Vector((-0.17, -0.32, 0.0)), Vector((-0.19, 0.27, 0.0)), Vector((0.19, 0.27, 0.0))]
RAISED_PAW = Vector((0.24, -0.69, 0.42))


# ---------------------------------------------------------------- helpers

def head_matrix():
    return (Matrix.Translation(HEAD_C)
            @ Matrix.Rotation(math.radians(HEAD_TURN), 4, "Z")
            @ Matrix.Rotation(math.radians(HEAD_DIP), 4, "X"))


HEAD_M = head_matrix()
HEAD_INV = HEAD_M.inverted()
HEAD_ROT = HEAD_M.to_3x3()


def hl(x, y, z):
    """Head-local point -> world."""
    return HEAD_M @ Vector((x, y, z))


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length, t


def chain_field(p, pts, radii, pad=0.0):
    """>0 inside a tapered capsule chain (normalised by the local radius)."""
    best = -1e9
    pts = [Vector(q) for q in pts]
    for i in range(len(pts) - 1):
        d, t = seg_dist(p, pts[i], pts[i + 1])
        r = radii[i] + (radii[i + 1] - radii[i]) * t + pad
        best = max(best, (r - d) / r)
    return best


def ellipsoid_field(p, c, r, rot=None):
    q = p - c
    if rot is not None:
        q = rot.transposed() @ q
    return 1.0 - Vector((q.x / r[0], q.y / r[1], q.z / r[2])).length


# ---------------------------------------------------------------- anatomy (fused)

def add_head_parts(body):
    def put(bm):
        body.add(nh.transform(bm, HEAD_M), WHITE)

    put(nh.ellipsoid((0, 0, 0), (0.25, 0.22, 0.215), subdivisions=4))
    for sx in (-1, 1):
        put(nh.ellipsoid((sx * 0.125, -0.06, -0.07), (0.135, 0.125, 0.115), subdivisions=3))   # cheek fluff
        put(nh.ellipsoid((sx * 0.085, -0.155, 0.075), (0.07, 0.05, 0.035), subdivisions=3))    # brow
        put(nh.ellipsoid((sx * 0.17, 0.04, 0.17), (0.085, 0.05, 0.08), subdivisions=3,           # ear
                         rotation=Euler((math.radians(-15), 0, math.radians(sx * -20))).to_matrix()))
    put(nh.ellipsoid((0, -0.17, -0.07), (0.105, 0.115, 0.085), subdivisions=3))   # muzzle
    put(nh.ellipsoid((0, -0.13, -0.135), (0.075, 0.08, 0.045), subdivisions=3))   # chin


def build_body():
    body = nh.MeshBuilder()
    hump = lambda v: 1.0 + 0.05 * max(0.0, v.z) - 0.04 * max(0.0, -v.z)  # noqa: E731
    body.add(nh.ellipsoid(BODY_C, BODY_R, subdivisions=4, deform=hump), WHITE)
    body.add(nh.ellipsoid((0, 0.27, 0.45), (0.29, 0.26, 0.28), subdivisions=4), WHITE)        # rump
    body.add(nh.ellipsoid((0, -0.30, 0.40), (0.25, 0.19, 0.22), subdivisions=3), WHITE)       # chest
    body.add(nh.ellipsoid((0, 0.06, 0.31), (0.25, 0.30, 0.15), subdivisions=3), WHITE)        # belly sag
    for sx in (-1, 1):                                                                         # shoulder blades
        body.add(nh.ellipsoid((sx * 0.12, -0.21, 0.67), (0.10, 0.15, 0.075), subdivisions=3,
                              rotation=Euler((math.radians(-20), math.radians(sx * 15), 0)).to_matrix()), WHITE)
    body.add(nh.tube([(0, -0.25, 0.56), (0.01, -0.42, 0.60), HEAD_C], [0.21, 0.19, 0.17], sides=16), WHITE)  # neck
    add_head_parts(body)

    for pts, radii in [FRONT_LEFT, RAISED_RIGHT] + HIND:
        body.add(nh.tube(pts, radii, sides=16), BLACK)
    for c, r in HAUNCHES:
        body.add(nh.ellipsoid(c, r, subdivisions=3), BLACK)
    for p in PAWS:
        body.add(nh.ellipsoid(p + Vector((0, -0.035, 0.055)), (0.105, 0.13, 0.065), subdivisions=3,
                              deform=lambda v: 1.0 - 0.25 * max(0.0, -v.z) ** 3), BLACK)
        for i in range(4):                                                                     # toe bumps
            t = (i - 1.5) / 1.5
            body.add(nh.ellipsoid(p + Vector((t * 0.065, -0.13 + 0.02 * t * t, 0.045)), (0.032, 0.035, 0.03),
                                  subdivisions=2), BLACK)
    body.add(nh.ellipsoid(RAISED_PAW, (0.075, 0.08, 0.09), subdivisions=3), BLACK)
    body.add(nh.ellipsoid((0, 0.54, 0.50), (0.07, 0.06, 0.07), subdivisions=2), WHITE)       # tail
    return body.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5)


# ---------------------------------------------------------------- fur + sculpt

def fur_weight(p, n, local):
    """How fluffy the fur is here: tufty on cheeks, belly and backs of the legs,
    smooth on the muzzle, ears and paws."""
    w = 0.45
    if p.z < 0.09:
        return 0.1                                   # paws
    if local.length < 0.36:                          # on the head
        if local.y < -0.1 and local.z < 0.02:
            return 0.05                              # muzzle
        if local.z > 0.12 and abs(local.x) > 0.11:
            return 0.15                              # ears
        if abs(local.x) > 0.15 and local.z < 0.0:
            return 1.4                               # cheek ruff
        return 0.5
    if n.z < -0.4 and 0.12 < p.z < 0.40 and -0.2 < p.y < 0.3:
        w = 1.3                                      # belly fringe
    if p.z < 0.40 and n.y > 0.4:
        w = max(w, 1.2)                              # backs of the legs
    return w


def displace_fur(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        p, n = v.co.copy(), v.normal.copy()
        local = HEAD_INV @ p
        w = fur_weight(p, n, local)
        fine = 0.005 * noise.noise(p * 16.0)
        clump = max(0.0, noise.noise(p * 11.0 + Vector((3.3, 1.1, 7.7)))) ** 2.2
        d = w * (fine + 0.02 * clump * (1.6 if w > 1.0 else 1.0))
        d += sculpt_grooves(local) + ear_cup(local, HEAD_ROT.transposed() @ n)
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m


def ear_cup(local, n_local):
    """Hollow the front of each ear so the inner ear reads as a cup."""
    if local.z < 0.12:
        return 0.0
    for sx in (-1, 1):
        q = local - Vector((sx * 0.17, 0.04, 0.17))
        r = Vector((q.x / 0.085, q.y / 0.05, q.z / 0.08)).length
        if r < 1.6 and n_local.y < -0.2:
            return -0.022 * max(0.0, -n_local.y) * max(0.0, 1.0 - r / 1.6)
    return 0.0


def mouth_curve():
    # philtrum down from the nose, then a gentle smile out to each side (head-local)
    return [[(0, -0.284, -0.065), (0, -0.282, -0.098)],
            [(0, -0.282, -0.098), (-0.035, -0.272, -0.11), (-0.068, -0.245, -0.098)],
            [(0, -0.282, -0.098), (0.035, -0.272, -0.11), (0.068, -0.245, -0.098)]]


def mouth_dist(local):
    best = 1e9
    for line in mouth_curve():
        pts = [Vector(q) for q in line]
        for a, b in zip(pts, pts[1:]):
            best = min(best, seg_dist(local, a, b)[0])
    return best


def sculpt_grooves(local):
    d = mouth_dist(local)
    return -0.008 * max(0.0, 1.0 - d / 0.014)


# ---------------------------------------------------------------- markings

def saddle_centre(z):
    return -0.20 + (z - BODY_C.z) * SADDLE_SLANT


EYE_PATCHES = []
for sx in (-1, 1):
    rot = HEAD_ROT @ Euler((math.radians(-15), math.radians(sx * -35), math.radians(sx * 22))).to_matrix()
    EYE_PATCHES.append((hl(sx * 0.09, -0.17, 0.03), (0.082, 0.07, 0.06), rot))


def black_field(p):
    local = HEAD_INV @ p
    on_head = local.length < 0.40
    f = -1.0
    if not on_head and p.z > 0.12:
        f = max(f, (SADDLE_HALF - abs(p.y - saddle_centre(p.z))) / SADDLE_HALF)
    for pts, radii in [FRONT_LEFT, RAISED_RIGHT] + HIND:
        f = max(f, chain_field(p, pts[1:], radii[1:], pad=0.025))
    for c, r in HAUNCHES:
        f = max(f, ellipsoid_field(p, c, r * 1.12))
    if p.z < 0.13:
        f = max(f, (0.13 - p.z) / 0.13)                      # paws
    f = max(f, ellipsoid_field(p, RAISED_PAW, (0.11, 0.12, 0.13)))
    if on_head:
        if local.z > 0.10:
            for sx in (-1, 1):                               # ears
                f = max(f, ellipsoid_field(local, Vector((sx * 0.17, 0.04, 0.17)), (0.12, 0.10, 0.11)))
        for c, r, rot in EYE_PATCHES:
            q = rot.transposed() @ (p - c)
            k = 1.0 + 0.35 * max(0.0, -q.z / r[2])          # teardrop: wider toward the cheek
            f = max(f, 1.0 - Vector((q.x / (r[0] * k), q.y / r[1], q.z / r[2])).length)
    return f


def mouth_field(p):
    return 0.0105 - mouth_dist(HEAD_INV @ p)


def cut_contour(bm, field):
    """Split the mesh exactly along the field's zero line: new vertices where edges cross
    it, joined across each face. Faces then lie wholly on one side, so per-face colours
    give a clean edge instead of a sawtooth."""
    vals = {v: field(v.co) for v in bm.verts}
    on_line = set()
    for e in list(bm.edges):
        a, b = e.verts
        fa, fb = vals[a], vals[b]
        if (fa > 0) == (fb > 0) or abs(fa - fb) < 1e-12:
            continue
        t = fa / (fa - fb)
        if t < 0.02 or t > 0.98:
            on_line.add(a if t < 0.5 else b)   # crossing sits on an existing vertex
            continue
        _e, v = bmesh.utils.edge_split(e, a, t)
        vals[v] = 0.0
        on_line.add(v)
    for f in list(bm.faces):
        vs = [v for v in f.verts if v in on_line]
        if len(vs) == 2 and not any(vs[1] in (e.other_vert(vs[0]),) for e in vs[0].link_edges):
            bmesh.ops.connect_verts(bm, verts=vs)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])


def decimate(bm, max_tris):
    """Collapse-decimate a bmesh in place down to about max_tris triangles."""
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    n = sum(len(p.vertices) - 2 for p in mesh.polygons)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = min(1.0, max_tris / max(n, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    bm.clear()
    bm.from_mesh(ev.to_mesh())
    ev.to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    if not bm.loops.layers.color.get("Col"):
        bm.loops.layers.color.new("Col")
    return bm


def paint(bm):
    col = bm.loops.layers.color.get("Col") or bm.loops.layers.color.new("Col")
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        n = f.normal
        local = HEAD_INV @ c
        if mouth_field(c) > 0:
            rgb = MOUTH
        elif black_field(c) > 0:
            if local.length < 0.40 and local.z > 0.12 and (HEAD_ROT.transposed() @ n).y < -0.3:
                rgb = EAR_INNER                               # front of the ear
            else:
                sheen = max(0.0, noise.noise(c * 9.0 + Vector((3.3, 1.1, 7.7))))
                rgb = nh.lerp(BLACK, BLACK_SHEEN, sheen * max(0.0, n.z) * 0.8)
        else:
            shade = nh.smoothstep(0.20, 0.52, c.z)
            if local.length < 0.40:
                shade = 1.0
            rgb = nh.lerp(WHITE_UNDER, WHITE, shade)
        for l in f.loops:
            l[col] = (rgb[0], rgb[1], rgb[2], 1.0)


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def on(self, p, lift=0.0):
        hit, n, _i, _d = self.tree.find_nearest(p)
        return (hit + n * lift, n) if hit is not None else (p, Vector((0, 0, 1)))


def add_face_details(mb, surf):
    # wet nose: wide, flat-topped, with a highlight and two nostrils
    nose_c, nose_n = surf.on(hl(0, -0.27, -0.035), lift=0.012)
    nose = nh.ellipsoid((0, 0, 0), (0.052, 0.034, 0.032), subdivisions=3,
                        deform=lambda v: 1.0 - 0.3 * max(0.0, -v.z) * abs(v.x))
    mb.add(nh.transform(nh.transform(nose, HEAD_ROT.to_4x4()), Matrix.Translation(nose_c)),
           lambda co, n: NOSE_SHINE if (HEAD_ROT.transposed() @ n).z > 0.75 else NOSE)
    for sx in (-1, 1):
        p = nose_c + HEAD_ROT @ Vector((sx * 0.02, -0.028, -0.006))
        mb.add(nh.transform(nh.ellipsoid((0, 0, 0), (0.011, 0.006, 0.007), subdivisions=2),
                            Matrix.Translation(p) @ HEAD_ROT.to_4x4()), NOSTRIL)
    # eyes: dark, slightly proud of the patch, with a glint up and out
    for sx in (-1, 1):
        c, n = surf.on(hl(sx * 0.088, -0.20, 0.045), lift=0.006)
        mb.add(nh.ellipsoid(c, (0.021, 0.021, 0.021), subdivisions=2), EYE)
        g = c + n * 0.016 + HEAD_ROT @ Vector((sx * -0.006, 0, 0.008))
        mb.add(nh.ellipsoid(g, (0.0065, 0.0065, 0.0065), subdivisions=1), GLINT)


def add_claws(mb, surf):
    for p in PAWS:
        for i in range(4):
            t = (i - 1.5) / 1.5
            toe = p + Vector((t * 0.065, -0.16 + 0.02 * t * t, 0.04))
            base, n = surf.on(toe)
            tip = base + Vector((0, -0.045, -0.025))
            mb.add(nh.tube([base + Vector((0, 0.01, 0.004)), tip], [0.011, 0.0], sides=5), CLAW)
    # raised paw: palm pad and toe beans facing the bamboo, claws curled round it
    palm_dir = Vector((-1.0, -0.3, 0.0)).normalized()
    c, n = surf.on(RAISED_PAW + palm_dir * 0.08, lift=0.004)
    mb.add(nh.ellipsoid(c, (0.03, 0.04, 0.045), subdivisions=2), PAD)
    for i in range(3):
        bean, _n = surf.on(RAISED_PAW + palm_dir * 0.06 + Vector((0, -0.03 + i * 0.03, 0.07 - i * 0.012)),
                           lift=0.003)
        mb.add(nh.ellipsoid(bean, (0.016, 0.016, 0.016), subdivisions=1), PAD)
        mb.add(nh.tube([bean, bean + Vector((-0.032, -0.012, -0.012))], [0.009, 0.0], sides=5), CLAW)


def add_bamboo(mb, grip, mouth):
    """Upright stalk held in the paw, passing the mouth corner, leafy top above head height."""
    bottom = grip + Vector((0.01, 0.01, -0.13))
    side = mouth + Vector((0.07, 0.0, 0.0))
    top = side + Vector((0.04, 0.03, 0.34))
    pts = [bottom, grip, side, top]
    mb.add(nh.tube(pts, [0.022, 0.023, 0.022, 0.018], sides=10), BAMBOO)
    for a, b, t in ((0, 1, 0.3), (1, 2, 0.5), (2, 3, 0.45)):
        p = pts[a].lerp(pts[b], t)
        d = (pts[b] - pts[a]).normalized() * 0.012
        mb.add(nh.tube([p - d, p + d], [0.028, 0.028], sides=10), BAMBOO_NODE)
    for k, (az, el) in enumerate(((20, 35), (100, 20), (170, 40), (250, 25), (320, 45), (60, 60))):
        a, e = math.radians(az), math.radians(el)
        leaf_dir = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        w = leaf_dir.cross(Vector((0, 0, 1))).normalized() * 0.03
        base = top - Vector((0, 0, 0.03 * (k % 2)))
        mid = base + leaf_dir * 0.08
        mb.add(nh.flat_panel([base, mid + w * 0.8, base + leaf_dir * 0.21, mid - w], thickness=0.006), LEAF)


# ---------------------------------------------------------------- build

def build():
    fused = build_body()
    displace_fur(fused)
    decimate(fused, BODY_TRIS)
    cut_contour(fused, black_field)
    cut_contour(fused, mouth_field)
    paint(fused)

    mb = nh.MeshBuilder()
    copy = fused.copy()
    surf = Surface(copy)
    mb.add(fused)
    add_face_details(mb, surf)
    add_claws(mb, surf)
    add_bamboo(mb, RAISED_PAW + Vector((-0.02, -0.03, 0.0)), hl(0.06, -0.24, -0.10))
    copy.free()

    obj = mb.to_object("GiantPanda", roughness=0.75)
    obj["ground_shift"] = min(v.co.z for v in obj.data.vertices)
    nh.ground_to_zero(obj)
    return obj


def render_head(path, obj):
    """Close-up of the face from the front three-quarter."""
    scene = bpy.context.scene
    cam = scene.camera
    target = HEAD_C + Vector((0.03, -0.12, -obj["ground_shift"]))
    cam.location = target + Vector((0.45, -0.75, 0.22))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, "GiantPanda")
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        nh.render_preview(obj, out, ground=(0.32, 0.45, 0.22), views=((35, 25), (-90, 8), (20, 60), (-30, 15)))
        render_head(out.with_name(out.stem + "_head.png"), obj)


if __name__ == "__main__":
    main()
