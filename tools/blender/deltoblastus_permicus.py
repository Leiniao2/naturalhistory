"""
Procedural Deltoblastus permicus (Permian blastoid echinoderm, theca ~2 cm) for map colonies.

One of the last blastoids, extremely common in the Permian of Timor: a small, bud-shaped
cup (theca) of a few large plates on a short stalk, with five petal-like food grooves
(ambulacra) running down from the top, each edged by a fringe of fine, upright
brachioles that strained food from the water. In Deltoblastus the large deltoid plates
between the petals make the top look like a five-pointed star. Pinkish-buff plates,
darker ambulacra, pale brachioles. A small group on a mud patch.
Faces -Y, pivot on the sea floor (Fixed style).

Usage:
  blender --background --python tools/blender/deltoblastus_permicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Deltoblastus.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, Matrix, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as oe  # noqa: E402

PLATE = (0.84, 0.66, 0.52)
DELTOID = (0.92, 0.78, 0.62)
SUTURE = (0.50, 0.36, 0.28)
AMB = (0.54, 0.30, 0.26)
POREL = (0.30, 0.16, 0.14)
BRACH = (0.96, 0.90, 0.78)
STEM = (0.72, 0.58, 0.46)
MUD = ((0.58, 0.54, 0.46), (0.68, 0.64, 0.54))


def theca_r(n):
    """Radial multiplier of the bud: pentagonal, petals as shallow grooves."""
    a = math.atan2(n.y, n.x)
    lobe = math.cos(5 * a)
    return 1.0 + 0.10 * lobe * nh.smoothstep(-0.6, 0.6, n.z)


def theca_col(c0, R, H):
    def col(co, n):
        p = co - c0
        a = math.atan2(p.y, p.x)
        lobe = math.cos(5 * a)
        h = (p.z / H) if H else 0.0                 # -1 .. 1 over the theca
        amb = nh.smoothstep(-0.80, -0.92, lobe) * nh.smoothstep(-0.55, -0.1, h)
        c = PLATE if h < 0.15 else DELTOID
        # suture between basal/radial and deltoid circlets, and radial sutures
        c = nh.lerp(c, SUTURE, 0.8 * nh.smoothstep(0.05, 0.0, abs(h - 0.15)))
        c = nh.lerp(c, SUTURE, 0.7 * nh.smoothstep(0.975, 0.995, lobe) * nh.smoothstep(0.1, -0.3, h))
        if amb > 0:
            stripe = 0.5 + 0.5 * math.sin(h * 60)
            c = nh.lerp(c, nh.lerp(AMB, POREL, stripe * 0.6), amb)
        k = 0.92 + 0.12 * noise.noise(co * 60)
        return tuple(x * k for x in c)
    return col


def blastoid(mb, rng, base, stem_h, R, lean):
    tilt = Matrix.Rotation(lean[0], 4, "X") @ Matrix.Rotation(lean[1], 4, "Y")
    up = (tilt @ Vector((0, 0, 1, 0))).to_3d().normalized()
    b = Vector(base)
    top_stem = b + up * stem_h
    pts = [b + up * stem_h * t for t in (0.0, 0.33, 0.66, 1.0)]
    mb.add(nh.tube(pts, [R * 0.26, R * 0.2, R * 0.18, R * 0.2], sides=8),
           lambda co, n: nh.lerp(STEM, SUTURE, 0.5 if math.sin((co - b).dot(up) * 260) > 0.6 else 0.0))  # columnal rings
    mb.add(nh.ellipsoid(tuple(b), (R * 0.45, R * 0.45, R * 0.15), subdivisions=2), STEM)
    H = R * 1.15
    c0 = top_stem + up * H
    th = nh.uv_ellipsoid((0, 0, 0), (R, R, H), segments=40, rings=24, deform=theca_r)
    # bud shape: narrower towards the stalk
    for v in th.verts:
        k = 0.55 + 0.45 * nh.smoothstep(-1.0, 0.1, v.co.z / H)
        v.co.x *= k
        v.co.y *= k
    nh.transform(th, Matrix.Translation(c0) @ tilt)
    mb.add(th, theca_col(c0, R, H))
    # brachiole fringes along each ambulacrum edge, rising above the top
    for k in range(5):
        a0 = math.pi / 5 + k * 2 * math.pi / 5
        for side in (-1, 1):
            a = a0 + side * 0.10
            for i in range(7):
                t = i / 6
                ang_z = -0.35 + 1.2 * t            # from mid-flank up to the summit
                rr = R * (0.55 + 0.45 * math.cos(ang_z * 0.9)) * (0.6 + 0.4 * (1 - t))
                p = Vector((rr * math.cos(a), rr * math.sin(a), H * math.sin(ang_z)))
                q = p + Vector((math.cos(a) * R * 0.1, math.sin(a) * R * 0.1, R * (0.9 + 0.5 * t)))
                p, q = c0 + (tilt @ p.to_4d()).to_3d(), c0 + (tilt @ q.to_4d()).to_3d()
                mb.add(nh.tube([p, p.lerp(q, 0.5), q], [R * 0.035, R * 0.03, R * 0.012], sides=4), BRACH)


def build():
    rng = random.Random(4)
    mb = nh.MeshBuilder()
    oe.mud_patch(mb, 0.80, MUD, seed=5)
    blastoid(mb, rng, (-0.12, 0.05, 0.015), 0.32, 0.20, (0.10, -0.12))
    blastoid(mb, rng, (0.32, -0.20, 0.015), 0.20, 0.15, (-0.15, 0.20))
    blastoid(mb, rng, (0.20, 0.42, 0.015), 0.12, 0.12, (0.25, 0.10))
    return oe._finish(mb, "Deltoblastus", roughness=0.6)


if __name__ == "__main__":
    nh.run(build, "Deltoblastus", ground=(0.62, 0.58, 0.48), views=((30, 25), (10, 70), (-100, 12)))
