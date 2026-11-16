"""
Procedural Rangea schneiderhoehni (Ediacaran rangeomorph frond, Namibia) for the map: a single
upright, spindle-shaped frond rising from a short bulbous base on a patch of microbial-mat
seafloor.

Unlike Charnia's flat two-sided leaf, Rangea is reconstructed with SIX vanes radiating around a
central axis like the fletching of an arrow (a six-pointed star seen from above). Each vane is a
grid laid along its primary branches - chunky, sigmoidal ridges that leave the axis, sweep up and
out and curl upward at the vane margin, alternating between neighbouring vanes - and each
primary is corrugated across into secondary branches, with a vertex-colour hint of a third,
finer order: the self-similar rangeomorph pattern. Muted ochre-tan with dark brown furrows.
Fixed style: pivot at the base (z = 0), frond upright and unbent so the map can sway it.

Usage:
  blender --background --python tools/blender/rangea_schneiderhoehni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rangea.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

VANES = 6             # vanes around the central axis
HEIGHT = 1.6          # base to tip
PRIMARIES = 7         # primary branches per vane
ROWS_PER = 5          # grid rows per primary branch (furrow, rise, crest, fall)
SECONDARIES = 5       # secondary branches along each primary
SLANT = 1.6           # how far (in primaries) a branch climbs from the axis to the margin
SHEAR = 0.7           # secondary furrows lean (rangeomorph units are inclined, not square)

CREST = (0.86, 0.70, 0.47)    # ochre-tan branch crests
BLADE = (0.72, 0.55, 0.35)
FURROW = (0.30, 0.20, 0.12)   # deep primary furrows
AXIS = (0.60, 0.45, 0.29)     # central axis
BASE = (0.52, 0.40, 0.27)     # bulbous base
MAT = (0.42, 0.40, 0.28)      # olive microbial mat
SAND = (0.66, 0.60, 0.46)


def vane_width(v, width):
    """Vane outline (radial reach from the axis): spindle-shaped - narrow at the base, broadest
    a little below the middle and tapering to a point at the tip."""
    v = max(0.0, min(1.0, v))
    return width * (math.sin(math.pi * v ** 0.85) ** 0.9)


def vane(length, width, thick, primaries, z0, off):
    """One vane in the local XZ plane (x = distance from the axis), as a closed front/back grid.
    off: phase offset (in primaries) so neighbouring vanes alternate. Returns (bm, {vert: rgb})."""
    bm = bmesh.new()
    vcol = {}
    cols = SECONDARIES * 2
    s_lo = -SLANT - 1.0 - off
    rows = int((primaries + SLANT + 2.0) * ROWS_PER)
    front, back = [], []
    for j in range(rows + 1):
        s = s_lo + j / ROWS_PER
        frow, brow = [], []
        for i in range(cols + 1):
            q = i / cols
            p = (s + off) - math.floor(s + off)                        # 0..1 inside the primary
            u = min(1.0, q + SHEAR / SECONDARIES * (p - 0.5) * (q > 0) * (q < 1))
            # sigmoidal branch: leaves the axis nearly flat, climbs, then curls up at the margin
            v = (s + SLANT * (0.25 * u + 0.75 * u ** 2.2)) / primaries
            vc = max(0.0, min(1.0, v))
            w = vane_width(vc, width)
            x = 0.018 + u * w
            z = z0 + vc * length
            env = math.sqrt(max(0.0, 1.0 - u ** 2.0)) * (1.0 - 0.35 * u) * (w / width) ** 0.5
            prim = 0.5 - 0.5 * math.cos(p * math.tau)                  # 0 in the furrow, 1 on the crest
            sec = 1.0 if i % 2 else 0.0
            t = thick * env * (0.16 + 0.54 * prim + 0.30 * sec * prim)
            tert = 0.5 + 0.5 * math.sin((q * cols * 2 + p * 3.0) * math.pi)
            c = nh.lerp(FURROW, BLADE, nh.smoothstep(0.0, 0.5, prim))
            c = nh.lerp(c, CREST, prim * sec)                          # secondary crests
            c = nh.lerp(c, FURROW, (1.0 - sec) * prim * 0.45 + 0.12 * tert)  # secondary furrows
            c = nh.lerp(c, AXIS, nh.smoothstep(0.1, 0.0, u) * 0.6)
            k = 1.0 + 0.07 * noise.noise(Vector((x * 9, z * 9, off * 5.0)))
            c = tuple(min(1.0, a * k) for a in c)
            vf = bm.verts.new((x, -t, z))
            vb = bm.verts.new((x, t, z)) if i < cols else vf           # the margin is shared
            vcol[vf] = vcol[vb] = c
            frow.append(vf)
            brow.append(vb)
        front.append(frow)
        back.append(brow)
    for j in range(rows):
        for i in range(cols):
            for grid, flip in ((front, False), (back, True)):
                quad = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
                if flip:
                    quad.reverse()
                if len(set(quad)) < 3:
                    continue
                try:
                    bm.faces.new(list(dict.fromkeys(quad)))
                except ValueError:
                    pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    vcol = {v: vcol.get(v, BLADE) for v in bm.verts}
    return bm, vcol


def seafloor(mb):
    """Low, lumpy microbial-mat patch the frond is rooted in."""
    bm = nh.uv_ellipsoid((0.0, 0.0, -0.03), (0.62, 0.56, 0.06), 28, 8,
                         deform=lambda n: 1.0 + 0.08 * noise.noise(n * 4.0 + Vector((7.0, 1.0, 3.0))))

    def col(co, n):
        m = noise.noise(co * 6.0) * 0.5 + 0.5
        wrinkle = abs(noise.noise(co * 22.0))
        c = nh.lerp(MAT, SAND, 0.3 + 0.4 * m)
        c = nh.lerp(c, (0.30, 0.30, 0.20), nh.smoothstep(0.08, 0.0, wrinkle) * 0.5)  # "elephant skin"
        return nh.lerp(c, SAND, nh.smoothstep(0.45, 0.72, math.hypot(co.x, co.y) / 0.62))

    mb.add(bm, col)


def build():
    mb = nh.MeshBuilder()
    seafloor(mb)
    base_h = HEIGHT * 0.07
    length = HEIGHT - base_h
    width = HEIGHT * 0.22
    thick = HEIGHT * 0.034
    for k in range(VANES):
        bm, vcol = vane(length, width, thick, PRIMARIES, base_h, off=0.5 * (k % 2))
        nh.transform(bm, Matrix.Rotation(math.radians(30 + k * 360 / VANES), 4, "Z"))
        nf.add_colored(mb, bm, vcol)
    # central axis: a slim spindle running the length of the frond into the tip
    pts, rad = [], []
    for k in range(14):
        t = k / 13
        pts.append((0.0, 0.0, base_h * 0.3 + (HEIGHT * 0.97 - base_h * 0.3) * t))
        rad.append(HEIGHT * (0.028 * (1 - t) + 0.006 * t) * (0.8 + 0.4 * math.sin(math.pi * t)) if k < 13 else 0.0)
    mb.add(nh.tube(pts, rad, sides=12), AXIS)
    # short bulbous base sunk into the mat
    mb.add(nh.uv_ellipsoid((0, 0, base_h * 0.4), (HEIGHT * 0.06, HEIGHT * 0.06, base_h * 1.1), 14, 8,
                           deform=lambda n: 1.0 + 0.06 * noise.noise(n * 3.0)), BASE)
    obj = mb.to_object("Rangea", roughness=0.7)
    for v in obj.data.vertices:  # flatten the buried underside of the mat
        v.co.z = max(v.co.z, -0.012)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Rangea", ground=(0.55, 0.52, 0.40), background=(0.05, 0.14, 0.18),
           views=((20, 18), (70, 30), (10, 65), (0, 89)))
