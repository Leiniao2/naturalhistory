"""
Ordovician echinoderms for the Ordovician batch: a rhombiferan cystoid
(echinosphaerites_aurantium.py), a stalked disparid crinoid (iocrinus_subcrassus.py) and
an early sea star (hudsonaster_incomptus.py). All Fixed style: pivot on the sea floor
(z = 0), facing -Y.

  * cystoid(): a near-spherical theca of many polygonal plates (Voronoi sutures from
    seed points) with pore-rhomb streaks, a small mouth on top with a few short
    brachioles, the anal pyramid on one side and a short stem stub, resting on the mud.
  * crinoid(): a holdfast, a long column of ridged columnals, a small conical cup and
    five arms that fork (isotomously) as they rise, spreading into a feeding fan.
  * seastar(): a flat five-armed star of rows of block-like plates around a low disc,
    with a central madreporite, arms slightly curled at the tips.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh


def _finish(mb, name, roughness=0.6):
    obj = mb.to_object(name, roughness=roughness)
    nh.ground_to_zero(obj)
    vs = obj.data.vertices
    xs, ys = [v.co.x for v in vs], [v.co.y for v in vs]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    for v in vs:
        v.co.x -= cx
        v.co.y -= cy
    return obj


def mud_patch(mb, radius, colors, seed=3):
    """Small, low, mottled disc of sea-floor sediment (top at about z = 0.02)."""
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=radius, segments=28)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    sv = Vector((seed, seed * 0.7, 0))
    for v in bm.verts:
        r = v.co.length / radius
        v.co.z = 0.02 * (1 - r ** 4) + 0.01 * noise.noise(v.co * 5 + sv) * (1 - r)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    mb.add(bm, lambda co, n: nh.lerp(colors[0], colors[1], 0.5 + 0.5 * noise.noise(co * 6 + sv)))


# ---------------------------------------------------------------- cystoid

def cystoid(name, radius=0.5, plate=(0.84, 0.60, 0.34), plate_dark=(0.62, 0.40, 0.20),
            suture=(0.36, 0.22, 0.12), rhomb=(0.30, 0.18, 0.10), mud=((0.36, 0.34, 0.30), (0.50, 0.47, 0.41))):
    mb = nh.MeshBuilder()
    mud_patch(mb, radius * 1.5, mud)
    rnd = random.Random(7)
    seeds = []
    sb = bmesh.new()
    bmesh.ops.create_icosphere(sb, subdivisions=2, radius=1.0)
    for v in sb.verts:
        p = v.co.normalized() + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.06
        seeds.append((p.normalized(), rnd.random()))
    sb.free()
    c0 = Vector((0, 0, radius * 0.97))

    def col(co, n):
        d = (co - c0).normalized()
        ds = sorted(((d - s).length, k) for s, k in seeds)[:2]
        (d0, k0), (d1, _k1) = ds
        c = nh.lerp(plate, plate_dark, 0.6 * k0)
        # pore rhombs: short dark streaks crossing some sutures
        if k0 > 0.65 and d1 - d0 < 0.05:
            c = rhomb
        c = nh.lerp(c, suture, 1.0 - nh.smoothstep(0.008, 0.03, d1 - d0))
        return c

    th = nh.ellipsoid(tuple(c0), (radius, radius, radius * 0.96), subdivisions=5)
    mb.add(th, col)
    top = c0 + Vector((0, 0, radius * 0.96))
    # mouth with a few short brachioles
    mb.add(nh.ellipsoid(tuple(top), (0.05, 0.05, 0.02), subdivisions=2), suture)
    for k in range(4):
        a = k / 4 * math.tau + 0.4
        d = Vector((math.cos(a), math.sin(a), 0.9)).normalized()
        b = top + Vector((math.cos(a), math.sin(a), 0)) * 0.03
        mb.add(nh.tube([b, b + d * 0.1, b + d * 0.2 + Vector((math.cos(a), math.sin(a), 0)) * 0.05],
                       [0.018, 0.014, 0.0], sides=6), plate_dark)
    # anal pyramid on the side
    side = c0 + Vector((0.0, -1.0, 0.45)).normalized() * radius
    mb.add(nh.tube([side - (side - c0).normalized() * 0.01, side + (side - c0).normalized() * 0.05],
                   [0.06, 0.0], sides=5), plate_dark, smooth=False)
    # stem stub at the base
    mb.add(nh.tube([c0 - Vector((0, 0, radius * 0.9)), c0 + Vector((0.25, 0.1, -radius * 1.0))],
                   [0.05, 0.04], sides=6), plate_dark)
    return _finish(mb, name)


# ---------------------------------------------------------------- crinoid

def _columnal_color(base, dark):
    def fn(co, n):
        k = 0.5 + 0.5 * math.sin(co.z * 160.0)
        return nh.lerp(base, dark, 0.55 * nh.smoothstep(0.75, 1.0, k))
    return fn


def crinoid(name, stem_h=1.2, stem_r=0.035, cup_h=0.12, arm_len=0.55, forks=2, spread=0.32,
            body=(0.72, 0.62, 0.66), dark=(0.46, 0.36, 0.42), arm=(0.80, 0.68, 0.70),
            mud=((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)), sway=0.08):
    mb = nh.MeshBuilder()
    mud_patch(mb, 0.35, mud)
    # holdfast: a few root-like radix branches
    for k in range(5):
        a = k / 5 * math.tau + 0.3
        mb.add(nh.tube([(0, 0, 0.03), (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.02),
                        (math.cos(a + 0.3) * 0.22, math.sin(a + 0.3) * 0.22, 0.01)],
                       [0.03, 0.018, 0.0], sides=5), dark)
    # stem with a gentle sway; pentagonal (5 sides)
    n = 14
    pts = [Vector((sway * math.sin(t * 2.2) * t, 0.0, 0.02 + stem_h * t)) for t in [i / n for i in range(n + 1)]]
    mb.add(nh.tube(pts, [stem_r * (1.1 - 0.2 * i / n) for i in range(n + 1)], sides=5),
           _columnal_color(body, dark), smooth=False)
    top = pts[-1]
    # cup (calyx): small cone widening upward
    mb.add(nh.tube([top, top + Vector((0, 0, cup_h * 0.6)), top + Vector((0, 0, cup_h))],
                   [stem_r * 1.2, cup_h * 0.55, cup_h * 0.75], sides=10), body)
    mb.add(nh.ellipsoid(tuple(top + Vector((0, 0, cup_h))), (cup_h * 0.72, cup_h * 0.72, cup_h * 0.25),
                        subdivisions=2), dark)
    # arms: five, each forking `forks` times
    def branch(p, d, L, r, level):
        steps = 4
        pts = [p]
        q = Vector(p)
        dd = Vector(d)
        for i in range(steps):
            dd = (dd + Vector((0, 0, 0.12))).normalized()
            q = q + dd * (L / steps)
            pts.append(q.copy())
        mb.add(nh.tube(pts, [r * (1 - 0.25 * i / steps) for i in range(steps)] + [r * 0.7 if level < forks else 0.0],
                       sides=5), arm)
        # pinnules: small side spikes give the arms their feathery look
        for i in range(1, steps + 1):
            side = dd.cross(Vector((0, 0, 1)))
            if side.length < 1e-4:
                side = Vector((1, 0, 0))
            side.normalize()
            for sg in (-1, 1):
                b = pts[i - 1].lerp(pts[i], 0.5)
                mb.add(nh.tube([b, b + (side * sg + dd * 0.6).normalized() * L * 0.12], [r * 0.4, 0.0], sides=3),
                       arm, smooth=False)
        if level < forks:
            axis = dd
            perp = axis.cross(Vector((0, 0, 1)))
            if perp.length < 1e-4:
                perp = Vector((1, 0, 0))
            perp.normalize()
            for sg in (-1, 1):
                nd = (axis + perp * sg * 0.45).normalized()
                branch(q, nd, L * 0.8, r * 0.75, level + 1)

    base = top + Vector((0, 0, cup_h))
    for k in range(5):
        a = k / 5 * math.tau + math.pi / 2
        d = Vector((math.cos(a) * spread, math.sin(a) * spread, 1.0)).normalized()
        branch(base + Vector((math.cos(a), math.sin(a), 0)) * cup_h * 0.6, d, arm_len * 0.45, 0.03, 0)
    return _finish(mb, name)


# ---------------------------------------------------------------- sea star

def seastar(name, R=0.75, r_disc=0.22, arm_w=0.16, height=0.08,
            plate=(0.82, 0.62, 0.44), plate_dark=(0.58, 0.38, 0.24), marginal=(0.90, 0.76, 0.58),
            mud=((0.36, 0.34, 0.30), (0.50, 0.47, 0.41))):
    mb = nh.MeshBuilder()
    mud_patch(mb, R * 1.15, mud)
    z0 = 0.02
    # disc
    mb.add(nh.ellipsoid((0, 0, z0 + height * 0.3), (r_disc, r_disc, height * 0.8), subdivisions=3),
           lambda co, n: nh.lerp(plate, plate_dark, 0.4 + 0.3 * noise.noise(co * 25)))
    mb.add(nh.ellipsoid((0.05, 0.05, z0 + height * 1.05), (0.03, 0.03, 0.012), subdivisions=2), marginal)
    for k in range(5):
        a = k / 5 * math.tau - math.pi / 2
        d = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-d.y, d.x, 0))
        # arm body: a tapering flattened tube, tip curled up a little
        pts, radii = [], []
        for i in range(9):
            t = i / 8
            p = d * (r_disc * 0.5 + (R - r_disc * 0.5) * t) + Vector((0, 0, z0 + height * 0.35 + 0.06 * t ** 3))
            pts.append(p)
            radii.append(arm_w * (1.0 - 0.75 * t) + 0.01)
        radii[-1] = 0.0
        mb.add(nh.tube(pts, radii, sides=10, scale_xy=(1.0, 0.45)),
               lambda co, n, d=d: nh.lerp(plate, plate_dark,
                                          0.6 * nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.sin(co.dot(d) * 70))))
        # rows of block-like marginal plates along both edges, and an axial row
        for i in range(10):
            t = (i + 0.5) / 10
            p = d * (r_disc * 0.6 + (R - r_disc * 0.6) * t) + Vector((0, 0, z0 + height * 0.35 + 0.06 * t ** 3))
            w = arm_w * (1.0 - 0.75 * t) + 0.01
            s = 0.035 * (1.0 - 0.6 * t) + 0.01
            for sg in (-1, 1):
                q = p + side * sg * w * 0.85
                mb.add(nh.ellipsoid(tuple(q), (s, s, s * 0.7), subdivisions=1), marginal)
            mb.add(nh.ellipsoid(tuple(p + Vector((0, 0, w * 0.4))), (s * 0.8, s * 0.8, s * 0.5), subdivisions=1),
                   plate_dark)
    return _finish(mb, name)


VIEWS = dict(background=(0.05, 0.15, 0.18), ground=(0.30, 0.29, 0.26), views=((30, 25), (0, 70), (-90, 8)))
