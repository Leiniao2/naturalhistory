"""
Procedural low-poly Globigerina bulloides, a spinose planktonic foraminifer.

A calcite test of four inflated, near-spherical chambers in the final whorl, each larger than the
last, set round a deep umbilicus in a low trochospiral (a bunch of four balloons of increasing
size, with a few tiny earlier chambers peeping out on the spiral side, +Z). The last and biggest
chamber opens into the umbilicus through one large, high, open arched aperture with a pale lip.
The wall is white-cream and finely pitted with pores. About forty long, very fine calcite spines
radiate out from the chambers, and golden-brown symbiont dots ride along some of them.
Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/globigerina_bulloides.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Globigerina.fbx
About 1.6 units across including the spines (the test itself ~0.75). The test is tipped so
its umbilical side and aperture face -Y (front). Pivot at the centre (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 4
SPINES = 40
REACH = 0.80            # spine tips end about this far from the centre
TEST_TRIS = 1500

# final whorl: (angle deg, distance from the coiling axis, z, radius); grows anticlockwise
# seen from the spiral side, the last chamber at the back (+Y) so its aperture faces -Y
CHAMBERS = [(165, 0.155, 0.06, 0.13), (260, 0.19, 0.04, 0.165), (355, 0.225, 0.01, 0.21), (92, 0.27, -0.03, 0.27)]
# tiny chambers of the earlier whorls, showing on the spiral side
EARLY = [(80, 0.07, 0.15, 0.085), (10, 0.04, 0.18, 0.065), (-40, 0.05, 0.19, 0.05)]

WALL = (0.95, 0.93, 0.85)
WALL_DEEP = (0.82, 0.78, 0.66)
PORE = (0.62, 0.57, 0.46)
SUTURE = (0.74, 0.70, 0.58)
APERTURE = (0.24, 0.20, 0.15)
LIP = (0.99, 0.98, 0.93)
SPINE = (0.96, 0.95, 0.88)
SYMBIONT = (0.86, 0.62, 0.12)
SYMBIONT_DARK = (0.66, 0.44, 0.08)


def chamber_list():
    out = []
    for ang, d, z, r in EARLY + CHAMBERS:
        a = math.radians(ang)
        out.append((Vector((math.cos(a) * d, math.sin(a) * d, z)), r))
    return out


def build():
    rng = random.Random(SEED)
    chambers = chamber_list()
    last_c, last_r = chambers[-1]
    # the aperture: on the last chamber, facing into the umbilicus and down
    umb = Vector((0.0, 0.0, -0.12))
    ap_dir = (umb - last_c).normalized()
    ap_dir = (ap_dir + Vector((0, 0, -0.35))).normalized()
    ap_side = ap_dir.cross(Vector((0, 0, 1))).normalized()
    ap_up = ap_side.cross(ap_dir).normalized()

    mb = nh.MeshBuilder()
    for c, r in chambers:
        mb.add(nh.ellipsoid(tuple(c), (r, r, r * 0.97), subdivisions=3), WALL)
    test = mb.fuse(voxel=0.012, smooth=4, max_tris=TEST_TRIS)

    def arch(co):
        """0..1 inside the arched aperture on the last chamber (a high, round-topped arch)."""
        d = co - last_c
        if d.length < 1e-6 or d.normalized().dot(ap_dir) < 0.3:
            return 0.0, 0.0
        u = d.dot(ap_side) / (last_r * 0.58)
        v = d.dot(ap_up) / (last_r * 0.70)
        # a round-topped arch whose foot opens into the umbilicus
        q = math.sqrt(u * u + v * v)
        return 1.0 - nh.smoothstep(0.75, 1.0, q), 1.0 - nh.smoothstep(1.0, 1.25, q)

    # sink the aperture into the last chamber
    for v in test.verts:
        inside, lip = arch(v.co)
        if lip > 0:
            n = (v.co - last_c).normalized()
            v.co += n * last_r * (0.06 * (lip - inside) - 0.55 * inside)   # a raised lip round a deep opening

    def test_col(co, n):
        inside, lip = arch(co)
        # nearest chamber -> how deep in a suture this point sits
        ds = sorted(((co - c).length - r) for c, r in chambers)
        suture = nh.smoothstep(-0.03, -0.005, ds[1]) if len(ds) > 1 else 0.0
        c = nh.lerp(WALL, WALL_DEEP, nh.smoothstep(0.2, -0.8, n.z) * 0.35)
        pit = noise.noise(co * 30.0)
        c = nh.lerp(c, PORE, nh.smoothstep(0.05, 0.4, pit))
        c = nh.lerp(c, SUTURE, suture * 0.6)
        c = nh.lerp(c, LIP, (lip - inside) * 0.9)
        return nh.lerp(c, APERTURE, inside)

    out = nh.MeshBuilder()
    out.add(test, test_col)

    # spines: radiating straight from the chamber walls, avoiding the aperture
    weights = [r * r for _c, r in chambers]
    placed = 0
    tries = 0
    centre = Vector((0.0, 0.0, 0.03))
    while placed < SPINES and tries < 5000:
        tries += 1
        c, r = rng.choices(chambers, weights=weights)[0]
        d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        p = c + d * r * 0.97
        if any((p - c2).length < r2 * 0.99 for c2, r2 in chambers if c2 is not c):
            continue
        if c is last_c and d.dot(ap_dir) > 0.55:
            continue
        out_dir = (d * 0.7 + (p - centre).normalized() * 0.3).normalized()
        if (p - centre).normalized().dot(out_dir) < 0.3:
            continue
        length = REACH * rng.uniform(0.85, 1.0) - (p - centre).length
        if length < 0.25:
            continue
        tip = p + out_dir * length
        base = p - out_dir * 0.01
        out.add(nh.tube([base, base + out_dir * length * 0.5, tip], [0.0075, 0.0055, 0.0], sides=3), SPINE)
        if placed % 2 == 0:
            for _k in range(rng.randint(1, 3)):
                t = rng.uniform(0.2, 0.85)
                s = rng.uniform(0.012, 0.018)
                q = base + out_dir * length * t
                col = SYMBIONT if rng.random() < 0.6 else SYMBIONT_DARK
                out.add(nh.ellipsoid(tuple(q), (s, s, s), subdivisions=1), col)
        placed += 1

    # drifting, tipped so the umbilical side and its aperture turn toward the front (-Y)
    nh.transform(out.bm, Matrix.Rotation(math.radians(-70), 4, "X"))
    obj = out.to_object("Globigerina", roughness=0.55)
    # pivot at the centre of the whole thing
    lo = [min(v.co[a] for v in obj.data.vertices) for a in range(3)]
    hi = [max(v.co[a] for v in obj.data.vertices) for a in range(3)]
    for v in obj.data.vertices:
        for a in range(3):
            v.co[a] -= (lo[a] + hi[a]) / 2
    return obj


if __name__ == "__main__":
    nh.run(build, "Globigerina", views=((20, 15), (35, 40), (180, 30)))
