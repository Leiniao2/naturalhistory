"""
Shared pieces for the Trichonympha models (trichonympha_campanula.py,
trichonympha_collaris.py): giant flagellates (parabasalids) from the hindgut of
termites, where they digest the wood their hosts swallow.

  * The cell is a body of revolution along Y, swept ring by ring from a profile of
    (t, radius) control points: t = 0 is the tip of the rostrum (front, -Y), t = 1 the
    rounded rear. The rostrum ends in a small cap; a species can pinch in a collar behind
    it. The front of the cell is pale and glassy, the rear (where wood is engulfed) a
    little greyer, and a faint nucleus shows through the middle.
  * Flagella: hundreds of fine strands in longitudinal rows (gently spiralling) from the
    rostrum back over the front part of the bell. Each strand leaves the surface, sweeps
    backwards and lies close over the body, so together they form the shaggy sheath that
    makes Trichonympha look like a hairy bell. The rostral ones are a little longer.
  * Wood particles: small angular brown splinters half-sunk into the rear, so they read
    through an opaque material as if seen inside the translucent cell.

Frame: forward -Y (rostrum first), pivot at the body centre (Drift style).
"""

import math
import random

from mathutils import Euler, Matrix, Vector, noise

import bmesh
import nh_model as nh

BODY = (0.74, 0.82, 0.88)        # pale translucent grey-blue
BODY_REAR = (0.66, 0.72, 0.76)   # greyer rear, full of food vacuoles
ROSTRUM = (0.84, 0.90, 0.94)
CAP = (0.92, 0.95, 0.97)
NUCLEUS = (0.52, 0.58, 0.66)
FLAG_BASE = (0.80, 0.87, 0.92)
FLAG_TIP = (0.93, 0.96, 0.98)
WOOD_HAZE = (0.62, 0.56, 0.46)
WOOD = [(0.50, 0.33, 0.16), (0.58, 0.40, 0.20), (0.42, 0.27, 0.13), (0.64, 0.47, 0.25)]


def catmull(ctrl, t):
    """Catmull-Rom interpolation of a sorted [(t, r)] profile at t."""
    if t <= ctrl[0][0]:
        return ctrl[0][1]
    if t >= ctrl[-1][0]:
        return ctrl[-1][1]
    i = max(k for k in range(len(ctrl) - 1) if ctrl[k][0] <= t)
    p0 = ctrl[max(i - 1, 0)][1]
    p1, p2 = ctrl[i][1], ctrl[i + 1][1]
    p3 = ctrl[min(i + 2, len(ctrl) - 1)][1]
    u = (t - ctrl[i][0]) / (ctrl[i + 1][0] - ctrl[i][0])
    u2, u3 = u * u, u * u * u
    return max(0.0, 0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2
                           + (-p0 + 3 * p1 - 3 * p2 + p3) * u3))


