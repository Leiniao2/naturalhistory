"""
Procedural Megachirella wachtleri for map colonies: the oldest known squamate, a small lizard
(~20 cm) from the Middle Triassic (about 240 million years ago) of the Dolomites, northern Italy.

Built on the green iguana's body plan (green_iguana.py) but as a plain, slender early lizard on
all fours: a low, narrow head with a pointed snout, no crest, no dewlap and no cheek shield, a
slim body, sprawling legs with long clawed toes (its name means "big hand") and a long tail
curled round to the side. Fine bumpy scales displaced into the surface. Painted a dull
olive-brown with darker blotchy bands across the back, a ringed tail and a pale belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/megachirella_wachtleri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Megachirella.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

GREEN = (0.42, 0.38, 0.24)       # olive-brown
GREEN_LIGHT = (0.58, 0.52, 0.34)
BAND = (0.24, 0.20, 0.13)        # dark blotchy bands
TAIL_RING = (0.20, 0.17, 0.11)
HEAD = (0.50, 0.45, 0.30)
BELLY = (0.76, 0.70, 0.52)
DEWLAP = BELLY
EAR = (0.18, 0.16, 0.12)
IRIS = (0.72, 0.56, 0.22)
PUPIL = (0.02, 0.02, 0.02)
CLAW = (0.20, 0.18, 0.15)
TOE = (0.36, 0.32, 0.20)

HEAD_Y = -0.29
DEWLAP_Z, DEWLAP_RZ = 0.072, 0.058

# tail centre line (base at the hips -> tip), curling round to the right side
TAIL_PTS = [Vector(p) for p in (
    (0.0, 0.17, 0.085), (0.01, 0.30, 0.055), (0.07, 0.45, 0.035), (0.19, 0.55, 0.026),
    (0.34, 0.56, 0.02), (0.45, 0.47, 0.016), (0.50, 0.33, 0.013), (0.48, 0.18, 0.011),
    (0.42, 0.05, 0.009), (0.36, -0.05, 0.008),
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


TAIL = catmull_rom(TAIL_PTS, 12)
TAIL_LEN = [0.0]
for _a, _b in zip(TAIL, TAIL[1:]):
    TAIL_LEN.append(TAIL_LEN[-1] + (_b - _a).length)


def tail_param(co):
    """(arc length along the tail, distance from the tail axis) of the nearest tail point."""
    best, bi = 1e9, 0
    for i, p in enumerate(TAIL):
        d = (p - co).length_squared
        if d < best:
            best, bi = d, i
    return TAIL_LEN[bi], math.sqrt(best)


def tail_radius(s):
    total = TAIL_LEN[-1]
    t = s / total
    return 0.056 * (1.0 - t) ** 1.25 + 0.009 * t


# ---------------------------------------------------------------- paint

def paint(co, n):
    s, d = tail_param(co)
    on_tail = co.y > 0.2 or (co.x > 0.25)
    fine = noise.noise(co * 70.0)
    if on_tail and d < tail_radius(s) * 1.6 + 0.02:
        c = nh.lerp(GREEN, GREEN_LIGHT, 0.25 + 0.25 * noise.noise(co * 6.0))
        ring = ((s - 0.08) / 0.085) % 1.0
        if s > 0.12 and ring < 0.42:
            c = nh.lerp(c, TAIL_RING, nh.smoothstep(0.12, 1.0, s / TAIL_LEN[-1] + 0.35))
        if n.z < -0.4:
            c = nh.lerp(c, BELLY, 0.5)
    else:
        c = nh.lerp(GREEN, GREEN_LIGHT, 0.35 + 0.3 * noise.noise(co * 5.0))
        # darker bluish-grey bands down the flanks of the body
        if -0.16 < co.y < 0.18 and n.z > -0.3:
            ph = ((co.y + 0.16) / 0.085 + 0.25 * noise.noise(co * 8.0)) % 1.0
            if ph < 0.34:
                c = nh.lerp(c, BAND, (0.35 + 0.2 * noise.noise(co * 14.0)) * nh.smoothstep(-0.3, 0.3, abs(n.x)))
        if n.z < -0.35:
            c = nh.lerp(c, BELLY, 0.6)
        if co.y < -0.19:                                   # paler head and jowls
            c = nh.lerp(c, HEAD, nh.smoothstep(-0.19, -0.25, co.y))
            if co.z < 0.095 and co.y < -0.2:              # dewlap
                c = nh.lerp(c, DEWLAP, 0.6)
            if co.y < -0.28 and abs(co.z - 0.112) < 0.004 and abs(co.x) > 0.012:   # mouth line
                c = nh.lerp(c, (0.20, 0.17, 0.11), 0.7)
    if fine > 0.42:
        c = nh.lerp(c, (0.22, 0.19, 0.12), 0.35)
    elif fine < -0.45:
        c = nh.lerp(c, GREEN_LIGHT, 0.4)
    return c


def displace(co, n):
    """Small bumpy scales everywhere, bigger tubercles on the head and jowls."""
    amp = 0.0012
    if co.y < -0.22:
        amp = 0.0016
    return amp * noise.noise(co * 65.0) + 0.0008 * noise.noise(co * 140.0)


# ---------------------------------------------------------------- fused body parts

def body_parts():
    parts = []
    # deep, slightly compressed torso with a little sag in the belly
    parts.append(nh.uv_ellipsoid((0, 0.0, 0.1), (0.066, 0.2, 0.056), 24, 16,
                                 deform=lambda v: 1.0 + 0.08 * max(0.0, -v.z) * (1 - abs(v.y))))
    parts.append(nh.uv_ellipsoid((0, 0.12, 0.1), (0.06, 0.09, 0.05), 20, 12))       # hips
    parts.append(nh.uv_ellipsoid((0, -0.13, 0.105), (0.058, 0.09, 0.05), 20, 12))   # shoulders
    parts.append(nh.uv_ellipsoid((0, -0.2, 0.115), (0.042, 0.07, 0.04), 20, 12))    # neck
    # head: boxy cranium, blunt snout, heavy jowls, brow ridges
    parts.append(nh.uv_ellipsoid((0, HEAD_Y, 0.128), (0.036, 0.07, 0.026), 20, 12,
                                 deform=lambda v: 1.0 - 0.12 * max(0.0, v.z) ** 2))   # flat crown
    parts.append(nh.uv_ellipsoid((0, HEAD_Y - 0.065, 0.122), (0.02, 0.05, 0.016), 16, 10))  # pointed snout
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid((sx * 0.024, HEAD_Y + 0.02, 0.114), (0.022, 0.04, 0.024), 16, 10))
    # sprawling legs
    for sx in (1, -1):
        parts.append(nh.tube([(sx * 0.05, -0.13, 0.11), (sx * 0.14, -0.14, 0.1), (sx * 0.155, -0.175, 0.04),
                              (sx * 0.16, -0.19, 0.014)], [0.032, 0.024, 0.018, 0.016], sides=12))
        parts.append(nh.uv_ellipsoid((sx * 0.105, -0.135, 0.1), (0.04, 0.03, 0.03), 14, 10))    # upper arm
        parts.append(nh.uv_ellipsoid((sx * 0.165, -0.205, 0.008), (0.022, 0.028, 0.01), 12, 8))  # front palm
        parts.append(nh.tube([(sx * 0.05, 0.13, 0.1), (sx * 0.17, 0.09, 0.1), (sx * 0.19, 0.17, 0.045),
                              (sx * 0.2, 0.19, 0.016)], [0.042, 0.03, 0.02, 0.017], sides=12))
        parts.append(nh.uv_ellipsoid((sx * 0.11, 0.115, 0.1), (0.055, 0.04, 0.038), 14, 10))   # thigh
        parts.append(nh.uv_ellipsoid((sx * 0.205, 0.21, 0.008), (0.024, 0.034, 0.01), 12, 8))   # hind sole
    # very long tail
    radii = [tail_radius(s) for s in TAIL_LEN]
    pts = [Vector((p.x, p.y, max(p.z, r * 0.95))) for p, r in zip(TAIL, radii)]
    parts.append(nh.tube(pts, [max(r, 0.009) for r in radii], sides=14))
    return parts


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def snap(self, p):
        hit, normal, _i, _d = self.tree.find_nearest(Vector(p))
        return hit, normal

    def top(self, x, y):
        hit, normal, _i, _d = self.tree.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
        return hit, normal


def oriented(bm, normal, pos, spin=0.0):
    if spin:
        nh.transform(bm, Matrix.Rotation(spin, 4, "Z"))
    nh.transform(bm, Vector((0, 0, 1)).rotation_difference(normal).to_matrix().to_4x4())
    nh.transform(bm, Matrix.Translation(pos))
    return bm


def toes(palm, forward, outward, lengths, spread):
    out = []
    n = len(lengths)
    for k, L in enumerate(lengths):
        a = (k / (n - 1) - 0.5) * spread
        d = (forward * math.cos(a) + outward * math.sin(a)).normalized()
        p0 = palm + Vector((0, 0, 0.006))
        p1 = p0 + d * L * 0.5 + Vector((0, 0, 0.002))
        p2 = p0 + d * L
        p2.z = 0.004
        out.append((nh.tube([p0, p1, p2], [0.0055, 0.0045, 0.0035], sides=6), TOE))
        out.append((nh.tube([p2, p2 + d * 0.011 + Vector((0, 0, -0.003))], [0.003, 0.0], sides=5), CLAW))
    return out


def details(surf):
    out = []
    for sx in (1, -1):
        side = Vector((sx, 0, 0))
        # ear opening behind the jaw
        p, n = surf.snap((sx * 0.045, HEAD_Y + 0.045, 0.125))
        out.append((oriented(nh.uv_ellipsoid((0, 0, 0), (0.007, 0.009, 0.0015), 12, 6), n, p), EAR))
        # eyes
        p, n = surf.snap((sx * 0.03, HEAD_Y - 0.015, 0.14))
        out.append((nh.ellipsoid(p - n * 0.003, (0.0068, 0.0068, 0.0068), subdivisions=2), IRIS))
        out.append((nh.ellipsoid(p + n * 0.0032, (0.003, 0.003, 0.003), subdivisions=1), PUPIL))
        # nostrils on the snout
        p, n = surf.snap((sx * 0.01, HEAD_Y - 0.11, 0.128))
        out.append((oriented(nh.uv_ellipsoid((0, 0, 0), (0.0018, 0.0018, 0.0009), 8, 6), n, p), EAR))
        # long clawed toes
        out += toes(Vector((sx * 0.168, -0.212, 0.0)), Vector((0.25 * sx, -1, 0)).normalized(), side,
                    [0.028, 0.04, 0.05, 0.046, 0.03], 1.9)
        out += toes(Vector((sx * 0.212, 0.226, 0.0)), Vector((0.6 * sx, 0.8, 0)).normalized(), side,
                    [0.026, 0.04, 0.052, 0.064, 0.034], 1.7)
    return out


def build():
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, GREEN)
    fused = body.fuse(voxel=0.011, smooth=4, smooth_factor=0.5, max_tris=None)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * displace(v.co, v.normal)
    fused.normal_update()
    surf = Surface(fused)
    extra = details(surf)
    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    for bm, col in extra:
        mb.add(bm, col)
    obj = mb.to_object("Megachirella", roughness=0.45)
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
    nh.run(build, "Megachirella", ground=(0.45, 0.40, 0.30), views=((35, 25), (-90, 8), (160, 60)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0.0, HEAD_Y, 0.12), 0.36, 40, 18)
