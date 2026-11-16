"""
Procedural coypu / nutria (Myocastor coypus) for map colonies.

A big, heavy semi-aquatic rodent crouched on the bank: one seamless fused body
(a deep, hunched barrel of a torso, a broad rump, a short thick neck and a large
square-ish head with a blunt, boxy muzzle, short front legs on small clawed
hands and big hind feet set flat on the ground). Coarse shaggy fur is displaced
into the surface and repainted procedurally: dark brown back with reddish-brown
guard-hair flecks, a paler grey-brown belly, and the white muzzle and chin.
Crisp details on top: the two pairs of huge ORANGE incisors showing under the
split upper lip, long white whiskers, small round ears set far back, small eyes
and nostrils set high on the head (for swimming with only the top of the head
above water), webbing between the inner four hind toes, dark claws, and the long,
round, sparsely haired scaly tail curving along the ground.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/myocastor_coypus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Coypu.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

FUR = (0.27, 0.17, 0.095)        # dark brown back
FUR_RED = (0.42, 0.26, 0.13)     # reddish-brown guard-hair tips
FUR_DARK = (0.12, 0.08, 0.05)
FLANK = (0.34, 0.24, 0.16)
BELLY = (0.46, 0.40, 0.33)       # paler grey-brown belly
MUZZLE = (0.88, 0.86, 0.80)      # white muzzle and chin
SKIN = (0.22, 0.17, 0.15)        # dark feet
WEB = (0.30, 0.23, 0.21)
TAIL = (0.17, 0.14, 0.13)        # dark scaly tail
TAIL_RING = (0.09, 0.075, 0.07)
EAR = (0.18, 0.12, 0.08)
EYE = (0.02, 0.02, 0.02)
NOSE = (0.06, 0.05, 0.05)
TOOTH = (0.95, 0.45, 0.08)       # iron-rich orange enamel
TOOTH_TIP = (0.98, 0.66, 0.30)
WHISKER = (0.92, 0.90, 0.85)
CLAW = (0.10, 0.08, 0.07)

HEAD = Vector((0.0, -0.33, 0.175))
TOES = []        # (base, direction, length, hind) of every finger and toe
HIND_FEET = []   # (sx, heel, toe base y) for the webbing


# ---------------------------------------------------------------- surface paint / fur

def muzzle_mask(co, n):
    """White lips, whisker pads and chin at the front of the snout."""
    d = co - HEAD
    if d.y > -0.03:
        return 0.0
    f = nh.smoothstep(-0.055, -0.095, d.y)          # front of the muzzle
    f *= nh.smoothstep(0.005, -0.02, d.z + 0.15 * abs(d.x))   # lower half only (nose stays dark-furred)
    f += nh.smoothstep(-0.02, -0.05, d.z) * nh.smoothstep(-0.02, -0.07, d.y)   # chin underneath
    f += 0.15 * noise.noise(co * 60.0)
    return nh.smoothstep(0.35, 0.6, f)


def fur(co, n):
    c = nh.lerp(FLANK, FUR, nh.smoothstep(-0.3, 0.6, n.z))
    c = nh.lerp(c, FUR_RED, 0.6 * nh.smoothstep(0.05, 0.5, noise.noise(co * 55.0)))    # guard hairs
    c = nh.lerp(c, FUR_DARK, 0.4 * nh.smoothstep(0.1, 0.6, noise.noise(co * 23.0 + Vector((5, 2, 1)))))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.2, -0.6, n.z + 0.1 * noise.noise(co * 20.0)))
    if co.z < 0.022:                                         # dark naked feet
        c = nh.lerp(c, SKIN, nh.smoothstep(0.022, 0.01, co.z))
    m = muzzle_mask(co, n)
    return nh.lerp(c, MUZZLE, m) if m > 0 else c


def fur_displace(co, n):
    """Coarse, shaggy guard hairs: stronger and streakier than a rat's."""
    if co.z < 0.025 or (co - HEAD).y < -0.06:
        return 0.0
    streak = noise.noise(Vector((co.x * 120.0, co.y * 30.0, co.z * 120.0)))
    return 0.0022 * noise.noise(co * 70.0) + 0.0016 * streak


