"""
Procedural low-poly Hylonomus lyelli (Late Carboniferous, the earliest known reptile,
about 20 cm long) for map colonies (Ground style).

A small, slender, lizard-like animal caught mid-stride on its sprawling legs: one
seamless fused body (a short, pointed head with a slightly raised brow over the eyes,
a thin neck, a long slim torso and a very long tapering tail, a bit over half the
total length, curving off to one side), with the upper arms and thighs held out
sideways and the lower legs angled down to the ground. Repainted procedurally:
warm brown back with a darker, broken stripe down each side of the spine and pale
speckles, a lighter flank and a cream belly, dark bands on the tail, a dark mouth line.
Crisp details on top: eyes, nostrils, a row of small sharp teeth along the upper jaw,
and five long, clawed, splayed toes on every foot.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/hylonomus_lyelli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hylonomus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

NAME = "Hylonomus"

BACK = (0.36, 0.25, 0.14)          # warm brown
STRIPE = (0.17, 0.11, 0.07)
FLANK = (0.54, 0.41, 0.25)
BELLY = (0.82, 0.74, 0.56)
SPECK = (0.80, 0.70, 0.48)
TAIL_BAND = (0.20, 0.13, 0.08)
HEAD = (0.42, 0.30, 0.18)
LIP = (0.16, 0.11, 0.08)
TOE = (0.44, 0.32, 0.20)
CLAW = (0.12, 0.10, 0.08)
TOOTH = (0.94, 0.92, 0.84)
IRIS = (0.70, 0.46, 0.14)
PUPIL = (0.02, 0.02, 0.02)

HEAD_Y = -0.43                    # middle of the head
BODY_Z = 0.070                    # torso centre height (held off the ground by the legs)

# spine centre line: snout -> neck -> torso -> long tail curving to the left
SPINE_PTS = [Vector(p) for p in (
    (0.0, -0.53, 0.078), (0.0, -0.44, 0.084), (0.0, -0.36, 0.078), (0.004, -0.28, BODY_Z),
    (0.008, -0.10, BODY_Z), (0.004, 0.06, 0.066), (-0.01, 0.20, 0.050), (-0.05, 0.36, 0.036),
    (-0.12, 0.50, 0.026), (-0.22, 0.60, 0.018), (-0.34, 0.65, 0.013), (-0.46, 0.64, 0.010),
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


SPINE = catmull_rom(SPINE_PTS, 8)
SPINE_LEN = [0.0]
for _a, _b in zip(SPINE, SPINE[1:]):
    SPINE_LEN.append(SPINE_LEN[-1] + (_b - _a).length)
TAIL_START = 0.62  # arc length where the tail starts (behind the hips)


def radius_at(s):
    """Half-width of the body along the spine (arc length s)."""
    key = [(0.0, 0.004), (0.03, 0.017), (0.08, 0.028), (0.12, 0.024), (0.17, 0.021),   # head, neck
           (0.24, 0.036), (0.40, 0.042), (0.56, 0.034), (0.64, 0.026), (0.80, 0.017),   # torso
           (1.00, 0.012), (1.20, 0.008), (SPINE_LEN[-1], 0.0042)]
    for (s0, r0), (s1, r1) in zip(key, key[1:]):
        if s <= s1:
            t = (s - s0) / max(s1 - s0, 1e-6)
            t = t * t * (3 - 2 * t)
            return r0 + (r1 - r0) * t
    return key[-1][1]


def spine_param(co):
    """(arc length, distance from the spine) of the nearest centre-line point."""
    best, bi = 1e9, 0
    for i, p in enumerate(SPINE):
        d = (p - co).length_squared
        if d < best:
            best, bi = d, i
    return SPINE_LEN[bi], math.sqrt(best), bi


# ---------------------------------------------------------------- fused body

def legs():
    """(shoulder/hip, elbow/knee, wrist/ankle, foot direction) for the four legs, mid-stride:
    left front and right hind forward, the other pair back."""
    out = []
    for sx in (-1, 1):
        fwd_f = -1 if sx < 0 else 1       # stride phase
        sh = Vector((sx * 0.028, -0.27, BODY_Z - 0.004))
        el = Vector((sx * 0.085, -0.27 + 0.025 * fwd_f, BODY_Z + 0.004))
        wr = Vector((sx * 0.105, -0.28 + 0.045 * fwd_f, 0.010))
        out.append((sh, el, wr, Vector((sx * 0.45, -1, 0)).normalized(), 0.0095, False))
        hp = Vector((sx * 0.026, 0.045, BODY_Z - 0.008))
        kn = Vector((sx * 0.10, 0.045 - 0.03 * fwd_f, BODY_Z + 0.006))
        an = Vector((sx * 0.12, 0.06 - 0.05 * fwd_f, 0.011))
        out.append((hp, kn, an, Vector((sx * 0.7, -0.7, 0)).normalized(), 0.0115, True))
    return out


def body_parts():
    parts = []
    radii = [radius_at(s) for s in SPINE_LEN]
    pts = []
    for p, s, r in zip(SPINE, SPINE_LEN, radii):
        pts.append(Vector((p.x, p.y, max(p.z, r * 0.8))))
    # slightly flattened trunk and tail
    parts.append(nh.tube(pts, [max(r, 0.0042) for r in radii], sides=14, scale_xy=(1.0, 0.82)))
    # head: pointed wedge, a little flat on top, brows over the eyes, cheeks
    parts.append(nh.uv_ellipsoid((0, HEAD_Y, 0.084), (0.026, 0.06, 0.018), 16, 10,
                                 deform=lambda v: 1.0 - 0.15 * max(0.0, v.z) ** 2))
    for sx in (-1, 1):
        parts.append(nh.uv_ellipsoid((sx * 0.016, HEAD_Y + 0.008, 0.095), (0.01, 0.016, 0.007), 10, 6))   # brow
        parts.append(nh.uv_ellipsoid((sx * 0.016, HEAD_Y + 0.03, 0.078), (0.015, 0.03, 0.016), 10, 8))    # jowl
    for sh, el, wr, _d, r, hind in legs():
        parts.append(nh.tube([sh, (sh + el) / 2 + Vector((0, 0, 0.004)), el], [r * 1.25, r * 1.1, r * 0.9], sides=8))
        parts.append(nh.tube([el, (el + wr) / 2, wr], [r * 0.85, r * 0.7, r * 0.6], sides=8))
        parts.append(nh.ellipsoid(wr + Vector((0, 0, -0.003)), (r * 0.9, r * 1.1, r * 0.5), subdivisions=2))
        if hind:
            parts.append(nh.ellipsoid((sh + el) / 2, (r * 1.7, r * 1.4, r * 1.3), subdivisions=2))   # thigh
    return parts


# ---------------------------------------------------------------- paint

def paint(co, n):
    s, d, i = spine_param(co)
    r = max(radius_at(s), 1e-3)
    p = SPINE[i]
    up = (co.z - p.z) / r
    fine = noise.noise(co * 160.0)
    coarse = noise.noise(co * 25.0)
    c = nh.lerp(FLANK, BACK, nh.smoothstep(-0.2, 0.6, up + 0.2 * coarse))
    if d > r * 1.6 and s > 0.15:  # legs: plain, darker on top
        c = nh.lerp(FLANK, BACK, nh.smoothstep(-0.3, 0.6, n.z))
    else:
        if s < 0.12:
            c = nh.lerp(c, HEAD, 0.5 * nh.smoothstep(0.0, 0.5, up))
            # mouth line along the side of the head
            if abs(co.x) > 0.008 and abs(co.z - 0.079) < 0.0025 and co.y < HEAD_Y + 0.045:
                c = LIP
        elif s < TAIL_START + 0.05:
            # broken dark dorsolateral stripes either side of the spine
            side = (co.x - p.x) / r
            stripe = math.exp(-((abs(side) - 0.45) / 0.18) ** 2) * nh.smoothstep(0.2, 0.6, up)
            stripe *= 0.6 + 0.4 * math.sin(s * 70.0 + coarse * 2.0)
            c = nh.lerp(c, STRIPE, max(0.0, stripe))
        else:
            ring = ((s - TAIL_START) / 0.07) % 1.0
            if ring < 0.4:
                c = nh.lerp(c, TAIL_BAND, 0.6 * nh.smoothstep(-0.6, 0.2, up))
        c = nh.lerp(c, BELLY, nh.smoothstep(-0.2, -0.7, up))
    if fine > 0.55 and n.z > 0.0:
        c = nh.lerp(c, SPECK, 0.35)
    k = 0.92 + 0.16 * (0.5 + 0.5 * coarse)
    return (c[0] * k, c[1] * k, c[2] * k)


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def toes(foot, forward, lengths, spread, r):
    out = []
    n = len(lengths)
    side = Vector((-forward.y, forward.x, 0.0))
    for k, L in enumerate(lengths):
        a = (k / (n - 1) - 0.5) * spread
        d = (forward * math.cos(a) + side * math.sin(a)).normalized()
        p0 = foot + Vector((0, 0, 0.004))
        p1 = p0 + d * L * 0.5 + Vector((0, 0, 0.001))
        p2 = p0 + d * L
        p2.z = 0.0018
        out.append((nh.tube([p0, p1, p2], [r, r * 0.8, r * 0.6], sides=5), TOE))
        out.append((nh.tube([p2, p2 + d * r * 2.2 + Vector((0, 0, -0.0015))], [r * 0.55, 0.0], sides=4), CLAW))
    return out


def details(surf):
    out = []
    for sh, el, wr, fwd, r, hind in legs():
        lengths = [0.018, 0.028, 0.036, 0.040, 0.026] if hind else [0.014, 0.022, 0.026, 0.024, 0.016]
        if fwd.x < 0:
            lengths = list(reversed(lengths))   # longest toe on the outer side, as in lizards
        out += toes(Vector((wr.x, wr.y, 0.0)) + fwd * 0.004, fwd, lengths, 2.0 if hind else 2.2,
                    0.0032 if hind else 0.0028)
    for sx in (-1, 1):
        # eyes under the brow
        loc, nrm = surf.hit((sx * 0.08, HEAD_Y + 0.004, 0.090), (-sx, 0, 0))
        if loc is not None:
            look = Vector((sx * 0.9, -0.3, 0.3)).normalized()
            c = loc - look * 0.003

            def eye_col(co, n, c=c, lk=look):
                k = (co - c).normalized().dot(lk)
                return PUPIL if k > 0.8 else (IRIS if k > 0.45 else (0.10, 0.08, 0.06))
            out.append((nh.ellipsoid(c, (0.0075, 0.0085, 0.0075), subdivisions=2), eye_col))
        # nostrils near the snout tip
        loc, nrm = surf.hit((sx * 0.006, HEAD_Y - 0.05, 0.2), (0, 0, -1))
        if loc is not None:
            out.append((nh.ellipsoid(loc, (0.0022, 0.0018, 0.0012), subdivisions=1), LIP))
        # small sharp teeth along the upper jaw
        y = HEAD_Y - 0.052
        while y < HEAD_Y + 0.035:
            loc, nrm = surf.hit((sx * 0.08, y, 0.0785), (-sx, 0, 0))
            if loc is not None:
                base = loc + Vector((-sx * 0.0012, 0, 0.0015))
                out.append((nh.tube([base, base + Vector((sx * 0.0006, 0, -0.0042))], [0.0013, 0.0], sides=4),
                            TOOTH))
            y += 0.0075
    return out


def drop_islands(bm, min_verts=60):
    """Removes stray voxel fragments (e.g. at the thin tail tip)."""
    import bmesh
    seen = set()
    for start in list(bm.verts):
        if start in seen or not start.is_valid:
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
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, FLANK)
    fused = body.fuse(voxel=0.0045, smooth=4, smooth_factor=0.5, max_tris=3400)
    drop_islands(fused)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * 0.0006 * noise.noise(v.co * 120.0)   # fine granular scales
    fused.normal_update()
    surf = Surface(fused)
    extra = details(surf)
    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    for bm, col in extra:
        mb.add(bm, col, smooth=False)
    obj = mb.to_object(NAME, roughness=0.5)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"height {max(zs):.4f}  shoulder z {legs()[0][0].z:.4f}")
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
    nh.run(build, NAME, ground=(0.30, 0.26, 0.18), views=((35, 25), (-90, 8), (160, 60)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0.0, HEAD_Y, 0.07), 0.25, 40, 18)
