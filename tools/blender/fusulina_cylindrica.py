"""
Procedural Fusulina cylindrica (Carboniferous fusulinid foraminifer) for colony instancing.

A small cluster of three spindle-shaped, rice-grain-like calcite tests. Each test is coiled
about its long axis, so its surface shows fine septal furrows running from pole to pole
(gently fluted, so they wave a little), the spiral suture where the last whorl wraps over the
one before, and faint transverse growth lines; the poles are bluntly pointed. Pale cream-tan,
a little darker toward the poles and in the furrows. One test is broken across its middle,
and the cut face shows the textbook section: a dark spiral wall coiling out from a tiny first
chamber, divided into chambers by the septa.
Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/fusulina_cylindrica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Fusulina.fbx
Faces -Y (long axis of the main test along Y), ~1.7 units across. Pivot at the cluster centre
(Drift style).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

AROUND = 32           # vertices around each test (two per septal furrow)
ALONG = 22            # stations from pole to pole
SEPTA = AROUND // 2

TEST = (0.95, 0.86, 0.66)       # pale cream calcite
TEST_TAN = (0.80, 0.64, 0.42)   # tan toward the poles
FURROW = (0.62, 0.48, 0.30)     # septal furrows
SUTURE = (0.48, 0.34, 0.20)
WALL = (0.50, 0.38, 0.24)        # spiral wall (spirotheca) in section
CHAMBER = (0.98, 0.93, 0.80)     # spiral suture of the last whorl

# (centre, yaw deg, pitch deg, roll deg, half-length, radius)
TESTS = [((0.0, 0.0, 0.0), 0, 0, 0, 0.80, 0.27, False),
         ((0.52, 0.42, 0.06), 62, 14, 70, 0.56, 0.18, True),
         ((-0.50, 0.40, -0.10), -38, -12, 140, 0.48, 0.155, False)]
WHORLS = 5.5          # whorls seen in the broken test's cross-section


def profile(t):
    """Radius fraction along the test (t = -1..1): sub-cylindrical middle, bluntly pointed poles."""
    a = abs(t)
    return (1.0 - a ** 2.3) ** 0.75


def test(half_len, radius, seed, broken=False):
    bm = bmesh.new()
    vcol = {}
    rings = []
    suture_phi = seed * 2.3
    last = ALONG // 2 if broken else ALONG
    for i in range(last + 1):
        u = i / ALONG
        t = -math.cos(u * math.pi)                         # denser toward the poles
        y = t * half_len
        if i == 0 or (i == ALONG and not broken):
            v = bm.verts.new((0.0, y * 1.01, 0.0))
            vcol[v] = TEST_TAN
            rings.append([v])
            continue
        r0 = radius * profile(t)
        ring = []
        for k in range(AROUND):
            # septal furrows wave gently along the length (septal fluting)
            phi = k / AROUND * math.tau + 0.035 * math.sin(t * 6.0 + k)
            furrow = 1.0 if k % 2 == 0 else 0.0
            # the last whorl overlaps the previous one along a spiral suture: a small step
            d = math.atan2(math.sin(phi - suture_phi - t * 0.4), math.cos(phi - suture_phi - t * 0.4))
            step = nh.smoothstep(-0.05, 0.25, d) * (1.0 - nh.smoothstep(2.6, 3.1, d))
            growth = 0.5 + 0.5 * math.cos(t * half_len * 46.0)
            r = r0 * (1.0 - 0.035 * furrow * (1.0 - abs(t) ** 4) + 0.012 * step - 0.006 * growth)
            co = Vector((math.cos(phi) * r, y, math.sin(phi) * r))
            v = bm.verts.new(co)
            c = nh.lerp(TEST, TEST_TAN, nh.smoothstep(0.45, 1.0, abs(t)))
            c = nh.lerp(c, FURROW, furrow * 0.55)
            c = nh.lerp(c, FURROW, growth * 0.12)
            c = nh.lerp(c, SUTURE, math.exp(-(d / 0.12) ** 2) * 0.8 * (1.0 - abs(t) ** 3))
            m = 1.0 + 0.06 * noise.noise(co * 14.0 + Vector((seed, 0, 0)))
            vcol[v] = tuple(min(1.0, x * m) for x in c)
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(AROUND):
            j = (k + 1) % AROUND
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[k]])
            elif len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    if broken:
        section(bm, vcol, rings[-1], radius * profile(0.0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def section(bm, vcol, edge, radius):
    """Cap a test broken across its middle: the cut face shows the coiled whorls (a dark spiral
    wall) divided into chambers by septa, around a tiny round first chamber (proloculus)."""
    n_r = 26
    rings = []
    for i in range(1, n_r):
        rho = i / n_r
        ring = []
        for k in range(AROUND):
            e = edge[k].co
            phi = math.atan2(e.z, e.x)
            co = Vector((e.x * rho, 0.0, e.z * rho))
            v = bm.verts.new(co)
            w = rho * WHORLS - (phi / math.tau) % 1.0        # spiral coordinate
            wall = math.exp(-(((w + 0.5) % 1.0 - 0.5) / 0.16) ** 2)
            septum = 1.0 if k % 2 == 0 else 0.0
            c = nh.lerp(CHAMBER, TEST_TAN, 0.2 + 0.25 * rho)
            c = nh.lerp(c, WALL, max(wall, septum * 0.45))
            c = nh.lerp(c, WALL, math.exp(-((rho - 0.06) / 0.03) ** 2))   # proloculus wall
            vcol[v] = c
            ring.append(v)
        rings.append(ring)
    centre = bm.verts.new((0.0, 0.0, 0.0))
    vcol[centre] = CHAMBER
    rings = [[centre]] + rings + [edge]
    for a, b in zip(rings, rings[1:]):
        for k in range(AROUND):
            j = (k + 1) % AROUND
            if len(a) == 1:
                bm.faces.new([a[0], b[k], b[j]])
            else:
                bm.faces.new([a[k], b[k], b[j], a[j]])


def build():
    mb = nh.MeshBuilder()
    for n, (c, yaw, pitch, roll, hl, r, broken) in enumerate(TESTS):
        bm, vcol = test(hl, r, n + 1, broken)
        m = (Matrix.Translation(Vector(c)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
             @ Matrix.Rotation(math.radians(pitch), 4, "X") @ Matrix.Rotation(math.radians(roll), 4, "Y"))
        nh.transform(bm, m)
        nf.add_colored(mb, bm, vcol)
    obj = mb.to_object("Fusulina", roughness=0.55)
    # pivot at the cluster centre
    lo = [min(v.co[a] for v in obj.data.vertices) for a in range(3)]
    hi = [max(v.co[a] for v in obj.data.vertices) for a in range(3)]
    mid = [(lo[a] + hi[a]) / 2 for a in range(3)]
    for v in obj.data.vertices:
        v.co.x -= mid[0]
        v.co.y -= mid[1]
        v.co.z -= mid[2]
    return obj


if __name__ == "__main__":
    nh.run(build, "Fusulina", background=(0.05, 0.14, 0.18), views=((35, 35), (-80, 15), (180, 60)))