# ---------------------------------------------------------------- fused body parts

def body_parts():
    h = HEAD
    parts = [
        nh.uv_ellipsoid((0, -0.13, 0.14), (0.10, 0.13, 0.10), 24, 16),          # chest
        nh.uv_ellipsoid((0, 0.05, 0.175), (0.128, 0.17, 0.128), 26, 18),        # deep hunched barrel
        nh.uv_ellipsoid((0, 0.19, 0.135), (0.115, 0.10, 0.105), 24, 16),        # broad rump
        nh.tube([(0, -0.18, 0.15), (0, -0.25, 0.165), h + Vector((0, 0.03, 0))], [0.09, 0.082, 0.074], sides=18),
        nh.uv_ellipsoid(h, (0.072, 0.075, 0.064), 22, 14),                      # broad skull
        # blunt, boxy muzzle
        nh.tube([h + Vector((0, -0.03, -0.005)), h + Vector((0, -0.07, -0.012)), h + Vector((0, -0.1, -0.02))],
                [0.055, 0.047, 0.036], sides=16, scale_xy=(1.15, 0.9)),
        nh.uv_ellipsoid(h + Vector((0, -0.05, -0.05)), (0.035, 0.045, 0.022), 12, 8),   # chin
    ]
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid(h + Vector((sx * 0.03, -0.085, -0.025)), (0.03, 0.03, 0.027), 12, 8))  # whisker pads
        parts.append(nh.uv_ellipsoid(h + Vector((sx * 0.05, 0.0, -0.02)), (0.045, 0.055, 0.045), 14, 10))   # cheeks / jaw
        # front legs: short, a little splayed
        parts.append(nh.tube([(sx * 0.065, -0.14, 0.12), (sx * 0.075, -0.15, 0.065), (sx * 0.072, -0.17, 0.025),
                              (sx * 0.07, -0.185, 0.01)], [0.048, 0.032, 0.021, 0.015], sides=12))
        parts.append(nh.uv_ellipsoid((sx * 0.07, -0.195, 0.01), (0.019, 0.022, 0.01), 10, 6))  # hand
        # hind legs: big haunch, shin down to the heel, long broad flat foot
        parts.append(nh.uv_ellipsoid((sx * 0.085, 0.15, 0.13), (0.06, 0.095, 0.085), 18, 12))
        parts.append(nh.tube([(sx * 0.1, 0.11, 0.10), (sx * 0.112, 0.17, 0.05), (sx * 0.116, 0.21, 0.014)],
                             [0.042, 0.024, 0.015], sides=12))
        parts.append(nh.tube([(sx * 0.116, 0.22, 0.009), (sx * 0.118, 0.15, 0.008), (sx * 0.12, 0.08, 0.008)],
                             [0.017, 0.023, 0.026], sides=10, scale_xy=(1.0, 0.6)))
        HIND_FEET.append((sx, 0.08))
        # fingers (front: 4 short, clawed) and toes (hind: 5 long, inner four webbed)
        for a in (-0.6, -0.2, 0.2, 0.6):
            d = Vector((math.sin(a) + sx * 0.1, -math.cos(a), 0)).normalized()
            TOES.append((Vector((sx * 0.07, -0.205, 0.005)), d, 0.02, False))
        for k, a in enumerate((-0.42, -0.21, 0.0, 0.21, 0.42)):
            a = a * -sx                                 # inner toe = k 0
            d = Vector((math.sin(a) * 1.3, -math.cos(a), 0)).normalized()
            L = (0.042, 0.05, 0.052, 0.048, 0.03)[k]
            TOES.append((Vector((sx * 0.12 + d.x * 0.014, 0.08, 0.006)), d, L, True))
    return parts


# ---------------------------------------------------------------- tail

