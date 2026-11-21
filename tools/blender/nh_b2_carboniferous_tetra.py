"""
Shared helpers for the batch-2 Carboniferous tetrapods built on nh_car_tetrapod
(dendrerpeton_acadianum.py, eucritta_melanolimnetes.py, greererpeton_burkemorani.py,
keraterpeton_galvani.py, ianthasaurus_hardestiorum.py, spinoaequalis_schultzei.py,
cochleosaurus_bohemicus.py).

nh_car_tetrapod.build() fuses only its own spine loft and legs; this module re-runs the
same pipeline but lets a species
  * fuse extra parts into the body before remeshing (tabular horns, cheek flanges),
  * wrap the procedural paint (tail bands, otic-notch shading, sail colour),
  * add crisp parts (a sail of spines with crossbars and webbing) through Spec.extra.

Usage (from a species script):
  import nh_b2_carboniferous_tetra as ct
  ct.run(SPEC, fused=[ct.tabular_horns(...)], paint=[ct.otic_notch(...)])
"""

import math
import sys
from pathlib import Path

import bmesh
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_tetrapod as tp  # noqa: E402


# ---------------------------------------------------------------- build pipeline
def build(sp, fused=(), paint=()):
    spine = tp.Spine(sp)
    body = nh.MeshBuilder()
    for p in tp.parts(sp, spine):
        body.add(p, sp.flank)
    for fn in fused:
        for p in fn(sp, spine):
            body.add(p, sp.flank)
    f = body.fuse(voxel=sp.voxel, smooth=4, smooth_factor=0.5, max_tris=sp.max_tris)
    tp.drop_islands(f)
    f.normal_update()
    for v in f.verts:
        v.co += v.normal * sp.voxel * 0.12 * noise.noise(v.co * 90.0)
    f.normal_update()
    tree = BVHTree.FromBMesh(f)
    extra = tp.details(sp, spine, tree)
    pfn = tp.make_paint(sp, spine)
    for wrap in paint:
        pfn = wrap(pfn, sp, spine)
    mb = nh.MeshBuilder()
    mb.add(f, color=pfn)
    for bm, col in extra:
        mb.add(bm, col, smooth=False)
    obj = mb.to_object(sp.name, roughness=0.5)
    if sp.swim:
        tp.centre(obj)
    else:
        nh.ground_to_zero(obj)
    return obj


def run(sp, fused=(), paint=(), ground=(0.30, 0.27, 0.18), background=(0.20, 0.28, 0.18)):
    views = ((35, 25), (-90, 8), (160, 60), (0, 10))
    if sp.swim:
        nh.run(lambda: build(sp, fused, paint), sp.name, background=(0.06, 0.18, 0.22), views=views)
    else:
        nh.run(lambda: build(sp, fused, paint), sp.name, ground=ground, background=background, views=views)


def _frame(spine, s):
    """Point, tailward unit vector and side unit vector (plan view) of the spine at arc length s."""
    i = max(1, min(spine.n - 1, int(round(s / spine.s_end * spine.n))))
    fwd = spine.pts[i + 1] - spine.pts[i - 1]
    fwd.z = 0
    fwd.normalize()
    return spine.pts[i], fwd, Vector((-fwd.y, fwd.x, 0.0))


# ---------------------------------------------------------------- fused parts
def tabular_horns(length, radius, at=0.97, out=0.85, up=0.25, spread=0.35, droop=0.0):
    """A pair of short horns sweeping back from the rear corners of the skull table.
    length/radius in model units; at: position along the head (fraction of head_len);
    out: lateral root position as a fraction of the local half-width; spread: sideways
    flare of the tip relative to its length."""
    def fn(sp, spine):
        s = sp.head_len * at
        p, fwd, side = _frame(spine, s)
        rx, rz = spine.rx(s), spine.rz(s)
        out_parts = []
        for sx in (-1, 1):
            root = p + side * sx * rx * out + Vector((0, 0, rz * up))
            back = fwd  # _frame's fwd runs snout -> tail
            tip = root + (back + side * sx * spread).normalized() * length + Vector((0, 0, -droop * length))
            mid = root.lerp(tip, 0.5) + Vector((0, 0, radius * 0.2))
            out_parts.append(nh.tube([root - back * radius, mid, tip], [radius * 1.3, radius * 0.85, radius * 0.15],
                                     sides=8, scale_xy=(1.0, 0.6)))
        return out_parts
    return fn


