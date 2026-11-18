"""
Procedural low-poly Nummulites gizehensis, a giant Eocene foraminifer (the "coin stones" of the
Giza pyramid limestone).

Three coin-sized, lens-shaped (biconvex, thin-rimmed) calcite tests of different sizes, lying on
the seabed and overlapping a little. Their faces show the many-whorled planispiral growth: a
tight spiral suture coiling out from a small raised central boss, crossed by fine, slightly
curved radial septa marking off the chambers of each whorl. The third test is split along its
equatorial plane, the way the fossils weather and break, and leans on edge against the largest,
its cut face toward the front showing the spiral wall and the rows of chambers between the septa,
round a tiny first chamber (proloculus). Stony cream-buff. Colour is in vertex colours (see
nh_model); the chamber pattern is painted per face on a spiral-following mesh, so it stays crisp.

Usage:
  blender --background --python tools/blender/nummulites_gizehensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Nummulites.fbx
About 1.6 units across, low (~0.5 high where the split test stands). The split test's section
faces -Y (front). Pivot at the bottom, on the seabed (Fixed).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEPT = 0.22           # septum width as a fraction of a chamber's angular width
CURVE = 0.10          # backward curve of the septa (radians at mid-whorl)

STONE = (0.88, 0.80, 0.62)       # cream-buff calcite
STONE_DEEP = (0.76, 0.66, 0.47)
SUTURE = (0.56, 0.45, 0.30)      # spiral suture on the faces
SEPTUM = (0.68, 0.57, 0.40)      # septal lines on the faces
BOSS = (0.95, 0.90, 0.76)
WALL = (0.96, 0.92, 0.80)        # spiral wall in section (clear calcite)
CHAMBER = (0.66, 0.54, 0.36)     # sediment-filled chambers in section
CHAMBER_DEEP = (0.52, 0.41, 0.26)

# (radius, half-thickness, whorls, spokes per whorl)
BIG = (0.56, 0.105, 5.0, 36)
MEDIUM = (0.36, 0.07, 4.0, 26)
SPLIT = (0.34, 0.07, 4.5, 30)


def lens_z(rho, R, H):
    """Height of the convex face at radius rho: biconvex, thin at the rim, a low central boss."""
    u = min(1.0, rho / R)
    return H * ((1.0 - u * u) ** 0.8 + 0.18 * math.exp(-(u / 0.12) ** 2))


def spiral_face(R, H, W, S, section=False, seed=0.0):
    """One face of a test as a mesh that follows the spiral: rows run along the coil (a thin row
    for the spiral wall/suture, a wide one for the chambers), spokes alternate thin (septum) and
    wide (chamber). section=True gives the flat equatorial cut (z = 0) instead of the convex face."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    rows = (0.0, 0.16, 1.0)
    vmap = {}

    def angle(m):
        return math.tau * (m // 2 + (SEPT if m % 2 else 0.0)) / (S / 2)

    def vert(m, j):
        t = rows[j]
        a = angle(m)
        rho = R * max(0.0, a / math.tau + t) / W
        rho = min(rho, R)
        phi = a - CURVE * math.sin(math.pi * t) * 2
        x, y = math.cos(phi) * rho, math.sin(phi) * rho
        key = (round(x, 5), round(y, 5))
        if rho < 1e-6:
            key = (0.0, 0.0)
        if key not in vmap:
            z = 0.0 if section else lens_z(rho, R, H)
            vmap[key] = bm.verts.new((x, y, z))
        return vmap[key]

    m_end = int(W * S) + 1
    for m in range(-S - 2, m_end):
        for j in range(len(rows) - 1):
            quad = [vert(m, j), vert(m + 1, j), vert(m + 1, j + 1), vert(m, j + 1)]
            uniq = []
            for v in quad:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) < 3:
                continue
            try:
                f = bm.faces.new(uniq)
            except ValueError:
                continue
            c3 = sum((v.co for v in uniq), Vector()) / len(uniq)
            rho = Vector((c3.x, c3.y)).length / R
            septum = (m % 2 == 0)
            wall = (j == 0)
            whorl = (angle(m) / math.tau)
            if section:
                c = nh.lerp(CHAMBER, CHAMBER_DEEP, 0.5 + 0.5 * math.sin(m * 1.7 + seed))
                c = nh.lerp(c, CHAMBER_DEEP, nh.smoothstep(0.3, 1.0, rho) * 0.4)
                if wall or septum:
                    c = WALL
                if rho < 0.07:
                    c = CHAMBER_DEEP if rho > 0.035 else WALL
            else:
                c = nh.lerp(STONE, STONE_DEEP, nh.smoothstep(0.55, 1.0, rho) * 0.6)
                c = nh.lerp(c, STONE_DEEP, 0.12 * (0.5 + 0.5 * noise.noise(c3 * 9.0 + Vector((seed, 0, 0)))))
                if septum:
                    c = nh.lerp(c, SEPTUM, 0.75)
                if wall:
                    c = SUTURE if whorl > 0.3 else c
                c = nh.lerp(c, BOSS, nh.smoothstep(0.16, 0.05, rho))
            for loop in f.loops:
                loop[col] = (c[0], c[1], c[2], 1.0)
    for f in bm.faces:
        f.smooth = not section
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    return bm


