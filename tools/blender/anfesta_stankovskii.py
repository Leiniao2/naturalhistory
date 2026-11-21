"""
Procedural Anfesta stankovskii (Ediacaran trilobozoan) for the map, Fixed style.

A domed disc with three-fold symmetry: three broad, gently curved tubular lobes radiate from
the centre, each crossed by fine ridges, separated by smoother sectors with a small swelling,
all inside a narrow, plain margin. Three individuals; olive-buff with pale lobes.
Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Anfesta.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

BODY = (0.72, 0.52, 0.42)
LOBE = (0.95, 0.82, 0.66)
STRIPE = (0.60, 0.42, 0.32)
RIM = (0.84, 0.68, 0.56)


def lobe(r, th):
    best = 0.0
    for k in range(3):
        c = k * math.tau / 3 + 0.9 * r      # lobes curve as they run out
        d = math.atan2(math.sin(th - c), math.cos(th - c))
        best = max(best, math.exp(-(d / 0.32) ** 2))
    return best * nh.smoothstep(0.0, 0.3, r) * (1 - nh.smoothstep(0.5, 0.85, r))


def height(r, th):
    h = 0.16 * (1 - r ** 2) ** 0.6 + 0.02
    h += 0.05 * lobe(r, th)
    h -= 0.012 * math.exp(-((r - 0.84) / 0.04) ** 2)
    return h


def color(r, th, co):
    lb = lobe(r, th)
    stripes = 0.5 + 0.5 * math.cos(r * 22 * math.pi)
    c = nh.lerp(BODY, nh.lerp(LOBE, STRIPE, stripes * 0.45), nh.smoothstep(0.2, 0.7, lb))
    c = nh.lerp(c, RIM, nh.smoothstep(0.82, 0.9, r))
    return ep.mottle(c, co)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.75)
    for x, y, R, yaw in [(-0.1, 0.05, 0.38, 0), (0.42, -0.28, 0.22, 50), (-0.45, -0.38, 0.17, 100)]:
        d = ep.polar_disc(R, lambda r, th, R=R: height(r, th) * R / 0.38, color, rings=22, segs=72)
        ep.place(d[0], x, y, yaw)
        ep.add(mb, d)
    return ep.finish(mb, "Anfesta")


if __name__ == "__main__":
    ep.export(build, "Anfesta")
