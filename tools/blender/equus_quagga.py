"""
Procedural plains zebra (Equus quagga) for map colonies.

A compact, deep-chested horse body standing square on slim legs with knees,
hocks, fetlocks and single dark hooves; a thick arched neck with a short,
upright, brush-like mane; a long head carried low, with big rounded ears, a dark
muzzle and nostrils; and a thin tail ending in a black tassel.

The body is built from overlapping parts, fused into one seamless surface and
decimated. The stripes are a procedural phase field: vertical bands on the
barrel and neck that bend into broad diagonal / horizontal bands over the
haunch, horizontal rings down the legs, fine bands across the face, a black
dorsal and belly line, and brownish "shadow stripes" inside the white bands of
the rump (the plains-zebra signature). Rather than blur them into vertex
colours, the mesh is cut along the stripe boundaries and painted face by face,
so the bands stay sharp at a modest triangle count. The upright mane is a crisp
brush, striped hair-column by hair-column with dark tips; eyes, nostrils, ears
and hooves are crisp details on top.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/equus_quagga.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PlainsZebra.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

WHITE = (0.93, 0.91, 0.86)
BLACK = (0.05, 0.045, 0.045)
SHADOW = (0.50, 0.40, 0.30)     # brownish shadow stripes on the rump
MUZZLE = (0.10, 0.08, 0.07)
HOOF = (0.08, 0.07, 0.06)
EYE = (0.05, 0.03, 0.02)
EYE_SHINE = (0.80, 0.80, 0.80)

FRONT_X, HIND_X = 0.085, 0.09
MAX_TRIS = 6000    # before the stripe refinement and cuts, which add roughly 3x more
NECK_AXIS = Vector((0.0, -0.55, 0.835)).normalized()   # along the neck, withers -> poll
HEAD_AXIS = Vector((0.0, -0.62, -0.78)).normalized()   # along the face, forehead -> muzzle
POLL = Vector((0.0, -0.545, 1.27))


# ---------------------------------------------------------------- shape helpers

def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14, deform=None):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def cup_ear(base, height, width, depth, tilt_x, splay):
    """Closed, cupped, rounded ear open toward -Y, solidified, then posed."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.15], context="VERTS")
    for v in bm.verts:
        z01 = (v.co.z + 1) * 0.5
        taper = 0.3 + 0.7 * math.sin(math.pi * min(1.0, z01 * 0.85 + 0.12)) ** 0.7  # broad, blunt-tipped
        v.co = Vector((v.co.x * width * taper, v.co.y * depth, z01 * height))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.008)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    nh.transform(bm, Matrix.Rotation(math.radians(splay), 4, "Y") @ Matrix.Rotation(math.radians(tilt_x), 4, "X"))
    nh.transform(bm, Matrix.Translation(Vector(base)))
    return bm


def render_closeups(path, target, dist, views):
    scene = bpy.context.scene
    cam = scene.camera
    out = Path(path)
    for i, (az, el) in enumerate(views):
        a, e = math.radians(az), math.radians(el)
        cam.location = Vector(target) + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- anatomy

def front_leg(x):
    return ([(x * 0.5, -0.29, 0.90), (x * 0.9, -0.30, 0.78), (x, -0.31, 0.64), (x, -0.32, 0.50),
             (x * 0.96, -0.32, 0.34), (x * 0.96, -0.32, 0.16), (x * 0.96, -0.325, 0.09), (x * 0.96, -0.345, 0.055)],
            [0.07, 0.09, 0.07, 0.05, 0.036, 0.027, 0.031, 0.027])


def hind_leg(x):
    return ([(x * 0.5, 0.30, 0.92), (x * 0.9, 0.30, 0.82), (x, 0.29, 0.70), (x, 0.26, 0.55),
             (x * 0.96, 0.40, 0.36), (x * 0.96, 0.38, 0.16), (x * 0.96, 0.375, 0.09), (x * 0.96, 0.36, 0.055)],
            [0.08, 0.11, 0.095, 0.065, 0.036, 0.027, 0.031, 0.027])


NECK_PTS = [(0, -0.22, 0.86), (0, -0.32, 0.95), (0, -0.40, 1.05), (0, -0.47, 1.15), (0, -0.53, 1.23)]
NECK_R = [0.16, 0.14, 0.115, 0.095, 0.08]


