"""
Procedural low-poly West Indian manatee (Trichechus manatus) for map colonies.

A big rounded grey-brown torpedo with wrinkly, mottled skin and a few algae
patches on the back, a broad rounded paddle tail, two small flippers with
nails, and a blunt, bristly snout with a split upper lip and tiny eyes.
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
from mathutils import Vector, Matrix, noise  # noqa: E402

SKIN = (0.40, 0.38, 0.34)        # grey-brown back
SKIN_DARK = (0.30, 0.29, 0.26)   # wrinkle shadows / mottling
BELLY = (0.56, 0.54, 0.49)       # paler underside
ALGAE = (0.36, 0.44, 0.24)       # green film on the back
SNOUT = (0.48, 0.44, 0.38)
BRISTLE = (0.16, 0.14, 0.12)
NAIL = (0.78, 0.74, 0.64)
EYE = (0.03, 0.03, 0.03)


def skin(co, n):
    up = nh.smoothstep(-0.6, 0.5, n.z)
    c = nh.lerp(BELLY, SKIN, up)
    # mottling and wrinkle rings
    mott = noise.noise(co * 6.0 + Vector((2.0, 5.0, 1.0)))
    c = nh.lerp(c, SKIN_DARK, 0.45 * max(0.0, mott))
    wr = 0.5 + 0.5 * math.sin(co.y * 60.0 + noise.noise(co * 3.0) * 3.0)
    c = nh.lerp(c, SKIN_DARK, 0.3 * wr ** 3 * (1.0 - abs(n.y)))
    # neck crease behind the head
    c = nh.lerp(c, SKIN_DARK, 0.6 * max(0.0, 1.0 - abs(co.y + 0.36) / 0.035))
    # algae patches on top only
    alg = noise.noise(co * 3.2 + Vector((7.0, 1.0, 3.0)))
    if n.z > 0.3 and alg > 0.15:
        c = nh.lerp(c, ALGAE, min(1.0, (alg - 0.15) * 4.0) * nh.smoothstep(0.3, 0.65, n.z) * 0.85)
    return c


def body():
    # snout (-Y) to tail stock (+Y): a smooth profile resampled densely along the length
    prof = [(-0.60, 0.10, -0.06), (-0.52, 0.17, -0.045), (-0.42, 0.20, -0.03), (-0.34, 0.215, -0.02),
            (-0.20, 0.29, 0.0), (0.0, 0.33, 0.0), (0.22, 0.31, 0.0), (0.42, 0.24, -0.01),
            (0.60, 0.19, -0.02), (0.76, 0.14, -0.02), (0.90, 0.11, -0.02)]
    pts, rs = [], []
    steps = 4
    for (y0, r0, z0), (y1, r1, z1) in zip(prof, prof[1:]):
        for k in range(steps):
            t = k / steps
            ts = t * t * (3 - 2 * t)
            pts.append((0, y0 + (y1 - y0) * t, z0 + (z1 - z0) * ts))
            rs.append(r0 + (r1 - r0) * ts)
    pts.append((0, prof[-1][0], prof[-1][2]))
    rs.append(prof[-1][1])
    bm = nh.tube(pts, rs, sides=22, scale_xy=(1.0, 0.82))
    for v in bm.verts:
        lump = 1.0 + 0.025 * noise.noise(v.co * 6.0) + 0.004 * math.sin(v.co.y * 60.0)
        v.co.x *= lump
        v.co.z = v.co.z * lump if v.co.z > 0 else v.co.z * lump * 0.9  # flatter belly
    return bm


def snout():
    """Blunt muzzle with the split, bristly upper lip (two lobes)."""
    parts = []
    parts.append((nh.uv_ellipsoid((0, -0.64, -0.075), (0.12, 0.08, 0.09), segments=14, rings=8), SNOUT))
    for sx in (1, -1):
        parts.append((nh.uv_ellipsoid((sx * 0.055, -0.70, -0.085), (0.065, 0.05, 0.06),
                                      segments=10, rings=6), SNOUT))
    # bristles: tiny dark bumps on the lip pads
    for sx in (1, -1):
        for i in range(7):
            a = i / 6.0
            p = (sx * (0.03 + 0.06 * a), -0.74 + 0.03 * a, -0.06 - 0.06 * math.sin(a * 3.0))
            parts.append((nh.ellipsoid(p, (0.009, 0.009, 0.009), subdivisions=0), BRISTLE))
    # mouth groove + nostrils
    parts.append((nh.uv_ellipsoid((0, -0.735, -0.075), (0.012, 0.02, 0.05), segments=6, rings=4), BRISTLE))
    for sx in (1, -1):
        parts.append((nh.uv_ellipsoid((sx * 0.035, -0.69, -0.012), (0.018, 0.012, 0.008),
                                      segments=6, rings=4), BRISTLE))
    return parts


def tail():
    """Large, flat, rounded spoon-shaped paddle."""
    bm = nh.uv_ellipsoid((0, 0, 0), (0.36, 0.30, 0.045), segments=28, rings=8)
    for v in bm.verts:
        t = nh.smoothstep(0.3, -0.3, v.co.y)  # 1 at the root
        v.co.x *= 1.0 - 0.4 * t ** 2
        v.co.z *= 1.0 + 0.8 * t
    nh.transform(bm, Matrix.Translation(Vector((0, 1.08, -0.02))))
    return bm


def flipper(sx):
    """Small paddle flipper angled back and down, three nails at the tip."""
    root = Vector((sx * 0.25, -0.30, -0.10))
    mid = Vector((sx * 0.36, -0.30, -0.17))
    tip = Vector((sx * 0.44, -0.24, -0.21))
    bm = nh.tube([root, mid, tip, tip + Vector((sx * 0.04, 0.03, -0.01))],
                 [0.06, 0.055, 0.045, 0.0], sides=8, scale_xy=(1.0, 0.45))
    nails = []
    for k in (-1, 0, 1):
        p = tip + Vector((sx * 0.025, 0.03 * k + 0.012, -0.012))
        nails.append(nh.ellipsoid(p, (0.012, 0.012, 0.008), subdivisions=1))
    return bm, nails


def build():
    mb = nh.MeshBuilder()
    mb.add(body(), skin)
    for bm, col in snout():
        mb.add(bm, col)
    mb.add(tail(), skin)
    for sx in (1, -1):
        fl, nails = flipper(sx)
        mb.add(fl, skin)
        for n in nails:
            mb.add(n, NAIL)
        mb.add(nh.ellipsoid((sx * 0.155, -0.50, 0.035), (0.018, 0.018, 0.018), subdivisions=1), EYE)
    return mb.to_object("AmericanManatee", roughness=0.75)


if __name__ == "__main__":
    nh.run(build, "AmericanManatee", background=(0.10, 0.32, 0.36),
           views=((35, 35), (-90, 8), (160, 70)))