class Cell:
    """Body of revolution. profile: [(t, radius)] with radius 0 at t = 0 and t = 1.
    length: front-to-back length; flatten: Z scale of the cross-section."""

    def __init__(self, profile, length=1.8, flatten=0.94, seed=1):
        self.profile = profile
        self.length = length
        self.flatten = flatten
        self.off = Vector((seed * 1.7, seed * 3.1, seed * 0.7))

    def radius(self, t):
        return catmull(self.profile, t)

    def point(self, t, phi):
        r = self.radius(t)
        # slight lumpiness so it isn't a lathe-turned bell
        r *= 1.0 + 0.025 * noise.noise(Vector((math.cos(phi) * 2, t * 4, math.sin(phi) * 2)) + self.off)
        y = (t - 0.5) * self.length
        return Vector((math.cos(phi) * r, y, math.sin(phi) * r * self.flatten))

    def surface(self, t, phi):
        """Point and outward normal at (t, phi)."""
        t = min(max(t, 0.002), 0.998)
        p = self.point(t, phi)
        dt = self.point(min(t + 0.004, 0.999), phi) - self.point(max(t - 0.004, 0.001), phi)
        dp = self.point(t, phi + 0.01) - self.point(t, phi - 0.01)
        n = dt.cross(dp).normalized()
        if n.dot(Vector((p.x, 0, p.z))) < 0:
            n = -n
        return p, n

    def mesh(self, rings=34, segments=22, ts=None):
        """Swept surface; rings are spaced more densely where the profile changes fast."""
        bm = bmesh.new()
        ts = ts or [0.5 - 0.5 * math.cos(math.pi * k / rings) for k in range(rings + 1)]
        tip = bm.verts.new(self.point(0.0, 0.0))
        tail = bm.verts.new(self.point(1.0, 0.0))
        loops = []
        for t in ts[1:-1]:
            loops.append([bm.verts.new(self.point(t, k / segments * math.tau)) for k in range(segments)])
        for k in range(segments):
            j = (k + 1) % segments
            bm.faces.new([tip, loops[0][j], loops[0][k]])
            bm.faces.new([tail, loops[-1][k], loops[-1][j]])
        for a, b in zip(loops, loops[1:]):
            for k in range(segments):
                j = (k + 1) % segments
                bm.faces.new([a[k], a[j], b[j], b[k]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm


def body_color(cell, nucleus_t=0.42, rostrum_t=0.12):
    L = cell.length

    def color(co, n):
        t = co.y / L + 0.5
        c = nh.lerp(BODY, BODY_REAR, nh.smoothstep(0.45, 0.85, t))
        # brownish haze of engulfed wood showing through the rear
        haze = nh.smoothstep(0.55, 0.8, t) * (0.5 + 0.5 * noise.noise(co * 9 + cell.off))
        c = nh.lerp(c, WOOD_HAZE, 0.75 * haze)
        c = nh.lerp(c, ROSTRUM, 1.0 - nh.smoothstep(rostrum_t * 0.6, rostrum_t * 1.4, t))
        c = nh.lerp(c, CAP, 1.0 - nh.smoothstep(0.02, 0.05, t))
        # nucleus seen through the upper and lower faces
        r = cell.radius(nucleus_t) + 1e-6
        d = math.hypot((t - nucleus_t) * L / (r * 0.55), co.x / (r * 0.6))
        c = nh.lerp(c, NUCLEUS, 0.6 * (1.0 - nh.smoothstep(0.6, 1.0, d)))
        k = 1.0 + 0.05 * noise.noise(co * 14 + cell.off)
        return tuple(min(1.0, x * k) for x in c)
    return color


def flagella(cell, rng, rows=26, per_row=11, t_range=(0.03, 0.55), length=(0.28, 0.42),
             t_max=0.72, twist=0.5, lift=0.035, radius=0.0055):
    """Rows of trailing flagella; returns (bmesh, colour fn). length: strand length as a
    fraction of the cell length at the front / back of the flagellated zone; no strand
    reaches past t_max, so the rear of the cell stays bare."""
    bm = bmesh.new()
    t0, t1 = t_range
    L = cell.length
    for row in range(rows):
        phi0 = row / rows * math.tau + rng.uniform(-0.04, 0.04)
        for k in range(per_row):
            u = (k + rng.uniform(0.1, 0.9)) / per_row
            t = t0 + (t1 - t0) * u ** 1.15
            phi = phi0 + twist * (t - t0)
            fl = L * (length[0] + (length[1] - length[0]) * u) * rng.uniform(0.85, 1.15)
            fl = min(fl, (t_max + rng.uniform(-0.03, 0.03) - t) * L)
            if fl < 0.03 * L:
                continue
            # leave the surface, sweep back and lie down over the body again
            pts, radii = [], []
            for s, rr in ((0.0, radius), (0.45, radius * 0.7), (1.0, 0.0)):
                tt = t + s * fl / L
                pp = phi + twist * s * fl / L
                p, n = cell.surface(tt, pp)
                h = 0.003 + lift * (1.2 * s if s < 0.5 else 0.6 + 0.9 * (s - 0.5))
                pts.append(p + n * h)
                radii.append(rr)
            tb = nh.tube(pts, radii, sides=3, cap_start=False)
            vmap = {v: bm.verts.new(v.co) for v in tb.verts}
            for f in tb.faces:
                bm.faces.new([vmap[v] for v in f.verts])
            tb.free()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        # distance from the body surface: tips are lighter
        t = co.y / L + 0.5
        r = cell.radius(min(max(t, 0.0), 1.0)) + 1e-6
        d = math.hypot(co.x, co.z / cell.flatten) / r
        return nh.lerp(FLAG_BASE, FLAG_TIP, nh.smoothstep(1.0, 1.12, d))
    return bm, color


def wood_particles(cell, rng, mb, count=34, t_range=(0.5, 0.95), size=(0.035, 0.07)):
    """Angular splinters of chewed wood, half-sunk into the rear of the cell."""
    for _ in range(count):
        t = rng.uniform(*t_range)
        phi = rng.uniform(0, math.tau)
        p, n = cell.surface(t, phi)
        L = rng.uniform(*size)
        rot = Euler((rng.uniform(0, math.tau), rng.uniform(0, math.tau), rng.uniform(0, math.tau))).to_matrix()
        bm = nh.ellipsoid(radii=(L * 0.35, L, L * 0.28), subdivisions=0, rotation=rot)
        nh.transform(bm, Matrix.Translation(p - n * L * 0.22))
        mb.add(bm, rng.choice(WOOD), smooth=False)


def build(profile, name, seed, length=1.8, flatten=0.94, nucleus_t=0.42, rostrum_t=0.12,
          flagella_args=None, wood_args=None):
    rng = random.Random(seed)
    cell = Cell(profile, length=length, flatten=flatten, seed=seed)
    mb = nh.MeshBuilder()
    mb.add(cell.mesh(), body_color(cell, nucleus_t, rostrum_t))
    mb.add(*flagella(cell, rng, **(flagella_args or {})))
    wood_particles(cell, rng, mb, **(wood_args or {}))
    obj = mb.to_object(name, roughness=0.35)
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj
