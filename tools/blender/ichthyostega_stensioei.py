"""
Procedural Ichthyostega stensioei (Late Devonian early tetrapod, ~1.5 m) for the map.

A heavy, low tetrapod hauled out on a mud bank: the chest is propped up on stout,
sprawling forelimbs with short broad hands, while the paddle-like hind limbs trail
backward like flippers. The body is lofted as one tube from the broad, flat,
parabolic snout (the skull is wide and flat like a crocodile's or a giant
salamander's, with the eyes set high and far back) through a deep barrel chest to
a long, laterally flattened fish-like tail. Limbs, feet and the raised orbits are
fused onto it, then the surface is sculpted by displacement: the heavy, broad,
overlapping ribs show as slanted shingle-like ridges down the flanks, the skull
roof is pitted dermal bone, the lip line is grooved and the skin is finely scaly.
Repainted procedurally: dark olive-brown back with blotches, ochre highlights on
the rib ridges, a pale yellow-grey belly.
Crisp details on top: the tail's fin fold (above and below, stiffened by fin
rays), seven webbed digits on each hind paddle, stubby toes on the hands, small
conical teeth along the upper jaw, eyes and nostrils.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ichthyostega_stensioei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ichthyostega.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

NAME = "Ichthyostega"
VOXEL = 0.0235

# Body profile along Y (snout at -Y): half-width, half-height, centre height.
KEY_Y = [-1.00, -0.97, -0.92, -0.84, -0.76, -0.68, -0.60, -0.50, -0.30, -0.05, 0.18, 0.34, 0.50, 0.68, 0.84, 1.00]
KEY_W = [0.050, 0.080, 0.112, 0.150, 0.178, 0.190, 0.168, 0.198, 0.228, 0.222, 0.170, 0.115, 0.076, 0.048, 0.030, 0.010]
KEY_H = [0.032, 0.040, 0.050, 0.058, 0.066, 0.074, 0.088, 0.112, 0.130, 0.124, 0.108, 0.094, 0.080, 0.062, 0.042, 0.012]
KEY_Z = [0.170, 0.172, 0.176, 0.182, 0.190, 0.198, 0.205, 0.205, 0.185, 0.158, 0.132, 0.110, 0.088, 0.068, 0.056, 0.048]
SNOUT = -1.00
HEAD_BACK = -0.66

# Palette
BACK = (0.33, 0.31, 0.19)        # dark olive-brown
BACK_LIGHT = (0.47, 0.43, 0.26)
BLOTCH = (0.19, 0.17, 0.10)
FLANK = (0.50, 0.45, 0.28)
RIB = (0.64, 0.55, 0.33)         # ochre highlights on the rib ridges
BELLY = (0.80, 0.75, 0.56)       # pale yellow-grey
SKULL = (0.40, 0.37, 0.23)
LIP = (0.10, 0.09, 0.06)
FIN = (0.44, 0.39, 0.24)
FIN_RAY = (0.24, 0.21, 0.13)
FIN_EDGE = (0.58, 0.52, 0.34)
FOOT = (0.42, 0.38, 0.24)
TOOTH = (0.86, 0.82, 0.68)
EYE = (0.62, 0.50, 0.16)
PUPIL = (0.02, 0.02, 0.015)


def interp(ys, vs, y):
    if y <= ys[0]:
        return vs[0]
    if y >= ys[-1]:
        return vs[-1]
    for i in range(len(ys) - 1):
        if ys[i] <= y <= ys[i + 1]:
            t = (y - ys[i]) / (ys[i + 1] - ys[i])
            t = t * t * (3 - 2 * t) * 0.5 + t * 0.5  # soften the kinks
            return vs[i] + (vs[i + 1] - vs[i]) * t
    return vs[-1]


def cx(y):
    """Gentle lateral curve: the tail sweeps off to one side."""
    s = max(0.0, (y - 0.15) / 0.85)
    return 0.16 * s * s


def W(y):
    return interp(KEY_Y, KEY_W, y)


def H(y):
    return interp(KEY_Y, KEY_H, y)


def CZ(y):
    return interp(KEY_Y, KEY_Z, y)


def section_power(y):
    if y < HEAD_BACK:
        return 3.2   # flat-topped, flat-bottomed skull
    if y > 0.3:
        return 2.0   # oval, laterally flattened tail
    return 2.4


def ring_point(y, a, w, h, z, p):
    u, v = math.cos(a), math.sin(a)
    ex = 2.0 / p
    px = cx(y) + w * math.copysign(abs(u) ** ex, u)
    pz = z + h * math.copysign(abs(v) ** ex, v) * (0.8 if v < 0 and y < -0.55 else 1.0)
    return Vector((px, y, pz))


def body_loft(sides=44):
    """One closed tube from the rounded snout tip to the tail tip."""
    bm = bmesh.new()
    rings = []
    r = W(SNOUT)
    tip_y = SNOUT - r * 0.6
    rings.append([bm.verts.new(Vector((cx(tip_y), tip_y, CZ(SNOUT) - 0.004)))])
    for phi_deg in (70, 50, 30, 12):         # rounded parabolic snout tip
        phi = math.radians(phi_deg)
        y = SNOUT - r * 0.6 * math.sin(phi)
        rings.append([bm.verts.new(ring_point(y, k / sides * math.tau, r * math.cos(phi),
                                              H(SNOUT) * math.cos(phi) ** 0.45, CZ(SNOUT), 3.2))
                      for k in range(sides)])
    y = SNOUT
    while y < 1.0:
        rings.append([bm.verts.new(ring_point(y, k / sides * math.tau, W(y), H(y), CZ(y), section_power(y)))
                      for k in range(sides)])
        y += 0.016
    rings.append([bm.verts.new(Vector((cx(1.02), 1.02, CZ(1.0))))])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[(k + 1) % sides], b[k]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


# ---------------------------------------------------------------- limbs

HAND_TOES = []      # (base, direction) of the stubby fingers
PADDLES = []        # (ankle, side) of the hind paddles


def limbs(body):
    for s in (-1, 1):
        # stout sprawling forelimb: humerus straight out, elbow bent, forearm down to a broad hand
        sh = Vector((s * 0.17, -0.46, 0.17))
        elbow = Vector((s * 0.34, -0.43, 0.15))
        wrist = Vector((s * 0.35, -0.50, 0.045))
        body.add(nh.tube([sh, elbow], [0.075, 0.06], sides=16), FLANK)
        body.add(nh.ellipsoid(elbow, (0.06, 0.06, 0.06), subdivisions=2), FLANK)
        body.add(nh.tube([elbow, wrist], [0.058, 0.048], sides=14), FLANK)
        body.add(nh.ellipsoid((s * 0.27, -0.45, 0.175), (0.08, 0.06, 0.055), subdivisions=3), FLANK)  # biceps
        hand = Vector((s * 0.37, -0.55, 0.022))
        body.add(nh.ellipsoid(hand, (0.065, 0.06, 0.024), subdivisions=3), FOOT)
        for a in (-0.6, -0.2, 0.2, 0.6):
            d = Vector((math.sin(a) + s * 0.35, -math.cos(a), 0)).normalized()
            HAND_TOES.append((hand + d * 0.045 + Vector((0, 0, -0.004)), d))
        # paddle-like hind limb trailing backwards
        hip = Vector((s * 0.13, 0.20, 0.13))
        knee = Vector((s * 0.25, 0.27, 0.08))
        ankle = Vector((s * 0.29, 0.37, 0.04))
        body.add(nh.tube([hip, knee], [0.06, 0.048], sides=14), FLANK)
        body.add(nh.tube([knee, ankle], [0.046, 0.036], sides=12, scale_xy=(1.0, 0.7)), FLANK)
        body.add(nh.ellipsoid((s * 0.16, 0.22, 0.12), (0.075, 0.08, 0.065), subdivisions=3), FLANK)  # thigh
        body.add(nh.ellipsoid(ankle + Vector((s * 0.01, 0.04, -0.016)), (0.05, 0.06, 0.018), subdivisions=3), FOOT)
        PADDLES.append((ankle + Vector((s * 0.01, 0.06, -0.02)), s))


def head_mounds(body):
    for s in (-1, 1):
        body.add(nh.ellipsoid((s * 0.068, -0.76, CZ(-0.76) + H(-0.76) - 0.005), (0.035, 0.04, 0.024),
                              subdivisions=3), SKULL)   # raised orbits set high and far back


# ---------------------------------------------------------------- sculpt / paint

def frac(x):
    return x - math.floor(x)


def rib_field(co):
    """Overlapping rib ridges on the flanks: 0..1 height and the 'shadowed' trailing edge."""
    y = co.y
    if not (-0.48 < y < 0.16):
        return 0.0, 0.0
    # ribs slant backward going down the flank
    z_rel = (co.z - CZ(y)) / max(H(y), 1e-3)
    u = (y + 0.05 * z_rel + 0.04 * z_rel * z_rel + 0.48) / 0.064
    t = frac(u)
    # shingle profile: slow rise to the crest, sharp drop where the next rib overlaps it
    h = nh.smoothstep(0.0, 0.62, t) * (1.0 - nh.smoothstep(0.66, 1.0, t))
    fade = nh.smoothstep(-0.48, -0.42, y) * (1.0 - nh.smoothstep(0.06, 0.14, y))
    fade *= nh.smoothstep(-0.8, -0.35, z_rel) * (1.0 - nh.smoothstep(0.55, 0.9, z_rel))
    edge = nh.smoothstep(0.75, 0.88, t) * (1.0 - nh.smoothstep(0.92, 1.0, t))
    return h * fade, edge * fade


def jaw_z(y):
    return CZ(y) - 0.25 * H(y)


def lip_dist(co):
    y = co.y
    if y > HEAD_BACK + 0.02 or abs(co.x - cx(y)) < 0.02:
        return 1.0
    return min(1.0, abs(co.z - jaw_z(y)) / 0.008)


def sculpt(bm):
    bm.normal_update()
    col = bm.loops.layers.color.get("Col") or bm.loops.layers.color.new("Col")
    disp, paint = {}, {}
    for vert in bm.verts:
        co, n = vert.co.copy(), vert.normal.copy()
        y = co.y
        rib, edge = rib_field(co)
        coarse = noise.noise(co * 7.0 + Vector((2.3, 0.4, 1.1)))
        fine = noise.noise(co * 55.0)
        d = 0.016 * rib - 0.004 * edge + 0.0018 * fine
        on_skull = y < HEAD_BACK and n.z > 0.5
        if on_skull:                                   # pitted dermal bone of the skull roof
            dist, _p = noise.voronoi(co * 40.0, distance_metric="DISTANCE")
            d -= 0.004 * (1.0 - nh.smoothstep(0.0, 0.35, dist[0]))
        ld = lip_dist(co)
        d -= 0.006 * (1.0 - ld)
        disp[vert] = n * d

        top = nh.smoothstep(-0.1, 0.65, n.z + 0.15 * coarse)
        belly = nh.smoothstep(-0.35, -0.7, n.z + 0.1 * coarse)
        c = nh.lerp(FLANK, BACK, top)
        c = nh.lerp(c, BACK_LIGHT, 0.35 * max(0.0, noise.noise(co * 16.0)) * top)
        c = nh.lerp(c, BLOTCH, 0.6 * nh.smoothstep(0.15, 0.5, coarse) * top)
        c = nh.lerp(c, RIB, 0.55 * nh.smoothstep(0.4, 0.9, rib))
        c = nh.lerp(c, BLOTCH, 0.6 * edge)
        if on_skull:
            c = nh.lerp(c, SKULL, 0.5)
        if ld < 1.0:
            c = nh.lerp(c, LIP, 0.8 * (1.0 - ld))
        if y < HEAD_BACK and co.z < jaw_z(y) - 0.004 and abs(co.x - cx(y)) > 0.03:
            c = nh.lerp(c, BELLY, 0.5)                 # paler lower jaw
        c = nh.lerp(c, BELLY, belly)
        k = 0.92 + 0.16 * (0.5 + 0.5 * fine)
        paint[vert] = (c[0] * k, c[1] * k, c[2] * k)
    for vert, dv in disp.items():
        vert.co += dv
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            c = paint[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        if loc is None:
            loc, normal, _i, _d = self.tree.find_nearest(Vector(origin))
        return loc, normal


def fin_strip(base_fn, height_fn, y0, y1, steps, thickness, up=1):
    """Thin fin fold rooted along base_fn(y) (inside the tail) and reaching height_fn(y) up
    (or down, up=-1). Returns (bmesh, colour fn) - fin rays darken in radial streaks."""
    bm = bmesh.new()
    rows = []
    for i in range(steps + 1):
        y = y0 + (y1 - y0) * i / steps
        b = base_fn(y)
        h = height_fn(y)
        ray_tilt = Vector((0, 0.45, up))       # rays lean back toward the tail tip
        tip = b + ray_tilt.normalized() * max(h, 0.002)
        x_off = Vector((thickness * 0.5, 0, 0))
        rows.append([bm.verts.new(b - x_off), bm.verts.new(tip - x_off * 0.4),
                     bm.verts.new(tip + x_off * 0.4), bm.verts.new(b + x_off)])
    for a, b in zip(rows, rows[1:]):
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, n):
        y = co.y
        rel = abs(co.z - base_fn(y).z) / max(height_fn(y), 0.004)
        ray = 1.0 - nh.smoothstep(0.1, 0.3, abs(frac((co.y - 0.45 * abs(co.z - base_fn(y).z)) / 0.022) - 0.5))
        c = nh.lerp(FIN, FIN_RAY, 0.7 * ray * nh.smoothstep(0.1, 0.3, rel))
        return nh.lerp(c, FIN_EDGE, nh.smoothstep(0.75, 1.0, rel))
    return bm, col


def fins(mb):
    def top(y):
        return Vector((cx(y), y, CZ(y) + H(y) * 0.75))

    def bottom(y):
        return Vector((cx(y), y, CZ(y) - H(y) * 0.75))

    def dorsal_h(y):
        return 0.07 * nh.smoothstep(0.28, 0.66, y) * (1.0 - nh.smoothstep(0.78, 0.97, y)) + 0.002

    def ventral_h(y):
        return 0.045 * nh.smoothstep(0.5, 0.76, y) * (1.0 - nh.smoothstep(0.82, 0.97, y)) + 0.002

    bm, col = fin_strip(top, dorsal_h, 0.26, 0.97, 60, 0.008, up=1)
    mb.add(bm, col)
    bm, col = fin_strip(bottom, ventral_h, 0.48, 0.97, 44, 0.008, up=-1)
    mb.add(bm, col)


def paddle(mb, ankle, s):
    """Seven long digits fanned backward and outward, joined by webbing."""
    tips = []
    for k in range(7):
        a = math.radians(-12 + 12 * k) * s           # fan from straight back toward the outside
        d = Vector((math.sin(a), math.cos(a), 0.0))
        L = 0.09 + 0.05 * math.sin(math.pi * (k + 0.5) / 7)
        base = ankle + d * 0.02
        tip = base + d * L + Vector((0, 0, -0.008))
        mb.add(nh.tube([base, base + d * L * 0.5, tip], [0.011, 0.009, 0.005], sides=8), FOOT)
        tips.append(tip)
    outline = [ankle + Vector((0, -0.01, 0))] + [t - (t - ankle).normalized() * 0.006 for t in tips]
    mb.add(nh.flat_panel([tuple(p + Vector((0, 0, -0.002))) for p in outline], thickness=0.006),
           nh.lerp(FOOT, BELLY, 0.25))


def teeth(mb, surf):
    y = -0.985
    while y < -0.72:
        for s in (-1, 1):
            w = W(y)
            z = jaw_z(y) + 0.004
            loc, nrm = surf.hit((cx(y) + s * (w + 0.1), y, z), (-s, 0, 0))
            if loc is not None:
                out = Vector((nrm.x, nrm.y, 0)).normalized() if abs(nrm.x) + abs(nrm.y) > 1e-3 else Vector()
                base = loc - out * 0.003
                mb.add(nh.tube([base, base + Vector((0, 0, -0.014)) + out * 0.002], [0.0045, 0.0], sides=6),
                       TOOTH)
        y += 0.024
    for a in (-0.7, -0.35, 0.0, 0.35, 0.7):             # around the snout tip
        d = Vector((math.sin(a), -math.cos(a), 0))
        y0 = SNOUT - 0.012
        loc, nrm = surf.hit((cx(y0) + d.x * 0.3, y0 + d.y * 0.3, jaw_z(y0) + 0.004), -d)
        if loc is not None:
            mb.add(nh.tube([loc - d * 0.003, loc + Vector((0, 0, -0.013))], [0.0045, 0.0], sides=6), TOOTH)


def eyes(mb, surf):
    for s in (-1, 1):
        # eyes on top of the skull, looking up and out from the raised orbits
        loc, nrm = surf.hit((s * 0.072, -0.765, 0.5), (0, 0, -1))
        look = (Vector((0, 0, 1)) + Vector((s * 0.7, -0.25, 0.0))).normalized()
        c = loc - look * 0.007
        mb.add(nh.ellipsoid(c, (0.018, 0.018, 0.016), subdivisions=3), EYE)
        mb.add(nh.ellipsoid(c + look * 0.012, (0.008, 0.008, 0.008), subdivisions=2), PUPIL)
        # nostrils near the front edge of the snout
        loc, _n = surf.hit((s * 0.045, SNOUT + 0.03, 0.5), (0, 0, -1))
        if loc is not None:
            mb.add(nh.ellipsoid(loc + Vector((0, 0, 0.001)), (0.007, 0.006, 0.004), subdivisions=2), PUPIL)


def hand_toes(mb):
    for base, d in HAND_TOES:
        mb.add(nh.tube([base, base + d * 0.03 + Vector((0, 0, -0.006))], [0.014, 0.008], sides=8), FOOT)


def refine_flanks(bm):
    """Doubles the resolution over the ribcage so the rib ridges displace cleanly."""
    def in_ribs(v):
        y = v.co.y
        return -0.5 < y < 0.18 and -0.75 * H(y) < v.co.z - CZ(y) < 0.9 * H(y) and abs(v.co.x - cx(y)) > 0.08
    edges = [e for e in bm.edges if in_ribs(e.verts[0]) or in_ribs(e.verts[1])]
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces)


def drop_islands(bm, min_verts=200):
    """Removes stray voxel fragments (e.g. where the tail tip gets thinner than a voxel)."""
    seen = set()
    for start in bm.verts:
        if start in seen:
            continue
        part, stack = [], [start]
        seen.add(start)
        while stack:
            v = stack.pop()
            part.append(v)
            for e in v.link_edges:
                o = e.other_vert(v)
                if o not in seen:
                    seen.add(o)
                    stack.append(o)
        if len(part) < min_verts:
            bmesh.ops.delete(bm, geom=part, context="VERTS")


def build():
    HAND_TOES.clear()
    PADDLES.clear()
    body = nh.MeshBuilder()
    body.add(body_loft(), FLANK)
    limbs(body)
    head_mounds(body)
    fused = body.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    drop_islands(fused)
    refine_flanks(fused)
    fused = sculpt(fused)

    surf = Surface(fused)
    mb = nh.MeshBuilder()
    fins(mb)
    for ankle, s in PADDLES:
        paddle(mb, ankle, s)
    hand_toes(mb)
    teeth(mb, surf)
    eyes(mb, surf)
    mb.add(fused)
    obj = mb.to_object(NAME, roughness=0.5)
    nh.ground_to_zero(obj)
    return obj


def render_extra(obj, path):
    """Head close-up, using the camera and light set up by nh.render_preview."""
    scene = bpy.context.scene
    cam = scene.camera
    target = Vector((0, -0.8, 0.2))
    for i, (az, el, dist) in enumerate(((38, 25, 0.9), (-70, 12, 0.85))):
        a, e = math.radians(az), math.radians(el)
        cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        out = Path(path)
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, NAME)
    if "--render" in argv:
        path = argv[argv.index("--render") + 1]
        nh.render_preview(obj, path, ground=(0.36, 0.34, 0.25), views=((35, 25), (-90, 8), (25, 62)))
        render_extra(obj, path)


if __name__ == "__main__":
    main()
