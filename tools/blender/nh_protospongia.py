"""
Shared body for the Protospongia models (protospongia_fenestrata.py, protospongia_hicksi.py,
protospongia_novaki.py, protospongia_rhenana.py): early reticulosan glass sponges, thin-walled
sacs whose single-layer skeleton is a square lattice of cross-shaped spicules (stauracts).

The sponge is a surface of revolution around Z: a closed profile runs from a small attachment
base up the outer wall to a rounded lip around the osculum (the top opening), then back down
the inner wall. Instead of thousands of tiny struts the lattice is built INTO the outer wall:
the grid of vertices is laid out along the lattice (Charnia-style), with a few samples per
primary mesh cell - a crest on the primary strand, its two edges, and (optionally) a lower
crest for the secondary strand halfway across - so the wall is displaced into raised
vertical and horizontal ribs with little windows between them. Where two primary strands
cross, the bumps add up into a knot (the centre of a large cross-shaped spicule). Vertex
colours repeat the pattern: pale silica ribs and knots, darker windows of soft tissue, a
darker inside seen through the osculum.

Each species script just sets the profile, mesh density, rib sizes and colours and calls
build_sponge(). Fixed style: pivot at the base (z = 0).
"""

import math
import random

import bmesh
from mathutils import Vector, noise

import nh_model as nh
import nh_coral as nc

# fractional positions across one primary lattice cell: primary crest, its edge, secondary
# strand (edge, crest, edge), primary edge again (the next cell starts on the next crest)
CELL_SAMPLES = (0.0, 0.1, 0.4, 0.5, 0.6, 0.9)
CELL_SAMPLES_PLAIN = (0.0, 0.12, 0.5, 0.88)   # no secondary strand


def _catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
                 for a, b, c, d in zip(p0, p1, p2, p3))


class Profile:
    """Smooth (r, z) curve through control points from the base to the rim, sampled by arc length."""

    def __init__(self, ctrl, samples=600):
        pts = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
        dense = []
        segs = len(ctrl) - 1
        for i in range(samples + 1):
            u = i / samples * segs
            k = min(int(u), segs - 1)
            dense.append(_catmull(pts[k], pts[k + 1], pts[k + 2], pts[k + 3], u - k))
        self.pts = dense
        self.cum = [0.0]
        for a, b in zip(dense, dense[1:]):
            self.cum.append(self.cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.length = self.cum[-1]

    def at(self, s):
        """Point (r, z) and outward unit normal (nr, nz) at arc-length fraction s (0 = base, 1 = rim)."""
        target = max(0.0, min(1.0, s)) * self.length
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] < target:
                lo = mid
            else:
                hi = mid
        seg = self.cum[hi] - self.cum[lo] or 1.0
        t = (target - self.cum[lo]) / seg
        a, b = self.pts[lo], self.pts[hi]
        r, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        i0, i1 = max(0, lo - 2), min(len(self.pts) - 1, hi + 2)
        dr, dz = self.pts[i1][0] - self.pts[i0][0], self.pts[i1][1] - self.pts[i0][1]
        n = math.hypot(dr, dz) or 1.0
        return (r, z), (dz / n, -dr / n)


def _rib(f, width):
    """1 on a strand centred on integer f, falling to 0 at +-width (in cell fractions)."""
    d = abs(f - round(f))
    return nh.smoothstep(width, 0.0, d)