def skull_table(width, length, at=0.6, up=0.55, flat=0.35):
    """Widens and flattens the rear of the skull (a broad flat skull table)."""
    def fn(sp, spine):
        s = sp.head_len * at
        p, _fwd, _side = _frame(spine, s)
        rz = spine.rz(s)
        c = p + Vector((0, 0, rz * (up - 0.5)))
        return [nh.ellipsoid(tuple(c), (width, length, rz * flat + 0.004), subdivisions=3)]
    return fn


def fin_height(height, u, start=0.05, end=1.0, peak=0.4):
    """Height of tail_fin's upper edge above the tail axis at tail fraction u."""
    if u < peak:
        k = nh.smoothstep(start - 0.02, peak, u)
    else:
        k = math.sqrt(max(0.0, 1.0 - ((u - peak) / max(end - peak, 1e-3)) ** 2))
    return height * (0.25 + 0.75 * k)


def tail_fin(height, below=0.6, start=0.05, end=1.0, thick=0.35, n=44, peak=0.4):
    """A laterally flattened swimming fin along the tail: overlapping thin ellipsoids centred on
    the tail axis, reaching `height` above it (below x height under it), profile rising from
    `start` to a broad maximum at `peak` and rounding off at `end` (fractions of tail length).
    thick: half-thickness as a fraction of the local tail half-width."""
    def fn(sp, spine):
        out = []
        seg = sp.tail_len * (end - start) / (n - 1) * 2.4
        for i in range(n):
            u = start + (end - start) * i / (n - 1)
            s = min(spine.s_trunk + sp.tail_len * u, spine.s_end * 0.995)
            p = spine.at(s)
            rx = max(spine.rx(s), 0.004)
            h = fin_height(height, u, start, end, peak)
            up, dn = h * 0.5, h * below * 0.5
            c = p + Vector((0, 0, up - dn))
            out.append(nh.ellipsoid(tuple(c), (rx * thick, seg, up + dn + 0.002), subdivisions=2))
        return out
    return fn


# ---------------------------------------------------------------- paint wrappers
def otic_notch(col=(0.10, 0.08, 0.05), at=0.93, width=0.22, out=0.7):
    """Dark crescent at each rear corner of the skull: reads as the otic notch / eardrum."""
    def wrap(base, sp, spine):
        def paint(co, n):
            c = base(co, n)
            s, p, _d = spine.nearest(co)
            u = s / sp.head_len
            if abs(u - at) < width * 0.5:
                rx = max(spine.rx(s), 1e-3)
                side = abs(co.x - p.x) / rx
                upz = (co.z - p.z) / max(spine.rz(s), 1e-3)
                k = math.exp(-((side - out) / 0.18) ** 2) * math.exp(-((upz - 0.35) / 0.35) ** 2)
                k *= 1.0 - abs(u - at) / (width * 0.5)
                c = nh.lerp(c, col, min(1.0, k * 1.6))
            return c
        return paint
    return wrap


def tail_bands(col, period=0.06, duty=0.4, start=0.0):
    """Dark rings round the tail (start: fraction of tail length where the bands begin)."""
    def wrap(base, sp, spine):
        def paint(co, n):
            c = base(co, n)
            s, p, d = spine.nearest(co)
            if s > spine.s_trunk + sp.tail_len * start:
                ph = ((s - spine.s_trunk) / period) % 1.0
                if ph < duty:
                    c = nh.lerp(c, col, 0.85)
            return c
        return paint
    return wrap


def far_colour(col, dist=1.6, s_range=(0.0, 0.25)):
    """Colour vertices far from the spine (fused horns) within s_range (fraction of total length)."""
    def wrap(base, sp, spine):
        def paint(co, n):
            c = base(co, n)
            s, p, d = spine.nearest(co)
            u = s / spine.s_end
            if s_range[0] <= u <= s_range[1]:
                r = max(spine.rx(s), spine.rz(s), 1e-3)
                if d > r * dist:
                    c = nh.lerp(c, col, nh.smoothstep(r * dist, r * (dist + 0.4), d))
            return c
        return paint
    return wrap


