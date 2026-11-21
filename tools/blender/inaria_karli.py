"""
Procedural Inaria karli (Ediacaran possible cnidarian) for the map, Fixed style.

A soft, onion-shaped sac half sunk in the sand: a broad bulb divided into a few rounded lobes
by vertical grooves, narrowing into a slim, tubular neck with an opening at the top, like a
simple sea anemone. Two individuals; translucent pinkish cream with darker grooves.
Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Inaria.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

BODY = (0.92, 0.76, 0.70)
GROOVE = (0.62, 0.42, 0.40)
NECK = (0.86, 0.66, 0.62)
MOUTH = (0.30, 0.16, 0.16)
LOBES = 6


def sac(H, R):
    def shape(u, v):
        th = u * math.tau
        lobe = 0.5 + 0.5 * math.cos(th * LOBES)
        if v < 0.96:
            t = v / 0.96
            bulb = math.sin(math.pi * min(1.0, t / 0.62)) ** 0.7 if t < 0.62 else 0.0
            neck = 0.16 * (1.0 - 0.2 * t) + 0.05 * nh.smoothstep(0.9, 1.0, t)
            r = R * max(neck, bulb * (0.86 + 0.14 * lobe ** 0.5) * (1 - 0.1 * t) + neck * (1 - bulb))
            if t < 0.05:
                r = R * (0.5 + 10 * t * 0.5) * (0.86 + 0.14 * lobe ** 0.5)
            return r, H * t
        t = (v - 0.96) / 0.04
        return R * 0.21 * (1 - 0.6 * t), H * (1 - 0.06 * t)

    def color(u, v, co):
        th = u * math.tau
        g = (0.5 - 0.5 * math.cos(th * LOBES)) ** 4 * (1 - nh.smoothstep(0.5, 0.65, v))
        c = nh.lerp(BODY, NECK, nh.smoothstep(0.5, 0.7, v))
        c = nh.lerp(c, GROOVE, g * 0.8)
        c = nh.lerp(c, MOUTH, nh.smoothstep(0.96, 0.99, v))
        return ep.mottle(c, co, 0.05)

    return ep.lathe(44, 36, shape, color)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.6)
    for x, y, H, R, yaw in [(-0.05, 0.05, 1.1, 0.42, 0), (0.42, -0.25, 0.65, 0.25, 25)]:
        p = sac(H, R)
        ep.place(p[0], x, y, yaw, z=-0.06 * H)
        ep.add(mb, p)
    return ep.finish(mb, "Inaria")


if __name__ == "__main__":
    ep.export(build, "Inaria")