def crest_line(steps=12):
    """(crest point, outward direction) samples along the top of the neck, withers -> poll."""
    out = []
    for i in range(steps + 1):
        t = i / steps * (len(NECK_PTS) - 1)
        k = min(int(t), len(NECK_PTS) - 2)
        f = t - k
        a, b = Vector(NECK_PTS[k]), Vector(NECK_PTS[k + 1])
        c = a.lerp(b, f)
        r = NECK_R[k] + (NECK_R[k + 1] - NECK_R[k]) * f
        fwd = (b - a).normalized()
        up = Vector((0, 0, 1)) - fwd * fwd.z
        up.normalize()
        out.append((c + up * r, up))
    return out


# ---------------------------------------------------------------- stripes

# stripe periods (one black + one white band), model units
P_BODY, P_HAUNCH, P_NECK, P_LEG, P_HEAD = 0.08, 0.10, 0.085, 0.052, 0.045
HAUNCH_Y = 0.19                         # centre of the barrel -> haunch transition
NECK_ANCHOR = Vector((0.0, -0.32, 0.92))
HEAD_ANCHOR = Vector((0.0, -0.55, 1.20))


def phase_upper(p):
    """Stripe phase (cycles) on the body, neck and head. Each region has its own linear field,
    anchored so neighbouring fields agree where they blend (no phase jumps = no smeared bands)."""
    body = p.y / P_BODY
    # haunch: bands rotate to diagonal, then horizontal over the thigh
    s_h = -(p.z - 0.85) * 1.1 + (p.y - HAUNCH_Y) * 0.35
    haunch = HAUNCH_Y / P_BODY + s_h / P_HAUNCH
    k = nh.smoothstep(HAUNCH_Y - 0.11, HAUNCH_Y + 0.11, p.y)
    ph = body * (1.0 - k) + haunch * k
    # neck: bands perpendicular to the neck axis, continuing onto the chest
    neck = NECK_ANCHOR.y / P_BODY + (p - NECK_ANCHOR).dot(NECK_AXIS) / P_NECK
    k = nh.smoothstep(-0.25, -0.37, p.y)
    ph = ph * (1.0 - k) + neck * k
    # head: fine bands across the face
    if p.y < -0.5:
        n_a = NECK_ANCHOR.y / P_BODY + (HEAD_ANCHOR - NECK_ANCHOR).dot(NECK_AXIS) / P_NECK
        head = n_a + (p - HEAD_ANCHOR).dot(HEAD_AXIS) / P_HEAD
        k = nh.smoothstep(-0.52, -0.58, p.y)
        ph = ph * (1.0 - k) + head * k
    return ph


def leg_top(p):
    return 0.57 if p.y < 0 else 0.60


def stripe_cycles(co, n=None):
    """Continuous stripe phase in cycles, plus the rump shadow-stripe weight."""
    p = Vector(co)
    ph = phase_upper(p)
    # legs: horizontal rings, anchored to the body pattern where the leg leaves the body
    zt = leg_top(p) - 0.05
    if p.z < zt + 0.06:
        leg = phase_upper(Vector((p.x, p.y, zt))) + (p.z - zt) / P_LEG
        k = nh.smoothstep(zt + 0.05, zt - 0.05, p.z)
        ph = ph * (1.0 - k) + leg * k
    else:
        k = 0.0
    warp = 0.9 * noise.noise(p * 3.5) + 0.25 * noise.noise(p * 11.0)
    shadow = nh.smoothstep(HAUNCH_Y - 0.05, HAUNCH_Y + 0.1, p.y) * (1.0 - k)
    return ph + warp / math.tau, shadow


def stripe_field(co, n=None):
    """Signed stripe value: > 0 on black stripes, < 0 on white. Also returns v and the shadow weight."""
    ph, shadow = stripe_cycles(co, n)
    v = math.sin(math.tau * ph)
    return v + 0.06, v, shadow


