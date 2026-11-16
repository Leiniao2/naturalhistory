"""
Extra helpers for the archaeocyath models that need more than nh_archaeocyath.py's ring-stack cup
(protopharetra_polymorpha.py, coscinocyathus_dianthus.py, ethmophyllum_whitneyi.py):

  * Painter: a bmesh with per-vertex colours whose faces are oriented toward a wanted direction
    when they are created, so open, thin-walled parts (cut-away walls, septa, tabulae) still have
    their front faces outward (Unity culls back faces);
  * seabed(): a small, low patch of lime mud with dark clotted microbial crust (the calcimicrobes
    that built early Cambrian reefs together with the archaeocyaths) heaped around the cup bases,
    plus a few loose limestone pebbles (no coralline algae, which are much younger);
  * finish(): grounds the object (pivot at the base, z = 0) and turns on back-face culling in
    the preview material, so the Blender preview shows what Unity will show.
"""

import math

import bmesh
from mathutils import Vector, noise

import nh_model as nh

WARP = Vector((5.1, 1.7, 3.3))
MUD = (0.52, 0.47, 0.37)            # pale lime mud
CRUST = (0.14, 0.09, 0.05)          # dark grey-brown clotted microbial crust
CRUST_LIGHT = (0.26, 0.18, 0.10)
PEBBLES = [(0.40, 0.37, 0.32), (0.33, 0.31, 0.27), (0.46, 0.42, 0.35)]


class Painter:
    """Builds one bmesh with per-vertex colours (copied into a "Col" layer by mesh())."""

    def __init__(self):
        self.bm = bmesh.new()
        self.vcol = {}

    def v(self, co, c):
        vert = self.bm.verts.new(co)
        self.vcol[vert] = c
        return vert

    def face(self, vs, want):
        """New face through vs, flipped if needed so its normal points along `want`."""
        try:
            f = self.bm.faces.new(vs)
        except ValueError:
            return None
        f.normal_update()
        if f.normal.dot(want) < 0:
            f.normal_flip()
        return f

    def grid(self, rows, want, wrap=False):
        """Quads between consecutive rows of verts. want(quad_verts) -> wanted normal."""
        for a, b in zip(rows, rows[1:]):
            n = len(a)
            for k in range(n if wrap else n - 1):
                j = (k + 1) % n
                q = [a[k], a[j], b[j], b[k]]
                self.face(q, want(q))

    def mesh(self):
        col = self.bm.loops.layers.color.new("Col")
        for f in self.bm.faces:
            for lp in f.loops:
                c = self.vcol[lp.vert]
                lp[col] = (c[0], c[1], c[2], 1.0)
        return self.bm


def centroid(vs):
    return sum((v.co for v in vs), Vector()) / len(vs)


def seabed(mb, rng, radius, clots, pebbles=4):
    """Low mud patch of about `radius` with microbial-crust clots [(x, y, z, rx, ry, rz)]."""
    hold = nh.MeshBuilder()
    seed = Vector((rng.random() * 40, rng.random() * 40, 0))
    hold.add(nh.ellipsoid((0, 0, -0.02), (radius, radius * 0.88, 0.045), subdivisions=3,
                          deform=lambda n: 1.0 + 0.18 * noise.noise(n * 2.2 + seed)), MUD)
    for x, y, z, rx, ry, rz in clots:
        hold.add(nh.ellipsoid((x, y, z), (rx, ry, rz), subdivisions=2,
                              deform=lambda n: 1.0 + 0.25 * noise.noise(n * 3.0 + seed)), CRUST)
    fused = hold.fuse(voxel=0.035, smooth=5, max_tris=600)

    def col(co, n):
        # crust on the raised clots (and in blotches on the mud next to them), mud elsewhere
        k = nh.smoothstep(0.005, 0.04, co.z + 0.02 * noise.noise(co * 8 + WARP))
        c = nh.lerp(MUD, CRUST, k)
        clot = noise.noise(co * 14 + WARP * 2)
        c = nh.lerp(c, CRUST_LIGHT if clot > 0 else CRUST, 0.35 * k * abs(clot) * 2)
        return nh.lerp(c, (c[0] * 0.85, c[1] * 0.85, c[2] * 0.85), 0.5 + 0.5 * noise.noise(co * 25))

    mb.add(fused, col)
    for _ in range(pebbles):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.6, 0.9) * radius
        s = rng.uniform(0.03, 0.06)
        ps = Vector((rng.random() * 50, rng.random() * 50, rng.random() * 50))
        bm = nh.ellipsoid((math.cos(a) * r, math.sin(a) * r * 0.88, 0.02), (s, s * rng.uniform(0.7, 1.1), s * 0.5),
                          subdivisions=1, deform=lambda n, ps=ps: 1.0 + 0.3 * noise.noise(n * 1.7 + ps))
        mb.add(bm, rng.choice(PEBBLES), smooth=False)


def finish(mb, name):
    obj = mb.to_object(name, roughness=0.8)
    obj.data.materials[0].use_backface_culling = True
    nh.ground_to_zero(obj)
    return obj