def plain_face(R, H, segments, rings=4, seed=0.0):
    """The face lying on the seabed (or leaning against another test): a plain lens dome,
    pointing down (-Z), with faint radial septal lines."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    centre = bm.verts.new((0, 0, -lens_z(0.0, R, H)))
    grid = []
    for i in range(1, rings + 1):
        rho = R * i / rings
        grid.append([bm.verts.new((math.cos(k / segments * math.tau) * rho, math.sin(k / segments * math.tau) * rho,
                                   -lens_z(rho, R, H))) for k in range(segments)])
    for k in range(segments):
        j = (k + 1) % segments
        bm.faces.new([centre, grid[0][j], grid[0][k]])
        for a, b in zip(grid, grid[1:]):
            bm.faces.new([a[k], a[j], b[j], b[k]])
    for f in bm.faces:
        f.smooth = True
        for loop in f.loops:
            co = loop.vert.co
            rho = Vector((co.x, co.y)).length / R
            phi = math.atan2(co.y, co.x)
            c = nh.lerp(STONE, STONE_DEEP, nh.smoothstep(0.4, 1.0, rho) * 0.7)
            c = nh.lerp(c, SEPTUM, 0.3 * (0.5 + 0.5 * math.cos(phi * segments / 2)) * nh.smoothstep(0.2, 0.5, rho))
            loop[col] = (c[0], c[1], c[2], 1.0)
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z > 0:
            f.normal_flip()
    return bm


def test(spec, seed, split=False):
    R, H, W, S = spec
    if split:
        parts = [spiral_face(R, H, W, S, section=True, seed=seed), plain_face(R, H, S, seed=seed)]
        # the split test keeps its lower half: section on top (z = 0), dome below
    else:
        parts = [spiral_face(R, H, W, S, seed=seed), plain_face(R, H, S, seed=seed)]
    return parts


def place(mb, parts, matrix, ground=True):
    """Transform the parts; ground=True drops the piece so its lowest point is at z = 0."""
    for p in parts:
        nh.transform(p, matrix)
    if ground:
        zmin = min(v.co.z for p in parts for v in p.verts)
        for p in parts:
            nh.transform(p, Matrix.Translation((0, 0, -zmin)))
    for p in parts:
        mb.add(p)


def build():
    mb = nh.MeshBuilder()
    # the largest test lying flat
    place(mb, test(BIG, 1.0), Matrix.Translation((-0.08, 0.18, 0.0)) @ Matrix.Rotation(0.4, 4, "Z"))
    # a middle-sized one overlapping its front-left rim, tipped up a little where it rests on it
    m = (Matrix.Translation((-0.50, -0.32, 0.075)) @ Matrix.Rotation(math.radians(-7), 4, "X")
         @ Matrix.Rotation(math.radians(-9), 4, "Y") @ Matrix.Rotation(1.9, 4, "Z"))
    place(mb, test(MEDIUM, 2.0), m, ground=False)
    # the split one standing on edge, leaning back on the big one, its cut face to the front
    m = (Matrix.Translation((0.40, -0.26, 0.0)) @ Matrix.Rotation(math.radians(-22), 4, "Z")
         @ Matrix.Rotation(math.radians(62), 4, "X"))
    place(mb, test(SPLIT, 3.0, split=True), m)
    obj = mb.to_object("Nummulites", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Nummulites", background=(0.05, 0.14, 0.18), views=((25, 30), (-120, 25), (0, 80)))
