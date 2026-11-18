"""
Shared helpers for the spiny Devonian trilobites added in the Devonian combat batch
(terataspis_grandis.py, dicranurus_monstrosus.py).

Thin layer over nh_ord_trilobite (parametric shell, genal / pleural / pygidial spines,
eyes, antennae, legs):

  * build(spec, extras): like nh_ord_trilobite.build(), but calls extras(mb, body) just
    before the mesh is turned into an object, so species can add their own pieces
    (horns, tubercles, axial spines) into the same mesh and get the same centring.
  * tubercles(): scatters small hemispherical bumps over the dorsal shell.
  * axial_spines(): an upright spine on every thoracic axial ring.
  * curl(): a tapering spine along a sampled curve (ram's-horn occipital spines).
"""

import math
import random

from mathutils import Vector

import nh_model as nh
import nh_ord_trilobite as tri

VIEWS = tri.VIEWS


def build(spec, extras=None):
    orig = nh.MeshBuilder.to_object

    def patched(self, name, roughness=0.6):
        nh.MeshBuilder.to_object = orig
        if extras:
            extras(self, tri.Body(spec))
        return orig(self, name, roughness)

    nh.MeshBuilder.to_object = patched
    try:
        return tri.build(spec)
    finally:
        nh.MeshBuilder.to_object = orig


def tubercles(mb, body, n, r, color, seed=1, y_range=None, edge=0.92):
    rnd = random.Random(seed)
    y0, y1 = y_range or (body.y_front + 0.02, body.y_back - 0.02)
    placed = 0
    tries = 0
    while placed < n and tries < n * 20:
        tries += 1
        y = rnd.uniform(y0, y1)
        w = body.half_width(y)
        x = rnd.uniform(-w * edge, w * edge)
        rr = r * rnd.uniform(0.7, 1.3)
        z = body.height(x, y)
        mb.add(nh.ellipsoid((x, y, z - rr * 0.2), (rr, rr, rr * 0.8), 1), color)
        placed += 1


def axial_spines(mb, body, length, r, color, lean=0.5, every=1):
    s = body.s
    for k in range(0, s.segments, every):
        y = body.y_ceph + body.seg * (k + 0.5)
        z = body.height(0, y)
        mb.add(tri.spine((0, y, z - 0.01), (0, y + length * lean, z + length), r, flat=1.0), color)


def curl(mb, pts, r0, color, sides=7):
    n = len(pts)
    radii = [r0 * (1.0 - 0.85 * i / (n - 1)) for i in range(n - 1)] + [0.0]
    mb.add(nh.tube([Vector(p) for p in pts], radii, sides=sides), color)
