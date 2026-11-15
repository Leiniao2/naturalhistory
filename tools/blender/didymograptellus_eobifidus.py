"""
Procedural Didymograptellus eobifidus, an Early-Middle Ordovician (Floian-Dapingian)
pendent didymograptid graptolite, for the map (Drift style).

A small planktonic colony shaped like a tuning fork: a slender conical sicula (the
founder zooid's tube, aperture down) hangs from a fine nema thread, and two stipes
bud from it, bend out briefly and then hang down side by side, diverging in a
narrow "V". Each stipe is a row of overlapping, inclined thecal tubes on a common
canal, so the inner (ventral) edges facing each other are saw-toothed, with the
thecal apertures opening inward and down; the stipes widen slightly away from the
sicula. Translucent pale amber with fine fusellar growth bands and darker
apertures. A few centimetres long in life, modelled thick so it reads on the map.

Usage:
  blender --background --python tools/blender/didymograptellus_eobifidus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Didymograptellus.fbx
Colony in the XZ plane (nema up +Z), pivot at the body centre. About 1.6 units tall.
"""

import math
import sys
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

AMBER = (0.80, 0.56, 0.26)
AMBER_PALE = (0.94, 0.78, 0.48)
AMBER_DARK = (0.44, 0.26, 0.10)
THREAD = (0.90, 0.82, 0.64)

SICULA_TOP, SICULA_BOTTOM = 0.32, 0.0
THECAE = 15
STIPE_LENGTH = 1.25
SPLAY = math.radians(13)     # each stipe leans this far off vertical


def fusellar(co, n):
    band = 0.5 + 0.5 * math.sin((co.x * 0.6 + co.z) * 170.0)
    return nh.lerp(AMBER, AMBER_PALE, 0.2 + 0.45 * band)


def stipe_path(side):
    """Dorsal (outer) edge of a stipe: out from the sicula, then down and slightly apart."""
    pts = []
    start = Vector((side * 0.03, 0.0, SICULA_TOP - 0.08))
    elbow = Vector((side * 0.13, 0.0, SICULA_TOP - 0.18))
    d = Vector((side * math.sin(SPLAY), 0.0, -math.cos(SPLAY)))
    pts = [start, elbow]
    for k in range(1, 7):
        t = k / 6
        p = elbow + d * (STIPE_LENGTH * t) + Vector((side * 0.04 * t * t, 0.0, 0.0))
        pts.append(p)
    return pts


def sample(path, t):
    lens = [0.0]
    for a, b in zip(path, path[1:]):
        lens.append(lens[-1] + (b - a).length)
    target = t * lens[-1]
    for i in range(len(path) - 1):
        if lens[i + 1] >= target:
            u = (target - lens[i]) / max(lens[i + 1] - lens[i], 1e-6)
            p = path[i].lerp(path[i + 1], u)
            return p, (path[i + 1] - path[i]).normalized()
    return path[-1], (path[-1] - path[-2]).normalized()


def build():
    mb = nh.MeshBuilder()

    # sicula: slender cone, apex up, aperture down, with a darker rim
    mb.add(nh.tube([Vector((0, 0, SICULA_TOP)), Vector((0, 0, SICULA_TOP - 0.12)),
                    Vector((0, 0, SICULA_BOTTOM + 0.02)), Vector((0, 0, SICULA_BOTTOM))],
                   [0.008, 0.024, 0.042, 0.044], sides=10, cap_end=True), fusellar)
    mb.add(nh.tube([Vector((0, 0, SICULA_BOTTOM + 0.004)), Vector((0, 0, SICULA_BOTTOM - 0.004))],
                   [0.047, 0.047], sides=10), AMBER_DARK)
    # nema: fine thread from the sicula's apex
    pts = [Vector((0.012 * math.sin(k * 0.8), 0.0, SICULA_TOP + 0.36 * k / 6)) for k in range(7)]
    mb.add(nh.tube(pts, [0.006] * 6 + [0.0], sides=4, cap_start=False), THREAD)

    for side in (-1, 1):
        path = stipe_path(side)
        # common canal along the dorsal (outer) edge
        radii = [0.022 + 0.014 * k / (len(path) - 1) for k in range(len(path))]
        mb.add(nh.tube(path, radii, sides=6), fusellar)
        inward = Vector((-side, 0.0, 0.0))
        for k in range(THECAE):
            t0 = (k + 0.05) / (THECAE + 0.6)
            base, d = sample(path, t0)
            grow = 0.75 + 0.5 * t0                       # thecae get a little larger distally
            # inclined tube: leaves the canal, leans across the stipe and down toward its aperture
            ventral = (inward - d * inward.dot(d)).normalized()
            p1 = base + d * (0.05 * grow) + ventral * (0.018 * grow)
            p2 = base + d * (0.12 * grow) + ventral * (0.045 * grow)
            ap = base + d * (0.155 * grow) + ventral * (0.06 * grow)
            mb.add(nh.tube([base, p1, p2, ap], [0.022 * grow, 0.026 * grow, 0.029 * grow, 0.031 * grow],
                           sides=6, cap_start=False, cap_end=False), fusellar)
            # dark aperture lip, slightly flared
            lip_dir = (ap - p2).normalized()
            mb.add(nh.tube([ap - lip_dir * 0.004, ap + lip_dir * 0.006], [0.032 * grow, 0.036 * grow],
                           sides=6, cap_start=True, cap_end=False), AMBER_DARK)

    obj = mb.to_object("Didymograptellus", roughness=0.35)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Didymograptellus", views=((0, 10), (35, 20), (90, 10)))
