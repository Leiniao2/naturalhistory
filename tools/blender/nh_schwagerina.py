"""
Shared builder for Schwagerina-type (schwagerinid) fusulinid foraminifers, Early Permian.

Each model is a small cluster of calcite tests (like fusulina_cylindrica.py, but schwagerinid):
larger, more inflated fusiform-to-subcylindrical tests with bluntly rounded poles, a thick
keriothecal (honeycomb-textured) wall, strong regular septal fluting showing on the surface as
deep, close septal furrows from pole to pole, and loosely coiled outer whorls. One test in each
cluster is broken across its middle; the cut face shows the coiled spirotheca, thickening and
spacing out toward the outside, with the dark-and-light banded keriotheca and the cross-cut
fluted septa between the whorls, around a small round proloculus.
Colour is in vertex colours (see nh_model).

Per-species scripts define a Spec and call build(spec). Faces -Y (long axis of the main test
along Y). Pivot at the cluster centre (Drift style).
"""

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

PER_SEPTUM = 4        # vertices around the test per septal furrow


@dataclass
class Spec:
    name: str
    # (centre, yaw deg, pitch deg, roll deg, half-length, radius, broken)
    tests: list = field(default_factory=lambda: [
        ((0.0, 0.0, 0.0), 0, 0, 0, 0.80, 0.34, False),
        ((0.58, 0.46, 0.06), 62, 14, 70, 0.58, 0.25, True),
        ((-0.56, 0.42, -0.10), -38, -12, 140, 0.50, 0.21, False)])
    # outline: radius fraction r(t) = (1 - |t|^p)^q, t = -1..1 from pole to pole;
    # large p = long straight (subcylindrical) middle, small q = blunt rounded poles
    prof_p: float = 2.4
    prof_q: float = 0.55
    pole_point: float = 0.0     # draws the poles out into a short point (0..1)
    septa: int = 20             # septal furrows around the test
    furrow: float = 0.07        # furrow depth as a fraction of radius
    flute: float = 0.06         # sideways wave of the furrows along the length (rad)
    along: int = 30             # stations from pole to pole
    whorls: float = 5.0         # whorls in the broken section
    loose: float = 1.6          # >1: outer whorls more loosely coiled than inner
    wall: float = 0.16          # spiral wall thickness (fraction of a whorl), inner whorls
    wall_out: float = 0.26      # ... outer whorls (thickens outward)
    rim: float = 0.06           # outer wall seen in the cut face (fraction of radius)
    # colours
    test: tuple = (0.93, 0.85, 0.68)      # calcite
    test_tan: tuple = (0.78, 0.64, 0.45)  # toward the poles
    furrow_col: tuple = (0.58, 0.46, 0.31)
    suture: tuple = (0.45, 0.34, 0.22)
    wall_col: tuple = (0.42, 0.32, 0.22)  # spirotheca (dark tectum)
    kerio: tuple = (0.70, 0.58, 0.42)     # honeycomb keriotheca (paler band in the wall)
    chamber: tuple = (0.97, 0.92, 0.80)   # chamber fill in section
    roughness: float = 0.6
    preview_bg: tuple = (0.05, 0.14, 0.18)


def _profile(spec, t):
    a = abs(t)
    r = max(0.0, 1.0 - a ** spec.prof_p) ** spec.prof_q
    if spec.pole_point:
        # pull the pole region in toward a narrower point
        r *= 1.0 - spec.pole_point * nh.smoothstep(0.55, 1.0, a) * 0.35
    return r


