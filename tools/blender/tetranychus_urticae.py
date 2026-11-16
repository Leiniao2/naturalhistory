"""
Procedural two-spotted spider mite (Tetranychus urticae) colony on a leaf, for map colonies.

A small green bean-type leaf lies on the ground, its surface flecked with the pale stipples
that spider-mite feeding leaves behind. On it, under a loose tent of fine white silk threads
spun from vein to vein, stand an adult female and a smaller, narrower male beside a few round,
pearly eggs. The mites are rounded, domed and pale yellow-green with the two big dark
blotches (food seen through the body wall) on either side of the back that give the species
its name, two pairs of red eyespots at the front corners, rows of fine pale dorsal setae, a
small gnathosoma with palps and eight pale legs ending in tiny claws.

Fixed style, like the ladybird: faces -Y, pivot on the ground (lowest point of the leaf at
z = 0).

Usage:
  blender --background --python tools/blender/tetranychus_urticae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SpiderMite.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_mite as mite  # noqa: E402

BODY = (0.84, 0.86, 0.46)        # pale yellow-green
BODY_SHADE = (0.62, 0.66, 0.30)
SPOT = (0.16, 0.17, 0.07)        # dark lateral blotches
EYE = (0.85, 0.08, 0.05)
LEG = (0.90, 0.88, 0.62)
LEG_JOINT = (0.70, 0.68, 0.40)
CLAW = (0.45, 0.40, 0.20)
SETA = (0.96, 0.96, 0.86)
SILK = (0.97, 0.97, 0.94)
EGG = (0.93, 0.93, 0.82)

HALF_LEN = 0.5


def stipple(co):
    """Pale feeding-damage speckles, densest around the mites in the middle of the leaf."""
    near = nh.smoothstep(0.75, 0.15, math.hypot(co.x, co.y * 0.8))
    s = nh.smoothstep(0.25, 0.55, noise.noise(Vector((co.x * 22, co.y * 22, 0.5))))
    return 0.75 * s * (0.35 + 0.65 * near)


LEAF = mite.Leaf(length=1.55, half_width=0.58, curl=0.07, stipple=stipple,
                 stipple_color=(0.86, 0.88, 0.58))


def spot(co, cx, cy, r):
    d = math.hypot((co.x - cx) / r, (co.y - cy) / (r * 1.6))
    d += 0.1 * noise.noise(co * 6)
    return nh.smoothstep(1.0, 0.8, d)


def body_color(co, n):
    c = nh.lerp(BODY_SHADE, BODY, nh.smoothstep(-0.7, 0.4, n.z))
    top = nh.smoothstep(-0.25, 0.3, n.z)
    s = max(spot(co, sx * 0.19, 0.04, 0.16) for sx in (-1, 1)) * top
    c = nh.lerp(c, SPOT, 0.96 * s)
    k = 0.95 + 0.08 * noise.noise(co * 14)
    return tuple(min(1.0, x * k) for x in c)


def spider_mite(male=False):
    """One mite in its own frame (feet at z = 0). The male is narrower with a tapered rear."""
    w, h, rear = (0.27, 0.2, 1.6) if male else (0.36, 0.28, 2.3)
    body = mite.Body(HALF_LEN, mite.oval(w, h, front=2.0, rear=rear,
                                         dz=lambda t: 0.03 * math.cos(t * 1.4)),
                     center_z=0.27, belly=0.55)
    L = 1.15 if male else 1.0
    legs = [
        mite.Leg(t=-0.70, length=0.50 * L, angle=60, lift=0.28, radius=0.034, sides=5, segments=4),
        mite.Leg(t=-0.45, length=0.44 * L, angle=24, lift=0.28, radius=0.034, sides=5, segments=4),
        mite.Leg(t=-0.12, length=0.42 * L, angle=-30, lift=0.26, radius=0.032, sides=5, segments=4, phi=-0.5),
        mite.Leg(t=0.08, length=0.48 * L, angle=-58, lift=0.24, radius=0.032, sides=5, segments=4, phi=-0.55),
    ]
    back = Vector((0, 1, -0.2))
    setae = [(t, phi, 0.17, None, back) for t, phi in
             ((-0.6, 1.2), (-0.35, 0.85), (-0.15, 1.3), (0.1, 0.9), (0.3, 1.25), (0.5, 0.7), (0.7, 1.15))]
    spec = mite.Spec(
        body=body, body_color=body_color, legs=legs,
        leg_color=LEG, leg_joint=LEG_JOINT, claw_color=CLAW,
        body_res=(18, 14), gnatho_size=0.15,
        gnatho_colors=(BODY, LEG, LEG), gnatho_kw=dict(palp_len=0.7, down=0.3),
        setae=setae, seta_color=SETA, seta_radius=0.007,
    )
    mb, _info = mite.build(spec)
    # two pairs of red eyespots at the front corners of the body
    for t, phi in ((-0.52, 0.42), (-0.40, 0.48)):
        for ph in (phi, math.pi - phi):
            p = body.point(t, ph) - body.normal(t, ph) * 0.006
            mb.add(nh.uv_ellipsoid(p, (0.03, 0.03, 0.03), segments=6, rings=4), EYE)
    return mb


def silk(mb, rng, height):
    """Loose tent of fine threads strung between points on the leaf, over the mites."""
    def anchor():
        while True:
            x, y = rng.uniform(-0.5, 0.5), rng.uniform(-0.6, 0.6)
            v = (y + LEAF.length * 0.5) / LEAF.length
            if abs(x) < LEAF.width(v) * 0.85:
                return Vector((x, y, height(x, y) + 0.004))
    for _ in range(22):
        a, b = anchor(), anchor()
        if (a - b).length < 0.3:
            continue
        lift = rng.uniform(0.06, 0.2)
        wob = Vector((rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), 0))
        pts = [a, a.lerp(b, 0.2) + Vector((0, 0, lift * 0.75)) + wob, a.lerp(b, 0.5) + Vector((0, 0, lift)),
               a.lerp(b, 0.8) + Vector((0, 0, lift * 0.75)) - wob, b]
        mb.add(nh.tube(pts, [0.0026] * 5, sides=3), SILK)
    # a few short threads dropping from the tent onto the leaf
    for _ in range(6):
        a = anchor()
        mb.add(nh.tube([a, a + Vector((rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), rng.uniform(0.08, 0.14)))],
                       [0.003, 0.003], sides=3), SILK)


def build():
    rng = random.Random(7)
    mb = nh.MeshBuilder()
    mite.leaf_patch(mb, LEAF, nu=12, nv=18)
    h = LEAF.height

    female_at = Vector((-0.06, 0.02, 0))
    mite.place(spider_mite(), mb, (female_at.x, female_at.y, h(female_at.x, female_at.y)), yaw=-15, scale=0.42)
    male_at = Vector((0.22, -0.36, 0))
    mite.place(spider_mite(male=True), mb, (male_at.x, male_at.y, h(male_at.x, male_at.y)), yaw=35, scale=0.32)
    for x, y in ((0.18, 0.30), (0.25, 0.24), (0.21, 0.38), (-0.28, -0.25)):
        mb.add(nh.ellipsoid((x, y, h(x, y) + 0.03), (0.034, 0.034, 0.032), subdivisions=1),
               lambda co, n: nh.lerp((0.75, 0.76, 0.62), EGG, nh.smoothstep(-0.5, 0.6, n.z)))
    silk(mb, rng, h)

    obj = mb.to_object("SpiderMite", roughness=0.45)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "SpiderMite", ground=(0.33, 0.28, 0.20), views=((35, 35), (10, 70), (-90, 12)))
