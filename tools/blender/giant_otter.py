"""
Procedural giant otter (Pteronura brasiliensis) for map colonies (large-animal detail).

One seamless fused body: a long sleek torso with defined shoulders and haunches,
a thick neck lifting the head alert, a sculpted head (broad flat skull, whisker
pads, chin), shaped legs on webbed five-toed feet, and a long tail that flattens
into a paddle. Short dense fur is displaced into the surface, and the body is
repainted procedurally: dark chocolate back, wet sheen on the flanks and the
crisp, ragged creamy throat patch that is unique to every giant otter.
Crisp details on top: nose pad with nostrils, eyes, small round ears, whiskers, claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/giant_otter.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GiantOtter.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

FUR = (0.19, 0.11, 0.065)        # dark chocolate back
FUR_SHEEN = (0.31, 0.19, 0.105)  # wet highlights on the flanks
FUR_TIP = (0.36, 0.24, 0.14)     # lighter guard-hair tips
CREAM = (0.90, 0.82, 0.62)       # throat patch
PAW = (0.13, 0.08, 0.05)
NOSE = (0.05, 0.04, 0.04)
EYE = (0.015, 0.015, 0.015)
WHISKER = (0.78, 0.74, 0.64)
CLAW = (0.20, 0.17, 0.14)


# ---------------------------------------------------------------- surface paint / fur

def throat_mask(co, n):
    """0..1 crisp, ragged creamy patch under the chin and down the throat."""
    if co.y > -0.22 or co.z < 0.22 or co.z > 0.46:
        return 0.0
    f = -n.z * 0.8 - n.y * 0.55 - abs(n.x) * 0.45
    f += 0.35 * noise.noise(co * 9.0 + Vector((3, 1, 7))) + 0.12 * noise.noise(co * 26.0)
    f -= 0.6 * nh.smoothstep(-0.30, -0.22, co.y)          # fade out toward the chest
    return nh.smoothstep(0.14, 0.2, f)


def fur(co, n):
    side = nh.smoothstep(0.9, 0.0, n.z)
    c = nh.lerp(FUR, FUR_SHEEN, 0.55 * side)
    c = nh.lerp(c, FUR_TIP, 0.35 * max(0.0, noise.noise(co * 30.0)))   # dense fur flecks
    c = nh.lerp(c, FUR, 0.4 * max(0.0, noise.noise(co * 5.0)))
    if co.z < 0.05:                                                   # feet
        c = nh.lerp(c, PAW, nh.smoothstep(0.05, 0.02, co.z))
    if co.y < -0.6:                                                   # darker muzzle
        c = nh.lerp(c, FUR, 0.5)
    m = throat_mask(co, n)
    return nh.lerp(c, CREAM, m) if m > 0 else c


def fur_displace(co, n):
    """Short dense fur: fine noise, a little streaking along the body, flat on the feet."""
    if co.z < 0.04:
        return 0.0
    streak = noise.noise(Vector((co.x * 70.0, co.y * 18.0, co.z * 70.0)))
    return 0.0016 * noise.noise(co * 55.0) + 0.0012 * streak


# ---------------------------------------------------------------- fused body parts

def torso():
    pts, rs = [], []
    n = 22
    for i in range(n + 1):
        t = -1.0 + 2.0 * i / n                        # -1 chest .. +1 rump
        pts.append((0, 0.38 * t, 0.205 + 0.04 * (1 - t * t) - 0.012 * t))
        rs.append(max(0.0, 0.124 * (1.0 - abs(t) ** 2.4) ** 0.5 * (1.0 - 0.05 * t)))
    return [nh.tube(pts, rs, sides=22, scale_xy=(0.95, 1.0))]


def shoulders_haunches():
    parts = []
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid((sx * 0.055, -0.22, 0.215), (0.07, 0.10, 0.09), segments=18, rings=12))
        parts.append(nh.uv_ellipsoid((sx * 0.062, 0.19, 0.205), (0.075, 0.12, 0.095), segments=18, rings=12))
    return parts


def neck_head():
    parts = [
        # thick neck rising forward from the chest
        nh.tube([(0, -0.18, 0.225), (0, -0.30, 0.255), (0, -0.38, 0.31), (0, -0.43, 0.37), (0, -0.47, 0.42)],
                [0.112, 0.108, 0.098, 0.09, 0.085], sides=22),
        # broad, flat skull
        nh.uv_ellipsoid((0, -0.50, 0.448), (0.103, 0.105, 0.066), segments=24, rings=14),
        # muzzle, whisker pads and chin
        nh.uv_ellipsoid((0, -0.585, 0.437), (0.06, 0.065, 0.044), segments=20, rings=12),
        nh.uv_ellipsoid((0, -0.565, 0.398), (0.045, 0.05, 0.03), segments=16, rings=10),
    ]
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid((sx * 0.038, -0.60, 0.425), (0.042, 0.04, 0.034), segments=16, rings=10))
        parts.append(nh.uv_ellipsoid((sx * 0.07, -0.49, 0.43), (0.05, 0.06, 0.045), segments=16, rings=10))  # cheeks
    return parts


TOE_TIPS = []


def leg(sx, front):
    """Shaped leg (muscle tapering to the wrist) on a webbed five-toed foot."""
    if front:
        top = Vector((sx * 0.07, -0.22, 0.20))
        elbow = Vector((sx * 0.093, -0.205, 0.115))
        wrist = Vector((sx * 0.095, -0.235, 0.045))
        radii = [0.06, 0.044, 0.03, 0.028]
        paw_c = Vector((sx * 0.097, -0.272, 0.018))
        paw_r = (0.04, 0.05, 0.018)
    else:
        top = Vector((sx * 0.072, 0.19, 0.19))
        elbow = Vector((sx * 0.104, 0.145, 0.115))   # knee forward
        wrist = Vector((sx * 0.104, 0.20, 0.05))     # hock back
        radii = [0.07, 0.048, 0.03, 0.028]
        paw_c = Vector((sx * 0.106, 0.148, 0.018))
        paw_r = (0.045, 0.062, 0.018)
    parts = [nh.tube([top, elbow, wrist, paw_c + Vector((0, 0.012, 0.012))], radii, sides=14),
             nh.uv_ellipsoid(paw_c, paw_r, segments=16, rings=10)]
    outline = []
    for k in range(5):
        a = math.radians(-52 + 26 * k)
        d = Vector((math.sin(a), -math.cos(a), 0))
        tip = paw_c + Vector((d.x * paw_r[0] * 1.45, d.y * paw_r[1] * 1.35, -0.004))
        parts.append(nh.tube([paw_c + Vector((d.x * paw_r[0] * 0.5, d.y * paw_r[1] * 0.5, 0.0)), tip],
                             [0.013, 0.010], sides=8))
        TOE_TIPS.append((tip, d))
        outline.append(paw_c + Vector((d.x * paw_r[0] * 1.3, d.y * paw_r[1] * 1.2, -0.006)))
    outline.append(paw_c + Vector((0, 0.025, -0.006)))
    parts.append(nh.flat_panel([tuple(p) for p in outline], thickness=0.012))  # webbing
    return parts


def tail():
    """Long tail: thick at the root, flattening sideways into a paddle, ending in a point."""
    pts = [(0, 0.22, 0.205), (0, 0.34, 0.18), (0, 0.46, 0.15), (0, 0.58, 0.118), (0, 0.70, 0.088),
           (0, 0.82, 0.065), (0, 0.92, 0.052), (0, 0.98, 0.046)]
    rs = [0.085, 0.075, 0.066, 0.056, 0.044, 0.03, 0.016, 0.0]
    bm = nh.tube(pts, rs, sides=18)
    for v in bm.verts:
        t = nh.smoothstep(0.32, 0.6, v.co.y)          # round root, flat paddle beyond
        axis_z = 0.205 + (0.046 - 0.205) * (v.co.y - 0.22) / 0.76
        v.co.x *= 1.0 + 0.6 * t
        v.co.z = axis_z + (v.co.z - axis_z) * (1.0 - 0.5 * t)
    return [bm]


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
    # nose pad: broad dark pad with two nostril slits
    base, nrm = surf.snap((0, -0.655, 0.452))
    out.append((oriented(nh.uv_ellipsoid((0, 0, 0), (0.024, 0.015, 0.008), segments=14, rings=8), nrm, base - nrm * 0.002), NOSE))
    for sx in (1, -1):
        p, n = surf.snap((sx * 0.011, -0.665, 0.448))
        out.append((oriented(nh.uv_ellipsoid((0, 0, 0), (0.006, 0.0035, 0.004), segments=8, rings=5),
                             n, p + n * 0.007, spin=math.radians(sx * 30)), (0.0, 0.0, 0.0)))
    for sx in (1, -1):
        # eyes
        p, n = surf.snap((sx * 0.055, -0.575, 0.478))
        out.append((nh.ellipsoid(p - n * 0.004, (0.011, 0.011, 0.011), subdivisions=2), EYE))
        # small round ears, set low and back
        p, n = surf.snap((sx * 0.095, -0.455, 0.49))
        ear = nh.uv_ellipsoid((0, 0, 0), (0.02, 0.008, 0.017), segments=12, rings=8)
        out.append((oriented(ear, Vector((sx, 0.3, 0.2)).normalized(), p, spin=0.0), FUR))
        # whiskers from the whisker pads, fanning back and out
        for k in range(8):
            u = k / 7.0
            p, n = surf.snap((sx * 0.06, -0.62 + 0.03 * u, 0.44 - 0.03 * u))
            d = (n * 0.5 + Vector((sx * 0.9, 0.35 + 0.2 * u, 0.05 - 0.15 * u))).normalized()
            out.append((nh.tube([p - n * 0.002, p + d * 0.06, p + d * 0.11 + Vector((0, 0, -0.012))],
                                [0.0018, 0.0012, 0.0], sides=3), WHISKER))
    # claws on every toe
    for tip, d in TOE_TIPS:
        base = tip + Vector((d.x * 0.002, d.y * 0.002, 0.0))
        out.append((nh.tube([base, base + Vector((d.x * 0.01, d.y * 0.01, -0.009))], [0.0045, 0.0], sides=6), CLAW))
    return out


def build():
    TOE_TIPS.clear()
    body = nh.MeshBuilder()
    parts = torso() + shoulders_haunches() + neck_head() + tail()
    for sx in (1, -1):
        for front in (True, False):
            parts += leg(sx, front)
    for p in parts:
        body.add(p, FUR)
    fused = body.fuse(voxel=0.0142, smooth=5, smooth_factor=0.5, max_tris=None)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * fur_displace(v.co, v.normal)
    fused.normal_update()
    surf = Surface(fused)

    mb = nh.MeshBuilder()
    extra = details(surf)
    mb.add(fused, color=fur)
    for bm, col in extra:
        mb.add(bm, col)
    obj = mb.to_object("GiantOtter", roughness=0.5)
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
    nh.run(build, "GiantOtter", ground=(0.30, 0.40, 0.24), views=((35, 25), (-90, 8), (160, 60)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0, -0.56, 0.44), 0.5, 35, 15)