def test(spec, half_len, radius, seed, broken=False):
    bm = bmesh.new()
    vcol = {}
    rings = []
    around = spec.septa * PER_SEPTUM
    suture_phi = seed * 2.3
    n = spec.along
    last = n // 2 if broken else n
    for i in range(last + 1):
        u = i / n
        t = -math.cos(u * math.pi)                         # denser toward the poles
        y = t * half_len
        if i == 0 or (i == n and not broken):
            v = bm.verts.new((0.0, y * 1.005, 0.0))
            vcol[v] = spec.test_tan
            rings.append([v])
            continue
        r0 = radius * _profile(spec, t)
        ring = []
        for k in range(around):
            # septal furrows wave along the length (septa strongly fluted throughout)
            base = k / around * math.tau
            phi = base + spec.flute * math.sin(t * 6.0 + 2.0 * base + seed)
            furrow = (0.5 + 0.5 * math.cos(spec.septa * base)) ** 3   # deep narrow furrow, broad crest
            d = math.atan2(math.sin(phi - suture_phi - t * 0.35), math.cos(phi - suture_phi - t * 0.35))
            growth = 0.5 + 0.5 * math.cos(t * half_len * 40.0)
            fade = 1.0 - abs(t) ** 6
            r = r0 * (1.0 - spec.furrow * furrow * fade - 0.005 * growth)
            co = Vector((math.cos(phi) * r, y, math.sin(phi) * r))
            v = bm.verts.new(co)
            c = nh.lerp(spec.test, spec.test_tan, nh.smoothstep(0.5, 1.0, abs(t)))
            c = nh.lerp(c, spec.furrow_col, furrow * 0.7 * fade)
            c = nh.lerp(c, spec.furrow_col, growth * 0.10)
            c = nh.lerp(c, spec.suture, math.exp(-(d / 0.2) ** 2) * 0.4 * (1.0 - abs(t) ** 3))
            # keriothecal wall: fine honeycomb mottling
            m = 1.0 + 0.05 * noise.noise(co * 16.0 + Vector((seed, 0, 0))) \
                + 0.04 * noise.noise(co * 55.0 + Vector((0, seed, 0)))
            vcol[v] = tuple(min(1.0, x * m) for x in c)
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(around):
            j = (k + 1) % around
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[k]])
            elif len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    if broken:
        section(spec, bm, vcol, rings[-1], seed)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def section(spec, bm, vcol, edge, seed):
    """Cap a test broken across its middle: coiled whorls of thick keriothecal wall, loosening
    outward, with cross-cut fluted septa between them, around a tiny round proloculus."""
    around = len(edge)
    rmean = sum(e.co.length for e in edge) / around
    n_r = 44
    rings = []
    for i in range(1, n_r):
        rho = i / n_r
        ring = []
        for k in range(around):
            e = edge[k].co
            phi = math.atan2(e.z, e.x)
            # inner whorls are round; only the outermost follows the fluted outline
            base = k / around * math.tau
            f_out = nh.smoothstep(0.75, 1.0, rho)
            s = (rmean + (e.length - rmean) * f_out) / max(e.length, 1e-6)
            co = Vector((e.x * rho * s, 0.0, e.z * rho * s))
            v = bm.verts.new(co)
            # spiral coordinate; rho = (w / W)^loose -> outer whorls more widely spaced
            w = spec.whorls * rho ** (1.0 / spec.loose) - ((phi + seed) / math.tau) % 1.0
            f = ((w + 0.5) % 1.0) - 0.5                    # -0.5..0.5 across a whorl
            thick = spec.wall + (spec.wall_out - spec.wall) * rho
            wall = math.exp(-(f / (thick * 0.6)) ** 4)     # flat-topped wall band
            # keriotheca: the inner part of the wall is a paler honeycomb layer below the dark tectum
            kerio = math.exp(-((f + thick * 0.25) / (thick * 0.35)) ** 2) * wall
            honey = 0.5 + 0.5 * math.sin(phi * spec.septa * 4.0) * math.sin(rho * 140.0)
            septum = (0.5 + 0.5 * math.cos(spec.septa * base)) ** 6
            # fluted septa cut across show as loops/arches in the chamber, not just lines
            loop = math.exp(-((abs(f) - 0.32) / 0.07) ** 2) * (0.5 + 0.5 * math.cos(phi * spec.septa * 2.0))
            c = nh.lerp(spec.chamber, spec.test_tan, 0.15 + 0.2 * rho)
            c = nh.lerp(c, spec.wall_col, max(septum * 0.4, loop * 0.25) * (rho > 0.08))
            c = nh.lerp(c, spec.wall_col, wall)
            c = nh.lerp(c, spec.kerio, kerio * (0.45 + 0.3 * honey))
            c = nh.lerp(c, spec.wall_col, math.exp(-((rho - 0.05) / 0.025) ** 2))   # proloculus wall
            c = nh.lerp(c, spec.wall_col, nh.smoothstep(1.0 - spec.rim, 1.0 - spec.rim * 0.3, rho) * 0.85)
            vcol[v] = c
            ring.append(v)
        rings.append(ring)
    centre = bm.verts.new((0.0, 0.0, 0.0))
    vcol[centre] = spec.chamber
    rings = [[centre]] + rings + [edge]
    for a, b in zip(rings, rings[1:]):
        for k in range(around):
            j = (k + 1) % around
            if len(a) == 1:
                bm.faces.new([a[0], b[k], b[j]])
            else:
                bm.faces.new([a[k], b[k], b[j], a[j]])


def build(spec):
    mb = nh.MeshBuilder()
    for n, (c, yaw, pitch, roll, hl, r, broken) in enumerate(spec.tests):
        bm, vcol = test(spec, hl, r, n + 1, broken)
        m = (Matrix.Translation(Vector(c)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
             @ Matrix.Rotation(math.radians(pitch), 4, "X") @ Matrix.Rotation(math.radians(roll), 4, "Y"))
        nh.transform(bm, m)
        nf.add_colored(mb, bm, vcol)
    obj = mb.to_object(spec.name, roughness=spec.roughness)
    # pivot at the cluster centre
    lo = [min(v.co[a] for v in obj.data.vertices) for a in range(3)]
    hi = [max(v.co[a] for v in obj.data.vertices) for a in range(3)]
    mid = [(lo[a] + hi[a]) / 2 for a in range(3)]
    for v in obj.data.vertices:
        v.co.x -= mid[0]
        v.co.y -= mid[1]
        v.co.z -= mid[2]
    return obj


VIEWS = ((35, 35), (-80, 15), (180, 60))


def main(spec):
    nh.run(lambda: build(spec), spec.name, background=spec.preview_bg, views=VIEWS)
