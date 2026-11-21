"""
Procedural Glossina oligocena (tsetse fly, late Eocene-early Oligocene, Florissant lake beds,
Colorado) for map swarms. A robust, housefly-like blood-sucking fly about 1.5 cm long: big
red-brown compound eyes, a long, stiff, piercing proboscis held straight forward, a grey-brown
striped thorax, a tan abdomen with dark bands, and long brownish wings folded flat over the
back one on top of the other like closed scissors (shown just parted, as in take-off).
Faces -Y, pivot at the body centre (Swarm).

Usage:
  blender --background --python tools/blender/glossina_oligocena.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GlossinaOligocena.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

DARK = (0.12, 0.10, 0.08)
THORAX = (0.42, 0.36, 0.28)
STRIPE = (0.20, 0.17, 0.13)
ABD = (0.62, 0.48, 0.30)
BAND = (0.22, 0.15, 0.09)
EYE = (0.45, 0.14, 0.08)
EYE_SHEEN = (0.70, 0.35, 0.22)
WING = (0.62, 0.55, 0.42)
VEIN = (0.30, 0.24, 0.16)
LEG = (0.30, 0.24, 0.17)

HEAD = Vector((0.0, -0.36, 0.05))
THX = Vector((0.0, -0.14, 0.06))
ABD0 = Vector((0.0, 0.05, 0.03))


def build():
    mb = nh.MeshBuilder()
    # head with large compound eyes
    mb.add(nh.uv_ellipsoid(HEAD, (0.085, 0.06, 0.075), segments=12, rings=8), THORAX)
    for sx in (-1, 1):
        mb.add(nh.uv_ellipsoid(HEAD + Vector((sx * 0.055, -0.01, 0.01)), (0.045, 0.05, 0.068), segments=10, rings=8),
               lambda co, n: nh.lerp(EYE, EYE_SHEEN, max(0.0, n.z) * 0.6))
        # short antennae with feathery arista
        b = HEAD + Vector((sx * 0.018, -0.055, 0.035))
        mb.add(nh.tube([b, b + Vector((sx * 0.02, -0.04, -0.01))], [0.01, 0.006], sides=4), STRIPE)
    # long stiff proboscis pointing straight forward, palps alongside
    base = HEAD + Vector((0, -0.04, -0.05))
    mb.add(nh.tube([base, base + Vector((0, -0.13, 0.0)), base + Vector((0, -0.27, 0.01))], [0.012, 0.009, 0.0],
                   sides=5), DARK)
    for sx in (-1, 1):
        mb.add(nh.tube([base + Vector((sx * 0.016, 0, 0.005)), base + Vector((sx * 0.016, -0.24, 0.012))],
                       [0.009, 0.004], sides=4), STRIPE)
    # thorax: grey-brown with dark stripes
    def thx(co, n):
        c = nh.lerp(THORAX, DARK, max(0.0, -n.z) * 0.6)
        if n.z > 0.3 and (abs(abs(co.x) - 0.035) < 0.012 or abs(co.x) < 0.006):
            c = nh.lerp(c, STRIPE, 0.85)
        return c
    mb.add(nh.uv_ellipsoid(THX, (0.11, 0.16, 0.1), segments=20, rings=14), thx)
    # abdomen: broad, flattened, banded
    def abd(co, n):
        t = (co.y - ABD0.y) / 0.36
        c = ABD
        ph = (t * 5) % 1.0
        if n.z > -0.2 and ph < 0.45 and abs(co.x) > 0.02:
            c = nh.lerp(c, BAND, 0.85)
        return nh.lerp(c, DARK, max(0.0, -n.z) * 0.3)
    mb.add(nh.uv_ellipsoid(ABD0 + Vector((0, 0.16, 0)), (0.1, 0.2, 0.065), segments=20, rings=14), abd)
    # six legs
    for sx in (-1, 1):
        for k, (dy, fy) in enumerate(((-0.2, -0.32), (-0.13, -0.08), (-0.06, 0.18))):
            hip = Vector((sx * 0.07, dy, 0.0))
            knee = Vector((sx * 0.2, (dy + fy) * 0.5, 0.04))
            foot = Vector((sx * 0.25, fy, -0.12))
            mb.add(nh.tube([hip, knee, foot], [0.014, 0.011, 0.006], sides=4), LEG)
    # wings: folded flat over the abdomen, one over the other, just parted (scissors)
    for sx, z, ang in ((1, 0.115, 6), (-1, 0.107, 6)):
        pts = []
        n = 16
        L, W = 0.62, 0.13
        for i in range(n + 1):
            t = i / n
            pts.append((W * 0.25 * math.sin(math.pi * t) * -1 + 0.0, t * L, 0.0))
        for i in range(n, -1, -1):
            t = i / n
            pts.append((W * math.sin(math.pi * min(1.0, t * 1.02)) ** 0.7 * (0.5 + 0.5 * t), t * L, 0.0))
        clean = []
        for p in pts:
            if not clean or (Vector(p) - Vector(clean[-1])).length > 1e-5:
                clean.append(p)
        if (Vector(clean[0]) - Vector(clean[-1])).length < 1e-5:
            clean.pop()
        clean = [(x * sx, y, zz) for x, y, zz in clean]
        bm = nh.flat_panel(clean, thickness=0.005)
        nh.transform(bm, Matrix.Rotation(math.radians(-ang * sx), 4, "Z"))
        root = Vector((sx * 0.005, -0.1, z))
        nh.transform(bm, Matrix.Translation(root))

        def wc(co, nrm, root=root, sx=sx):
            q = co - root
            c = WING
            # dark longitudinal veins and the 'hatchet' cell
            if abs((q.x * sx) - 0.05 - q.y * 0.08) < 0.006 or abs((q.x * sx) - 0.025 - q.y * 0.02) < 0.005:
                c = VEIN
            return nh.lerp(c, VEIN, 0.25 * nh.smoothstep(0.0, 0.2, -q.y + 0.1))
        mb.add(bm, wc, smooth=False)
    obj = mb.to_object("GlossinaOligocena", roughness=0.4)
    vs = obj.data.vertices
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) * 0.5
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "GlossinaOligocena", background=(0.30, 0.40, 0.30), views=((35, 30), (-90, 5), (0, 80)))
