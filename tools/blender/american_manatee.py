"""
Procedural West Indian manatee (Trichechus manatus) for map colonies (large-animal detail).

One seamless fused body (torso, head, lip pads, flippers and a paddle tail that
thins to its edge) with fine skin creases and wrinkles displaced into the surface,
mottled grey-brown skin with green algae film and a few pale healed scars on the
back. Crisp details on top: a prehensile split upper lip covered in bristles,
nostrils on top of the snout, tiny eyes, and four nails on each flipper.
Faces -Y, pivot at the body centre (Swim style: shown at the water surface).

Usage:
  blender --background --python tools/blender/american_manatee.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AmericanManatee.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

SKIN = (0.40, 0.38, 0.34)        # grey-brown back
SKIN_DARK = (0.27, 0.26, 0.23)   # crease shadows / mottling
BELLY = (0.55, 0.53, 0.48)       # paler underside
ALGAE = (0.34, 0.42, 0.22)       # green film on the back
SCAR = (0.56, 0.54, 0.50)        # healed scars
LIP = (0.46, 0.42, 0.37)
BRISTLE = (0.86, 0.82, 0.72)     # pale stiff bristles
DARK = (0.08, 0.07, 0.06)
NAIL = (0.80, 0.76, 0.66)
EYE = (0.02, 0.02, 0.02)

# a few healed scars on the back: (start, end) in XY, painted and slightly sunk
SCARS = [((-0.10, -0.05), (0.12, 0.10)), ((0.06, 0.18), (0.16, 0.30)),
         ((-0.14, 0.26), (-0.04, 0.40)), ((0.02, -0.20), (0.10, -0.12))]


def _seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - ax - dx * t, p[1] - ay - dy * t)


def scar_amount(co, n):
    if n.z < 0.45:
        return 0.0
    d = min(_seg_dist((co.x, co.y), a, b) for a, b in SCARS)
    return nh.smoothstep(0.011, 0.003, d)


def crease(co):
    """0..1: fine transverse skin creases, wobbly and broken up, stronger behind the head."""
    w = noise.noise(co * 4.0) * 2.5 + noise.noise(co * 11.0) * 0.6
    line = abs(math.sin(co.y * 120.0 + w + 2.0 * noise.noise(co * 2.0)))
    k = (1.0 - line) ** 8                                   # thin lines
    k *= nh.smoothstep(0.0, 0.45, noise.noise(co * 7.0 + Vector((9, 2, 4))))  # broken, short creases
    neck = math.exp(-((co.y + 0.36) / 0.08) ** 2)            # neck folds
    return min(1.0, k * (0.6 + 1.2 * neck))


def displace(co, n):
    """Offset along the normal: fine wrinkle creases, skin pebbling, sunk scars."""
    d = -0.0035 * crease(co)
    d += 0.0012 * noise.noise(co * 70.0)
    d += 0.004 * noise.noise(co * 9.0)
    d -= 0.002 * scar_amount(co, n)
    # cleft between the two lobes of the split upper lip
    if co.y < -0.66 and co.z < 0.0:
        d -= 0.016 * math.exp(-(co.x / 0.014) ** 2) * nh.smoothstep(-0.66, -0.72, co.y)
    return d


def skin(co, n):
    up = nh.smoothstep(-0.6, 0.5, n.z)
    c = nh.lerp(BELLY, SKIN, up)
    mott = noise.noise(co * 7.0 + Vector((2.0, 5.0, 1.0)))
    c = nh.lerp(c, SKIN_DARK, 0.4 * max(0.0, mott))
    c = nh.lerp(c, nh.lerp(SKIN, BELLY, 0.5), 0.25 * max(0.0, noise.noise(co * 18.0)))
    c = nh.lerp(c, SKIN_DARK, 0.45 * crease(co))
    alg = noise.noise(co * 3.2 + Vector((7.0, 1.0, 3.0))) + 0.25 * noise.noise(co * 14.0)
    if n.z > 0.25 and alg > 0.12:
        c = nh.lerp(c, ALGAE, min(1.0, (alg - 0.12) * 4.0) * nh.smoothstep(0.25, 0.65, n.z) * 0.8)
    s = scar_amount(co, n)
    if s > 0:
        c = nh.lerp(c, SCAR, s * 0.7)
    if co.y < -0.62:  # muzzle a touch browner
        c = nh.lerp(c, LIP, 0.5)
    return c


# ---------------------------------------------------------------- body parts (fused)

def torso():
    # snout (-Y) to tail stock (+Y), smooth profile resampled densely
    prof = [(-0.56, 0.12, -0.05), (-0.48, 0.18, -0.04), (-0.40, 0.205, -0.03), (-0.34, 0.215, -0.02),
            (-0.20, 0.29, 0.0), (0.0, 0.33, 0.0), (0.22, 0.31, 0.0), (0.42, 0.24, -0.01),
            (0.60, 0.19, -0.02), (0.76, 0.14, -0.02), (0.90, 0.10, -0.02)]
    pts, rs = [], []
    for (y0, r0, z0), (y1, r1, z1) in zip(prof, prof[1:]):
        for k in range(4):
            t = k / 4
            ts = t * t * (3 - 2 * t)
            pts.append((0, y0 + (y1 - y0) * t, z0 + (z1 - z0) * ts))
            rs.append(r0 + (r1 - r0) * ts)
    pts.append((0, prof[-1][0], prof[-1][2]))
    rs.append(prof[-1][1])
    bm = nh.tube(pts, rs, sides=28, scale_xy=(1.0, 0.82))
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z *= 0.9  # flatter belly
    return bm


def muzzle():
    """Square-ish snout with the two big fleshy lobes of the split upper lip, chin below."""
    parts = [nh.uv_ellipsoid((0, -0.60, -0.06), (0.125, 0.09, 0.10), segments=24, rings=14)]
    for sx in (1, -1):
        parts.append(nh.uv_ellipsoid((sx * 0.058, -0.675, -0.085), (0.068, 0.06, 0.07),
                                     segments=20, rings=12))
    parts.append(nh.uv_ellipsoid((0, -0.635, -0.15), (0.07, 0.06, 0.035), segments=16, rings=8))  # chin
    return parts


def tail():
    """Large rounded paddle that thins out toward its edge."""
    bm = nh.uv_ellipsoid((0, 0, 0), (0.37, 0.31, 0.05), segments=40, rings=16)
    for v in bm.verts:
        t = nh.smoothstep(0.31, -0.31, v.co.y)          # 1 at the root
        rad = math.hypot(v.co.x / 0.37, v.co.y / 0.31)  # 0 centre .. 1 rim
        v.co.x *= 1.0 - 0.4 * t ** 2
        v.co.z *= (1.0 + 0.9 * t) * (1.0 - 0.4 * rad ** 2)
    nh.transform(bm, Matrix.Translation(Vector((0, 1.10, -0.02))))
    return bm


FLIPPER_TIPS = {}


def flipper(sx):
    """Paddle flipper flowing out of the chest, angled back and down."""
    root = Vector((sx * 0.20, -0.30, -0.08))
    a = Vector((sx * 0.31, -0.30, -0.14))
    b = Vector((sx * 0.40, -0.26, -0.19))
    tip = Vector((sx * 0.47, -0.21, -0.215))
    FLIPPER_TIPS[sx] = (b, tip)
    return nh.tube([root, a, b, tip, tip + Vector((sx * 0.025, 0.02, -0.005))],
                   [0.09, 0.065, 0.058, 0.045, 0.0], sides=14, scale_xy=(1.0, 0.42))


# ---------------------------------------------------------------- crisp details

class Surface:
    """Snaps detail positions onto the fused body."""

    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def snap(self, p, lift=0.0):
        hit, normal, _i, _d = self.tree.find_nearest(Vector(p))
        return hit + normal * lift, normal


def bristles(surf):
    """Short pale bristles studding the two lip pads, angled outward and down."""
    parts = []
    for sx in (1, -1):
        for i in range(13):
            for j in range(6):
                u = i / 12.0 + (0.5 / 12.0 if j % 2 else 0.0)
                v = j / 5.0
                ang = math.radians(-70 + 140 * u)
                p = (sx * (0.058 + 0.06 * math.sin(ang) * 0.9 + 0.012),
                     -0.675 - 0.06 * math.cos(ang) * 0.95,
                     -0.05 - 0.07 * v)
                base, nrm = surf.snap(p)
                if base.y > -0.64:  # keep them on the front/sides of the pads
                    continue
                tip = base + (nrm * 0.8 + Vector((0, 0, -0.4))).normalized() * 0.008
                parts.append(nh.tube([base - nrm * 0.002, tip], [0.0022, 0.0], sides=3))
    return parts


def nostrils(surf):
    parts = []
    for sx in (1, -1):
        base, nrm = surf.snap((sx * 0.028, -0.70, 0.0))
        # a crescent slit: flattened dark ellipsoid set into the top of the snout
        bm = nh.uv_ellipsoid((0, 0, 0), (0.010, 0.0055, 0.003), segments=10, rings=6)
        nh.transform(bm, Matrix.Rotation(math.radians(sx * 25), 4, "Z"))
        rot = Vector((0, 0, 1)).rotation_difference(nrm).to_matrix().to_4x4()
        nh.transform(bm, rot)
        nh.transform(bm, Matrix.Translation(base))
        parts.append(bm)
    return parts


def eyes(surf):
    parts = []
    for sx in (1, -1):
        base, nrm = surf.snap((sx * 0.16, -0.50, 0.03))
        parts.append((nh.ellipsoid(base - nrm * 0.004, (0.009, 0.009, 0.009), subdivisions=2), EYE))
    return parts


def nails(surf):
    parts = []
    for sx in (1, -1):
        b, tip = FLIPPER_TIPS[sx]
        for k in range(4):
            t = 0.25 + 0.17 * k
            p = b.lerp(tip, 0.55) + Vector((0, (t - 0.5) * 0.09, 0.03))
            base, nrm = surf.snap(p)
            bm = nh.uv_ellipsoid((0, 0, 0), (0.011, 0.013, 0.005), segments=10, rings=6)
            rot = Vector((0, 0, 1)).rotation_difference(nrm).to_matrix().to_4x4()
            nh.transform(bm, rot)
            nh.transform(bm, Matrix.Translation(base + nrm * 0.001))
            parts.append(bm)
    return parts


def build():
    body = nh.MeshBuilder()
    body.add(torso(), SKIN)
    for p in muzzle():
        body.add(p, SKIN)
    body.add(tail(), SKIN)
    for sx in (1, -1):
        body.add(flipper(sx), SKIN)
    fused = body.fuse(voxel=0.0235, smooth=5, smooth_factor=0.5, max_tris=None)

    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * displace(v.co, v.normal)
    fused.normal_update()
    surf = Surface(fused)

    mb = nh.MeshBuilder()
    details = []
    details += [(b, BRISTLE) for b in bristles(surf)]
    details += [(b, DARK) for b in nostrils(surf)]
    details += eyes(surf)
    details += [(b, NAIL) for b in nails(surf)]
    # mouth split between the lip pads
    details.append((nh.uv_ellipsoid(surf.snap((0, -0.73, -0.09))[0], (0.003, 0.008, 0.03),
                                    segments=8, rings=6), SKIN_DARK))
    mb.add(fused, color=skin)
    for bm, col in details:
        mb.add(bm, col)
    return mb.to_object("AmericanManatee", roughness=0.75)


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
    nh.run(build, "AmericanManatee", background=(0.10, 0.32, 0.36),
           views=((35, 35), (-90, 8), (160, 70)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0, -0.62, -0.05), 0.75, 30, 20)
