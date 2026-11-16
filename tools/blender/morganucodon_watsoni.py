"""
Procedural Morganucodon watsoni (Late Triassic-Early Jurassic mammaliaform, ~10 cm) for map
colonies.

One of the earliest mammal relatives, a shrew-like insect-eater, scurrying low to the
ground: one seamless fused body (long, low torso, slightly arched over the loins, a short
neck and a long, narrow head tapering to a pointed, mobile snout). The legs are short and
held a little out to the sides (more sprawling than in most living mammals), the elbows
and knees bent outward, on small five-toed hands and feet.
Dense fur is displaced into the surface and the body is repainted procedurally: warm
grey-brown back with darker guard-hair flecks, paler buff-grey flanks and a pale belly,
pinkish snout tip and feet.
Crisp details on top: the long, thin, furred tail curving along the ground, small rounded
ears, small black bead eyes, a pink nose, whiskers, and fingers and toes with tiny claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/morganucodon_watsoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Morganucodon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

NAME = "Morganucodon"

FUR = (0.38, 0.29, 0.20)         # warm grey-brown back
FUR_DARK = (0.19, 0.14, 0.10)    # dark guard-hair tips
FUR_FLANK = (0.54, 0.46, 0.36)   # buff-grey flanks
BELLY = (0.76, 0.70, 0.60)       # pale belly
SKIN = (0.82, 0.60, 0.54)        # pink feet, snout tip
TAIL = (0.36, 0.28, 0.20)
TAIL_UNDER = (0.56, 0.48, 0.38)
EAR = (0.44, 0.34, 0.27)
EAR_INNER = (0.68, 0.52, 0.47)
EYE = (0.02, 0.02, 0.02)
NOSE = (0.72, 0.46, 0.44)
WHISKER = (0.16, 0.14, 0.12)
CLAW = (0.86, 0.82, 0.76)

TOES = []        # (base, direction, length) of every finger and toe
HIP_Z = 0.075


# ---------------------------------------------------------------- surface paint / fur

def snout(co):
    """1 on the short-haired, pointed tip of the snout."""
    return nh.smoothstep(-0.322, -0.345, co.y)


def fur(co, n):
    c = nh.lerp(FUR_FLANK, FUR, nh.smoothstep(-0.2, 0.6, n.z))
    c = nh.lerp(c, FUR_DARK, 0.5 * nh.smoothstep(0.1, 0.5, noise.noise(co * 80.0)))   # guard hairs
    c = nh.lerp(c, FUR_FLANK, 0.2 * max(0.0, noise.noise(co * 20.0)))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.15, -0.55, n.z + 0.1 * noise.noise(co * 25.0)))
    c = nh.lerp(c, SKIN, 0.8 * snout(co))
    if co.z < 0.016:                                         # pink feet
        c = nh.lerp(c, SKIN, nh.smoothstep(0.016, 0.008, co.z))
    return c


def fur_displace(co, n):
    if co.z < 0.018:
        return 0.0
    streak = noise.noise(Vector((co.x * 180.0, co.y * 45.0, co.z * 180.0)))
    return (1.0 - snout(co)) * (0.0012 * noise.noise(co * 100.0) + 0.0009 * streak)


# ---------------------------------------------------------------- fused body parts

def body_parts():
    parts = [
        nh.uv_ellipsoid((0, -0.09, 0.075), (0.052, 0.10, 0.050), 22, 14),        # chest
        nh.uv_ellipsoid((0, 0.04, 0.084), (0.064, 0.13, 0.060), 24, 16),         # long, slightly arched body
        nh.uv_ellipsoid((0, 0.14, 0.076), (0.058, 0.07, 0.054), 22, 14),         # hips
        nh.tube([(0, -0.13, 0.078), (0, -0.18, 0.083), (0, -0.215, 0.086)], [0.044, 0.038, 0.034], sides=18),  # neck
        nh.uv_ellipsoid((0, -0.225, 0.088), (0.034, 0.052, 0.032), 20, 12),      # braincase
        nh.tube([(0, -0.25, 0.085), (0, -0.285, 0.077), (0, -0.315, 0.069), (0, -0.338, 0.063)],
                [0.029, 0.021, 0.0145, 0.0095], sides=16, scale_xy=(1.0, 0.85)),   # long pointed snout
    ]
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid((sx * 0.022, -0.235, 0.078), (0.022, 0.035, 0.022), 12, 8))   # cheeks
        # front legs: short, elbows bent out to the side
        parts.append(nh.uv_ellipsoid((sx * 0.040, -0.10, 0.065), (0.026, 0.035, 0.030), 12, 8))     # shoulder
        parts.append(nh.tube([(sx * 0.042, -0.10, 0.062), (sx * 0.066, -0.105, 0.036), (sx * 0.062, -0.125, 0.014),
                              (sx * 0.060, -0.135, 0.006)], [0.020, 0.013, 0.009, 0.007], sides=12))
        parts.append(nh.uv_ellipsoid((sx * 0.062, -0.142, 0.006), (0.011, 0.013, 0.006), 10, 6))    # hand
        # hind legs: haunch, knee bent out, shin back to the heel, foot flat on the ground
        parts.append(nh.uv_ellipsoid((sx * 0.046, 0.13, 0.066), (0.032, 0.05, 0.042), 16, 10))
        parts.append(nh.tube([(sx * 0.052, 0.11, 0.055), (sx * 0.078, 0.10, 0.030), (sx * 0.070, 0.15, 0.010)],
                             [0.020, 0.012, 0.008], sides=12))
        parts.append(nh.tube([(sx * 0.070, 0.155, 0.006), (sx * 0.070, 0.125, 0.005), (sx * 0.069, 0.100, 0.005)],
                             [0.009, 0.010, 0.009], sides=10, scale_xy=(1.0, 0.75)))
        for a in (-0.7, -0.35, 0.0, 0.35, 0.7):
            d = Vector((math.sin(a) + sx * 0.25, -math.cos(a), 0)).normalized()
            for base, L in ((Vector((sx * 0.063, -0.150, 0.004)), 0.012), (Vector((sx * 0.069, 0.093, 0.004)), 0.014)):
                TOES.append((base, d, L * (0.75 if abs(a) > 0.6 else 1.0)))
    return parts


# ---------------------------------------------------------------- tail

TAIL_PTS = [Vector(p) for p in ((0, 0.18, 0.068), (0.006, 0.23, 0.045), (0.022, 0.28, 0.022), (0.05, 0.33, 0.011),
                                (0.09, 0.38, 0.008), (0.12, 0.43, 0.007), (0.13, 0.48, 0.007), (0.115, 0.53, 0.006))]
TAIL_R = [0.017, 0.012, 0.0095, 0.0080, 0.0068, 0.0056, 0.0045, 0.003]


def tail():
    """Long, thin furred tail resting on the ground in a lazy curve, darker above."""
    pts, rs = [], []
    for (a, b), (ra, rb) in zip(zip(TAIL_PTS, TAIL_PTS[1:]), zip(TAIL_R, TAIL_R[1:])):
        for k in range(6):
            t = k / 6
            pts.append(a.lerp(b, t))
            rs.append(ra + (rb - ra) * t)
    pts.append(TAIL_PTS[-1] + (TAIL_PTS[-1] - TAIL_PTS[-2]).normalized() * 0.008)
    rs.append(0.0)
    bm = nh.tube(pts, rs, sides=8, cap_start=False)

    def col(co, n):
        c = nh.lerp(TAIL_UNDER, TAIL, nh.smoothstep(-0.3, 0.5, n.z))
        return nh.lerp(c, FUR_DARK, 0.35 * nh.smoothstep(0.0, 0.6, noise.noise(co * 120.0)))
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
    p, n = surf.snap((0, -0.36, 0.064))
    out.append((nh.uv_ellipsoid(p - n * 0.0025, (0.0065, 0.004, 0.0052), 10, 6), NOSE))
    for sx in (1, -1):
        # small black bead eyes
        p, n = surf.snap((sx * 0.03, -0.26, 0.098))
        out.append((nh.uv_ellipsoid(p - n * 0.002, (0.0055, 0.0055, 0.005), 10, 8), EYE))
        # small rounded ears
        p, n = surf.snap((sx * 0.026, -0.205, 0.118))
        ear = nh.uv_ellipsoid((0, 0, 0), (0.012, 0.012, 0.0035), 12, 6)
        for v in ear.verts:                      # cup it: rim bends forward
            v.co.z += 0.004 * (v.co.x / 0.012) ** 2
        ear = oriented(ear, Vector((sx * 0.55, -0.8, 0.25)).normalized(), p + Vector((0, 0, 0.004)))
        out.append((ear, lambda co, nn: EAR_INNER if nn.y < -0.3 else EAR))
        # whiskers fanning from the snout
        for k in range(5):
            u = k / 4.0
            p, n = surf.snap((sx * 0.02, -0.318 + 0.012 * u, 0.070 - 0.006 * u))
            d = (n * 0.4 + Vector((sx * 0.9, 0.25 + 0.2 * u, 0.12 - 0.25 * u))).normalized()
            out.append((nh.tube([p - n * 0.002, p + d * 0.03, p + d * 0.055 + Vector((0, 0, -0.006))],
                                [0.0006, 0.0004, 0.0], sides=3), WHISKER))
    for base, d, L in TOES:
        tip = base + d * L
        out.append((nh.tube([base - d * 0.003, base + d * L * 0.5 + Vector((0, 0, 0.001)), tip],
                            [0.0030, 0.0026, 0.0021], sides=6), SKIN))
        out.append((nh.tube([tip, tip + d * 0.004 + Vector((0, 0, -0.002))], [0.0016, 0.0], sides=5), CLAW))
    return out


def build():
    TOES.clear()
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, FUR)
    fused = body.fuse(voxel=0.0105, smooth=5, smooth_factor=0.5, max_tris=None)
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
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"  height {max(zs):.3f}, hip {HIP_Z:.3f} -> hip fraction {HIP_Z / max(zs):.2f}")
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
    nh.run(build, NAME, ground=(0.36, 0.33, 0.27), views=((35, 25), (-90, 8), (160, 60)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0, -0.27, 0.08), 0.26, 35, 15)
