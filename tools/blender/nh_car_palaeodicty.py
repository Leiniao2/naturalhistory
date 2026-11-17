"""
Parametric palaeodictyopteran (beaked Palaeozoic insects) for the "car" batch
(mazothairos_enormis.py, stenodictya_lobata.py).

In level flight: a head with a downturned piercing-sucking beak, a thorax carrying a pair of
small flat prothoracic winglets in front of the two pairs of long wings held straight out
(they could not fold them back), a long ringed abdomen and two long cerci. Wings are
gridded, solidified sheets so a colour pattern (bands / spots / veins) can be painted per
vertex. Faces -Y, pivot at the body centre (flier).
"""

import math
from dataclasses import dataclass

import bmesh
from mathutils import Vector, noise

import nh_model as nh


@dataclass
class Spec:
    name: str
    span: float = 1.0            # half-span of the forewing tip from the midline
    chord: float = 0.16          # forewing max chord
    hind_chord: float = 0.20
    body_len: float = 0.55
    body_r: float = 0.035
    winglet: float = 0.07        # prothoracic winglet length
    cerci: float = 0.35
    body: tuple = (0.18, 0.13, 0.09)
    body_mark: tuple = (0.55, 0.40, 0.20)
    wing: tuple = (0.75, 0.70, 0.58)
    wing_root: tuple = (0.45, 0.35, 0.22)
    mark: tuple = (0.15, 0.11, 0.08)
    pattern: str = "bands"       # bands, spots, smoky
    bands: tuple = (0.35, 0.62, 0.85)
    vein: tuple = (0.30, 0.24, 0.16)
    eye: tuple = (0.12, 0.10, 0.08)


