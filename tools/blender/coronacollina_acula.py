"""
Procedural low-poly Coronacollina acula (Ediacaran, Ediacara Member, South Australia).

A small, thimble-shaped, truncated-cone body sitting on the seafloor with a
flat top and a slight rim, propped by four very long, straight, needle-like
spicules that radiate from its sides down to the sediment like guy ropes,
each many times the body's height. One of the earliest animals with mineral
skeletal elements, possibly a sponge. Sandy pinkish body, pale ivory spicules.
Pivot on the seabed (Fixed).

Output: Assets/Resources/Models/Species/Coronacollina.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.80, 0.60, 0.50)
BODY_DARK = (0.56, 0.40, 0.32)
TOP = (0.66, 0.46, 0.38)
SPICULE = (0.96, 0.92, 0.80)

H = 0.22
R0, R1 = 0.16, 0.10


def build():
    mb = nh.MeshBuilder()
    pts = [(0, 0, 0.0), (0, 0, H * 0.5), (0, 0, H), (0, 0, H + 0.005)]
    body = nh.tube(pts, [R0, (R0 + R1) / 2 + 0.01, R1 + 0.01, R1 * 0.85], sides=18)

    def col(co, n):
        if n.z > 0.8:
            return TOP
        ring = 0.5 + 0.5 * math.cos(co.z * math.tau / 0.05)
        return nh.lerp(BODY, BODY_DARK, 0.4 * nh.smoothstep(0.7, 1.0, ring))

    mb.add(body, col)
    mb.add(nh.ellipsoid((0, 0, H + 0.003), (R1 * 0.8, R1 * 0.8, 0.02), subdivisions=2), BODY_DARK)
    # four long spicules from the sides of the body down to the seabed
    for k in range(4):
        a = math.radians(45 + 90 * k + (8 if k % 2 else -6))
        out = Vector((math.cos(a), math.sin(a), 0.0))
        start = out * (R1 + 0.03) + Vector((0, 0, H * 0.75))
        length = 1.0 + 0.15 * (k % 2)
        end = out * length + Vector((0, 0, 0.0))
        start2 = start - (end - start).normalized() * 0.03
        mb.add(nh.tube([start2, start.lerp(end, 0.5), end], [0.012, 0.009, 0.0035], sides=5), SPICULE)
    return ec.ground(mb.to_object("Coronacollina", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Coronacollina", fixed=True, views=((35, 30), (0, 75)))
