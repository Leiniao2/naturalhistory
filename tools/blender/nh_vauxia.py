"""
Shared builder for the Vauxia models (vauxia_gracilenta.py, vauxia_pregracilenta.py): Cambrian
aspiculate (spongin-skeleton) demosponges that grew as small upright bushes of tubular branches.

Each branch is a deeply conical, almost cylindrical tube with a simple open central cavity (the
spongocoel) ending in an osculum at its tip. Here every branch is a closed, hollow, open-topped
annular solid (outer wall up the branch axis, a lip, then an inner wall back down part of the
way), so the voxel fuse keeps the openings while merging all branches, the stem and the
holdfast into one seamless body. Side branches start inside their parent, curve upward and
open in their own osculum.

The skeleton was a two-layered net of spongin fibres without spicules: a polygonal (4-6 sided)
endosomal mesh under a thin dermal layer with small pores. That is painted as a Voronoi net of
pale raised fibres with darker pore centres; branch interiors are darkened.

A species script supplies a branch table and a holdfast description and calls build().
Fixed style: pivot at the base (z = 0).
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh
import nh_coral as nc

UP = Vector((0, 0, 1))
MUD = [(0.36, 0.33, 0.29), (0.44, 0.40, 0.34), (0.30, 0.28, 0.25)]


class Branch:
    """parent: index of the parent branch (-1 = rises from the holdfast at `start`).
    t: where along the parent it leaves (0-1). azim/tilt: initial direction (degrees; tilt from
    vertical). length, r0 -> r1: base and rim radius. upturn: how strongly it bends back toward
    vertical. bend: sideways wander. depth: fraction of the length that stays hollow."""

    def __init__(self, parent=-1, t=0.0, azim=0.0, tilt=0.0, length=1.0, r0=0.06, r1=0.07,
                 upturn=0.5, start=(0.0, 0.0), depth=0.35):
        self.parent, self.t, self.azim, self.tilt = parent, t, azim, tilt
        self.length, self.r0, self.r1, self.upturn = length, r0, r1, upturn
        self.start, self.depth = start, depth
        self.pts, self.radii = [], []


def _direction(azim, tilt):
    a, t = math.radians(azim), math.radians(tilt)
    return Vector((math.sin(t) * math.cos(a), math.sin(t) * math.sin(a), math.cos(t)))


def lay_out(branches, segments=10, rng=None):
    """Fills each branch's axis points and radii (parents must come before children)."""
    rng = rng or random.Random(0)
    for b in branches:
        if b.parent < 0:
            p = Vector((b.start[0], b.start[1], 0.0))
        else:
            par = branches[b.parent]
            f = b.t * (len(par.pts) - 1)
            i = min(int(f), len(par.pts) - 2)
            p = par.pts[i].lerp(par.pts[i + 1], f - i)
        d = _direction(b.azim, b.tilt)
        wob = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0.0)) * 0.15
        step = b.length / segments
        b.pts = [p.copy()]
        for k in range(segments):
            d = (d + UP * b.upturn * 0.18 + wob * 0.1).normalized()
            p = p + d * step
            b.pts.append(p.copy())
        # conical tube: slim at the base, widening toward the osculum, slight swelling below the rim
        b.radii = [b.r0 + (b.r1 - b.r0) * (k / segments) ** 0.8 - 0.006 * nh.smoothstep(0.85, 1.0, k / segments)
                   for k in range(segments + 1)]
    return branches


def hollow_branch(pts, radii, wall, depth_rings, sides=20):
    """Closed annular solid: outer wall up `pts`, a lip, then the inner wall back down
    `depth_rings` rings, closed by a floor - so the remesh keeps the opening."""
    bm = bmesh.new()
    frames = []
    prev = None
    for i, p in enumerate(pts):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        if prev is None:
            ref = Vector((1, 0, 0)) if abs(fwd.x) < 0.9 else Vector((0, 1, 0))
            side = fwd.cross(ref).normalized()
        else:
            side = (prev - fwd * prev.dot(fwd)).normalized()
        prev = side
        frames.append((p, side, side.cross(fwd).normalized()))

    def ring(i, r):
        p, side, up = frames[i]
        return [bm.verts.new(p + side * math.cos(k / sides * math.tau) * r + up * math.sin(k / sides * math.tau) * r)
                for k in range(sides)]

    n = len(pts)
    rings = [ring(i, r) for i, r in enumerate(radii)]
    rings += [ring(i, max(0.012, radii[i] - wall)) for i in range(n - 1, n - 2 - depth_rings, -1)]
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def mud_patch(mb, rng, inner, outer, count=8, size=(0.04, 0.08)):
    """A few low, rounded lumps of dark mud and shale chips around the sponge (no coralline
    algae - this is a Cambrian mud bottom)."""
    for _ in range(count):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(inner, outer)
        s = rng.uniform(*size)
        seed = Vector((rng.random() * 50, rng.random() * 50, rng.random() * 50))
        bm = nh.ellipsoid((math.cos(a) * r, math.sin(a) * r, s * 0.1),
                          (s, s * rng.uniform(0.6, 1.0), s * 0.35), subdivisions=1,
                          deform=lambda n, seed=seed: 1.0 + 0.25 * noise.noise(n * 1.5 + seed))
        base = rng.choice(MUD)
        mb.add(bm, lambda co, n, base=base, seed=seed:
               tuple(min(1.0, x * (0.85 + 0.3 * noise.noise(co * 25 + seed))) for x in base))