def wing_grid(root, span, chord, sweep_deg, colour, nu=16, nv=6, th=0.006, lead_curve=0.15):
    """Wing along +X from root (x, y, z); leading edge at -Y. Returns bmesh with 'Col' colours
    given by colour(u, v)."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    sw = math.tan(math.radians(sweep_deg))
    grid = []
    for i in range(nu + 1):
        u = i / nu
        x = root[0] + span * u
        c = chord * (0.55 + 0.45 * math.sin(math.pi * min(1.0, 0.25 + u * 0.85))) * (1 - 0.65 * u ** 6)
        lead = root[1] + sw * span * u - lead_curve * chord * u * u
        row = []
        for j in range(nv + 1):
            v = j / nv
            y = lead + c * v
            z = root[2] + 0.02 * span * u * u
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    uv = {}
    for i in range(nu):
        for j in range(nv):
            f = bm.faces.new([grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]])
            for l in f.loops:
                ii = next(a for a in range(nu + 1) if l.vert in grid[a])
                jj = grid[ii].index(l.vert)
                c = colour(ii / nu, jj / nv)
                l[col] = (c[0], c[1], c[2], 1.0)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=th)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def mirror(bm):
    for v in bm.verts:
        v.co.x = -v.co.x
    for f in bm.faces:
        f.normal_flip()
    return bm


def wing_colour(sp):
    def c(u, v):
        base = nh.lerp(sp.wing_root, sp.wing, nh.smoothstep(0.0, 0.2, u))
        m = 0.0
        if sp.pattern == "bands":
            for b in sp.bands:
                m = max(m, math.exp(-((u - b) / 0.05) ** 2))
        elif sp.pattern == "spots":
            for b in sp.bands:
                for vv in (0.3, 0.7):
                    m = max(m, math.exp(-(((u - b) / 0.06) ** 2 + ((v - vv) / 0.2) ** 2)))
        elif sp.pattern == "smoky":
            m = 0.6 + 0.3 * noise.noise(Vector((u * 6, v * 3, 0.3)))
        col = nh.lerp(base, sp.mark, min(1.0, m))
        if v < 0.08:  # thick leading-edge veins
            col = nh.lerp(col, sp.vein, 0.7)
        return col
    return c


def build(sp):
    mb = nh.MeshBuilder()
    L = sp.body_len
    y_head = -L * 0.5
    # fused body: head, beak, thorax, abdomen
    body = nh.MeshBuilder()
    body.add(nh.ellipsoid((0, y_head, 0.0), (sp.body_r * 1.1, sp.body_r * 1.0, sp.body_r * 0.95), 2), sp.body)
    body.add(nh.tube([(0, y_head - sp.body_r * 0.8, -sp.body_r * 0.2), (0, y_head - sp.body_r * 1.6, -sp.body_r * 1.2),
                      (0, y_head - sp.body_r * 1.4, -sp.body_r * 2.6)], [sp.body_r * 0.35, sp.body_r * 0.28, sp.body_r * 0.12],
                     sides=6), sp.body)
    body.add(nh.uv_ellipsoid((0, y_head + L * 0.22, 0.0), (sp.body_r * 1.35, L * 0.17, sp.body_r * 1.3), 14, 10), sp.body)
    n = 10
    for i in range(n):
        t = i / (n - 1)
        y = y_head + L * 0.38 + t * L * 0.62
        r = sp.body_r * (1.0 - 0.45 * t)
        body.add(nh.ellipsoid((0, y, 0.0), (r, L * 0.045, r * 0.9), 2), sp.body_mark if i % 2 else sp.body)
    fused = body.fuse(voxel=sp.body_r * 0.25, smooth=3, max_tris=3000)
    mb.add(fused)
    # eyes
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * sp.body_r * 0.9, y_head - sp.body_r * 0.2, sp.body_r * 0.3),
                            (sp.body_r * 0.45,) * 3, 2), sp.eye)
        # antennae
        mb.add(nh.tube([(sx * sp.body_r * 0.4, y_head - sp.body_r * 0.8, sp.body_r * 0.6),
                        (sx * sp.body_r * 2.0, y_head - sp.body_r * 4.0, sp.body_r * 1.4)],
                       [sp.body_r * 0.12, sp.body_r * 0.05], sides=4), sp.body)
        # cerci
        y_end = y_head + L
        mb.add(nh.tube([(0, y_end, 0), (sx * sp.cerci * 0.12, y_end + sp.cerci * 0.5, 0.01),
                        (sx * sp.cerci * 0.25, y_end + sp.cerci, 0.02)], [sp.body_r * 0.2, sp.body_r * 0.12, 0.0],
                       sides=5), sp.body)
        # legs folded under the thorax
        for k in range(3):
            y = y_head + L * (0.12 + 0.09 * k)
            mb.add(nh.tube([(sx * sp.body_r * 0.8, y, -sp.body_r * 0.6), (sx * sp.body_r * 2.2, y + 0.02 * (k - 1), -sp.body_r * 1.4),
                            (sx * sp.body_r * 2.0, y + 0.06, -sp.body_r * 2.0)], [sp.body_r * 0.2, sp.body_r * 0.15, sp.body_r * 0.08],
                           sides=4), sp.body)
    wc = wing_colour(sp)
    x0 = sp.body_r * 0.9
    for sx in (-1, 1):
        for root_y, chord, sweep, span in ((y_head + L * 0.12, sp.chord, -2, sp.span),
                                           (y_head + L * 0.28, sp.hind_chord, 6, sp.span * 0.93)):
            w = wing_grid((x0, root_y, sp.body_r * 0.4), span - x0, chord, sweep, wc, th=sp.span * 0.006)
            mb.add(mirror(w) if sx < 0 else w, smooth=False)
        # prothoracic winglet
        wl = wing_grid((x0 * 0.8, y_head + L * 0.04, sp.body_r * 0.4), sp.winglet, sp.winglet * 0.55, 20,
                       lambda u, v: nh.lerp(sp.wing_root, sp.mark, 0.3), nu=4, nv=2, th=sp.span * 0.006, lead_curve=0.0)
        mb.add(mirror(wl) if sx < 0 else wl, smooth=False)
    obj = mb.to_object(sp.name, roughness=0.5)
    vs = obj.data.vertices
    mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (mn + mx) / 2
    for v in vs:
        v.co -= c
    return obj


def run(sp):
    nh.run(lambda: build(sp), sp.name, background=(0.20, 0.28, 0.18), views=((35, 30), (0, 80), (-90, 8)))
