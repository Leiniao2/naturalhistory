"""
Procedural low-poly Eldonia ludwigi (Burgess Shale eldonid).

A flat, round, jellyfish-like disc with a gently domed top and a scalloped
margin of fine radial lobes; inside, the dark, coiled, C-shaped gut sac shows
through the translucent body; on one side (here the front) a tuft of branching
feeding tentacles around the mouth. Pale bluish cream disc with a brown gut,
radial lines and rosy tentacles. Not a jellyfish: probably a distant relative
of echinoderms and hemichordates. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Eldonia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

DISC = (0.84, 0.82, 0.74)
DISC_EDGE = (0.68, 0.66, 0.60)
RADIAL = (0.60, 0.54, 0.46)
GUT = (0.42, 0.26, 0.16)
TENT = (0.88, 0.58, 0.52)

R = 0.5


def build():
    mb = nh.MeshBuilder()

    def deform(n):
        a = math.atan2(n.y, n.x)
        rr = math.hypot(n.x, n.y)
        return 1.0 + 0.03 * math.cos(a * 32) * rr ** 4

    disc = nh.uv_ellipsoid((0, 0, 0), (R, R, 0.07), segments=64, rings=10, deform=deform)
    for v in disc.verts:
        if v.co.z < 0:
            v.co.z *= 0.5

    def disc_col(co, n):
        a = math.atan2(co.y, co.x)
        rr = math.hypot(co.x, co.y) / R
        c = nh.lerp(DISC, DISC_EDGE, nh.smoothstep(0.6, 1.0, rr))
        line = nh.smoothstep(0.85, 1.0, 0.5 + 0.5 * math.cos(a * 32))
        return nh.lerp(c, RADIAL, 0.5 * line * nh.smoothstep(0.55, 0.75, rr))

    mb.add(disc, disc_col)
    # coiled gut sac: a C-shaped tube just under the top surface, opening towards the tentacles
    pts, radii = [], []
    for i in range(25):
        t = i / 24
        a = math.radians(-75 - 300 * t)  # sweeps round from the front
        rr = 0.3 - 0.12 * t
        pts.append((rr * math.cos(a), rr * math.sin(a), 0.045 - 0.01 * t))
        radii.append(0.035 + 0.025 * math.sin(math.pi * t))
    mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.7)), GUT)
    # tentacle tuft at the front
    base = Vector((0.1, -0.44, 0.0))
    for k in range(5):
        a = math.radians(-50 + 25 * k)
        d = Vector((math.sin(a), -math.cos(a), 0.1)).normalized()
        p1 = base + d * 0.18
        mb.add(nh.tube([base, p1], [0.018, 0.012], sides=5), TENT)
        for b in (-1, 1):
            d2 = (d + Vector((b * 0.5, 0, 0.1))).normalized()
            mb.add(nh.tube([p1, p1 + d2 * 0.1], [0.011, 0.0], sides=4), TENT)
    return ec.centre(mb.to_object("Eldonia", roughness=0.35))


if __name__ == "__main__":
    ec.export(build, "Eldonia")