TAIL_PTS = [Vector(p) for p in ((0, 0.26, 0.11), (0.01, 0.33, 0.065), (0.035, 0.40, 0.03), (0.075, 0.47, 0.016),
                                (0.125, 0.53, 0.013), (0.165, 0.60, 0.011), (0.18, 0.67, 0.01), (0.165, 0.74, 0.009),
                                (0.13, 0.80, 0.008))]
TAIL_R = [0.03, 0.025, 0.021, 0.018, 0.016, 0.014, 0.012, 0.0095, 0.0065]


def tail():
    """Long, round, thick-rooted tail (not flattened like a beaver's), lying in a lazy S;
    painted with rings of scales, sparse bristles shown as darker flecks."""
    pts, rs = [], []
    for (a, b), (ra, rb) in zip(zip(TAIL_PTS, TAIL_PTS[1:]), zip(TAIL_R, TAIL_R[1:])):
        for k in range(8):
            t = k / 8
            pts.append(a.lerp(b, t))
            rs.append(ra + (rb - ra) * t)
    pts.append(TAIL_PTS[-1] + (TAIL_PTS[-1] - TAIL_PTS[-2]).normalized() * 0.008)
    rs.append(0.0)
    bm = nh.tube(pts, rs, sides=9, cap_start=False)
    along = [0.0]
    for a, b in zip(pts, pts[1:]):
        along.append(along[-1] + (b - a).length)

    def col(co, n):
        i = min(range(len(pts)), key=lambda k: (pts[k] - co).length_squared)
        ring = (along[i] / 0.009) % 1.0
        c = nh.lerp(TAIL, TAIL_RING, nh.smoothstep(0.75, 0.95, ring))
        c = nh.lerp(c, TAIL_RING, 0.4 * nh.smoothstep(0.3, 0.6, noise.noise(co * 140.0)))
        return nh.lerp(c, FUR, nh.smoothstep(0.05, 0.0, along[i]))   # furred root
    return bm, col


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def snap(self, p):
        hit, normal, _i, _d = self.tree.find_nearest(Vector(p))
        return hit, normal


def oriented(bm, normal, pos, spin=0.0):
    if spin:
        nh.transform(bm, Matrix.Rotation(spin, 4, "Z"))
    nh.transform(bm, Vector((0, 0, 1)).rotation_difference(normal).to_matrix().to_4x4())
    nh.transform(bm, Matrix.Translation(pos))
    return bm


def incisor(top, length, width, curve):
    """Broad chisel tooth hanging from `top`, curving back by `curve` (towards +Y)."""
    pts = [top, top + Vector((0, -0.004, -length * 0.5)), top + Vector((0, curve, -length))]
    bm = nh.tube(pts, [width, width * 0.95, width * 0.85], sides=8, scale_xy=(0.55, 1.0))
    z0, z1 = top.z, top.z - length
    return bm, (lambda co, n: nh.lerp(TOOTH, TOOTH_TIP, nh.smoothstep(z0, z1, co.z) * 0.6))


