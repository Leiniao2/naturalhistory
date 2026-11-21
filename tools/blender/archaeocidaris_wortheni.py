"""
Procedural Archaeocidaris wortheni (Early Carboniferous of North America, a Palaeozoic sea
urchin with a test about 5 cm across) for map colonies (Fixed style).

A round, somewhat flattened purple-brown test: five narrow ambulacral zones of small plates
alternate with five broad interambulacra, each of two columns of large plates; every large
plate carries one big rounded tubercle with a long, stout, buff spine banded darker and
covered in small thorns. Far fewer but much longer spines than a modern urchin. It stands on
a small patch of sandy sea floor. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/archaeocidaris_wortheni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Archaeocidaris.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

NAME = "Archaeocidaris"
R = 0.30            # test radius
FLAT = 0.72
TZ = 0.25           # test centre height

TEST_DARK = (0.24, 0.10, 0.16)
TEST_MID = (0.42, 0.20, 0.26)
AMBUL = (0.55, 0.36, 0.30)
TUBERCLE = (0.72, 0.56, 0.48)
SPINE_A = (0.70, 0.56, 0.36)
SPINE_B = (0.34, 0.22, 0.14)
THORN = (0.80, 0.68, 0.48)
SAND = (0.62, 0.56, 0.42)
SAND_DARK = (0.44, 0.40, 0.30)
SHELL = (0.82, 0.78, 0.68)


def tp(d):
    return Vector((d.x * R, d.y * R, d.z * R * FLAT + TZ))


def direction(lon, lat):
    return Vector((math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)))


def build():
    rng = random.Random(7)
    mb = nh.MeshBuilder()

    # sandy seabed patch with a few shell bits
    def sand_def(n):
        return 1.0 + 0.12 * noise.noise(n * 3.0)
    mb.add(nh.ellipsoid((0, 0, 0.02), (0.62, 0.58, 0.05), subdivisions=3, deform=sand_def),
           lambda co, n: nh.lerp(SAND_DARK, SAND, 0.5 + 0.5 * noise.noise(co * 9.0)))
    for k in range(5):
        a = rng.uniform(0, math.tau)
        rr = rng.uniform(0.38, 0.55)
        mb.add(nh.ellipsoid((math.cos(a) * rr, math.sin(a) * rr, 0.06), (0.035, 0.025, 0.012), 1), SHELL)

    # test: interambulacra purple-brown, ambulacra paler narrow bands
    def test_col(co, n):
        c = co - Vector((0, 0, TZ))
        lon = math.atan2(c.y, c.x)
        k = (lon / (math.tau / 5)) % 1.0
        if abs(k - 0.5) > 0.44:
            return AMBUL
        t = 0.5 + 0.5 * noise.noise(co * 14.0)
        return nh.lerp(TEST_DARK, TEST_MID, t)
    mb.add(nh.ellipsoid((0, 0, TZ), (R, R, R * FLAT), subdivisions=3), test_col)

    # apical disc
    mb.add(nh.ellipsoid((0, 0, TZ + R * FLAT), (0.06, 0.06, 0.015), 2), AMBUL)

    # large plates: 5 interambulacra x 2 columns x rows of latitudes
    lats = [math.radians(a) for a in (62, 36, 10, -16, -42)]
    for ia in range(5):
        centre = (ia + 0.5) * math.tau / 5 + math.radians(90)
        for col in (-1, 1):
            for ri, lat in enumerate(lats):
                lon = centre + col * math.radians(15 if ri else 11) + (math.radians(7) if ri % 2 else 0)
                d = direction(lon, lat)
                p = tp(d)
                nrm = Vector((d.x, d.y, d.z / FLAT)).normalized()
                # tubercle: a scrobicule ring and a boss
                mb.add(nh.ellipsoid(tuple(p), (0.045, 0.045, 0.045), 2), TUBERCLE)
                mb.add(nh.ellipsoid(tuple(p + nrm * 0.03), (0.022, 0.022, 0.022), 2), (0.86, 0.74, 0.64))
                if lat < math.radians(-30):
                    # short stubby lower spines (the urchin rests on them)
                    L = 0.16
                    out = (nrm + Vector((0, 0, -0.5))).normalized()
                else:
                    L = (0.62 if lat < 0.9 else 0.48) * rng.uniform(0.9, 1.08)
                    out = (nrm + Vector((0, 0, 0.18)) + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * 0.08).normalized()
                base = p + nrm * 0.04
                tip = base + out * L
                r0 = 0.026

                def spine_col(co, n, b=base, L=L):
                    t = (co - b).length / L
                    band = (t * 6.0) % 1.0
                    c = nh.lerp(SPINE_A, SPINE_B, 0.75 if band < 0.32 else 0.0)
                    return c
                pts = [base] + [base + out * (0.03 + (L - 0.03) * k / 8) for k in range(9)]
                rads = [r0 * 0.7] + [r0 * (1 - 0.8 * (k / 8) ** 1.4) for k in range(8)] + [0.004]
                mb.add(nh.tube(pts, rads, sides=5), spine_col)
                # thorns along the spine
                side = out.cross(Vector((0, 0, 1)))
                if side.length < 1e-3:
                    side = Vector((1, 0, 0))
                side.normalize()
                up = side.cross(out).normalized()
                nth = int(L / 0.06)
                for t in range(1, nth):
                    q = base + out * (L * t / nth)
                    a = t * 2.1 + ri
                    dd = (side * math.cos(a) + up * math.sin(a)).normalized()
                    rr = r0 * (1 - 0.6 * t / nth)
                    mb.add(nh.tube([q + dd * rr * 0.6, q + dd * (rr + 0.03) + out * 0.012], [0.008, 0.0], sides=3), THORN)

    # small ambulacral spines / tube feet
    for ia in range(5):
        lon = ia * math.tau / 5 + math.radians(90)
        for lat in range(-50, 75, 12):
            d = direction(lon, math.radians(lat))
            p = tp(d)
            nrm = Vector((d.x, d.y, d.z / FLAT)).normalized()
            mb.add(nh.tube([p, p + nrm * 0.05], [0.008, 0.0], sides=4), (0.70, 0.50, 0.46))

    obj = mb.to_object(NAME, roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.25, 0.32, 0.30), views=((35, 30), (-90, 10), (10, 75)))