def build(name, branches, holdfast, palette, wall=0.026, voxel=0.011, max_tris=4800,
          net_freq=26.0, seed=1, mud=(0.3, 0.55)):
    """branches: list of Branch. holdfast: list of ((x, y, z), (rx, ry, rz)[, z-angle radians])
    flattened ellipsoids making the base. palette: dict with body, shade, fibre, pore, rim, vent, holdfast."""
    rng = random.Random(seed)
    lay_out(branches, rng=rng)
    warp = Vector((rng.random() * 40, rng.random() * 40, rng.random() * 40))

    mb = nh.MeshBuilder()
    vents = []
    for b in branches:
        depth_rings = max(2, round(b.depth * (len(b.pts) - 1)))
        mb.add(hollow_branch(b.pts, b.radii, wall, depth_rings), palette["body"])
        vents.append((b, depth_rings))
    for c, r, *angle in holdfast:
        bm = nh.ellipsoid((0, 0, 0), r, subdivisions=3,
                          deform=lambda n: 1.0 + 0.08 * noise.noise(n * 2.0 + warp))
        nh.transform(bm, Matrix.Translation(Vector(c)) @ Matrix.Rotation(angle[0] if angle else 0.0, 4, "Z"))
        mb.add(bm, palette["holdfast"])

    body = mb.fuse(voxel=voxel, smooth=5, smooth_factor=0.5)

    def net(co):
        d = noise.voronoi(co * net_freq + warp)[0]
        fibre = nh.smoothstep(0.12, 0.02, d[1] - d[0])     # cell borders = spongin fibres
        pore = nh.smoothstep(0.32, 0.12, d[0])            # cell centres = pores
        return fibre, pore

    for v in body.verts:
        fibre, pore = net(v.co)
        if v.co.z > 0.04:
            v.co += v.normal * (0.004 * fibre - 0.004 * pore)
    body = nc.decimate(body, max_tris)

    def inside(co, n):
        k = 0.0
        for b, depth_rings in vents:
            pts, radii = b.pts, b.radii
            i0 = len(pts) - 1 - depth_rings
            for i in range(i0, len(pts) - 1):
                a, c = pts[i], pts[i + 1]
                ax = c - a
                t = max(0.0, min(1.0, (co - a).dot(ax) / ax.length_squared))
                q = a + ax * t
                radial = co - q
                rl = radial.length
                r = radii[i] + (radii[i + 1] - radii[i]) * t
                if rl < 1e-6 or rl > r:
                    continue
                facing = nh.smoothstep(0.2, -0.4, n.dot(radial / rl))
                below = nh.smoothstep(-0.005, 0.03, (pts[-1] - co).dot(ax.normalized()))
                k = max(k, facing * nh.smoothstep(r - wall * 0.15, r - wall * 0.7, rl) * below)
        return k

    def rim(co):
        k = 0.0
        for b, _d in vents:
            top, axis = b.pts[-1], (b.pts[-1] - b.pts[-2]).normalized()
            rel = co - top
            k = max(k, nh.smoothstep(0.035, 0.0, abs(rel.dot(axis) + 0.008)) *
                    nh.smoothstep(b.radii[-1] - wall - 0.01, b.radii[-1] - wall * 0.3,
                                  (rel - axis * rel.dot(axis)).length))
        return k

    zmax = max(p.z for b in branches for p in b.pts)

    def color(co, n):
        fibre, pore = net(co)
        h = max(0.0, co.z / zmax)
        c = nh.lerp(palette["shade"], palette["body"], nh.smoothstep(0.0, 0.5, h))
        c = nh.lerp(c, palette["holdfast"], nh.smoothstep(0.08, 0.02, co.z))
        c = nh.lerp(c, palette["shade"], 0.15 * nh.smoothstep(0.1, -0.5, noise.noise(co * 4 + warp)))
        c = nh.lerp(c, palette["fibre"], 0.3 * fibre)
        c = nh.lerp(c, palette["pore"], 0.2 * pore)
        c = nh.lerp(c, palette["rim"], 0.7 * rim(co))
        return nh.lerp(c, palette["vent"], inside(co, n))

    out = nh.MeshBuilder()
    out.add(body, color)
    if mud:
        mud_patch(out, rng, *mud)
    obj = out.to_object(name, roughness=0.8)
    nh.ground_to_zero(obj)
    return obj