def build_sponge(name, profile, cells_around, ribs=(0.035, 0.016), rib_width=(0.1, 0.1),
                 secondary=True, wall=0.035, lip_rings=3, inner_rings=4,
                 colors=None, wobble=0.03, seed=1, rubble=(5, (0.04, 0.08)), knot=0.3,
                 row_scale=1.0, flare=None, cell_samples=None, inner_bottom=0.45):
    """Builds the sponge object.

      profile:       (r, z) control points from the base (small r at z ~ 0) to the rim
      cells_around:  number of primary vertical strands around the body
      ribs:          (primary, secondary) rib heights
      rib_width:     (primary, secondary) half-widths of the strands in cell fractions
                     (only used for colouring; the geometry follows CELL_SAMPLES)
      secondary:     build a secondary strand halfway across each primary cell
      wall:          wall thickness (osculum rim)
      colors:        dict with RIB, KNOT, WINDOW, INSIDE, RIM, BASE (rgb)
      wobble:        irregular bulging of the body (fraction of the radius)
      knot:          extra height of the knots where two primary strands cross (x primary rib)
      row_scale:     primary cell height relative to its width at the widest point
      flare:         None or (start fraction, extra radius) to flare the rim outward
      cell_samples:  override the sample positions across a cell (e.g. extra window vertices
                     for a coarse mesh so the body stays round)
      inner_bottom:  arc-length fraction where the visible inner wall ends in a floor
    """
    rng = random.Random(seed)
    c = colors
    prof = Profile(profile)
    rmax = max(p[0] for p in profile)
    samples = cell_samples or (CELL_SAMPLES if secondary else CELL_SAMPLES_PLAIN)
    segs = cells_around * len(samples)
    thetas = [(k + f) / cells_around * math.tau for k in range(cells_around) for f in samples]
    cell_len = math.tau * rmax / cells_around * row_scale
    rows = max(2, round(prof.length / cell_len))
    vfrac = [(rw + f) / rows for rw in range(rows) for f in samples] + [1.0]
    warp = Vector((rng.uniform(0, 50), rng.uniform(0, 50), rng.uniform(0, 50)))

    def bulge(theta, z):
        p = Vector((math.cos(theta) * 1.3, math.sin(theta) * 1.3, z * 2.2)) + warp
        return 1.0 + wobble * noise.noise(p)

    def flare_r(s):
        if not flare:
            return 0.0
        return flare[1] * nh.smoothstep(flare[0], 1.0, s) ** 1.5

    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    vcol = {}

    def ring(r_of, z_of, colour_of, n_of=None):
        out = []
        for k, th in enumerate(thetas):
            r, z = r_of(k, th), z_of(k, th)
            v = bm.verts.new((math.cos(th) * r, math.sin(th) * r, z))
            vcol[v] = colour_of(k, th, z)
            out.append(v)
        return out

    # ---- outer wall with the lattice
    def lattice(u, v):
        """(height, rib colour weights) for lattice coordinates u (around) and v (up), in cells."""
        pu, pv = _rib(u, rib_width[0]), _rib(v, rib_width[0])
        su = _rib(u - 0.5, rib_width[1]) if secondary else 0.0
        sv = _rib(v - 0.5, rib_width[1]) if secondary else 0.0
        h = ribs[0] * max(pu, pv) + ribs[0] * knot * pu * pv + ribs[1] * max(su, sv) * (1 - max(pu, pv))
        return h, max(pu, pv), pu * pv, max(su, sv)

    def outer_colour(u, v, z, s):
        _h, prim, kn, sec = lattice(u, v)
        w = nh.lerp(c["WINDOW"], c["RIB"], 0.6 * sec)
        w = nh.lerp(w, c["RIB"], prim)
        w = nh.lerp(w, c["KNOT"], kn)
        w = nh.lerp(c["BASE"], w, nh.smoothstep(0.0, 0.12, s))
        k = 0.93 + 0.1 * noise.noise(Vector((u * 0.7, v * 0.7, z * 3.0)) + warp)
        return tuple(min(1.0, x * k) for x in w)

    rings = []
    for vi, s in enumerate(vfrac):
        (r, z), (nr, nz) = prof.at(s)
        v_cells = s * rows
        rr = []
        for k, th in enumerate(thetas):
            u_cells = th / math.tau * cells_around
            h, *_ = lattice(u_cells, v_cells)
            if vi == len(vfrac) - 1:
                h *= 0.35  # the rim strand blends into the lip
            b = bulge(th, z)
            rad = r * b + flare_r(s) + nr * h
            zz = z + nz * h
            vert = bm.verts.new((math.cos(th) * rad, math.sin(th) * rad, zz))
            vcol[vert] = outer_colour(u_cells, v_cells, zz, s)
            rr.append(vert)
        rings.append(rr)

    # ---- lip: rounded rim from the outer to the inner wall
    (r1, z1), (nr1, nz1) = prof.at(1.0)
    tr, tz = -nz1, nr1   # tangent pointing up along the profile
    for i in range(1, lip_rings + 1):
        a = i / (lip_rings + 1) * math.pi
        off_n = wall * 0.5 * (math.cos(a) - 1.0)        # from 0 (outer) to -wall (inner)
        off_t = wall * 0.5 * math.sin(a)
        rings.append(ring(
            lambda k, th: r1 * bulge(th, z1) + flare_r(1.0) + nr1 * off_n + tr * off_t,
            lambda k, th: z1 + nz1 * off_n + tz * off_t,
            lambda k, th, z: c["RIM"]))

    # ---- inner wall: back down into the cavity (rings packed toward the rim, where it shows
    # and where a narrowing neck needs them so the inner wall can't cut through the outer one)
    for i in range(inner_rings + 1):
        s = 1.0 - (1.0 - inner_bottom) * (i / inner_rings) ** 1.4
        (r, z), (nr, nz) = prof.at(s)
        depth = 1.0 - s
        rings.append(ring(
            lambda k, th, r=r, z=z, nr=nr, s=s: max(0.01, r * bulge(th, z) + flare_r(s) - nr * wall),
            lambda k, th, z=z, nz=nz: z - nz * wall,
            lambda k, th, zz, depth=depth: nh.lerp(c["RIM"], c["INSIDE"], nh.smoothstep(0.0, 0.18, depth))))

    for a, b in zip(rings, rings[1:]):
        for k in range(segs):
            j = (k + 1) % segs
            bm.faces.new([a[k], a[j], b[j], b[k]])
    # close the base (outer) and the bottom of the inner cavity with fans
    (rb, zb), _ = prof.at(0.0)
    cb = bm.verts.new((0, 0, zb - 0.005))
    vcol[cb] = c["BASE"]
    for k in range(segs):
        bm.faces.new([rings[0][(k + 1) % segs], rings[0][k], cb])
    last = rings[-1]
    zc = sum(v.co.z for v in last) / segs - 0.01
    ci = bm.verts.new((0, 0, zc))
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
    if rubble:
        count, size = rubble
        nc.rubble(mb, rng, rmax * 0.95, rmax * 1.5, count=count, size=size)
    obj = mb.to_object(name, roughness=0.7)
    nh.ground_to_zero(obj)
    return obj
