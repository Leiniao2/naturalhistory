"""
Procedural Albumares brunsae (Ediacaran trilobozoan) for the map, Fixed style.

A small, low disc with three-fold symmetry: three short grooves meet in the middle like a
three-pointed star, and from them fine branching channels run out to a fringe of many slender
marginal rays. Two individuals. Pale fawn with darker channels. Pivot at the base (z = 0),
faces -Y.

Output: Assets/Resources/Models/Species/Albumares.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

BODY = (0.84, 0.72, 0.58)
CHANNEL = (0.46, 0.33, 0.24)
FRINGE = (0.92, 0.82, 0.68)


def field(r, th):
    # three central grooves (three-fold), then 12 branching channels, then 48 marginal rays
    a3 = abs(math.cos(1.5 * (th + math.pi / 2)))
    star = math.exp(-((1 - a3) / 0.04)) * (1 - nh.smoothstep(0.25, 0.4, r))
    ch = (0.5 + 0.5 * math.cos(th * 12)) ** 6 * nh.smoothstep(0.25, 0.4, r) * (1 - nh.smoothstep(0.75, 0.82, r))
    rays = (0.5 + 0.5 * math.cos(th * 48)) * nh.smoothstep(0.8, 0.86, r)
    return star, ch, rays


def height(r, th):
    star, ch, rays = field(r, th)
    h = 0.12 * (1 - r ** 2) ** 0.8 + 0.03
    h -= 0.03 * star + 0.02 * ch
    h += 0.015 * rays
    return h


def color(r, th, co):
    star, ch, rays = field(r, th)
    c = nh.lerp(BODY, CHANNEL, min(1.0, star * 0.9 + ch * 0.75))
    c = nh.lerp(c, nh.lerp(CHANNEL, FRINGE, rays), nh.smoothstep(0.8, 0.86, r))
    return ep.mottle(c, co)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.75)
    d = ep.polar_disc(0.45, height, color, rings=24, segs=96, base_inset=0.98)
    ep.place(d[0], -0.1, 0.05, 15)
    ep.add(mb, d)
    d = ep.polar_disc(0.25, lambda r, th: height(r, th) * 0.7, color, rings=18, segs=96, base_inset=0.98)
    ep.place(d[0], 0.48, -0.3, -50)
    ep.add(mb, d)
    return ep.finish(mb, "Albumares")


if __name__ == "__main__":
    ep.export(build, "Albumares")