# ---------------------------------------------------------------- crisp extras
def dorsal_sail(s0, s1, height, n=20, spine_r=0.0045, spine_col=(0.18, 0.11, 0.07),
                sail_col=(0.72, 0.36, 0.16), edge_col=(0.50, 0.22, 0.10), crossbars=3,
                bar_col=(0.22, 0.14, 0.09), web_t=0.003):
    """Edaphosaur-style sail: n tall neural spines along the back between arc lengths s0..s1
    (fractions of the trunk, 0 = shoulders), rounded profile peaking mid-trunk, short
    crossbar tubercles sticking out sideways, and a thin translucent-looking web between them."""
    def fn(sp, spine):
        out = []
        a = spine.s_neck + sp.trunk_len * s0
        b = spine.s_neck + sp.trunk_len * s1
        tops = []
        for i in range(n):
            t = i / (n - 1)
            s = a + (b - a) * t
            p, fwd, side = _frame(spine, s)
            base = p + Vector((0, 0, spine.rz(s) * 0.6))
            h = height * (math.sin(math.pi * (0.08 + 0.84 * t)) ** 0.8) * (1.0 - 0.15 * t)
            lean = fwd * h * 0.12  # spines lean slightly back
            top = base + Vector((0, 0, h)) + lean
            tops.append((base, top, h, side))
            out.append((nh.tube([base, base.lerp(top, 0.5), top], [spine_r * 1.3, spine_r, spine_r * 0.6],
                                sides=5), spine_col))
            for k in range(crossbars):
                q = base.lerp(top, 0.3 + 0.55 * k / max(crossbars - 1, 1) + 0.04 * (i % 2))
                L = spine_r * 2.6 * (1.0 - 0.3 * k / max(crossbars, 1))
                out.append((nh.tube([q - side * L, q + side * L], [spine_r * 0.75, spine_r * 0.75], sides=4),
                            bar_col))
        # web: a thin double-sided strip of quads between consecutive spines
        bm = bmesh.new()
        prev = None
        for base, top, h, side in tops:
            col = []
            for j in range(5):
                q = base.lerp(top, j / 4 * 0.97)
                col.append((bm.verts.new(q + side * web_t), bm.verts.new(q - side * web_t)))
            if prev:
                for j in range(4):
                    bm.faces.new([prev[j][0], col[j][0], col[j + 1][0], prev[j + 1][0]])
                    bm.faces.new([prev[j][1], prev[j + 1][1], col[j + 1][1], col[j][1]])
            prev = col
        zs = [t[0].z for t in tops]
        z0 = min(zs)
        hmax = max(t[2] for t in tops)

        def web_col(co, nrm):
            u = (co.z - z0) / max(hmax, 1e-6)
            c = nh.lerp(sail_col, edge_col, nh.smoothstep(0.55, 1.0, u))
            k = 0.9 + 0.2 * noise.noise(co * 40.0)
            return (c[0] * k, c[1] * k, c[2] * k)
        out.append((bm, web_col))
        return out
    return fn


def otic_disc(at=0.9, size=0.13, col=(0.07, 0.05, 0.03), rim=(0.20, 0.16, 0.09), out=0.9, up=0.3):
    """A dark recessed oval (with a paler rim) at each rear corner of the skull, set in the
    skin as a crisp part: reads as the otic notch / eardrum of temnospondyls."""
    def fn(sp, spine):
        res = []
        s = sp.head_len * at
        p, fwd, side = _frame(spine, s)
        rx, rz = spine.rx(s), spine.rz(s)
        L = sp.head_len * size
        for sx in (-1, 1):
            c = p + side * sx * rx * out + Vector((0, 0, rz * up))
            res.append((nh.ellipsoid(tuple(c), (rx * 0.16, L * 1.25, rz * 0.62), subdivisions=2), rim))
            res.append((nh.ellipsoid(tuple(c + side * sx * rx * 0.05), (rx * 0.13, L, rz * 0.48), subdivisions=2), col))
        return res
    return fn
