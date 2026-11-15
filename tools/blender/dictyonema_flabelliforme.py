"""
Procedural Dictyonema (Rhabdinopora) flabelliformis, an Early Ordovician planktonic
dendroid graptolite colony, for the map (Drift style).

A conical, net-like rhabdosome a few centimetres long hanging apex-up from a thin
thread (the nema). From the tiny sicula at the apex four primary stipes radiate
down the cone and fork again and again (4 -> 8 -> 16 -> 32 stipes at the rim). Thin
cross-links (dissepiments) join neighbouring stipes at irregular intervals, which
gives the open mesh its look, and small tooth-like thecae (the zooids' tubes) line
the inner side of each stipe. The living colony was translucent pale amber; stipes
carry faint fusellar banding and the thecal tips are darker. Modelled much
thicker than life so it reads on the map.

Usage:
  blender --background --python tools/blender/dictyonema_flabelliforme.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dictyonema.fbx
Cone axis along Z (apex and nema up), pivot at the body centre. About 1.5 units tall.
"""

import math
import random
import sys
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

SEED = 5
HEIGHT = 1.05            # apex to rim
RIM = 0.55               # rim radius
FORKS = (0.10, 0.26, 0.50)   # dichotomies, as fractions of the height
STIPE_R = 0.014
DISSEPIMENT_R = 0.0065
NEMA_LENGTH = 0.42

AMBER = (0.80, 0.54, 0.24)
AMBER_PALE = (0.94, 0.76, 0.46)
AMBER_DARK = (0.48, 0.28, 0.11)
THREAD = (0.88, 0.80, 0.62)

Z_APEX = HEIGHT * 0.5


def surface(t, phi):
    """Point on the colony cone: t = 0 apex .. 1 rim, phi around the axis."""
    r = RIM * (t ** 0.85) * (1.0 + 0.06 * math.sin(phi * 3.0 + 1.0) * t)
    return Vector((r * math.cos(phi), r * math.sin(phi), Z_APEX - HEIGHT * t))


def stipe_color(co, n):
    t = (Z_APEX - co.z) / HEIGHT
    band = 0.5 + 0.5 * math.sin(co.length * 150.0)        # fusellar growth bands
    col = nh.lerp(AMBER, AMBER_PALE, 0.25 + 0.4 * band)
    return nh.lerp(col, AMBER_DARK, 0.35 * (1.0 - nh.smoothstep(0.0, 0.25, t)))


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # stipe tree: each node spans [t0, t1] and drifts from its parent's angle to its own
    starts = [(k + 0.5) / 4 * math.tau for k in range(4)]
    nodes = [(0.012, FORKS[0], a, a) for a in starts]       # (t0, t1, phi_from, phi_to)
    level = starts
    bounds = list(FORKS[1:]) + [1.0]
    for i, t0 in enumerate(FORKS):
        width = math.tau / (len(level) * 2)
        child = []
        for a in level:
            for sgn in (-1, 1):
                b = a + sgn * width * 0.5 + rng.uniform(-0.04, 0.04)
                child.append(b)
                nodes.append((t0, bounds[i], a, b))
        level = child

    def phi_at(node, t):
        t0, t1, a, b = node
        u = nh.smoothstep(t0, t0 + (t1 - t0) * 0.35 + 0.03, t)
        return a + (b - a) * u

    for node in nodes:
        t0, t1, _, _ = node
        steps = max(2, int((t1 - t0) / 0.09) + 1)
        pts, radii = [], []
        for k in range(steps + 1):
            t = t0 + (t1 - t0) * k / steps
            pts.append(surface(t, phi_at(node, t)))
            radii.append(STIPE_R * (1.0 + 0.25 * t))
        mb.add(nh.tube(pts, radii, sides=4, cap_start=False, cap_end=t1 >= 1.0), stipe_color)

        # thecae: small teeth on the inner face of the stipe, pointing down the cone
        nt = int((t1 - t0) / 0.075)
        for k in range(nt):
            t = t0 + (t1 - t0) * (k + 0.6) / max(nt, 1)
            if t < 0.06:
                continue
            p = surface(t, phi_at(node, t))
            inward = Vector((-p.x, -p.y, 0.0)).normalized() if p.xy.length > 1e-4 else Vector((0, 0, -1))
            tip = p + inward * 0.03 + Vector((0, 0, -0.035))
            mb.add(nh.tube([p, tip], [STIPE_R * 0.9, 0.0], sides=3, cap_start=False),
                   lambda co, n, tip=tip: AMBER_DARK if (co - tip).length < 0.01 else AMBER)

    # dissepiments: cross-links between neighbouring stipes at irregular heights
    leaves = [n for n in nodes if n[1] >= 1.0]
    mids = [n for n in nodes if n[1] == FORKS[2]]
    for group, t_lo, t_hi in ((mids, FORKS[1] + 0.05, FORKS[2]), (leaves, FORKS[2] + 0.04, 0.99)):
        group = sorted(group, key=lambda n: n[3] % math.tau)
        for i, a in enumerate(group):
            b = group[(i + 1) % len(group)]
            t = t_lo + rng.uniform(0.0, 0.05)
            while t < t_hi:
                pa, pb = surface(t, phi_at(a, t)), surface(t, phi_at(b, t))
                if (pa - pb).length > 0.01:
                    mid = (pa + pb) * 0.5
                    mid.xy *= 0.995
                    mb.add(nh.tube([pa, mid, pb], [DISSEPIMENT_R] * 3, sides=3,
                                   cap_start=False, cap_end=False), AMBER)
                t += rng.uniform(0.07, 0.12)

    # sicula (the founder zooid's cone) at the apex and the nema thread above it
    top = Vector((0, 0, Z_APEX))
    mb.add(nh.tube([top + Vector((0, 0, -0.05)), top + Vector((0, 0, 0.01)), top + Vector((0, 0, 0.05))],
                   [0.022, 0.016, 0.006], sides=6), AMBER_DARK)
    pts = [top + Vector((0.025 * math.sin(k * 0.9), 0.0, 0.04 + NEMA_LENGTH * k / 6)) for k in range(7)]
    mb.add(nh.tube(pts, [0.006] * 6 + [0.0], sides=4, cap_start=False), THREAD)
    # small vane where the nema ended (the colony probably hung from it)
    mb.add(nh.ellipsoid(pts[-1] + Vector((0, 0, 0.01)), (0.03, 0.006, 0.04), subdivisions=1), THREAD)

    obj = mb.to_object("Dictyonema", roughness=0.35)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Dictyonema", views=((35, 20), (0, -35), (20, 60)))
