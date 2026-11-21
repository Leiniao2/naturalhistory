"""
Procedural Aulacoceras sulcatum (Late Triassic aulacocerid coleoid, ~50 cm with guard).

A squid-like relative of the belemnites from the Alpine seas of the Late Triassic: a
streamlined mantle with small fins, a head with large eyes and ten hooked arms, and inside
the back end a chambered shell sheathed in a long, slender, pointed guard (rostrum) whose
surface is scored with deep lengthwise grooves (sulcatum means "furrowed"). The guard
pokes out behind as a long spike. Faces -Y (arms forward), pivot at the body centre.

Output: Assets/Resources/Models/Species/Aulacoceras.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402

PALE = (0.86, 0.70, 0.58)
DORSAL = (0.50, 0.28, 0.20)
SPOT = (0.34, 0.16, 0.10)
ARM = (0.72, 0.48, 0.38)
HOOK = (0.94, 0.90, 0.80)
GUARD = (0.82, 0.76, 0.62)
GROOVE = (0.42, 0.36, 0.26)
EYE = (0.03, 0.03, 0.05)
IRIS = (0.62, 0.56, 0.36)


def body_col(co, n):
    up = nh.smoothstep(-0.4, 0.6, n.z)
    c = nh.lerp(PALE, DORSAL, up * 0.85)
    sp = noise.noise(co * 24.0)
    return nh.lerp(c, SPOT, nh.smoothstep(0.30, 0.50, sp) * (0.3 + 0.5 * up))


def guard_col(co, n):
    a = math.atan2(co.z, co.x)
    g = 0.5 + 0.5 * math.cos(a * 8.0)
    return nh.lerp(GUARD, GROOVE, nh.smoothstep(0.75, 0.98, g))


def build():
    parts = nh.MeshBuilder()
    g = (0.5, 0.5, 0.5)
    parts.add(nh.tube([(0, -0.30, 0), (0, -0.15, 0), (0, 0.05, 0), (0, 0.22, 0), (0, 0.32, 0)],
                      [0.085, 0.095, 0.090, 0.065, 0.030], sides=20), g)
    parts.add(nh.ellipsoid((0, -0.38, 0.0), (0.075, 0.09, 0.065), 3), g)
    for s in (-1, 1):
        parts.add(nh.ellipsoid((s * 0.05, -0.38, 0.015), (0.04, 0.045, 0.04), 3), g)
    parts.add(nh.ellipsoid((0, -0.47, 0.0), (0.055, 0.05, 0.05), 3), g)
    fused = parts.fuse(voxel=0.012, smooth=4, smooth_factor=0.5)
    mb = nh.MeshBuilder()
    mb.add(fused, body_col)
    # long grooved guard projecting behind
    gp = [Vector((0, 0.20 + 0.70 * t, 0.0)) for t in [k / 12 for k in range(13)]]
    mb.add(nh.tube(gp, [0.034 * (1.0 - t) ** 0.7 + 0.001 for t in [k / 12 for k in range(13)]], sides=16), guard_col)
    # small rounded fins near the rear of the mantle
    for s in (-1, 1):
        pts = [(s * 0.05, 0.08, 0.0), (s * 0.13, 0.13, 0.004), (s * 0.14, 0.20, 0.004), (s * 0.08, 0.27, 0.0),
               (s * 0.03, 0.27, 0.0), (s * 0.03, 0.08, 0.0)]
        if s < 0:
            pts.reverse()
        mb.add(nh.flat_panel(pts, thickness=0.010), lambda co, n: nh.lerp(PALE, DORSAL, 0.4), smooth=False)
        c = Vector((s * 0.088, -0.385, 0.02))
        mb.add(nh.ellipsoid(c, (0.022, 0.032, 0.03), 2), lambda co, n, s=s: EYE if n.x * s > 0.5 else IRIS)
    # ten arms reaching forward with rows of pale hooks
    for k in range(10):
        a = k / 10 * math.tau + math.pi / 10
        L = 0.30 + 0.03 * math.cos(a * 2.0)
        pts, rad = [], []
        for i in range(11):
            t = i / 10
            spread = 0.04 * (1.0 + 1.0 * math.sin(t * math.pi * 0.85)) * (1.0 - 0.2 * t)
            pts.append((math.cos(a) * spread, -0.48 - L * t, math.sin(a) * spread * 0.9 - 0.015 * t))
            rad.append(0.016 * (1.0 - 0.85 * t) + 0.0015)
        rad[-1] = 0.0
        mb.add(nh.tube(pts, rad, sides=6, cap_start=False), ARM)
        for i in range(2, 9, 2):
            p = Vector(pts[i])
            inward = Vector((-math.cos(a), 0, -math.sin(a))) * rad[i]
            mb.add(nh.ellipsoid(tuple(p + inward), (0.004, 0.004, 0.004), 1), HOOK)
    return kit.finish(mb, "Aulacoceras", pivot="center", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "Aulacoceras", background=(0.05, 0.16, 0.22), views=((35, 25), (-90, 8), (150, 35)))
