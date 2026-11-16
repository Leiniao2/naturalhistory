"""
Shared builder for thin-walled glass sponges whose wall is a DIAGONAL lattice of cross-shaped
spicules (diagoniella_cyathiformis.py, triticispongia_diagonata.py): a variant of
nh_protospongia's square lattice sac, with the spicule strands running at +-45 degrees around
the body instead of vertically and horizontally.

The body is a surface of revolution (outer wall, rounded lip, inner wall back down into the
cavity, closed by a floor) like nh_protospongia, and the lattice is again built into the outer
wall as raised ribs. To keep diagonal ribs crisp with few vertices the wall is sampled on a
grid that is square in lattice units: m samples per cell around AND up (the row spacing is
tied to the local circumference, so cells stay square and shrink toward the narrow base, as
the spicules do on a real sponge). Diagonal lines u + v = k and u - v = k then pass exactly
through grid vertices, so each strand is a clean line of raised vertices. Where two primary
strands cross the bumps add up into a knot (the centre of a large stauract); with m = 4 a
lower secondary strand runs halfway across each cell. Vertex colours repeat the pattern.

build() returns (MeshBuilder, surface) so the species script can add its own spicules (a root
tuft, protruding needles) before calling finish(). surface(theta, s, off) gives the outer wall
point and normal at angle theta and profile fraction s. Fixed style: pivot at z = 0.
"""

import math
import random

import bmesh
from mathutils import Vector, noise

import nh_model as nh
import nh_protospongia as npr   # Profile
import nh_vauxia as nv          # mud_patch


