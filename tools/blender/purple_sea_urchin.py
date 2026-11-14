"""
Purple sea urchin (Strongylocentrotus purpuratus) for the map, Ground style.

A slightly flattened violet test bristling with a few hundred stout spines of
varied length and tilt, tiny tube feet peeking between them, sitting on a small
rock with pink coralline crust and a scrap of kelp holdfast. Reads as a spiky
purple ball from above. Pivot on the ground (rock base at z = 0), faces -Y.

  blender --background --python tools/blender/purple_sea_urchin.py -- [--render out.png]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SEED = 11
TEST_R = 0.42          # test (shell) radius
TEST_FLAT = 0.68       # vertical squash
TEST_Z = 0.34          # centre height above the rock base
SPINES = 340

TEST_DARK = (0.16, 0.03, 0.20)
TEST_MID = (0.30, 0.06, 0.38)
SPINE_BASE = (0.30, 0.05, 0.42)
SPINE_TIP = (0.62, 0.26, 0.85)
TUBE_FOOT = (0.75, 0.45, 0.80)
ROCK_DARK = (0.30, 0.28, 0.26)
ROCK_LIGHT = (0.52, 0.48, 0.43)
CORALLINE = (0.78, 0.42, 0.52)
KELP = (0.30, 0.24, 0.08)


def fib_dirs(n, rng, zmin=-0.55):
    out = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 1 - (i + 0.5) / n * 2
        if z < zmin:
            continue
        r = math.sqrt(max(0.0, 1 - z * z))
        a = golden * i
        v = Vector((math.cos(a) * r, math.sin(a) * r, z))
        v += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.05
        out.append(v.normalized())
    return out


def test_point(d):
    return Vector((d.x * TEST_R, d.y * TEST_R, d.z * TEST_R * TEST_FLAT + TEST_Z))


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # Rock base: a lumpy, flattened boulder
    def rock_deform(n):
        return 1.0 + noise.noise(n * 2.2 + Vector((4.0, 1.0, 2.0))) * 0.22

    rock = nh.ellipsoid((0.04, 0.06, 0.05), (0.58, 0.50, 0.15), subdivisions=2, deform=rock_deform)

    def rock_col(co, n):
        t = 0.5 + 0.5 * noise.noise(co * 6.0)
        c = nh.lerp(ROCK_DARK, ROCK_LIGHT, t)
        crust = noise.noise(co * 3.3 + Vector((9.0, 2.0, 0.0)))
        if crust > 0.0 and n.z > 0.0:
            c = nh.lerp(c, CORALLINE, min(1.0, crust * 3.0))
        return c

    mb.add(rock, rock_col)

    # Kelp holdfast: a few root-like strands gripping the rock edge
    for k in range(5):
        a = rng.uniform(0, math.tau)
        p0 = Vector((math.cos(a) * 0.40, math.sin(a) * 0.34 + 0.05, 0.08))
        p1 = p0 + Vector((math.cos(a) * 0.12, math.sin(a) * 0.12, -0.06))
        p2 = p1 + Vector((math.cos(a + 0.6) * 0.1, math.sin(a + 0.6) * 0.1, -0.05))
        mb.add(nh.tube([p0, p1, p2], [0.025, 0.018, 0.008], sides=5), KELP)

    # Test (shell): flattened sphere with tubercle bumps
    def test_deform(n):
        return 1.0 + max(0.0, 0.6 - noise.cell(n * 9.0)) * 0.05

    test = nh.ellipsoid((0, 0, TEST_Z), (TEST_R, TEST_R, TEST_R * TEST_FLAT), subdivisions=3,
                        deform=test_deform)

    def test_col(co, n):
        t = 0.5 + 0.5 * noise.noise(co * 11.0)
        return nh.lerp(TEST_DARK, TEST_MID, t)

    mb.add(test, test_col)

    # Spines: stout 5-sided cones, longest around the equator, shorter on top and below
    dirs = fib_dirs(SPINES, rng, zmin=-0.45)
    # extra short, splayed spines on the crown so the test doesn't show through from above
    dirs += [d for d in fib_dirs(260, rng) if d.z > 0.55]
    for d in dirs:
        base = test_point(d) - d * 0.02
        lat = abs(d.z)
        length = (0.30 - 0.05 * lat) * rng.uniform(0.75, 1.15)
        # tilt a little toward random neighbours, droop the lower ones downward
        tilt = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * (0.18 + 0.25 * max(0.0, d.z - 0.5))
        out_dir = (d + tilt + Vector((0, 0, -0.15 if d.z < 0 else 0.0))).normalized()
        mid = base + out_dir * length * 0.45
        tip = base + out_dir * length
        r0 = 0.024 * rng.uniform(0.85, 1.15)
        spine = nh.tube([base, mid, tip], [r0, r0 * 0.62, 0.0], sides=4, cap_start=False)
        total = length

        def spine_col(co, n, b=base, L=total):
            t = min(1.0, (co - b).length / L)
            return nh.lerp(SPINE_BASE, SPINE_TIP, t ** 1.3)

        mb.add(spine, spine_col)

    # Tube feet: tiny pale knobs between spines
    for d in fib_dirs(70, rng, zmin=-0.4):
        p = test_point(d) + d * 0.01
        mb.add(nh.ellipsoid(tuple(p), (0.012, 0.012, 0.012), subdivisions=0), TUBE_FOOT)

    obj = mb.to_object("PurpleSeaUrchin", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "PurpleSeaUrchin", ground=(0.25, 0.32, 0.30),
           views=((35, 30), (-90, 10), (10, 75)))
