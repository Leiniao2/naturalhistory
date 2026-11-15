"""
Procedural Komodo dragon (Varanus komodoensis) for the map (large-animal detail).

A big adult monitor striding on sprawled, heavily muscled legs with the body held
off the ground: one seamless fused body (long flat head with a rounded snout, a
long thick neck with a loose throat pouch, a broad heavy torso with a sagging
belly, and the long muscular tail, laterally flattened toward the tip, swept round
to one side so the animal stays compact on its tile). The surface is sculpted by
displacement into loose, wrinkled skin: transverse folds across the neck and
throat, creases where the legs meet the body, long folds low on the flanks and a
fine net of wrinkles all over, then repainted procedurally in earthy grey-brown
with a darker back, faint rust and ochre mottling, small bead-like scales picked
out as speckles, and a paler belly.
Crisp details on top: the long forked yellow tongue flicking out of the mouth,
small dark eyes under the brows, nostrils near the snout tip, and five toes on
each foot with strong curved dark claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/varanus_komodoensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/KomodoDragon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

NAME = "KomodoDragon"
VOXEL = 0.016
MAX_TRIS = 22000

BASE = (0.47, 0.42, 0.34)        # earthy grey-brown
BACK = (0.37, 0.33, 0.27)
LIGHT = (0.60, 0.55, 0.45)
RUST = (0.55, 0.40, 0.27)
OCHRE = (0.62, 0.53, 0.35)
BELLY = (0.64, 0.58, 0.47)
HEAD = (0.50, 0.46, 0.37)
CREASE = (0.22, 0.19, 0.15)
LIP = (0.66, 0.60, 0.48)
TONGUE = (0.93, 0.78, 0.22)
TONGUE_TIP = (0.85, 0.62, 0.16)
EYE = (0.05, 0.04, 0.03)
EYE_RIM = (0.30, 0.26, 0.20)
NOSTRIL = (0.06, 0.05, 0.04)
TOE = (0.42, 0.38, 0.31)
CLAW = (0.10, 0.09, 0.08)
CLAW_TIP = (0.30, 0.28, 0.24)

SNOUT_Y = -1.20
MOUTH_Z = 0.302
NECK_Y0, NECK_Y1 = -0.90, -0.60
BODY_Z = 0.37

# tail centre line: from the hips straight back, then swept round to the right
TAIL_PTS = [Vector(p) for p in (
    (0.0, 0.16, 0.305), (0.01, 0.40, 0.280), (0.08, 0.64, 0.245), (0.22, 0.84, 0.205),
    (0.42, 0.96, 0.180), (0.64, 0.98, 0.160), (0.84, 0.91, 0.145), (0.98, 0.80, 0.135),
)]


def catmull_rom(pts, n=10):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


TAIL = catmull_rom(TAIL_PTS, 10)
TAIL_LEN = [0.0]
for _a, _b in zip(TAIL, TAIL[1:]):
    TAIL_LEN.append(TAIL_LEN[-1] + (_b - _a).length)


def tail_radius(s):
    t = s / TAIL_LEN[-1]
    return 0.150 * (1.0 - t) ** 1.15 + 0.020 * t


def tail_param(co):
    best, bi = 1e9, 0
    for i, p in enumerate(TAIL):
        d = (p - co).length_squared
        if d < best:
            best, bi = d, i
    return TAIL_LEN[bi], math.sqrt(best)


# ---------------------------------------------------------------- fused body parts

LEGS = []   # (side, front?, shoulder, elbow, wrist, palm, forward)


def legs():
    for sx in (1, -1):
        LEGS.append((sx, True,
                     Vector((sx * 0.14, -0.56, 0.29)), Vector((sx * 0.33, -0.53, 0.215)),
                     Vector((sx * 0.40, -0.62, 0.065)), Vector((sx * 0.42, -0.67, 0.022)),
                     Vector((sx * 0.40, -1.0, 0)).normalized()))
        LEGS.append((sx, False,
                     Vector((sx * 0.14, 0.12, 0.29)), Vector((sx * 0.37, 0.05, 0.25)),
                     Vector((sx * 0.44, 0.17, 0.068)), Vector((sx * 0.47, 0.23, 0.022)),
                     Vector((sx * 0.55, -0.8, 0)).normalized()))


def body_parts():
    parts = []
    # neck -> shoulders -> torso -> hips: one wide, flattened tube
    spine = [(0, -0.92, 0.330), (0, -0.80, 0.335), (0, -0.66, 0.330), (0, -0.50, 0.322),
             (0, -0.30, 0.318), (0, -0.10, 0.316), (0, 0.06, 0.312), (0, 0.20, 0.305)]
    radii = [0.090, 0.110, 0.140, 0.175, 0.205, 0.205, 0.180, 0.155]
    parts.append(nh.tube(spine, radii, sides=24, scale_xy=(1.0, 0.72)))
    # heavy sagging belly between the legs
    parts.append(nh.uv_ellipsoid((0, -0.22, 0.24), (0.175, 0.34, 0.085), 20, 12))
    # long flat head, rounded snout, bulging jaw muscles and brows
    parts.append(nh.uv_ellipsoid((0, -1.00, 0.322), (0.076, 0.175, 0.050), 20, 12,
                                 deform=lambda v: 1.0 - 0.18 * max(0.0, v.z) ** 2))
    parts.append(nh.uv_ellipsoid((0, -1.115, 0.306), (0.050, 0.088, 0.033), 16, 10))
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid((sx * 0.050, -0.90, 0.300), (0.052, 0.090, 0.052), 14, 10))
        parts.append(nh.uv_ellipsoid((sx * 0.044, -1.025, 0.350), (0.024, 0.050, 0.012), 12, 8))
    # loose throat pouch and the folds under the neck
    parts.append(nh.uv_ellipsoid((0, -0.86, 0.250), (0.085, 0.14, 0.055), 16, 10))
    # sprawled, heavily muscled legs
    legs()
    for sx, front, sh, el, wr, palm, fwd in LEGS:
        r0, r1, r2 = (0.085, 0.068, 0.052) if front else (0.10, 0.078, 0.056)
        parts.append(nh.tube([sh, sh.lerp(el, 0.5) + Vector((0, 0, 0.01)), el, el.lerp(wr, 0.5), wr],
                             [r0, r0 * 0.92, r1, r1 * 0.85, r2], sides=14))
        mid = sh.lerp(el, 0.55)
        if front:
            parts.append(nh.uv_ellipsoid(mid, (0.09, 0.075, 0.075), 14, 10))
        else:
            parts.append(nh.uv_ellipsoid(mid + Vector((-sx * 0.03, 0.02, 0.0)), (0.13, 0.10, 0.095), 14, 10))
        parts.append(nh.uv_ellipsoid(el.lerp(wr, 0.3), (0.06, 0.06, 0.07), 12, 8))
        parts.append(nh.uv_ellipsoid(palm, (0.062, 0.070, 0.026), 12, 8))
    # long, thick, muscular tail, laterally flattened toward the tip
    rad = [tail_radius(s) for s in TAIL_LEN]
    parts.append(nh.tube(TAIL, rad, sides=20, scale_xy=(0.82, 0.92)))
    return parts


def drop_islands(bm, min_verts=200):
    """Removes stray voxel fragments."""
    seen = set()
    for start in list(bm.verts):
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


# ---------------------------------------------------------------- sculpt + paint

def ridged(co, f):
    """Sharp creases where the noise crosses zero: a net of skin wrinkles."""
    return (1.0 - min(1.0, abs(noise.noise(co * f)) * 3.0)) ** 3


def mouth_z(y):
    # nearly straight lip line that drops a little and curls up at the back of the jaw
    t = (y - SNOUT_Y) / 0.34
    return MOUTH_Z - 0.006 * math.sin(min(1.0, max(0.0, t)) * math.pi) + 0.010 * nh.smoothstep(0.7, 1.0, t)


def sculpt(bm):
    bm.normal_update()
    disp, paint = {}, {}
    for v in bm.verts:
        co, n = v.co.copy(), v.normal.copy()
        y = co.y
        d = 0.0
        # fine net of wrinkles everywhere and pebbly bead scales
        d -= 0.0045 * ridged(co, 11.0)
        d += 0.0016 * noise.noise(co * 70.0)
        # transverse folds across the neck and throat, deepest underneath
        if NECK_Y0 - 0.05 < y < NECK_Y1 + 0.05:
            w = nh.smoothstep(NECK_Y0 - 0.05, NECK_Y0 + 0.04, y) * nh.smoothstep(NECK_Y1 + 0.05, NECK_Y1 - 0.04, y)
            fold = math.sin((y + 0.012 * noise.noise(co * 9.0)) / 0.034 * math.pi) ** 8
            d -= 0.010 * fold * w * (0.6 + 0.4 * max(0.0, -n.z))
        # long loose folds low on the flanks of the body
        on_body = -0.62 < y < 0.16 and abs(n.x) > 0.3 and co.z > 0.14
        if on_body:
            fold = math.sin((co.z + 0.01 * noise.noise(co * 6.0)) / 0.028 * math.pi) ** 6
            d -= 0.006 * fold * nh.smoothstep(0.33, 0.22, co.z)
        # creases round the shoulders and hips
        for sx, front, sh, el, wr, palm, fwd in LEGS:
            dd = (co - sh).length
            if dd < 0.2:
                ring = math.sin(dd / 0.04 * math.pi) ** 6
                d -= 0.006 * ring * nh.smoothstep(0.2, 0.08, dd)
        # lip groove along the side of the head
        on_head = y < -0.84
        mz = mouth_z(y)
        lip = 0.0
        if on_head and (abs(co.x) > 0.018 or y < SNOUT_Y + 0.03):
            lip = max(0.0, 1.0 - abs(co.z - mz) / 0.013) * nh.smoothstep(-0.84, -0.88, y)
            d -= 0.008 * lip
        disp[v] = n * d

        # ---- colour
        s, td = tail_param(co)
        on_tail = y > 0.18 and td < tail_radius(s) * 1.4 + 0.03
        coarse = noise.noise(co * 4.0 + Vector((1.3, 2.1, 0.7)))
        top = nh.smoothstep(-0.1, 0.8, n.z)
        c = nh.lerp(BASE, BACK, top * 0.8)
        c = nh.lerp(c, RUST, 0.45 * nh.smoothstep(0.1, 0.6, coarse))
        c = nh.lerp(c, OCHRE, 0.35 * nh.smoothstep(0.2, 0.7, noise.noise(co * 7.0 + Vector((5, 1, 2)))))
        if on_head:
            c = nh.lerp(c, HEAD, 0.55)
            if co.z < mz:
                c = nh.lerp(c, LIP, 0.75)
            if lip > 0.0:
                c = nh.lerp(c, CREASE, 0.9 * lip)
        if on_tail:
            # faint darker bands down the tail
            band = 0.5 + 0.5 * math.sin(s / 0.16 * math.tau)
            c = nh.lerp(c, BACK, 0.3 * nh.smoothstep(0.6, 1.0, band))
        c = nh.lerp(c, BELLY, nh.smoothstep(-0.25, -0.75, n.z))
        # bead-like scales: light and dark speckles, dark in the creases
        sp = noise.noise(co * 95.0)
        if sp > 0.35:
            c = nh.lerp(c, LIGHT, 0.45)
        elif sp < -0.4:
            c = nh.lerp(c, CREASE, 0.3)
        c = nh.lerp(c, CREASE, 0.55 * min(1.0, -d / 0.009) if d < 0 else 0.0)
        paint[v] = c

    for v, dv in disp.items():
        v.co += dv
    bm.normal_update()
    col = bm.loops.layers.color.get("Col") or bm.loops.layers.color.new("Col")
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            c = paint[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


def decimate(bm, max_tris):
    """Collapse-decimates the sculpted body down to about max_tris (colours follow the verts)."""
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    n = sum(len(p.vertices) - 2 for p in mesh.polygons)
    if n > max_tris:
        dec = obj.modifiers.new("decimate", "DECIMATE")
        dec.decimate_type = "COLLAPSE"
        dec.ratio = max_tris / n
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    for f in out.faces:
        f.smooth = True
    return out


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def ray(self, origin, direction):
        hit, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return hit, normal

    def snap(self, p):
        hit, normal, _i, _d = self.tree.find_nearest(Vector(p))
        return hit, normal


def tongue(mb):
    """Long forked tongue flicking out of the front of the closed mouth."""
    base = Vector((0, SNOUT_Y + 0.03, MOUTH_Z - 0.006))
    fork = Vector((0, SNOUT_Y - 0.09, MOUTH_Z - 0.022))
    mb.add(nh.tube([base, Vector((0, SNOUT_Y - 0.04, MOUTH_Z - 0.016)), fork],
                   [0.011, 0.0095, 0.008], sides=8, scale_xy=(1.0, 0.6)), TONGUE)
    for sx in (1, -1):
        tip = fork + Vector((sx * 0.030, -0.06, -0.008 + 0.012 * sx))
        mid = fork.lerp(tip, 0.5) + Vector((sx * 0.004, 0, 0))
        mb.add(nh.tube([fork, mid, tip], [0.0075, 0.0055, 0.0], sides=6, scale_xy=(1.0, 0.6)),
               lambda co, n, f=fork: nh.lerp(TONGUE, TONGUE_TIP, nh.smoothstep(0.03, 0.08, (co - f).length)))


def eyes(mb, surf):
    for sx in (1, -1):
        look = Vector((sx, -0.3, 0.25)).normalized()
        hit, nrm = surf.ray(Vector((sx * 0.3, -1.045, 0.336)), Vector((-sx, 0, 0)))
        if hit is None:
            continue
        mb.add(nh.ellipsoid(hit - nrm * 0.008, (0.016, 0.014, 0.011), subdivisions=2), EYE_RIM)
        mb.add(nh.ellipsoid(hit - nrm * 0.002, (0.010, 0.0095, 0.0085), subdivisions=2),
               lambda co, n, lk=look, h=hit: (0.40, 0.28, 0.10) if (co - h).normalized().dot(lk) < 0.75 else EYE)


def nostrils(mb, surf):
    for sx in (1, -1):
        hit, nrm = surf.ray(Vector((sx * 0.3, SNOUT_Y + 0.04, 0.312)), Vector((-sx, 0, 0)))
        if hit is not None:
            mb.add(nh.ellipsoid(hit, (0.004, 0.007, 0.0035), subdivisions=1), NOSTRIL)


def feet(mb):
    for sx, front, sh, el, wr, palm, fwd in LEGS:
        out = Vector((sx, 0, 0))
        lengths = (0.055, 0.085, 0.10, 0.095, 0.065) if front else (0.06, 0.09, 0.11, 0.12, 0.075)
        spread = 1.5
        for k, L in enumerate(lengths):
            a = (k / 4 - 0.5) * spread * (-sx)
            d = (fwd * math.cos(a) + out * math.sin(a) * 0.9).normalized()
            p0 = palm + d * 0.03 + Vector((0, 0, 0.008))
            p1 = p0 + d * L * 0.5 + Vector((0, 0, 0.004))
            p2 = p0 + d * L
            p2.z = 0.014
            mb.add(nh.tube([p0, p1, p2], [0.021, 0.017, 0.013], sides=8), TOE)
            # strong curved claw, hooking down to the ground
            c0 = p2 - d * 0.004 + Vector((0, 0, 0.004))
            c1 = p2 + d * 0.022 + Vector((0, 0, 0.004))
            c2 = p2 + d * 0.040 + Vector((0, 0, -0.012))
            mb.add(nh.tube([c0, c1, c2], [0.010, 0.0075, 0.0], sides=7),
                   lambda co, n, b=c0: nh.lerp(CLAW, CLAW_TIP, nh.smoothstep(0.02, 0.045, (co - b).length)))


# ---------------------------------------------------------------- build / preview

def build():
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, BASE)
    fused = body.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    drop_islands(fused)
    fused = sculpt(fused)
    fused = decimate(fused, MAX_TRIS)
    surf = Surface(fused)
    mb = nh.MeshBuilder()
    mb.add(fused)
    tongue(mb)
    eyes(mb, surf)
    nostrils(mb, surf)
    feet(mb)
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


def closeup(path, target, dist, az, el, lens=60):
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.lens = lens
    a, e = math.radians(az), math.radians(el)
    target = Vector(target)
    cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.48, 0.42, 0.32), views=((35, 25), (-90, 8), (25, 62)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0.0, -1.0, 0.28), 0.9, 35, 15)
        closeup(out.with_name(out.stem + "_head1.png"), (0.0, -1.0, 0.28), 0.8, -75, 6)
