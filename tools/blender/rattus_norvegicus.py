"""
Procedural brown rat (Rattus norvegicus) for map colonies.

A heavy-set rat scurrying with its back arched: one seamless fused body (pear-shaped
torso, broad rump, a thick neck, a blunt wedge of a head with a rounded muzzle,
short front legs on little hands and long hind feet set flat on the ground).
Short coarse fur is displaced into the surface and the body is repainted
procedurally: grizzled grey-brown back with darker guard-hair flecks, paler
grey-buff flanks and a pale grey belly, pinkish feet.
Crisp details on top: the long, thick, scaly pink-grey tail (ringed scales, darker
above) curving along the ground, small furry rounded ears, black bead eyes, a
pink nose, whiskers, and pink fingers and toes with tiny claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/rattus_norvegicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BrownRat.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

FUR = (0.42, 0.34, 0.25)         # grizzled grey-brown back
FUR_DARK = (0.22, 0.18, 0.14)    # dark guard-hair tips
FUR_FLANK = (0.56, 0.50, 0.42)   # greyer flanks
BELLY = (0.74, 0.71, 0.65)       # pale grey-buff belly
SKIN = (0.86, 0.62, 0.58)        # pink feet, nose
TAIL = (0.66, 0.54, 0.50)        # pink-grey scaly tail
TAIL_TOP = (0.44, 0.38, 0.35)
EAR = (0.48, 0.40, 0.36)
EAR_INNER = (0.70, 0.55, 0.52)
EYE = (0.02, 0.02, 0.02)
NOSE = (0.80, 0.52, 0.50)
WHISKER = (0.20, 0.18, 0.16)
CLAW = (0.88, 0.84, 0.78)

TOES = []        # (base, direction, length) of every finger and toe


# ---------------------------------------------------------------- surface paint / fur

def fur(co, n):
    c = nh.lerp(FUR_FLANK, FUR, nh.smoothstep(-0.2, 0.6, n.z))
    c = nh.lerp(c, FUR_DARK, 0.55 * nh.smoothstep(0.1, 0.5, noise.noise(co * 70.0)))   # guard hairs
    c = nh.lerp(c, FUR_FLANK, 0.25 * max(0.0, noise.noise(co * 18.0)))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.15, -0.55, n.z + 0.1 * noise.noise(co * 25.0)))
    if co.y < -0.3:                                          # short-haired muzzle, a little paler
        c = nh.lerp(c, FUR_FLANK, 0.3)
    if co.z < 0.016:                                         # pink feet
        c = nh.lerp(c, SKIN, nh.smoothstep(0.016, 0.008, co.z))
    return c


def fur_displace(co, n):
    if co.z < 0.02:
        return 0.0
    streak = noise.noise(Vector((co.x * 160.0, co.y * 40.0, co.z * 160.0)))
    return 0.0011 * noise.noise(co * 90.0) + 0.0008 * streak


# ---------------------------------------------------------------- fused body parts

def body_parts():
    parts = [
        nh.uv_ellipsoid((0, -0.10, 0.105), (0.066, 0.11, 0.07), 22, 14),        # chest
        nh.uv_ellipsoid((0, 0.06, 0.12), (0.085, 0.14, 0.085), 24, 16),         # arched abdomen
        nh.uv_ellipsoid((0, 0.17, 0.105), (0.078, 0.085, 0.075), 22, 14),       # broad rump
        nh.tube([(0, -0.14, 0.11), (0, -0.21, 0.12), (0, -0.25, 0.122)], [0.06, 0.052, 0.046], sides=18),  # neck
        nh.uv_ellipsoid((0, -0.255, 0.122), (0.046, 0.058, 0.044), 20, 12),     # skull
        nh.tube([(0, -0.28, 0.12), (0, -0.315, 0.109), (0, -0.342, 0.099)], [0.036, 0.027, 0.017], sides=16,
                scale_xy=(1.0, 0.9)),                                          # blunt muzzle
    ]
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid((sx * 0.024, -0.325, 0.099), (0.019, 0.02, 0.017), 12, 8))   # whisker pads
        parts.append(nh.uv_ellipsoid((sx * 0.032, -0.245, 0.103), (0.03, 0.04, 0.03), 12, 8))   # cheeks
        # front legs: short, elbows tucked in
        parts.append(nh.tube([(sx * 0.045, -0.10, 0.09), (sx * 0.052, -0.11, 0.05), (sx * 0.05, -0.135, 0.02),
                              (sx * 0.048, -0.15, 0.008)], [0.03, 0.019, 0.012, 0.009], sides=12))
        parts.append(nh.uv_ellipsoid((sx * 0.048, -0.16, 0.008), (0.014, 0.017, 0.008), 10, 6))  # hand
        # hind legs: thick haunch, shin down to the heel, long flat foot
        parts.append(nh.uv_ellipsoid((sx * 0.058, 0.15, 0.095), (0.042, 0.07, 0.06), 16, 10))
        parts.append(nh.tube([(sx * 0.066, 0.12, 0.075), (sx * 0.07, 0.17, 0.04), (sx * 0.068, 0.205, 0.012)],
                             [0.03, 0.016, 0.01], sides=12))
        parts.append(nh.tube([(sx * 0.068, 0.21, 0.007), (sx * 0.068, 0.165, 0.006), (sx * 0.066, 0.125, 0.006)],
                             [0.012, 0.013, 0.012], sides=10, scale_xy=(1.0, 0.75)))
        # toes (crisp details, too thin for the voxel grid)
        for a in (-0.55, -0.18, 0.18, 0.55):
            d = Vector((math.sin(a) + sx * 0.1, -math.cos(a), 0)).normalized()
            for base, L in ((Vector((sx * 0.048, -0.168, 0.004)), 0.018), (Vector((sx * 0.066, 0.118, 0.004)), 0.022)):
                TOES.append((base, d, L))
    return parts


# ---------------------------------------------------------------- tail

TAIL_PTS = [Vector(p) for p in ((0, 0.235, 0.08), (0.008, 0.30, 0.05), (0.03, 0.37, 0.022), (0.07, 0.44, 0.011),
                                (0.12, 0.50, 0.009), (0.16, 0.57, 0.008), (0.17, 0.64, 0.008), (0.15, 0.71, 0.007),
                                (0.11, 0.77, 0.006))]
TAIL_R = [0.022, 0.018, 0.0145, 0.012, 0.010, 0.0085, 0.007, 0.0055, 0.0035]


def tail():
    """Thick-rooted naked tail, as long as the body, resting on the ground in a lazy S;
    painted with rings of scales, darker on top."""
    # resample the polyline densely so the rings of scales have geometry to sit on
    pts, rs = [], []
    for (a, b), (ra, rb) in zip(zip(TAIL_PTS, TAIL_PTS[1:]), zip(TAIL_R, TAIL_R[1:])):
        for k in range(8):
            t = k / 8
            pts.append(a.lerp(b, t))
            rs.append(ra + (rb - ra) * t)
    pts.append(TAIL_PTS[-1] + (TAIL_PTS[-1] - TAIL_PTS[-2]).normalized() * 0.006)
    rs.append(0.0)
    bm = nh.tube(pts, rs, sides=8, cap_start=False)
    along = [0.0]
    for a, b in zip(pts, pts[1:]):
        along.append(along[-1] + (b - a).length)

    def col(co, n):
        # nearest sample along the tail -> ring phase
        i = min(range(len(pts)), key=lambda k: (pts[k] - co).length_squared)
        ring = (along[i] / 0.0075) % 1.0
        c = nh.lerp(TAIL, TAIL_TOP, nh.smoothstep(-0.1, 0.7, n.z))
        c = nh.lerp(c, nh.lerp(c, (0.3, 0.25, 0.23), 0.6), nh.smoothstep(0.75, 0.95, ring))
        return nh.lerp(c, FUR, nh.smoothstep(0.03, 0.0, along[i]))   # furred root
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


def details(surf):
    out = []
    # pink nose at the tip of the muzzle
    p, n = surf.snap((0, -0.36, 0.103))
    out.append((nh.uv_ellipsoid(p - n * 0.002, (0.009, 0.006, 0.007), 10, 6), NOSE))
    for sx in (1, -1):
        # black bead eyes, bulging a little on the sides of the head
        p, n = surf.snap((sx * 0.04, -0.28, 0.137))
        out.append((nh.uv_ellipsoid(p - n * 0.003, (0.0085, 0.0085, 0.008), 10, 8), EYE))
        # small rounded ears, furry, cupped forward and out
        p, n = surf.snap((sx * 0.035, -0.225, 0.162))
        ear = nh.uv_ellipsoid((0, 0, 0), (0.019, 0.02, 0.005), 12, 6,
                              deform=lambda v: 1.0 + 0.0 * v.z)
        for v in ear.verts:                      # cup it: rim bends forward
            v.co.z += 0.006 * (v.co.x / 0.019) ** 2
        ear = oriented(ear, Vector((sx * 0.5, -0.8, 0.3)).normalized(), p + Vector((0, 0, 0.012)))
        out.append((ear, lambda co, nn, s=sx: EAR_INNER if nn.y < -0.3 else EAR))
        # whiskers fanning from the whisker pads
        for k in range(6):
            u = k / 5.0
            p, n = surf.snap((sx * 0.035, -0.33 + 0.012 * u, 0.103 - 0.008 * u))
            d = (n * 0.4 + Vector((sx * 0.9, 0.25 + 0.2 * u, 0.12 - 0.25 * u))).normalized()
            out.append((nh.tube([p - n * 0.002, p + d * 0.04, p + d * 0.075 + Vector((0, 0, -0.008))],
                                [0.0008, 0.0005, 0.0], sides=3), WHISKER))
    for base, d, L in TOES:
        tip = base + d * L
        out.append((nh.tube([base - d * 0.004, base + d * L * 0.5 + Vector((0, 0, 0.001)), tip],
                            [0.0042, 0.0036, 0.003], sides=6), SKIN))
        out.append((nh.tube([tip, tip + d * 0.005 + Vector((0, 0, -0.003))], [0.0022, 0.0], sides=5), CLAW))
    return out


def build():
    TOES.clear()
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, FUR)
    fused = body.fuse(voxel=0.0145, smooth=5, smooth_factor=0.5, max_tris=None)
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
    obj = mb.to_object("BrownRat", roughness=0.6)
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
    nh.run(build, "BrownRat", ground=(0.36, 0.33, 0.27), views=((35, 25), (-90, 8), (160, 60)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0, -0.28, 0.12), 0.32, 35, 15)