def details(surf):
    out = []
    h = HEAD
    # nose pad high on the snout, nostrils on top
    p, n = surf.snap(h + Vector((0, -0.125, 0.0)))
    out.append((nh.uv_ellipsoid(p - n * 0.003, (0.02, 0.009, 0.012), 12, 6), NOSE))
    for sx in (1, -1):
        out.append((nh.uv_ellipsoid(p + Vector((sx * 0.009, -0.004, 0.006)), (0.005, 0.003, 0.003), 8, 4),
                    (0.0, 0.0, 0.0)))
    # incisors: two upper (broad, showing under the split lip) and two lower, all bright orange
    lip, ln = surf.snap(h + Vector((0, -0.12, -0.045)))
    for sx in (1, -1):
        # broad uppers side by side, chisel tips meeting the lowers just below the lip
        out.append(incisor(lip + Vector((sx * 0.0078, 0.006, 0.008)), 0.03, 0.0084, 0.005))
        out.append(incisor(lip + Vector((sx * 0.006, 0.014, -0.034)), -0.016, 0.0066, -0.003))
    for sx in (1, -1):
        # small eyes set high on the head
        p, n = surf.snap(h + Vector((sx * 0.05, -0.035, 0.035)))
        out.append((nh.uv_ellipsoid(p - n * 0.003, (0.011, 0.011, 0.01), 10, 8), EYE))
        # small round ears set far back, nearly hidden in the fur
        p, n = surf.snap(h + Vector((sx * 0.05, 0.045, 0.045)))
        ear = nh.uv_ellipsoid((0, 0, 0), (0.017, 0.016, 0.006), 12, 6)
        for v in ear.verts:
            v.co.z += 0.005 * (v.co.x / 0.017) ** 2
        out.append((oriented(ear, Vector((sx * 0.6, -0.6, 0.5)).normalized(), p + Vector((0, 0, 0.006))), EAR))
        # long white whiskers fanning from the whisker pads
        for k in range(8):
            u = k / 7.0
            p, n = surf.snap(h + Vector((sx * 0.05, -0.095 + 0.025 * u, -0.012 - 0.018 * u)))
            d = (n * 0.4 + Vector((sx * 0.9, 0.3 + 0.25 * u, 0.15 - 0.3 * u))).normalized()
            out.append((nh.tube([p - n * 0.002, p + d * 0.07, p + d * 0.13 + Vector((0, 0, -0.015))],
                                [0.0014, 0.001, 0.0], sides=3), WHISKER))
    hind_tips = {1: [], -1: []}
    for base, d, L, hind in TOES:
        tip = base + d * L
        r = 0.0062 if hind else 0.005
        out.append((nh.tube([base - d * 0.004, base + d * L * 0.5 + Vector((0, 0, 0.002)), tip],
                            [r, r * 0.9, r * 0.75], sides=6), SKIN))
        out.append((nh.tube([tip, tip + d * 0.008 + Vector((0, 0, -0.004))], [r * 0.6, 0.0], sides=5), CLAW))
        if hind:
            hind_tips[1 if base.x > 0 else -1].append(tip)
    # webbing between the inner four hind toes
    for sx, toe_y in HIND_FEET:
        tips = hind_tips[sx]
        tips = sorted(tips, key=lambda t: -sx * t.x)            # inner toe first
        inner4 = tips[:4]
        outline = [Vector((sx * 0.12 - sx * 0.014, toe_y + 0.004, 0.006))]
        outline += [t.lerp(Vector((t.x, toe_y, t.z)), 0.15) for t in inner4]
        outline.append(Vector((sx * 0.12 + sx * 0.01, toe_y + 0.004, 0.006)))
        pts = [(p.x, p.y, 0.007) for p in outline]
        if sx < 0:
            pts.reverse()
        out.append((nh.flat_panel(pts, thickness=0.003), WEB))
    return out


def build():
    TOES.clear()
    HIND_FEET.clear()
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, FUR)
    fused = body.fuse(voxel=0.016, smooth=5, smooth_factor=0.5, max_tris=None)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * fur_displace(v.co, v.normal)
    fused.normal_update()
    surf = Surface(fused)

    mb = nh.MeshBuilder()
    extra = details(surf)
    mb.add(fused, color=fur)
    tail_bm, tail_col = tail()
    mb.add(tail_bm, tail_col)
    for bm, col in extra:
        mb.add(bm, col)
    obj = mb.to_object("Coypu", roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


def closeup(path, target, dist, az, el, lens=60):
    """Extra render aimed at `target` (after nh.run set up the scene and camera)."""
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
    nh.run(build, "Coypu", ground=(0.32, 0.36, 0.24), views=((35, 25), (-90, 8), (160, 60)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), HEAD + Vector((0, -0.06, -0.01)), 0.38, 25, 10)
        closeup(out.with_name(out.stem + "_foot.png"), (0.12, 0.12, 0.02), 0.4, 120, 35)
