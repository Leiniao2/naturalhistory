"""
Small fish helpers for the Jurassic batch (hybodus_hauffianus.py, lepidotes_gigas.py), on top
of nh_fish: piecewise-linear side-view outlines and a fin builder that takes the fin as a
base line on the body plus an outer edge line. Side view: length along Y (snout -Y),
height along Z, thickness X. Pivot at the body centre.
"""

import nh_model as nh
import nh_fish as fish


def interp(table, y):
    if y <= table[0][0]:
        return table[0][1]
    for (y0, v0), (y1, v1) in zip(table, table[1:]):
        if y0 <= y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0)
    return table[-1][1]


class Outline:
    """rows: (y, top z, bottom z, half width)."""

    def __init__(self, rows):
        self.rows = rows
        self.top = lambda y: interp([(r[0], r[1]) for r in rows], y)
        self.bot = lambda y: interp([(r[0], r[2]) for r in rows], y)
        self.width = lambda y: max(1e-4, interp([(r[0], r[3]) for r in rows], y))
        self.y0, self.y1 = rows[0][0], rows[-1][0]

    def body(self, mb, color, stations=48, ring=22):
        fish.body(mb, self.top, self.bot, self.width, self.y0, self.y1, color, stations=stations, ring=ring)


def midfin(mb, base, edge, color, th0=0.02, th1=0.004):
    """Median fin (dorsal/anal/caudal) in the x = 0 plane: base and edge are [(y, z)]."""
    fish.fin(mb, [(0.0, y, z) for y, z in base], [(0.0, y, z) for y, z in edge], color, rows=3,
             th0=th0, th1=th1, normal=(1, 0, 0))


def pairfin(mb, base, edge, color, th0=0.016, th1=0.004):
    """Paired fins: base/edge as [(x, y, z)] for the right side, mirrored to the left."""
    for sx in (1, -1):
        fish.fin(mb, [(sx * x, y, z) for x, y, z in base], [(sx * x, y, z) for x, y, z in edge], color, rows=3,
                 th0=th0, th1=th1)
