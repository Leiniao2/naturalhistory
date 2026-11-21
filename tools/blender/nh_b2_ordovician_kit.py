"""
Shared helpers for the batch-2 Ordovician species (tag "b2 ord"): small, mostly sessile
sea-floor animals that need a few generic shapes the older modules don't have.

  * mud(): the low mottled sediment disc of nh_ord_echino (top at about z = 0.02).
  * finish_fixed(): object, grounded (z = 0 at the base) and centred in X/Y (Fixed style).
  * finish_swim(): object centred on the body (Swim style).
  * heightfield_disc(): a dome-like surface z = h(x, y) over a disc of radius R, skirted down to
    z = 0 (coral heads, edrioasteroid discs, low colonies).
  * valve(): one valve of a bivalved shell (bivalve, ostracod, brachiopod) as a closed lens half:
    an outline in the commissure plane (polar function about a centre) bulged out to one side,
    max inflation `infl` near the umbo; painted by a colour fn. Two mirrored valves make a shell.
  * stars(): pale star-shaped spots for a colour function (Constellaria's maculae).
  * voronoi_plates(): polygonal plate pattern with dark sutures for a colour function.
"""

import math
import random

import bmesh
from mathutils import Vector, noise

import nh_model as nh
import nh_ord_echino as ec

MUD = ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41))
VIEWS = dict(background=(0.05, 0.15, 0.18), ground=(0.30, 0.29, 0.26), views=((30, 25), (0, 70), (-90, 8)))
SWIM_VIEWS = dict(background=(0.05, 0.20, 0.24), views=((30, 35), (0, 85), (-90, 10)))


def mud(mb, radius, colors=MUD, seed=3):
    ec.mud_patch(mb, radius, colors, seed=seed)


def finish_fixed(mb, name, roughness=0.6):
    return ec._finish(mb, name, roughness)


def finish_swim(mb, name, roughness=0.5):
    obj = mb.to_object(name, roughness=roughness)
    vs = obj.data.vertices
    xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


def heightfield_disc(R, hfn, n_r=30, n_a=72, outline=None):
    """Surface z = hfn(x, y) over a disc (radius R * outline(angle)), with a skirt to z = 0."""
    bm = bmesh.new()
    rings = []
    for i in range(1, n_r + 1):
        t = i / n_r
        ring = []
        for j in range(n_a):
            a = j / n_a * math.tau
            r = R * t * (outline(a) if outline else 1.0)
            x, y = r * math.cos(a), r * math.sin(a)
            ring.append(bm.verts.new((x, y, hfn(x, y))))
        rings.append(ring)
    c = bm.verts.new((0, 0, hfn(0, 0)))
    for j in range(n_a):
        bm.faces.new([c, rings[0][j], rings[0][(j + 1) % n_a]])
    for i in range(n_r - 1):
        for j in range(n_a):
            jj = (j + 1) % n_a
            bm.faces.new([rings[i][j], rings[i + 1][j], rings[i + 1][jj], rings[i][jj]])
    base = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in rings[-1]]
    for j in range(n_a):
        jj = (j + 1) % n_a
        bm.faces.new([rings[-1][j], base[j], base[jj], rings[-1][jj]])
    bm.faces.new(list(reversed(base)))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def valve(outline, infl, side=1, n_r=16, n_a=48, peak=(0.0, 0.0), power=0.7, frame=None):
    """One valve. outline(a) -> radius of the margin at polar angle a (in the commissure plane
    (u, v), measured about the origin); infl: max bulge; peak: (u, v) of the point of maximum
    inflation (umbo region) as a fraction of the local radius; side: +1/-1 bulge direction.
    frame(u, v, w) -> (x, y, z) maps commissure coordinates (u, v) and bulge w to model space
    (default: u = y, v = z, w = x, i.e. the shell stands on its edge, facing -Y).
    Returns a bmesh whose open edge is the margin (pair it with the mirrored valve)."""
    if frame is None:
        frame = lambda u, v, w: (w, u, v)  # noqa: E731
    bm = bmesh.new()
    pu, pv = peak
    rings = []
    for i in range(1, n_r + 1):
        t = i / n_r
        ring = []
        for j in range(n_a):
            a = j / n_a * math.tau
            R = outline(a)
            # blend the polar centre towards the peak so the bulge maximum sits there
            u = (1 - t) * pu * R + t * R * math.cos(a)
            v = (1 - t) * pv * R + t * R * math.sin(a)
            w = side * infl * (1.0 - t ** 2) ** power
            ring.append(bm.verts.new(frame(u, v, w)))
        rings.append(ring)
    R0 = outline(0.0)
    c = bm.verts.new(frame(pu * R0, pv * R0, side * infl))
    faces = []
    for j in range(n_a):
        faces.append([c, rings[0][j], rings[0][(j + 1) % n_a]])
    for i in range(n_r - 1):
        for j in range(n_a):
            jj = (j + 1) % n_a
            faces.append([rings[i][j], rings[i + 1][j], rings[i + 1][jj], rings[i][jj]])
    for f in faces:
        bm.faces.new(f if side > 0 else list(reversed(f)))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.normal_update()
    # make normals point away from the commissure plane
    probe = Vector(frame(0, 0, side))
    origin = Vector(frame(0, 0, 0))
    out = (probe - origin).normalized()
    if sum(f.normal.dot(out) for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return bm


def stars(co, n, cell=0.07, r=0.024, rays=6, seed=0.0):
    """0..1 mask of star-shaped spots (rays arms) scattered on a surface (3D Worley cells)."""
    try:
        d, pts = noise.voronoi(co / cell + Vector((seed, seed, seed)), distance_metric='DISTANCE', exponent=2.5)
    except TypeError:
        d, pts = noise.voronoi(co / cell + Vector((seed, seed, seed)))
    p = (pts[0] - Vector((seed, seed, seed))) * cell
    v = co - p
    nn = Vector(n).normalized() if Vector(n).length > 1e-6 else Vector((0, 0, 1))
    v = v - nn * v.dot(nn)
    t = nn.cross(Vector((0, 0, 1)) if abs(nn.z) < 0.9 else Vector((1, 0, 0))).normalized()
    b = nn.cross(t)
    ang = math.atan2(v.dot(b), v.dot(t))
    lim = r * (0.45 + 0.55 * max(0.0, math.cos(rays * ang)) ** 2)
    return 1.0 - nh.smoothstep(lim * 0.7, lim, v.length)


def voronoi_plates(co, scale, seed=0.0):
    """(edge closeness 0..1, cell random 0..1) for a polygonal plate pattern."""
    try:
        d, pts = noise.voronoi(co * scale + Vector((seed, seed * 0.7, seed * 0.3)), distance_metric='DISTANCE')
    except TypeError:
        d, pts = noise.voronoi(co * scale + Vector((seed, seed * 0.7, seed * 0.3)))
    edge = 1.0 - nh.smoothstep(0.0, 0.12, d[1] - d[0])
    k = 0.5 + 0.5 * noise.noise(pts[0] * 3.1)
    return edge, k


def seeded(seed):
    return random.Random(seed)
