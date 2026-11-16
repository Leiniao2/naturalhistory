"""
Procedural Juramaia sinensis (Jurassic early eutherian mammal) for map colonies.

A tiny shrew-like insectivore scurrying low over the forest floor: one seamless
fused body (a slender, slightly arched torso, a narrow neck and a long, tapering
head drawn out into a pointed, mobile snout, slim limbs held a little out to the
sides on small grasping hands and feet). Soft dense fur is displaced into the
surface and repainted procedurally: warm grey-brown back flecked darker, buff
flanks and a pale cream belly, pink naked snout tip and feet.
Crisp details on top: big dark eyes, small rounded ears, a fan of whiskers, a
pink nose, long spread fingers and toes ending in curved climbing claws (the
hand bones point to a tree-climbing animal), and a long slender furred tail
held up off the ground in a balancing curve.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/juramaia_sinensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Juramaia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

FUR = (0.36, 0.27, 0.19)         # warm grey-brown back
FUR_DARK = (0.18, 0.13, 0.09)    # darker guard-hair flecks
FLANK = (0.55, 0.44, 0.32)       # buff flanks
BELLY = (0.82, 0.75, 0.62)       # pale cream belly
SKIN = (0.84, 0.60, 0.55)        # pink snout tip and feet
TAIL = (0.30, 0.23, 0.17)
TAIL_UNDER = (0.50, 0.41, 0.31)
EAR = (0.40, 0.30, 0.24)
EAR_INNER = (0.72, 0.55, 0.50)
EYE = (0.02, 0.02, 0.025)
NOSE = (0.55, 0.32, 0.30)
WHISKER = (0.15, 0.12, 0.10)
CLAW = (0.20, 0.16, 0.12)

HEAD = Vector((0.0, -0.22, 0.105))
TOES = []        # (base, direction, length) of every finger and toe


# ---------------------------------------------------------------- surface paint / fur

def fur(co, n):
    c = nh.lerp(FLANK, FUR, nh.smoothstep(-0.2, 0.6, n.z))
    c = nh.lerp(c, FUR_DARK, 0.5 * nh.smoothstep(0.1, 0.5, noise.noise(co * 80.0)))     # guard hairs
    c = nh.lerp(c, FUR_DARK, 0.25 * nh.smoothstep(0.55, 1.0, n.z))                      # darker back line
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.15, -0.55, n.z + 0.1 * noise.noise(co * 30.0)))
    if co.y < HEAD.y - 0.075:                                # naked pink snout tip
        c = nh.lerp(c, SKIN, nh.smoothstep(HEAD.y - 0.075, HEAD.y - 0.1, co.y))
    if co.z < 0.014:                                         # pink feet
        c = nh.lerp(c, SKIN, nh.smoothstep(0.014, 0.006, co.z))
    return c


def fur_displace(co, n):
    if co.z < 0.018 or co.y < HEAD.y - 0.06:
        return 0.0
    streak = noise.noise(Vector((co.x * 180.0, co.y * 45.0, co.z * 180.0)))
    return 0.0009 * noise.noise(co * 110.0) + 0.0007 * streak


# ---------------------------------------------------------------- fused body parts

def body_parts():
    h = HEAD
    parts = [
        nh.uv_ellipsoid((0, -0.09, 0.08), (0.048, 0.08, 0.05), 22, 14),        # chest
        nh.uv_ellipsoid((0, 0.03, 0.09), (0.056, 0.10, 0.056), 24, 16),        # slender, arched body
        nh.uv_ellipsoid((0, 0.12, 0.08), (0.052, 0.06, 0.05), 20, 12),         # hips
        nh.tube([(0, -0.12, 0.085), (0, -0.17, 0.095), h + Vector((0, 0.03, 0))], [0.04, 0.035, 0.032], sides=16),
        nh.uv_ellipsoid(h, (0.034, 0.045, 0.031), 20, 12),                     # small skull
        # long, tapering, pointed snout dipping slightly at the tip
        nh.tube([h + Vector((0, -0.025, -0.004)), h + Vector((0, -0.06, -0.012)), h + Vector((0, -0.09, -0.02)),
                 h + Vector((0, -0.11, -0.026))], [0.024, 0.0175, 0.012, 0.008], sides=14, scale_xy=(1.0, 0.85)),
    ]
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid(h + Vector((sx * 0.02, -0.01, -0.01)), (0.02, 0.03, 0.02), 12, 8))  # cheeks
        # front legs: slim, elbows a little out to the side
        parts.append(nh.tube([(sx * 0.03, -0.09, 0.07), (sx * 0.05, -0.095, 0.04), (sx * 0.055, -0.115, 0.014),
                              (sx * 0.056, -0.125, 0.008)], [0.021, 0.0135, 0.01, 0.009], sides=10))
        parts.append(nh.uv_ellipsoid((sx * 0.057, -0.13, 0.006), (0.011, 0.013, 0.0065), 10, 6))   # hand
        # hind legs: thigh, shin back to the heel, long slim foot
        parts.append(nh.uv_ellipsoid((sx * 0.04, 0.11, 0.075), (0.028, 0.045, 0.04), 14, 10))
        parts.append(nh.tube([(sx * 0.048, 0.09, 0.06), (sx * 0.062, 0.12, 0.032), (sx * 0.066, 0.145, 0.008)],
                             [0.019, 0.012, 0.009], sides=10))
        parts.append(nh.tube([(sx * 0.066, 0.15, 0.007), (sx * 0.068, 0.12, 0.0065), (sx * 0.07, 0.095, 0.0065)],
                             [0.009, 0.0105, 0.011], sides=8, scale_xy=(1.0, 0.65)))
        # long spread fingers and toes (crisp details); the inner toe diverges a little
        for a in (-0.75, -0.3, 0.05, 0.4, 0.75):
            d = Vector((math.sin(a) + sx * 0.25, -math.cos(a), 0)).normalized()
            TOES.append((Vector((sx * 0.057, -0.139, 0.003)), d, 0.016))
        for k, a in enumerate((-0.95, -0.35, 0.0, 0.3, 0.65)):
            a = a * -sx
            d = Vector((math.sin(a) + sx * 0.15, -math.cos(a), 0)).normalized()
            TOES.append((Vector((sx * 0.07, 0.088, 0.003)), d, (0.014, 0.018, 0.02, 0.019, 0.015)[k]))
    return parts


# ---------------------------------------------------------------- tail

TAIL_PTS = [Vector(p) for p in ((0, 0.16, 0.08), (0.0, 0.22, 0.085), (0.01, 0.29, 0.095), (0.03, 0.36, 0.095),
                                (0.06, 0.43, 0.085), (0.09, 0.50, 0.07), (0.105, 0.57, 0.055), (0.10, 0.63, 0.045))]
TAIL_R = [0.022, 0.0125, 0.0105, 0.009, 0.0078, 0.0066, 0.0052, 0.003]


def tail():
    """Long slender tail, longer than the body, held up off the ground in a gentle balancing curve;
    short-furred, darker above."""
    pts, rs = [], []
    for (a, b), (ra, rb) in zip(zip(TAIL_PTS, TAIL_PTS[1:]), zip(TAIL_R, TAIL_R[1:])):
        for k in range(5):
            t = k / 5
            pts.append(a.lerp(b, t))
            rs.append(ra + (rb - ra) * t)
    pts.append(TAIL_PTS[-1] + (TAIL_PTS[-1] - TAIL_PTS[-2]).normalized() * 0.006)
    rs.append(0.0)
    bm = nh.tube(pts, rs, sides=8, cap_start=False)

    def col(co, n):
        c = nh.lerp(TAIL_UNDER, TAIL, nh.smoothstep(-0.4, 0.4, n.z))
        return nh.lerp(c, FUR_DARK, 0.3 * nh.smoothstep(0.2, 0.6, noise.noise(co * 120.0)))
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
    h = HEAD
    p, n = surf.snap(h + Vector((0, -0.12, -0.025)))
    out.append((nh.uv_ellipsoid(p - n * 0.003, (0.005, 0.0035, 0.004), 10, 6), NOSE))
    for sx in (1, -1):
        # big dark eyes (a small nocturnal hunter)
        p, n = surf.snap(h + Vector((sx * 0.026, -0.03, 0.012)))
        out.append((nh.uv_ellipsoid(p - n * 0.002, (0.0085, 0.009, 0.008), 10, 8), EYE))
        # small rounded ears, cupped forward and out
        p, n = surf.snap(h + Vector((sx * 0.024, 0.012, 0.028)))
        ear = nh.uv_ellipsoid((0, 0, 0), (0.014, 0.015, 0.0035), 12, 6)
        for v in ear.verts:
            v.co.z += 0.005 * (v.co.x / 0.014) ** 2
        ear = oriented(ear, Vector((sx * 0.55, -0.75, 0.35)).normalized(), p + Vector((0, 0, 0.008)))
        out.append((ear, lambda co, nn: EAR_INNER if nn.y < -0.3 else EAR))
        # whiskers fanning from the sides of the snout
        for k in range(5):
            u = k / 4.0
            p, n = surf.snap(h + Vector((sx * 0.012, -0.085 + 0.02 * u, -0.018 - 0.004 * u)))
            d = (n * 0.4 + Vector((sx * 0.9, 0.3 + 0.2 * u, 0.1 - 0.25 * u))).normalized()
            out.append((nh.tube([p - n * 0.001, p + d * 0.03, p + d * 0.055 + Vector((0, 0, -0.005))],
                                [0.0007, 0.0005, 0.0], sides=3), WHISKER))
    for base, d, L in TOES:
        tip = base + d * L
        out.append((nh.tube([base - d * 0.003, base + d * L * 0.5 + Vector((0, 0, 0.0012)), tip],
                            [0.0026, 0.0022, 0.0018], sides=5), SKIN))
        # long curved climbing claws
        out.append((nh.tube([tip + Vector((0, 0, 0.001)), tip + d * 0.005 + Vector((0, 0, 0.0005)),
                             tip + d * 0.008 + Vector((0, 0, -0.003))], [0.0016, 0.0011, 0.0], sides=5), CLAW))
    return out


def build():
    TOES.clear()
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, FUR)
    fused = body.fuse(voxel=0.0085, smooth=5, smooth_factor=0.5, max_tris=3000)
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
    obj = mb.to_object("Juramaia", roughness=0.6)
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
    nh.run(build, "Juramaia", ground=(0.30, 0.34, 0.20), views=((35, 25), (-90, 8), (160, 60)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), HEAD + Vector((0, -0.05, -0.05)), 0.3, 30, 20)
