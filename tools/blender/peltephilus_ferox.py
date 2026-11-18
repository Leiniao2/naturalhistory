"""
Procedural Peltephilus ferox (Early Miocene of Patagonia) for map colonies: the
"horned armadillo", about 1-1.2 m long including the tail.

An armadillo build: a long, low carapace of rectangular osteoderms with rigid
shoulder and hip shields and flexible transverse bands across the middle, a
broad, short head covered by a bony head shield, and its trademark pair of tall,
pointed horn-like scales standing up side by side over the nose. Short sturdy
legs with long digging claws and a tapering tail sheathed in rings of armour.
Brownish-grey shell with darker band seams, grey-pink skin.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/peltephilus_ferox.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PeltephilusFerox.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.47, 0.42, 0.36)
SHELL_PALE = (0.62, 0.57, 0.49)
SEAM = (0.22, 0.19, 0.16)
SKIN = (0.46, 0.40, 0.37)
HORN = (0.40, 0.35, 0.29)
EYE = (0.05, 0.04, 0.03)
CLAW = (0.20, 0.17, 0.14)

ZC = 0.30
RX, RY, RZ = 0.25, 0.48, 0.24
BANDS = (-0.12, 0.18)   # the flexible banded zone between the shields (y range)


def build():
    b = nh.MeshBuilder()
    b.add(nh.ellipsoid((0, 0, ZC), (RX, RY, RZ), subdivisions=4,
                       deform=lambda v: 1.0 + 0.05 * max(0.0, -v.z) - 0.05 * max(0.0, v.z) ** 2), SHELL)
    b.add(nh.ellipsoid((0, 0, ZC - 0.08), (RX * 0.85, RY * 0.85, RZ * 0.5)), SKIN)        # belly
    # flexible bands: raised hoops across the middle
    for i in range(7):
        y = BANDS[0] + (BANDS[1] - BANDS[0]) * i / 6
        k = math.sqrt(max(0.0, 1 - (y / RY) ** 2))
        b.add(nh.ellipsoid((0, y, ZC + 0.005), (RX * k * 1.03, 0.018, RZ * k * 1.03), subdivisions=3), SHELL)
    # head: short, broad, with a bony shield
    hc = Vector((0, -RY - 0.07, ZC - 0.02))
    b.add(nh.ellipsoid(tuple(hc), (0.10, 0.11, 0.09)), SKIN)
    b.add(nh.ellipsoid(tuple(hc + Vector((0, -0.10, -0.03))), (0.058, 0.095, 0.052)), SKIN)
    b.add(nh.ellipsoid(tuple(hc + Vector((0, -0.04, 0.05))), (0.095, 0.13, 0.045)), SHELL)  # head shield
    b.add(nh.ellipsoid(tuple(hc + Vector((0, 0.08, 0.04))), (0.09, 0.05, 0.05)), SHELL)    # nuchal band
    # tail
    t0 = Vector((0, RY * 0.9, ZC - 0.05))
    pts = [t0, t0 + Vector((0, 0.15, -0.05)), t0 + Vector((0, 0.30, -0.12)), t0 + Vector((0, 0.42, -0.17))]
    b.add(nh.tube([tuple(p) for p in pts], [0.075, 0.06, 0.04, 0.015], sides=12), SHELL)
    for i in range(6):
        t = i / 6
        p = pts[0].lerp(pts[2], t * 1.2)
        r = 0.08 - 0.045 * t
        b.add(nh.tube([tuple(p + Vector((0, -0.01, 0))), tuple(p + Vector((0, 0.012, 0)))], [r, r], sides=12), SHELL)
    claws = []
    for (x, y, st, front) in ((-0.17, -0.30, -0.04, True), (0.17, -0.30, 0.04, True), (-0.17, 0.28, 0.03, False),
                              (0.17, 0.28, -0.04, False)):
        b.add(nh.tube([(x * 0.9, y, ZC - 0.05), (x * 1.05, y + st, 0.04)], [0.06, 0.045], sides=10), SKIN)
        b.add(nh.ellipsoid((x * 1.05, y + st - 0.02, 0.025), (0.05, 0.065, 0.025)), SKIN)
        for a in (-0.45, 0.0, 0.45):
            claws.append((Vector((x * 1.05 + math.sin(a) * 0.035, y + st - 0.075, 0.02)), 0.06 if front else 0.035))
    fused = b.fuse(voxel=0.011, smooth=3, smooth_factor=0.5, max_tris=9000)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")

    def shellish(co):
        q = co - Vector((0, 0, ZC))
        on = (q.x / RX) ** 2 + (q.y / RY) ** 2 + (q.z / RZ) ** 2 > 0.75 and co.z > ZC - 0.10 and abs(co.y) < RY * 1.02
        tail = co.y > RY * 0.95 and co.z > 0.03
        return on, tail

    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            c = (c[0], c[1], c[2])
            co = l.vert.co
            on, tail = shellish(co)
            if on or tail:
                if BANDS[0] - 0.02 < co.y < BANDS[1] + 0.02 and on:
                    ph = ((co.y - BANDS[0]) / ((BANDS[1] - BANDS[0]) / 6)) % 1.0
                    seam = 1.0 - nh.smoothstep(0.0, 0.25, min(ph, 1 - ph))
                else:
                    # rectangular-ish osteoderm grid on the shields and tail
                    gx = (math.atan2(co.x, co.z - ZC + 0.3) * 9.0) % 1.0
                    gy = (co.y * 22.0) % 1.0
                    seam = 1.0 - nh.smoothstep(0.0, 0.14, min(gx, 1 - gx, gy, 1 - gy))
                base = nh.lerp(SHELL, SHELL_PALE, 0.5 + 0.5 * noise.noise(co * 14.0))
                c = nh.lerp(base, SEAM, 0.8 * seam)
                if co.z < ZC - 0.07 and on:
                    c = nh.lerp(c, SEAM, 0.3)
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    # the paired nasal horns: tall flattened cones, side by side over the nose
    for sx in (-1, 1):
        root = hc + Vector((sx * 0.035, -0.13, 0.025))
        tip = root + Vector((sx * 0.015, 0.035, 0.15))
        mb.add(nh.tube([tuple(root), tuple(root.lerp(tip, 0.5)), tuple(tip)], [0.036, 0.025, 0.0], sides=10,
                       scale_xy=(0.6, 1.0)), HORN)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid(tuple(hc + Vector((sx * 0.085, -0.06, 0.02))), (0.013,) * 3, subdivisions=2), EYE)
    for c, ln in claws:
        mb.add(nh.tube([tuple(c + Vector((0, 0.02, 0.01))), tuple(c + Vector((0, -ln, -0.018)))], [0.010, 0.0], sides=5),
               CLAW)
    obj = mb.to_object("PeltephilusFerox")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "PeltephilusFerox", ground=(0.45, 0.42, 0.30), views=((35, 20), (-90, 5), (-20, 10)))