def build(profile, cells_around, m=4, ribs=(0.03, 0.014), knot=0.5, wall=0.03, colors=None,
          wobble=0.03, seed=1, rmin=0.08, lip_rings=3, inner_rings=5, inner_bottom=0.45,
          twist=0.0):
    """profile: (r, z) control points from the base to the rim. cells_around: primary diagonal
    cells around the body. m: samples per cell (4 = with secondary strands). ribs: (primary,
    secondary) heights. rmin: radius below which cells stop shrinking toward the base.
    colors: RIB, KNOT, WINDOW, RIM, INSIDE, BASE. twist: extra lattice shear (cells) per cell up."""
    rng = random.Random(seed)
    c = colors
    prof = npr.Profile(profile)
    N = cells_around
    segs = N * m
    warp = Vector((rng.uniform(0, 50), rng.uniform(0, 50), rng.uniform(0, 50)))

    # lattice v coordinate (in cells) as a function of the profile fraction
    K = 400
    vs = [0.0]
    for i in range(1, K + 1):
        (r0, _), _n = prof.at((i - 1) / K)
        (r1, _), _n = prof.at(i / K)
        r = max(rmin, 0.5 * (r0 + r1))
        vs.append(vs[-1] + prof.length / K / (math.tau * r / N))
    V = vs[-1]
    R = max(2, round(V * m))           # rows of samples
    scale = R / (V * m)                # stretch v slightly so the rows land on 1/m steps

    def s_of_v(v):
        target = v / scale
        lo, hi = 0, K
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if vs[mid] < target:
                lo = mid
            else:
                hi = mid
        seg = vs[hi] - vs[lo] or 1.0
        return (lo + (target - vs[lo]) / seg) / K

    def bulge(theta, z):
        p = Vector((math.cos(theta) * 1.3, math.sin(theta) * 1.3, z * 2.2)) + warp
        return 1.0 + wobble * noise.noise(p)

    def strand(x, width):
        d = abs(x - round(x))
        return nh.smoothstep(width, 0.0, d)

    w1 = 1.0 / m * 0.999

    def lattice(u, v):
        a, b = u + v + twist * v, u - v + twist * v
        pa, pb = strand(a, w1), strand(b, w1)
        if m >= 4:
            sa, sb = strand(a - 0.5, w1), strand(b - 0.5, w1)
        else:
            sa = sb = 0.0
        prim = max(pa, pb)
        sec = max(sa, sb) * (1 - prim)
        h = ribs[0] * prim + ribs[0] * knot * pa * pb + ribs[1] * sec
        return h, prim, pa * pb, sec

    def surface(theta, s, off=0.0):
        (r, z), (nr, nz) = prof.at(s)
        rad = r * bulge(theta, z) + nr * off
        p = Vector((math.cos(theta) * rad, math.sin(theta) * rad, z + nz * off))
        return p, Vector((math.cos(theta) * nr, math.sin(theta) * nr, nz))

    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    vcol = {}
    thetas = [k / segs * math.tau for k in range(segs)]

    def outer_colour(u, v, z, s):
        _h, prim, kn, sec = lattice(u, v)
        w = nh.lerp(c["WINDOW"], c["RIB"], 0.55 * sec)
        w = nh.lerp(w, c["RIB"], prim)
        w = nh.lerp(w, c["KNOT"], kn)
        w = nh.lerp(c["BASE"], w, nh.smoothstep(0.0, 0.12, s))
        k = 0.93 + 0.1 * noise.noise(Vector((u * 0.7, v * 0.7, z * 3.0)) + warp)
        return tuple(min(1.0, x * k) for x in w)

    rmax = max(p[0] for p in profile)
    rings = []
    height = {}
    for j in range(R + 1):
        v = j / m
        s = s_of_v(v)
        (r, _z), _n = prof.at(s)
        size = max(0.3, min(1.0, r / (0.7 * rmax)))   # smaller cells -> lower ribs
        rr = []
        for k, th in enumerate(thetas):
            u = k / m
            h, *_ = lattice(u, v)
            if j == R:
                h *= 0.35
            p, n = surface(th, s, h * size)
            vert = bm.verts.new(p)
            vcol[vert] = outer_colour(u, v, p.z, s)
            height[vert] = h
            rr.append(vert)
        rings.append(rr)
    n_outer = len(rings)

    def ring(pos_of, colour):
        out = []
        for th in thetas:
            vert = bm.verts.new(pos_of(th))
            vcol[vert] = colour
            out.append(vert)
        return out

    (r1, z1), (nr1, nz1) = prof.at(1.0)
    tr, tz = -nz1, nr1
    for i in range(1, lip_rings + 1):
        a = i / (lip_rings + 1) * math.pi
        off_n = wall * 0.5 * (math.cos(a) - 1.0)
        off_t = wall * 0.5 * math.sin(a)

        def pos(th, off_n=off_n, off_t=off_t):
            rad = r1 * bulge(th, z1) + nr1 * off_n + tr * off_t
            return (math.cos(th) * rad, math.sin(th) * rad, z1 + nz1 * off_n + tz * off_t)
        rings.append(ring(pos, c["RIM"]))
    for i in range(inner_rings + 1):
        s = 1.0 - (1.0 - inner_bottom) * (i / inner_rings) ** 1.4
        depth = 1.0 - s

        def pos(th, s=s):
            p, n = surface(th, s, -wall)
            rr = math.hypot(p.x, p.y)
            if rr < 0.01:
                p.x, p.y = math.cos(th) * 0.01, math.sin(th) * 0.01
            return p
        rings.append(ring(pos, nh.lerp(c["RIM"], c["INSIDE"], nh.smoothstep(0.0, 0.15, depth))))

    for i, (a, b) in enumerate(zip(rings, rings[1:])):
        for k in range(segs):
            j = (k + 1) % segs
            if i + 1 < n_outer:
                # split each lattice quad along whichever diagonal carries a strand, so both
                # diagonal families stay crisp ridges
                if height[a[k]] + height[b[j]] >= height[a[j]] + height[b[k]]:
                    bm.faces.new([a[k], a[j], b[j]])
                    bm.faces.new([a[k], b[j], b[k]])
                else:
                    bm.faces.new([a[k], a[j], b[k]])
                    bm.faces.new([a[j], b[j], b[k]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    (rb, zb), _ = prof.at(0.0)
    cb = bm.verts.new((0, 0, zb - 0.005))
    vcol[cb] = c["BASE"]
    for k in range(segs):
        bm.faces.new([rings[0][(k + 1) % segs], rings[0][k], cb])
    last = rings[-1]
    ci = bm.verts.new((0, 0, sum(v.co.z for v in last) / segs - 0.01))
    vcol[ci] = c["INSIDE"]
    for k in range(segs):
        bm.faces.new([last[k], last[(k + 1) % segs], ci])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
        for loop in f.loops:
            cc = vcol[loop.vert]
            loop[col] = (cc[0], cc[1], cc[2], 1.0)

    mb = nh.MeshBuilder()
    mb.add(bm)
    return mb, surface, rng


def spicule(mb, pts, r0, base_col, tip_col, sides=4):
    """A thin tapering spicule along pts (list of Vectors), coloured base -> tip."""
    radii = [r0 * (1.0 - 0.8 * i / (len(pts) - 1)) for i in range(len(pts))]
    radii[-1] = 0.0
    total = sum((b - a).length for a, b in zip(pts, pts[1:])) or 1.0
    p0 = pts[0]
    mb.add(nh.tube(pts, radii, sides=sides, cap_start=True),
           lambda co, n: nh.lerp(base_col, tip_col, min(1.0, (co - p0).length / total)))


def finish(mb, name, rng, mud=(0.3, 0.55), mud_count=7, mud_size=(0.035, 0.07)):
    if mud:
        nv.mud_patch(mb, rng, *mud, count=mud_count, size=mud_size)
    obj = mb.to_object(name, roughness=0.7)
    nh.ground_to_zero(obj)
    return obj
