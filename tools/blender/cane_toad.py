"""
Procedural cane toad (Rhinella marina) for map colonies.

A squat adult sitting up on its front legs: one seamless fused body (plump torso
tilted nose-up, broad flat head with a rounded snout, the big triangular parotoid
glands behind the eyes, bony ridges over the eyes, thick folded hind legs) with
round warts of two sizes displaced into the back and flanks.
Repainted procedurally: warm olive-brown with darker blotches, dark-tipped warts,
tan parotoids, a cream belly and throat, and a dark lip line.
Crisp details on top: bulging golden eyes with horizontal pupils, ear drums,
nostrils, and blunt fingers and toes.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/cane_toad.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CaneToad.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

BROWN = (0.44, 0.36, 0.20)       # olive-tan ground colour
OLIVE = (0.48, 0.43, 0.24)
BLOTCH = (0.20, 0.12, 0.06)      # dark chocolate blotches
WART_TIP = (0.09, 0.06, 0.04)
PAROTOID = (0.62, 0.50, 0.29)
PORE = (0.25, 0.17, 0.09)
BELLY = (0.86, 0.80, 0.62)
BELLY_SPECK = (0.62, 0.52, 0.36)
LIP = (0.16, 0.11, 0.07)
RIDGE = (0.16, 0.10, 0.06)
IRIS = (0.85, 0.62, 0.18)
IRIS_DARK = (0.45, 0.28, 0.08)
PUPIL = (0.02, 0.02, 0.02)
EAR = (0.36, 0.27, 0.16)
DIGIT = (0.50, 0.40, 0.25)
DIGIT_TIP = (0.30, 0.20, 0.12)

EYE_R = 0.021
EYES = [Vector((sx * 0.073, -0.16, 0.173)) for sx in (1, -1)]

# bony ridges over the eyes (canthal + supraorbital + postorbital), one side (+x)
RIDGE_PTS = [Vector(p) for p in ((0.026, -0.235, 0.15), (0.038, -0.19, 0.184), (0.046, -0.155, 0.195),
                                 (0.068, -0.13, 0.19), (0.088, -0.125, 0.176))]
RIDGE_R = [0.008, 0.012, 0.013, 0.012, 0.009]


def parotoid_frame(sx):
    """Centre, axes (length, width, height) and radii of the parotoid gland on side sx:
    a long bulging oval lying on the shoulder, slanting back, out and down."""
    front = Vector((sx * 0.08, -0.123, 0.184))
    back = Vector((sx * 0.124, -0.025, 0.146))
    length = (back - front).normalized()
    up = Vector((sx * 0.45, 0.0, 0.9))
    height = (up - length * up.dot(length)).normalized()
    width = height.cross(length).normalized()
    return (front + back) * 0.5, (length, width, height), (0.07, 0.035, 0.026)


def parotoid_local(co, sx):
    c, axes, r = parotoid_frame(sx)
    q = co - c
    return [q.dot(a) / ri for a, ri in zip(axes, r)]


def ridge_dist(co):
    """Distance from co to the ridge polyline (mirrored), minus its radius."""
    q = Vector((abs(co.x), co.y, co.z))
    best = 1e9
    for a, b, ra, rb in zip(RIDGE_PTS, RIDGE_PTS[1:], RIDGE_R, RIDGE_R[1:]):
        ab = b - a
        t = max(0.0, min(1.0, (q - a).dot(ab) / ab.length_squared))
        best = min(best, (q - (a + ab * t)).length - (ra + (rb - ra) * t))
    return best


def mouth_z(y):
    """Height of the lip line along the side of the head (snout tip -> corner of the mouth)."""
    return 0.122 - 0.03 * nh.smoothstep(-0.25, -0.08, y)


# ---------------------------------------------------------------- warts

def wart_field(co):
    """0..1 height of the nearest wart (big sparse ones + small dense ones)."""
    best = 0.0
    for freq, size in ((20.0, 0.85), (36.0, 0.7)):
        dist, pts = noise.voronoi(co * freq, distance_metric="DISTANCE")
        # vary wart size per cell
        r = size * (0.7 + 0.5 * (noise.noise(pts[0] * 1.37) * 0.5 + 0.5))
        h = 1.0 - nh.smoothstep(0.0, r, dist[0])
        h = h * h * (3 - 2 * h)
        best = max(best, h * (1.0 if freq < 30 else 0.72))
    return best


def dorsal(co, n):
    """1 on the back and upper flanks, 0 on the belly and throat."""
    d = nh.smoothstep(-0.35, 0.15, n.z) * nh.smoothstep(0.02, 0.07, co.z)
    if in_parotoid(co) or co.y < -0.2:                 # glands and snout stay smooth
        d = 0.0
    return d


def displace(co, n):
    d = 0.014 * wart_field(co) * dorsal(co, n)
    if in_parotoid(co):                                # pitted with pores
        dist, _pts = noise.voronoi(co * 45.0, distance_metric="DISTANCE")
        d -= 0.0015 * (1.0 - nh.smoothstep(0.0, 0.3, dist[0]))
    # crease along the lips
    if co.y < -0.07 and abs(co.x) > 0.03:
        d -= 0.003 * (1.0 - nh.smoothstep(0.0, 0.006, abs(co.z - mouth_z(co.y))))
    return d + 0.0006 * noise.noise(co * 120.0)


# ---------------------------------------------------------------- paint

def in_parotoid(co):
    for sx in (1, -1):
        l, w, h = parotoid_local(co, sx)
        if h > -0.2 and (l / 1.12) ** 2 + (w / 1.15) ** 2 + (h / 1.5) ** 2 < 1.0:
            return True
    return False


def paint(co, n):
    c = nh.lerp(BROWN, OLIVE, 0.5 + 0.5 * noise.noise(co * 5.0))
    # dark blotches on the back
    b = noise.noise(co * 9.0 + Vector((3.1, 0.7, 1.9))) + 0.3 * noise.noise(co * 25.0)
    c = nh.lerp(c, BLOTCH, (0.4 if co.y < -0.15 else 0.9) * nh.smoothstep(-0.08, 0.18, b))   # lighter on the face
    w = wart_field(co) * dorsal(co, n)
    c = nh.lerp(c, nh.lerp(BLOTCH, OLIVE, 0.3), 0.5 * nh.smoothstep(0.1, 0.4, w))   # wart flanks
    c = nh.lerp(c, WART_TIP, nh.smoothstep(0.5, 0.7, w))
    if in_parotoid(co) and n.z > -0.3:
        dist, _pts = noise.voronoi(co * 45.0, distance_metric="DISTANCE")
        c = nh.lerp(nh.lerp(PAROTOID, OLIVE, 0.2 + 0.3 * noise.noise(co * 30.0)), PORE,
                    0.85 * (1.0 - nh.smoothstep(0.2, 0.4, dist[0])))
    if ridge_dist(co) < 0.004 and n.z > -0.2:          # dark bony crests
        c = RIDGE
    # cream belly and throat with faint speckles
    belly = (1.0 - nh.smoothstep(-0.55, -0.05, n.z)) * nh.smoothstep(0.11, 0.07, co.z)
    limb = max(nh.smoothstep(0.13, 0.15, abs(co.x)),   # legs: only the undersides are pale
               nh.smoothstep(0.06, 0.08, abs(co.x)) * nh.smoothstep(0.06, 0.04, co.z) * nh.smoothstep(-0.11, -0.13, co.y))
    belly = belly * (1.0 - limb) + limb * (1.0 - nh.smoothstep(-0.85, -0.5, n.z))
    if co.y < -0.08 and abs(co.x) < 0.13:              # throat under the lip line
        throat = nh.smoothstep(0.004, -0.012, co.z - mouth_z(co.y)) * (1 - nh.smoothstep(0.0, 0.6, n.z))
        belly = max(belly, throat * (1.0 - limb))
    if belly > 0.0:
        bc = BELLY
        if noise.noise(co * 45.0) > 0.45:
            bc = nh.lerp(BELLY, BELLY_SPECK, 0.6)
        c = nh.lerp(c, bc, belly)
    # dark lip line
    if co.y < -0.07 and abs(co.x) > 0.03:
        c = nh.lerp(c, LIP, 0.8 * (1.0 - nh.smoothstep(0.002, 0.006, abs(co.z - mouth_z(co.y)))))
    return c


# ---------------------------------------------------------------- fused body parts

def rot_x(deg):
    return Matrix.Rotation(math.radians(deg), 4, "X")


def body_parts():
    parts = []
    # plump torso, wider behind, tilted nose-up
    torso = nh.uv_ellipsoid((0, 0, 0), (0.14, 0.165, 0.085), 28, 18,
                            deform=lambda v: 1.0 + 0.10 * max(0.0, v.y) - 0.05 * max(0.0, v.z) * max(0.0, -v.y))
    nh.transform(torso, rot_x(-14))
    nh.transform(torso, Matrix.Translation((0, 0.03, 0.092)))
    parts.append(torso)
    parts.append(nh.uv_ellipsoid((0, 0.12, 0.075), (0.115, 0.075, 0.066), 20, 12))       # rump
    # broad flat head, rounded snout
    parts.append(nh.uv_ellipsoid((0, -0.15, 0.135), (0.115, 0.085, 0.05), 24, 14,
                                 deform=lambda v: 1.0 - 0.08 * max(0.0, v.z) ** 2))
    parts.append(nh.uv_ellipsoid((0, -0.215, 0.128), (0.072, 0.045, 0.034), 18, 10))
    parts.append(nh.uv_ellipsoid((0, -0.13, 0.095), (0.105, 0.07, 0.045), 18, 10))      # throat / jaw
    for sx in (1, -1):
        # eye sockets (the eyeballs sit in them as details)
        parts.append(nh.ellipsoid(EYES[0] * Vector((sx, 1, 1)) + Vector((0, 0.004, -0.008)),
                                  (EYE_R * 1.15, EYE_R * 1.15, EYE_R * 1.0), subdivisions=3))
        # bony ridges over the eyes (canthal + supraorbital + postorbital)
        parts.append(nh.tube([p * Vector((sx, 1, 1)) for p in RIDGE_PTS], RIDGE_R, sides=10))
        # big triangular parotoid glands behind the eyes, angling back and out
        c, (al, aw, ah), (rl, rw, rh) = parotoid_frame(sx)
        par = nh.uv_ellipsoid((0, 0, 0), (rl, rw, rh), 20, 12)
        nh.transform(par, Matrix((al, aw, ah)).transposed().to_4x4())
        nh.transform(par, Matrix.Translation(c))
        parts.append(par)
        # front legs: arms straight down, slightly splayed
        parts.append(nh.tube([(sx * 0.075, -0.105, 0.085), (sx * 0.108, -0.125, 0.055), (sx * 0.1, -0.142, 0.03),
                              (sx * 0.094, -0.15, 0.012)],
                             [0.042, 0.035, 0.028, 0.022], sides=14))
        parts.append(nh.uv_ellipsoid((sx * 0.09, -0.162, 0.009), (0.024, 0.024, 0.01), 12, 8))   # hand
        # hind legs folded at the sides: thigh forward to the knee, shin back to the heel
        parts.append(nh.tube([(sx * 0.07, 0.13, 0.08), (sx * 0.15, 0.08, 0.075), (sx * 0.19, 0.03, 0.06)],
                             [0.048, 0.044, 0.032], sides=14))                                    # thigh
        parts.append(nh.tube([(sx * 0.19, 0.03, 0.06), (sx * 0.175, 0.11, 0.04), (sx * 0.13, 0.18, 0.025)],
                             [0.032, 0.03, 0.02], sides=12))                                      # shin
        parts.append(nh.tube([(sx * 0.13, 0.18, 0.02), (sx * 0.18, 0.14, 0.012), (sx * 0.22, 0.09, 0.009)],
                             [0.02, 0.018, 0.012], sides=10, scale_xy=(1.0, 0.6)))               # foot
    return parts


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def snap(self, p):
        hit, normal, _i, _d = self.tree.find_nearest(Vector(p))
        return hit, normal


def oriented(bm, normal, pos):
    nh.transform(bm, Vector((0, 0, 1)).rotation_difference(normal).to_matrix().to_4x4())
    nh.transform(bm, Matrix.Translation(pos))
    return bm


def eye(centre, sx):
    out = []
    look = Vector((sx * 0.75, -0.55, 0.45)).normalized()

    def iris(co, n, c=centre):
        # golden iris with fine dark veining
        v = noise.noise((co - c) * 400.0)
        return nh.lerp(IRIS, IRIS_DARK, 0.6 if v > 0.35 else 0.0)
    out.append((nh.ellipsoid(centre, (EYE_R, EYE_R, EYE_R), subdivisions=3), iris))
    # horizontal pupil: flat dark lozenge on the front of the eye
    side = look.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(look).normalized()
    pup = nh.ellipsoid((0, 0, 0), (0.0125, 0.0055, 0.0035), subdivisions=2)
    nh.transform(pup, Matrix((side, up, look)).transposed().to_4x4())
    nh.transform(pup, Matrix.Translation(centre + look * (EYE_R - 0.0012)))
    out.append((pup, PUPIL))
    # thin highlight ring of eyelid over the top
    return out


def digits(palm, forward, lengths, spread, radius):
    out = []
    n = len(lengths)
    for k, L in enumerate(lengths):
        a = (k / (n - 1) - 0.5) * spread
        d = Matrix.Rotation(a, 3, "Z") @ forward
        p0 = palm + Vector((0, 0, 0.005))
        p1 = p0 + d * L * 0.55 + Vector((0, 0, 0.002))
        p2 = p0 + d * L
        p2.z = radius * 0.8
        out.append((nh.tube([p0, p1, p2], [radius, radius * 0.85, radius * 0.75], sides=8),
                    lambda co, nn, a=p0, l=L: nh.lerp(DIGIT, DIGIT_TIP, nh.smoothstep(0.6, 1.0, (co - a).length / l))))
        out.append((nh.ellipsoid(p2, (radius * 0.78,) * 3, subdivisions=1), DIGIT_TIP))
    return out


def details(surf):
    out = []
    for i, sx in enumerate((1, -1)):
        out += eye(EYES[i], sx)
        # ear drum between the eye and the parotoid
        p, n = surf.snap((sx * 0.105, -0.135, 0.142))
        out.append((oriented(nh.uv_ellipsoid((0, 0, 0), (0.013, 0.013, 0.0025), 14, 6), n, p),
                    lambda co, nn: EAR))
        # nostrils near the snout tip
        p, n = surf.snap((sx * 0.02, -0.25, 0.148))
        out.append((oriented(nh.uv_ellipsoid((0, 0, 0), (0.0035, 0.0035, 0.0015), 8, 6), n, p - n * 0.0008),
                    LIP))
        # four blunt fingers, turned in a little; five long hind toes
        out += digits(Vector((sx * 0.09, -0.165, 0.0)), Vector((-0.55 * sx, -1, 0)).normalized(),
                      [0.022, 0.028, 0.032, 0.024], 1.4, 0.009)
        out += digits(Vector((sx * 0.215, 0.095, 0.0)), Vector((0.55 * sx, -0.85, 0)).normalized(),
                      [0.026, 0.036, 0.05, 0.06, 0.04], 1.3, 0.0085)
    return out


def build():
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, BROWN)
    fused = body.fuse(voxel=0.013, smooth=4, smooth_factor=0.5, max_tris=None)
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
    obj = mb.to_object("CaneToad", roughness=0.5)
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
    nh.run(build, "CaneToad", background=(0.55, 0.58, 0.55), ground=(0.42, 0.38, 0.26), views=((35, 25), (-90, 8), (160, 55)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0.0, -0.15, 0.14), 0.42, 30, 20)