def zebra_paint(co, n, black=None):
    """Final colour; black = which side of a stripe boundary this face lies on (None = soft)."""
    p = Vector(co)
    g, v, shadow = stripe_field(p, n)
    if black is None:
        black = nh.smoothstep(-0.15, 0.15, g)
    c = nh.lerp(WHITE, BLACK, black)
    # shadow stripe running down the middle of the white bands on the rump
    if shadow > 0.05:
        mid = nh.smoothstep(-0.72, -0.9, v)
        c = nh.lerp(c, SHADOW, 0.85 * mid * shadow)
    # dorsal line along the spine and a belly line
    if -0.30 < p.y < 0.45:
        if n.z > 0.85 and abs(p.x) < 0.02:
            c = BLACK
        if n.z < -0.85 and abs(p.x) < 0.035 and p.y < 0.2:
            c = BLACK
    # pale lower belly between the stripe ends
    if n.z < -0.7 and 0.66 < p.z < 0.7 and abs(p.x) > 0.05:
        c = nh.lerp(c, WHITE, 0.3)
    # dark muzzle shading into the stripes
    if p.y < -0.74:
        c = nh.lerp(c, MUZZLE, nh.smoothstep(-0.745, -0.775, p.y))
    # hoof bands
    if p.z < 0.07:
        c = nh.lerp(BLACK, c, nh.smoothstep(0.045, 0.07, p.z))
    return c


