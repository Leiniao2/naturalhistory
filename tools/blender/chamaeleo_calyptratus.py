"""
Procedural veiled chameleon (Chamaeleo calyptratus) gripping a branch, for map colonies.

An adult male walking along a short horizontal branch that sits on a forked post
stuck in the ground. One seamless fused body: the laterally flattened, deep torso
with an arched back, the head with its tall helmet-like casque, the cone-shaped
turret eyes, the thin legs and the prehensile tail rolled into a tight coil below
the end of the branch. Repainted procedurally: bright green with broad yellow-orange
bands and turquoise mottling on the flanks, a pale lateral stripe, yellow stripes up
the casque and a banded tail.
Crisp details on top: the dorsal crest of small cones from the neck to the tail
base, the white gular and ventral crest, the tiny pupils at the tips of the eye
turrets, and the zygodactyl feet, each split into two opposed toe bundles that
clasp the branch from both sides.
Faces -Y, pivot on the ground (foot of the post).

Usage:
  blender --background --python tools/blender/chamaeleo_calyptratus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/VeiledChameleon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

GREEN = (0.22, 0.56, 0.18)
GREEN_LIGHT = (0.44, 0.72, 0.24)
YELLOW = (0.94, 0.80, 0.20)
ORANGE = (0.94, 0.52, 0.12)
TURQUOISE = (0.16, 0.62, 0.58)
PALE = (0.86, 0.90, 0.62)
CREST = (0.62, 0.76, 0.36)
WHITE = (0.92, 0.92, 0.82)
PUPIL = (0.03, 0.03, 0.02)
TOE = (0.40, 0.62, 0.24)
CLAW = (0.70, 0.66, 0.50)
BARK = (0.36, 0.25, 0.15)
BARK_DARK = (0.22, 0.15, 0.09)
LEAF = (0.30, 0.52, 0.18)

BR_Z = 0.30          # branch axis height
BR_R = 0.022         # branch radius
BR_Y0, BR_Y1 = -0.42, 0.15
TOP = BR_Z + BR_R    # top of the branch

BODY_C = Vector((0.0, 0.0, BR_Z + 0.16))
HEAD_C = Vector((0.0, -0.205, BR_Z + 0.205))
EYE_C = [Vector((sx * 0.033, -0.222, BR_Z + 0.218)) for sx in (1, -1)]

# tail: from the hips back past the end of the branch, then rolled into a coil
COIL_C = Vector((0.0, 0.25, BR_Z - 0.03))
COIL_R0 = 0.085


def tail_points():
    pts = [Vector((0, 0.12, BR_Z + 0.145)), Vector((0, 0.18, BR_Z + 0.115)),
           Vector((0, 0.225, BR_Z + 0.075))]
    n = 44
    turns = 2.15 * math.pi
    for k in range(n + 1):
        f = k / n
        phi = -0.35 + f * turns
        r = COIL_R0 * (1.0 - 0.78 * f)
        pts.append(COIL_C + Vector((0, math.sin(phi) * r, math.cos(phi) * r)))
    return pts


TAIL = tail_points()
TAIL_LEN = [0.0]
for _a, _b in zip(TAIL, TAIL[1:]):
    TAIL_LEN.append(TAIL_LEN[-1] + (_b - _a).length)


def tail_radius(s):
    t = s / TAIL_LEN[-1]
    return 0.030 * (1.0 - t) ** 1.1 + 0.005 * t


def tail_param(co):
    best, bi = 1e9, 0
    for i, p in enumerate(TAIL):
        d = (p - co).length_squared
        if d < best:
            best, bi = d, i
    return TAIL_LEN[bi], math.sqrt(best)


# ---------------------------------------------------------------- paint

def paint(co, n):
    fine = noise.noise(co * 90.0)
    s, d = tail_param(co)
    if co.y > 0.15 and d < tail_radius(s) * 1.8 + 0.01:
        c = nh.lerp(GREEN, GREEN_LIGHT, 0.3 + 0.3 * noise.noise(co * 20.0))
        ring = (s / 0.05) % 1.0
        if ring < 0.33:
            c = nh.lerp(c, YELLOW if ring < 0.18 else TURQUOISE, 0.7)
    elif co.y > -0.15 or co.z < BR_Z + 0.12 and co.y > -0.17:
        c = nh.lerp(GREEN, GREEN_LIGHT, 0.35 + 0.3 * noise.noise(co * 14.0))
        rel = co - BODY_C
        torso = abs(co.x) < 0.05 and co.z > BR_Z + 0.075
        if abs(rel.y) < 0.15 and abs(n.x) > 0.25 and torso:
            # broad vertical bands: yellow above, orange low on the flank
            ph = ((rel.y + 0.15) / 0.07 + 0.25 * noise.noise(co * 18.0)) % 1.0
            if ph < 0.42:
                c = nh.lerp(YELLOW, ORANGE, nh.smoothstep(0.04, -0.06, rel.z))
            elif ph < 0.62:
                c = nh.lerp(c, TURQUOISE, 0.5 + 0.3 * noise.noise(co * 30.0))
            elif noise.noise(co * 40.0) > 0.3:
                c = nh.lerp(c, TURQUOISE, 0.6)
            # pale lateral stripe low on the side
            if abs(rel.z + 0.035) < 0.008 * (1 + 0.4 * noise.noise(co * 25)):
                c = nh.lerp(c, PALE, 0.7)
        if n.z > 0.75 and abs(co.x) < 0.012:
            c = nh.lerp(c, YELLOW, 0.5)
        if n.z < -0.6:
            c = nh.lerp(c, GREEN_LIGHT, 0.5)
    else:
        # head and casque
        c = nh.lerp(GREEN, GREEN_LIGHT, 0.4 + 0.3 * noise.noise(co * 18.0))
        rel = co - HEAD_C
        if rel.z > 0.03:
            ph = ((co.y + 0.30) / 0.032 + 4.0 * rel.z) % 1.0
            if ph < 0.3 and abs(n.x) > 0.3:
                c = nh.lerp(c, YELLOW, 0.75)
            if abs(co.x) < 0.006 and n.z > 0.3:
                c = nh.lerp(c, GREEN_LIGHT, 0.6)
        for e in EYE_C:
            de = (co - e).length
            if de < 0.034:
                ring = (de / 0.0065) % 1.0
                c = nh.lerp(GREEN_LIGHT, YELLOW, 0.35 if ring < 0.4 else 0.0)
        if abs(rel.z + 0.022 + 0.25 * (rel.y + 0.06)) < 0.0045 and rel.y < 0.02 and abs(n.x) > 0.3:
            c = nh.lerp(YELLOW, PALE, 0.4)                    # downturned mouth line
        if rel.z < -0.03:
            c = nh.lerp(c, PALE, 0.4)
    if fine > 0.45:
        c = nh.lerp(c, (0.10, 0.28, 0.12), 0.25)
    return c


# ---------------------------------------------------------------- fused body parts

def body_parts():
    parts = []
    # deep, flattened torso with a strongly arched back and a keeled belly
    parts.append(nh.uv_ellipsoid(BODY_C, (0.037, 0.155, 0.100), 24, 16,
                                 deform=lambda v: 1.0 + 0.10 * max(0.0, v.z) * (1 - v.y * v.y)
                                 - 0.06 * abs(v.x)))
    parts.append(nh.uv_ellipsoid(BODY_C + Vector((0, 0.11, -0.02)), (0.036, 0.06, 0.06), 16, 10))   # hips
    parts.append(nh.uv_ellipsoid(BODY_C + Vector((0, -0.12, 0.0)), (0.036, 0.06, 0.07), 16, 10))    # shoulders
    # neck and head: blunt snout, wide jaws, cheeks
    parts.append(nh.uv_ellipsoid(HEAD_C + Vector((0, 0.06, -0.01)), (0.032, 0.05, 0.045), 16, 10))
    parts.append(nh.uv_ellipsoid(HEAD_C + Vector((0, 0.0, -0.012)), (0.034, 0.065, 0.036), 18, 12))
    parts.append(nh.uv_ellipsoid(HEAD_C + Vector((0, -0.062, -0.010)), (0.017, 0.030, 0.019), 14, 10))
    # tall helmet casque, flattened side to side: it rises from above the eyes to a peak
    # over the back of the head, then drops steeply to the neck
    parts.append(nh.uv_ellipsoid(HEAD_C + Vector((0, 0.012, 0.03)), (0.026, 0.06, 0.045), 16, 12))
    casque = nh.uv_ellipsoid((0, 0, 0), (0.018, 0.062, 0.105), 18, 14,
                             deform=lambda v: 1.0 - 0.12 * max(0.0, -v.y) * max(0.0, v.z))
    nh.transform(casque, Matrix.Rotation(math.radians(-38), 4, "X"))
    nh.transform(casque, Matrix.Translation(HEAD_C + Vector((0, 0.035, 0.06))))
    parts.append(casque)
    # turret eyes: big scaly cones on the sides of the head
    for e, sx in zip(EYE_C, (1, -1)):
        look = Vector((sx * 1.0, -0.4, 0.1)).normalized()
        parts.append(nh.uv_ellipsoid(e, (0.019, 0.021, 0.021), 14, 10))
        parts.append(nh.tube([e, e + look * 0.02, e + look * 0.034], [0.019, 0.0135, 0.007], sides=12))
    # thin legs: shoulder/hip -> elbow/knee (out to the side) -> wrist on the branch top
    for sx in (1, -1):
        for y_shoulder, y_foot, knee_back in ((-0.11, -0.16 if sx > 0 else -0.12, -0.02),
                                              (0.11, 0.13 if sx > 0 else 0.09, 0.03)):
            sh = Vector((sx * 0.03, y_shoulder, BR_Z + 0.14))
            el = Vector((sx * 0.07, y_shoulder + knee_back, BR_Z + 0.085))
            wr = Vector((sx * 0.012, y_foot, TOP + 0.012))
            parts.append(nh.tube([sh, el, wr], [0.018, 0.0125, 0.010], sides=10))
            parts.append(nh.uv_ellipsoid(el, (0.013, 0.013, 0.013), 10, 8))
    # prehensile tail
    radii = [tail_radius(s) for s in TAIL_LEN]
    parts.append(nh.tube(TAIL, radii, sides=12, scale_xy=(0.85, 1.0)))
    return parts


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def snap(self, p):
        hit, normal, _i, _d = self.tree.find_nearest(Vector(p))
        return hit, normal

    def ray(self, origin, direction):
        hit, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction))
        return hit, normal


def cone(base, direction, h, r, sides=5):
    return nh.tube([base - direction * r * 0.5, base + direction * h], [r, 0.0], sides=sides)


def crests(surf):
    out = []
    # dorsal crest: small cones from the neck down the arched back to the tail base
    y = -0.15
    while y < 0.16:
        hit, nrm = surf.ray((0, y, 1.0), (0, 0, -1))
        if hit is not None and hit.z > BR_Z + 0.1:
            t = (y + 0.15) / 0.31
            h = 0.011 * (1.0 - 0.55 * t) + 0.004
            d = (nrm + Vector((0, 0.35, 0))).normalized()
            out.append((cone(hit, d, h, 0.0045), CREST))
        y += 0.0115
    # white gular and ventral crest along the throat and belly midline
    y = -0.25
    while y < 0.08:
        hit, nrm = surf.ray((0, y, BR_Z + 0.08 if y > -0.17 else BR_Z + 0.12), (0, 0, 1))
        if y < -0.17:
            hit, nrm = surf.ray((0, y, BR_Z + 0.05), (0, 0, 1))
        if hit is not None:
            out.append((cone(hit, Vector((0, 0.25, -1)).normalized(), 0.006, 0.0028, 4), WHITE))
        y += 0.010
    return out


def branch_pt(theta, y, extra):
    return Vector((math.sin(theta) * (BR_R + extra), y, BR_Z + math.cos(theta) * (BR_R + extra)))


def foot(sx, y):
    """Two opposed toe bundles wrapping the branch from the wrist on top."""
    out = []
    wrist = Vector((sx * 0.010, y, TOP + 0.008))
    for side, th_end, dy in ((sx, 2.0, -0.004), (-sx, 1.7, 0.005)):
        pts = [wrist]
        for k in range(1, 6):
            th = side * (0.25 + (th_end - 0.25) * k / 5)
            pts.append(branch_pt(th, y + dy * k / 5, 0.007))
        out.append((nh.tube(pts, [0.009, 0.0085, 0.008, 0.007, 0.0065, 0.005], sides=7), TOE))
        tip = pts[-1]
        d = (pts[-1] - pts[-2]).normalized()
        out.append((nh.tube([tip, tip + d * 0.007 + Vector((0, 0, 0))], [0.003, 0.0], sides=4), CLAW))
    return out


def details(surf):
    out = crests(surf)
    for e, sx in zip(EYE_C, (1, -1)):
        look = Vector((sx * 1.0, -0.4, 0.1)).normalized()
        hit, nrm = surf.ray(e + look * 0.08, -look)
        if hit is not None:
            out.append((nh.ellipsoid(hit, (0.0040, 0.0040, 0.0040), subdivisions=1), PUPIL))
    for sx in (1, -1):
        out += foot(sx, -0.16 if sx > 0 else -0.12)
        out += foot(sx, 0.13 if sx > 0 else 0.09)
    return out


# ---------------------------------------------------------------- perch

def perch():
    out = []
    bark = lambda co, n: nh.lerp(BARK, BARK_DARK, 0.5 + 0.5 * noise.noise(
        Vector((co.x * 30, co.y * 12, co.z * 30))))
    branch = [Vector((0.006 * math.sin(t * 7.0), BR_Y0 + (BR_Y1 - BR_Y0) * t, BR_Z + 0.008 * math.sin(t * 4.0)))
              for t in (k / 10 for k in range(11))]
    # keep the section under the feet exactly on the axis
    for p in branch:
        if -0.2 < p.y < 0.16:
            p.x, p.z = 0.0, BR_Z
    rad = [BR_R * (1.05 - 0.15 * k / 10) for k in range(11)]
    rad[0] = BR_R * 0.6
    out.append((nh.tube(branch, rad, sides=9), bark))
    # post stuck in the ground, joining the branch from below
    post = [(0.02, -0.05, 0.0), (0.012, -0.07, 0.12), (0.0, -0.085, 0.22), (0.0, -0.09, BR_Z)]
    out.append((nh.tube(post, [0.03, 0.026, 0.024, 0.022], sides=8), bark))
    # small side twig with a couple of leaves near the front
    tw = [(0.0, -0.34, BR_Z), (0.05, -0.39, BR_Z + 0.05), (0.09, -0.42, BR_Z + 0.11)]
    out.append((nh.tube(tw, [0.010, 0.007, 0.0], sides=5), BARK))
    for base, tip, side in (((0.05, -0.39, BR_Z + 0.05), (0.12, -0.36, BR_Z + 0.09), 1),
                            ((0.09, -0.42, BR_Z + 0.11), (0.10, -0.50, BR_Z + 0.16), -1)):
        b, t = Vector(base), Vector(tip)
        d = t - b
        w = d.cross(Vector((0, 0, 1))).normalized() * d.length * 0.28
        leaf = nh.flat_panel([tuple(b), tuple(b + d * 0.4 + w), tuple(t), tuple(b + d * 0.4 - w)], 0.004)
        out.append((leaf, LEAF))
    return out


def build():
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, GREEN)
    fused = body.fuse(voxel=0.0055, smooth=4, smooth_factor=0.5, max_tris=12000)
    fused.normal_update()
    surf = Surface(fused)
    extra = details(surf)
    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    for bm, col in extra:
        mb.add(bm, col)
    for bm, col in perch():
        mb.add(bm, col)
    obj = mb.to_object("VeiledChameleon", roughness=0.45)
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
    nh.run(build, "VeiledChameleon", ground=(0.40, 0.36, 0.26), views=((35, 20), (-90, 5), (150, 40)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0.0, -0.17, BR_Z + 0.2), 0.45, 50, 15)
