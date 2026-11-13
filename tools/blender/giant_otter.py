"""
Procedural low-poly giant otter (Pteronura brasiliensis) for map colonies.

A long, sleek chocolate-brown body standing on four short shaped legs with
webbed feet, head raised alert on a thick neck, a long flattened paddle tail
tapering to a point, a broad flat head with small round ears and whiskers, and
the irregular creamy throat patch every giant otter has (unique per animal).
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
from mathutils import Vector, Matrix, noise  # noqa: E402

FUR = (0.20, 0.12, 0.07)         # dark chocolate back
FUR_SHEEN = (0.32, 0.20, 0.11)   # wet highlights on the flanks
CREAM = (0.90, 0.82, 0.62)       # throat patch
NOSE = (0.05, 0.04, 0.04)
EYE = (0.02, 0.02, 0.02)
WHISKER = (0.75, 0.70, 0.60)
FOOT = (0.14, 0.09, 0.06)


def fur(co, n):
    side = nh.smoothstep(0.9, 0.0, n.z)
    c = nh.lerp(FUR, FUR_SHEEN, 0.5 * side)
    return nh.lerp(c, FUR_SHEEN, 0.3 * max(0.0, noise.noise(co * 14.0)))


def throat(co, n):
    """Creamy, ragged-edged patch on the front of the throat and chest."""
    c = fur(co, n)
    if co.y < -0.22 and n.y < 0.2:
        front = -n.y * 0.8 - n.z * 0.7 - abs(n.x) * 0.35  # under the chin and down the throat
        edge = 0.0 + 0.3 * noise.noise(co * 12.0 + Vector((3, 1, 7)))
        h = nh.smoothstep(0.2, 0.25, co.z) * nh.smoothstep(0.48, 0.43, co.z)
        if front > edge and h > 0.0:
            return nh.lerp(c, CREAM, h * nh.smoothstep(edge, edge + 0.08, front))
    return c


def torso():
    # chest (-Y) to hips (+Y) to tail root; slight arch over the back
    # elliptical profile so both ends round off like a real rump/chest; slight arch over the back
    pts, rs = [], []
    n = 18
    for i in range(n + 1):
        t = -1.0 + 2.0 * i / n                       # -1 chest .. +1 rump
        y = 0.38 * t
        z = 0.205 + 0.04 * (1 - t * t) - 0.012 * t
        r = 0.127 * (1.0 - abs(t) ** 2.4) ** 0.5 * (1.0 - 0.06 * t)
        pts.append((0, y, z))
        rs.append(max(r, 0.0))
    return nh.tube(pts, rs, sides=16, scale_xy=(0.95, 1.0))


def neck_head():
    parts = []
    # thick neck rising forward from the chest
    neck = nh.tube([(0, -0.18, 0.225), (0, -0.36, 0.29), (0, -0.42, 0.37), (0, -0.46, 0.42)],
                   [0.112, 0.102, 0.092, 0.086], sides=14)
    parts.append((neck, throat))
    # broad, flat head
    head = nh.uv_ellipsoid((0, -0.50, 0.445), (0.104, 0.11, 0.072), segments=18, rings=10)
    parts.append((head, throat))
    # blunt muzzle
    muzzle = nh.uv_ellipsoid((0, -0.59, 0.432), (0.07, 0.062, 0.046), segments=14, rings=8)
    parts.append((muzzle, throat))
    parts.append((nh.uv_ellipsoid((0, -0.64, 0.445), (0.03, 0.018, 0.02), segments=8, rings=6), NOSE))
    for sx in (1, -1):
        # small round ears set low on the sides of the head
        parts.append((nh.uv_ellipsoid((sx * 0.09, -0.465, 0.49), (0.018, 0.012, 0.02),
                                      segments=8, rings=5), FUR))
        parts.append((nh.ellipsoid((sx * 0.058, -0.57, 0.478), (0.014, 0.014, 0.014), subdivisions=1), EYE))
        # whiskers fanning back and out from the muzzle
        for k in range(3):
            root = Vector((sx * 0.052, -0.61, 0.42 + 0.012 * k))
            tip = root + Vector((sx * 0.11, 0.03 + 0.015 * k, -0.01 + 0.015 * k))
            parts.append((nh.tube([root, tip], [0.003, 0.0], sides=3), WHISKER))
    return parts


def tail():
    """Long, flattened paddle tail: thick at the root, widening sideways, ending in a point."""
    pts = [(0, 0.22, 0.205), (0, 0.42, 0.16), (0, 0.56, 0.12), (0, 0.70, 0.085), (0, 0.84, 0.06), (0, 0.95, 0.05)]
    rs = [0.085, 0.07, 0.058, 0.044, 0.025, 0.0]
    bm = nh.tube(pts, rs, sides=10, scale_xy=(1.35, 0.55))
    # root stays round, flattening increases toward the middle
    for v in bm.verts:
        t = nh.smoothstep(0.30, 0.50, v.co.y)
        z0 = 0.19 + (0.05 - 0.19) * (v.co.y - 0.30) / 0.65
        v.co.z = z0 + (v.co.z - z0) * (1.0 - 0.0 * t)
    return bm


def leg(sx, front):
    """Shaped leg: muscular upper limb blending into the body, tapering to the wrist,
    flat webbed paw with five toes."""
    if front:
        top = Vector((sx * 0.075, -0.22, 0.22))
        elbow = Vector((sx * 0.095, -0.205, 0.12))
        wrist = Vector((sx * 0.095, -0.235, 0.045))
        radii = [0.07, 0.048, 0.034]
        paw_c = Vector((sx * 0.097, -0.27, 0.018))
        paw_r = (0.042, 0.055, 0.02)
    else:
        top = Vector((sx * 0.075, 0.20, 0.215))
        elbow = Vector((sx * 0.105, 0.15, 0.12))   # knee forward
        wrist = Vector((sx * 0.105, 0.20, 0.05))   # hock back
        radii = [0.085, 0.052, 0.034]
        paw_c = Vector((sx * 0.107, 0.15, 0.018))
        paw_r = (0.048, 0.068, 0.02)
    limb = nh.tube([top, elbow, wrist, paw_c + Vector((0, 0.01, 0.01))], radii + [0.03], sides=9)
    paw = nh.uv_ellipsoid(paw_c, paw_r, segments=10, rings=6)
    toes = []
    for k in range(5):
        a = math.radians(-50 + 25 * k)
        p = paw_c + Vector((math.sin(a) * paw_r[0] * 1.05, -math.cos(a) * paw_r[1] * 1.0, -0.004))
        toes.append(nh.ellipsoid(p, (0.012, 0.014, 0.011), subdivisions=1))
    # webbing: thin flat fan joining the toes
    outline = [paw_c + Vector((math.sin(math.radians(-55 + 27.5 * k)) * paw_r[0] * 1.15,
                               -math.cos(math.radians(-55 + 27.5 * k)) * paw_r[1] * 1.1, -0.008))
               for k in range(5)]
    outline.append(paw_c + Vector((0, 0.02, -0.008)))
    web = nh.flat_panel([tuple(p) for p in outline], thickness=0.006)
    return limb, paw, toes, web


def build():
    mb = nh.MeshBuilder()
    mb.add(torso(), fur)
    for bm, col in neck_head():
        mb.add(bm, col)
    mb.add(tail(), fur)
    for sx in (1, -1):
        for front in (True, False):
            limb, paw, toes, web = leg(sx, front)
            mb.add(limb, fur)
            mb.add(paw, FOOT)
            for t in toes:
                mb.add(t, FOOT)
            mb.add(web, FOOT, smooth=False)
    obj = mb.to_object("GiantOtter", roughness=0.5)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "GiantOtter", ground=(0.30, 0.40, 0.24), views=((35, 25), (-90, 8), (160, 60)))