def mane_brush(steps=44, thickness=0.014):
    """Crisp upright brush of stiff hair along the crest, striped hair-column by hair-column with
    dark tips; sits over the fused mane base. Faces are painted individually so bands stay sharp."""
    crest = crest_line(steps)
    c, up = crest[-1]
    crest.append((Vector((0, POLL.y + 0.005, POLL.z + 0.02)), Vector((0, 0.35, 0.94)).normalized()))
    bm = bmesh.new()
    cols = []
    for i, (c, up) in enumerate(crest):
        t = i / (len(crest) - 1)
        h = 0.055 + 0.065 * math.sin(math.pi * min(1.0, t * 1.08))
        jag = 0.008 * noise.noise(Vector((t * 40.0, 0.5, 0.5)))  # ragged clipped-brush edge
        rows = []
        for k in range(6):
            q = c + up * (-0.03 + (h + jag + 0.03) * k / 5)
            rows.append(q)
        cols.append([(bm.verts.new(q + Vector((thickness * 0.5 * (1.0 - 0.6 * k / 5), 0, 0))),
                      bm.verts.new(q - Vector((thickness * 0.5 * (1.0 - 0.6 * k / 5), 0, 0)))) for k, q in enumerate(rows)])
    faces = []
    for a, b in zip(cols, cols[1:]):
        for k in range(5):
            faces.append(bm.faces.new([a[k][0], b[k][0], b[k + 1][0], a[k + 1][0]]))
            faces.append(bm.faces.new([a[k + 1][1], b[k + 1][1], b[k][1], a[k][1]]))
        faces.append(bm.faces.new([a[5][0], b[5][0], b[5][1], a[5][1]]))   # top edge
    for end in (cols[0], cols[-1]):
        for k in range(5):
            faces.append(bm.faces.new([end[k][0], end[k + 1][0], end[k + 1][1], end[k][1]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    col = bm.loops.layers.color.new("Col")
    for f in bm.faces:
        m = f.calc_center_median()
        black = stripe_field(m)[0] > 0.0
        c = BLACK if black else WHITE
        # dark tips: the upper third of the brush is black-brown
        i = min(range(len(crest)), key=lambda j: (crest[j][0] - m).length)
        hgt = (m - crest[i][0]).dot(crest[i][1])
        if hgt > 0.04 + 0.03 * math.sin(math.pi * min(1.0, i / (len(crest) - 1) * 1.08)):
            c = nh.lerp(c, BLACK, 0.85)
        for l in f.loops:
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


def tail_paint(co, n):
    # thin striped dock, black tassel
    c = nh.lerp(WHITE, BLACK, nh.smoothstep(-0.2, 0.2, math.sin(co.z * math.tau / 0.05)))
    return nh.lerp(c, BLACK, nh.smoothstep(0.72, 0.65, co.z))


def cut_stripes(bm):
    """Splits the mesh along the stripe boundaries (zero isoline of stripe_field) so every face
    lies wholly on a black or a white stripe, then paints per face: crisp stripes at a low
    triangle count instead of vertex-colour blur."""
    # refine edges that span too much of a stripe cycle for a linear cut to follow
    for _ in range(1):
        bm.normal_update()
        cyc = {v: stripe_cycles(v.co)[0] for v in bm.verts}
        long_edges = [e for e in bm.edges if abs(cyc[e.verts[0]] - cyc[e.verts[1]]) > 0.6]
        if not long_edges:
            break
        bmesh.ops.subdivide_edges(bm, edges=long_edges, cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.normal_update()
    val = {v: stripe_field(v.co, v.normal)[0] for v in bm.verts}
    zero = set()
    for e in list(bm.edges):
        a, b = e.verts
        fa, fb = val[a], val[b]
        if fa * fb < 0.0:
            t = fa / (fa - fb)
            if t < 0.02 or t > 0.98:  # snap to the nearer vertex instead of a sliver
                zero.add(a if t < 0.5 else b)
                continue
            _e, nv = bmesh.utils.edge_split(e, a, t)
            val[nv] = 0.0
            zero.add(nv)
    for f in list(bm.faces):
        zs = [v for v in f.verts if v in zero]
        if len(zs) == 2:
            pairs = [zs]
        elif len(zs) == 4:  # two boundaries through one face: pair the zeros that are closest
            a = [(zs[0], zs[1]), (zs[2], zs[3])]
            b = [(zs[1], zs[2]), (zs[3], zs[0])]
            la = sum((p[0].co - p[1].co).length for p in a)
            lb = sum((p[0].co - p[1].co).length for p in b)
            pairs = a if la < lb else b
        else:
            continue
        for u, w in pairs:
            if any(e.other_vert(u) is w for e in u.link_edges):
                continue
            bmesh.ops.connect_verts(bm, verts=[u, w])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.normal_update()
    col = bm.loops.layers.color.get("Col") or bm.loops.layers.color.new("Col")
    for f in bm.faces:
        side = stripe_field(f.calc_center_median())[0]
        black = 1.0 if side > 0.0 else 0.0
        for l in f.loops:
            c = zebra_paint(l.vert.co, l.vert.normal, black)
            l[col] = (c[0], c[1], c[2], 1.0)
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


# ---------------------------------------------------------------- build

def build():
    body = nh.MeshBuilder()

    def barrel(n):
        k = 1.0 + 0.12 * max(0.0, -n.y) * max(0.0, -n.z + 0.4)  # deep chest
        k *= 1.0 + 0.10 * max(0.0, n.y) * max(0.0, n.z + 0.5)   # round rump
        k *= 1.0 + 0.04 * max(0.0, -n.z)                         # rounded belly (well-fed grazer)
        return k
    body.add(oriented((0, 0.0, 0.81), (0.19, 0.42, 0.22), pitch=2, segments=28, rings=20, deform=barrel), WHITE)
    body.add(oriented((0, -0.14, 0.79), (0.20, 0.24, 0.235)), WHITE)                       # ribcage
    body.add(oriented((0, -0.26, 0.97), (0.075, 0.14, 0.07), pitch=-10), WHITE)            # withers
    body.add(oriented((0, 0.30, 0.92), (0.15, 0.17, 0.10)), WHITE)                         # croup
    for sx in (-1, 1):
        body.add(oriented((sx * 0.11, -0.29, 0.84), (0.075, 0.12, 0.17), pitch=-18), WHITE)   # shoulder
        body.add(oriented((sx * 0.11, 0.28, 0.83), (0.09, 0.17, 0.18), pitch=10), WHITE)      # haunch
        body.add(oriented((sx * 0.10, 0.27, 0.66), (0.075, 0.11, 0.14), pitch=-15), WHITE)    # gaskin
        body.add(oriented((sx * 0.095, -0.31, 0.65), (0.06, 0.075, 0.11), pitch=-5), WHITE)   # forearm
        pts, radii = front_leg(sx * FRONT_X)
        body.add(nh.tube(pts, radii, sides=14), WHITE)
        body.add(oriented((sx * FRONT_X * 0.96, -0.322, 0.34), (0.034, 0.036, 0.045)), WHITE)       # knee
        body.add(oriented((sx * FRONT_X * 0.96, -0.328, 0.09), (0.033, 0.036, 0.03)), WHITE)        # fetlock
        pts, radii = hind_leg(sx * HIND_X)
        body.add(nh.tube(pts, radii, sides=14), WHITE)
        body.add(oriented((sx * HIND_X * 0.96, 0.41, 0.36), (0.03, 0.045, 0.05), pitch=20), WHITE)  # hock
        body.add(oriented((sx * HIND_X * 0.96, 0.378, 0.09), (0.033, 0.036, 0.03)), WHITE)          # fetlock

    # neck: thick, laterally flattened, arched crest
    body.add(nh.tube(NECK_PTS, NECK_R, sides=18, scale_xy=(0.7, 1.0)), WHITE)
    body.add(oriented((0, -0.40, 1.00), (0.07, 0.10, 0.08), pitch=-35), WHITE)                # throat
    crest = [c + up * 0.012 for c, up in crest_line()[1:]]
    body.add(nh.tube(crest, [0.022] * len(crest), sides=8), WHITE)             # thick crest the mane grows from

    # head: long, carried at about 45 degrees, broad jowls, slim nose, soft muzzle
    body.add(oriented((0, -0.575, 1.23), (0.075, 0.08, 0.075), pitch=-35), WHITE)             # cranium
    body.add(oriented((0, -0.585, 1.15), (0.065, 0.07, 0.085), pitch=-35), WHITE)             # jowls
    body.add(nh.tube([(0, -0.57, 1.24), (0, -0.64, 1.16), (0, -0.70, 1.08), (0, -0.755, 1.01), (0, -0.78, 0.975)],
                     [0.068, 0.058, 0.047, 0.042, 0.03], sides=18, scale_xy=(0.85, 1.0)), WHITE)
    body.add(oriented((0, -0.762, 0.995), (0.046, 0.045, 0.042), pitch=-40), WHITE)            # muzzle
    body.add(oriented((0, -0.735, 0.965), (0.036, 0.04, 0.022), pitch=-40), WHITE)             # lower lip
    for sx in (-1, 1):
        body.add(oriented((sx * 0.052, -0.605, 1.225), (0.022, 0.035, 0.022), pitch=-35), WHITE)  # brow

    fused = body.fuse(voxel=0.0105, smooth=4, smooth_factor=0.5)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * noise.noise(v.co * 40.0) * 0.0015
    fused = cut_stripes(decimate(fused, MAX_TRIS))
    mb = nh.MeshBuilder()
    mb.add(fused)

    # ---- crisp details
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.066, -0.612, 1.205), (0.012, 0.022, 0.017), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((sx * 0.074, -0.62, 1.21), (0.003, 0.004, 0.003), subdivisions=1), EYE_SHINE)
        mb.add(oriented((sx * 0.03, -0.795, 1.005), (0.008, 0.012, 0.018), pitch=-40, roll=sx * 20,
                        segments=8, rings=6), (0.01, 0.01, 0.01))                                  # nostrils

        def ear_color(co, n):
            inner = nh.smoothstep(-0.4, -0.8, n.y)
            tip = nh.smoothstep(1.38, 1.42, co.z)
            band = nh.smoothstep(0.012, 0.0, abs(co.z - 1.33))
            c = nh.lerp(WHITE, BLACK, max(tip, band * (1.0 - inner)))
            return nh.lerp(c, nh.lerp(WHITE, (0.75, 0.70, 0.66), 0.5), inner * (1.0 - tip))
        mb.add(cup_ear((sx * 0.045, -0.535, 1.29), 0.125, 0.04, 0.024, tilt_x=12, splay=sx * 24), ear_color)

        for lx, ly in ((FRONT_X, -0.345), (HIND_X, 0.36)):
            hx = sx * lx * 0.96
            mb.add(nh.tube([(hx, ly + 0.008, 0.062), (hx, ly + 0.002, 0.035), (hx, ly - 0.006, 0.006),
                            (hx, ly - 0.01, 0.0)], [0.026, 0.031, 0.034, 0.03], sides=14), HOOF)

    mb.add(mane_brush(), smooth=False)

    # tail: thin dock hanging from the croup, black tassel
    mb.add(nh.tube([(0, 0.44, 0.94), (0, 0.49, 0.90), (0, 0.515, 0.80), (0, 0.52, 0.70)],
                   [0.03, 0.024, 0.018, 0.016], sides=10), tail_paint)
    mb.add(oriented((0, 0.525, 0.60), (0.03, 0.026, 0.11), deform=lambda v: 1.0 + 0.2 * noise.noise(v * 5.0)), BLACK)

    obj = mb.to_object("PlainsZebra")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "PlainsZebra", ground=(0.55, 0.50, 0.30), views=((35, 25), (-90, 8), (20, 65), (200, 20)))
    if "--render" in sys.argv:
        render_closeups(sys.argv[sys.argv.index("--render") + 1], (0, -0.62, 1.15), 0.7, ((30, 10), (-80, 5)))
