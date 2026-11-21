"""
Procedural Hiemalora stellaris (Ediacaran disc) for the map, Fixed style.

A small domed disc ringed by a starburst of long, thin, tentacle-like rays lying out over the
mat, like a little sea anemone or the holdfast of a frond. Three individuals; pale amber body,
rosy rays. Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Hiemalora.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

BODY = (0.84, 0.66, 0.46)
DARK = (0.50, 0.36, 0.26)
RAY = (0.82, 0.56, 0.48)
RAY_TIP = (0.92, 0.78, 0.70)


def one(mb, x, y, R, rng):
    def height(r, th):
        return R * (0.55 * (1 - r * r) ** 0.7 + 0.08) + R * 0.03 * math.cos(th * 18) * r

    def color(r, th, co):
        c = nh.lerp((0.94, 0.80, 0.60), BODY, nh.smoothstep(0.0, 0.5, r))
        c = nh.lerp(c, DARK, (0.5 + 0.5 * math.cos(th * 18)) * 0.35 * nh.smoothstep(0.3, 0.9, r))
        return ep.mottle(c, co)

    d = ep.polar_disc(R, height, color, rings=10, segs=36)
    ep.place(d[0], x, y)
    ep.add(mb, d)
    n = 22
    for k in range(n):
        a = k / n * math.tau + rng.uniform(-0.06, 0.06)
        L = R * rng.uniform(1.3, 2.0)
        o = (math.cos(a), math.sin(a))
        w = (o[1] * rng.uniform(-0.3, 0.3), -o[0] * rng.uniform(-0.3, 0.3))
        pts = [(x + o[0] * R * 0.85, y + o[1] * R * 0.85, R * 0.12),
               (x + o[0] * (R + L * 0.4) + w[0] * L * 0.2, y + o[1] * (R + L * 0.4) + w[1] * L * 0.2, R * 0.08),
               (x + o[0] * (R + L) + w[0] * L * 0.5, y + o[1] * (R + L) + w[1] * L * 0.5, R * 0.05)]
        r0 = R * 0.075
        mb.add(nh.tube(pts, [r0, r0 * 0.7, 0.0], sides=5),
               lambda co, n, x=x, y=y, R=R, L=L: nh.lerp(RAY, RAY_TIP, nh.smoothstep(R, R + L, math.hypot(co.x - x, co.y - y))))


def build():
    rng = random.Random(6)
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.85)
    one(mb, -0.05, 0.05, 0.2, rng)
    one(mb, 0.48, -0.25, 0.12, rng)
    one(mb, -0.42, -0.4, 0.1, rng)
    return ep.finish(mb, "Hiemalora")


if __name__ == "__main__":
    ep.export(build, "Hiemalora")
