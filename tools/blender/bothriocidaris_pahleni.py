"""
Procedural Bothriocidaris pahleni (Late Ordovician sea urchin, Estonia; one of the oldest
known echinoids) for map colonies (Fixed style).

A small, globular sea urchin about 1-2 cm across, very different from living ones: each
of its five food-groove zones (ambulacra) has two columns of plates, but the zones between
them are just one column of plates wide. The plates carry short, stubby spines; the mouth
is underneath and the anus on top. It crept over the sea floor grazing on algae and
detritus. Built as a slightly flattened globe painted with its plate columns, spiny all
over, on a patch of mud. Dull plum-red with paler ambulacra. Pivot on the sea floor
(z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/bothriocidaris_pahleni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BothriocidarisPahleni.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "BothriocidarisPahleni"
INTER = (0.56, 0.26, 0.26)
AMBU = (0.80, 0.56, 0.48)
SUTURE = (0.28, 0.12, 0.12)
SPINE = (0.86, 0.72, 0.62)
SPINE_TIP = (0.98, 0.92, 0.84)

RAD = 0.42
C = Vector((0, 0, RAD * 0.86 + 0.02))
ROWS = 9


def cell(co):
    d = co - C
    d = Vector((d.x, d.y, d.z / 0.86)).normalized()
    lat = math.acos(max(-1.0, min(1.0, d.z)))          # 0 top .. pi bottom
    phi = math.atan2(d.y, d.x) % math.tau
    sector = phi / math.tau * 10                          # 10 zones: amb, inter, amb...
    zone = int(sector) % 10
    f = sector - math.floor(sector)
    amb = zone % 2 == 0
    row = lat / math.pi * ROWS
    return amb, f, row, lat


def col(co, n):
    amb, f, row, lat = cell(co)
    if amb:
        sub = f * 2
        fx = sub - math.floor(sub)
        rr = row + (0.5 if int(sub) % 2 else 0.0)
    else:
        fx = f
        rr = row
    fy = rr - math.floor(rr)
    edge = min(fx, 1 - fx, fy, 1 - fy)
    c = AMBU if amb else INTER
    c = nh.lerp(c, SUTURE, 1.0 - nh.smoothstep(0.0, 0.08, edge))
    if lat < 0.18 or lat > math.pi - 0.25:
        c = SUTURE
    return c


def build():
    mb = nh.MeshBuilder()
    kit.mud(mb, 0.75)
    mb.add(nh.ellipsoid(tuple(C), (RAD, RAD, RAD * 0.86), subdivisions=5), col)
    # spines: one per plate centre
    for zone in range(10):
        amb = zone % 2 == 0
        cols = 2 if amb else 1
        for cc in range(cols):
            for r in range(1, ROWS - 1):
                rr = r + 0.5 + (0.5 if (amb and cc == 1) else 0.0)
                if rr >= ROWS - 0.6:
                    continue
                lat = rr / ROWS * math.pi
                phi = (zone + (cc + 0.5) / cols) / 10 * math.tau
                d = Vector((math.sin(lat) * math.cos(phi), math.sin(lat) * math.sin(phi), math.cos(lat)))
                p = C + Vector((d.x * RAD, d.y * RAD, d.z * RAD * 0.86))
                nrm = Vector((d.x, d.y, d.z / 0.86)).normalized()
                if p.z < 0.08:
                    continue
                L = 0.10 if not amb else 0.07
                mb.add(nh.ellipsoid(tuple(p), (0.022, 0.022, 0.022), 1), SPINE)
                mb.add(nh.tube([p, p + nrm * L], [0.014, 0.0], sides=5),
                       lambda co, n, p=p, L=L: nh.lerp(SPINE, SPINE_TIP, min(1.0, (co - p).length / L)))
    return kit.finish_fixed(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
