"""
Procedural Charnia masoni (Ediacaran rangeomorph frond) for the map: a small cluster of three
upright, leaf-shaped fronds of different heights, each on a short stalk rising from a buried
disc holdfast on a patch of microbial-mat seafloor.

Each frond is two half-blades either side of a raised central axis. A half-blade is a grid laid
along its primary branches - oblique ridges that sweep up and out from the axis, offset by half
a branch between the two sides so they alternate - and each primary branch is corrugated
across into secondary branches (with a vertex-colour hint of a third, finer order): the
self-similar "fern-like" rangeomorph pattern. Pale salmon-tan with darker furrows.
Fixed style: pivot at the base (z = 0), fronds upright and unbent so the map can sway them.

Usage:
  blender --background --python tools/blender/charnia_masoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Charnia.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

SEED = 5
PRIMARIES = 11        # primary branches per side (tallest frond)
ROWS_PER = 4          # grid rows per primary branch (furrow, rise, crest, fall)
SECONDARIES = 5       # secondary branches along each primary
SLANT = 2.4           # how far (in primaries) a branch climbs from the axis to the margin
SHEAR = 0.6          # secondary furrows lean (rangeomorph units are inclined, not square)

CREST = (0.90, 0.68, 0.52)    # pale salmon-tan branch crests
BLADE = (0.78, 0.53, 0.38)
FURROW = (0.34, 0.18, 0.12)   # deep primary furrows
AXIS = (0.66, 0.42, 0.29)     # central axis / stalk
STALK = (0.58, 0.38, 0.27)
DISC = (0.52, 0.40, 0.30)
MAT = (0.42, 0.40, 0.28)      # olive microbial mat
SAND = (0.66, 0.60, 0.46)

# (x, y, height, yaw degrees, lean degrees) for each frond in the cluster
FRONDS = [(0.0, 0.0, 1.55, 12, 3), (0.40, 0.26, 1.08, -48, 7), (-0.36, 0.24, 0.78, 62, 6)]


def half_width(v, width):
    """Frond outline: narrow where it leaves the stalk, broadest a little below the middle,
    tapering to a rounded point."""
    v = max(0.0, min(1.0, v))
    return width * (math.sin(math.pi * v ** 0.8) ** 0.75) * (1.0 - 0.15 * v)


def half_blade(side, length, width, thick, primaries, z0):
    """One side of the frond (side = +1 right / -1 left) as a closed front/back grid.
    Returns (bm, {vert: rgb})."""
    bm = bmesh.new()
    vcol = {}
    cols = SECONDARIES * 2
    off = 0.0 if side > 0 else 0.5               # alternate the branches between the sides
    s_lo = -SLANT - 1.0 - off
    rows = int((primaries + SLANT + 2.0) * ROWS_PER)
    front, back = [], []
    for j in range(rows + 1):
        s = s_lo + j / ROWS_PER
        frow, brow = [], []
        for i in range(cols + 1):
            q = i / cols
            p = (s + off) - math.floor(s + off)                       # 0..1 inside the primary
            u = min(1.0, q + SHEAR / SECONDARIES * (p - 0.5) * (q > 0) * (q < 1))
            # branch lines sweep up and out, curving upward toward the margin (sigmoid-ish)
            v = (s + SLANT * (0.55 * u + 0.45 * u * u)) / primaries
            vc = max(0.0, min(1.0, v))
            w = half_width(vc, width)
            x = side * (0.012 * (1.0 - vc) + u * w)
            z = z0 + vc * length
            # thickness: domed across the blade, corrugated by the primary and secondary branches
            env = math.sqrt(max(0.0, 1.0 - u ** 2.2)) * (w / width) ** 0.6
            prim = 0.5 - 0.5 * math.cos(p * math.tau)                 # 0 in the furrow, 1 on the crest
            sec = 1.0 if i % 2 else 0.0
            t = thick * env * (0.32 + 0.38 * prim + 0.30 * sec * prim)
            # third order: tiny colour-only crinkles along the secondaries
            tert = 0.5 + 0.5 * math.sin((q * cols * 2 + p * 3.0) * math.pi)
            c = nh.lerp(FURROW, BLADE, nh.smoothstep(0.0, 0.5, prim))
            c = nh.lerp(c, CREST, prim * sec)                          # secondary crests
            c = nh.lerp(c, FURROW, (1.0 - sec) * prim * 0.45 + 0.1 * tert)  # secondary furrows
            c = nh.lerp(c, AXIS, nh.smoothstep(0.08, 0.0, u) * 0.6)
            k = 1.0 + 0.06 * noise.noise(Vector((x * 9, z * 9, side * 3.0)))
            c = tuple(min(1.0, a * k) for a in c)
            vf = bm.verts.new((x, -t, z))
            vb = bm.verts.new((x, t, z)) if i < cols else vf          # the margin is shared
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
    # merge the collapsed rows below the frond base and above its tip
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:  # the front faces -Y
        f.normal_update()
    vcol = {v: vcol.get(v, BLADE) for v in bm.verts}
    return bm, vcol


def _nearest_col(bm, vcol):
    """remove_doubles keeps one of each merged pair; colours were keyed per original vert."""
    return {v: vcol[v] for v in bm.verts if v in vcol}


def frond(mb, height, rng):
    stalk_h = height * 0.13
    length = height - stalk_h
    width = height * 0.17
    thick = height * 0.020
    primaries = max(9, round(PRIMARIES * (0.55 + 0.45 * height / 1.55)))
    parts = []
    for side in (-1, 1):
        bm, vcol = half_blade(side, length, width, thick, primaries, stalk_h)
        parts.append((bm, vcol))
    # raised central axis running the length of the frond, tapering into the tip
    pts, rad = [], []
    for k in range(12):
        t = k / 11
        pts.append((0.0, 0.0, stalk_h * 0.2 + (height * 0.95 - stalk_h * 0.2) * t))
        rad.append(height * (0.022 * (1 - t) + 0.007 * t) if k < 11 else 0.0)
    axis = nh.tube(pts, rad, sides=8, scale_xy=(0.8, 1.0))
    # short stalk flaring into the holdfast disc
    stalk = nh.tube([(0, 0, -0.01), (0, 0, stalk_h * 0.3), (0, 0, stalk_h * 0.8), (0, 0, stalk_h * 1.1)],
                    [height * 0.045, height * 0.032, height * 0.027, height * 0.022], sides=10)
    disc_r = height * 0.13
    disc = nh.uv_ellipsoid((0, 0, 0.0), (disc_r, disc_r, disc_r * 0.22), 18, 8,
                           deform=lambda n: 1.0 + 0.05 * noise.noise(n * 3.0 + Vector((height, 0, 0))))
    return parts, axis, stalk, disc, disc_r


def disc_color(r_disc):
    def fn(co, n):
        r = math.hypot(co.x, co.y) / r_disc
        ring = 0.5 + 0.5 * math.cos(r * 5.5 * math.tau)       # concentric holdfast rings
        c = nh.lerp(DISC, nh.lerp(DISC, SAND, 0.45), ring * 0.6)
        return nh.lerp(c, STALK, nh.smoothstep(0.35, 0.0, r))
    return fn


def place(bm, x, y, yaw, lean):
    m = (Matrix.Translation(Vector((x, y, 0.0))) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
         @ Matrix.Rotation(math.radians(lean), 4, "X"))
    nh.transform(bm, m)
    return bm


def seafloor(mb, rng):
    """Low, lumpy microbial-mat patch the cluster is rooted in."""
    bm = nh.uv_ellipsoid((0.0, 0.12, -0.03), (0.72, 0.58, 0.06), 28, 8,
                         deform=lambda n: 1.0 + 0.08 * noise.noise(n * 4.0 + Vector((2.0, 5.0, 1.0))))

    def col(co, n):
        m = noise.noise(co * 6.0) * 0.5 + 0.5
        wrinkle = abs(noise.noise(co * 22.0))
        c = nh.lerp(MAT, SAND, 0.3 + 0.4 * m)
        c = nh.lerp(c, (0.30, 0.30, 0.20), nh.smoothstep(0.08, 0.0, wrinkle) * 0.5)  # "elephant skin" wrinkles
        return nh.lerp(c, SAND, nh.smoothstep(0.45, 0.72, math.hypot(co.x, co.y - 0.12) / 0.72))

    mb.add(bm, col)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    seafloor(mb, rng)
    for x, y, h, yaw, lean in FRONDS:
        parts, axis, stalk, disc, disc_r = frond(mb, h, rng)
        for bm, vcol in parts:
            place(bm, x, y, yaw, lean)
            nf.add_colored(mb, bm, _nearest_col(bm, vcol))
        mb.add(place(axis, x, y, yaw, lean), AXIS)
        mb.add(place(stalk, x, y, yaw, lean), STALK)
        f = disc_color(disc_r)
        mb.add(place(disc, x, y, yaw, 0.0),
               lambda co, n, x=x, y=y, f=f: f(Vector((co.x - x, co.y - y, co.z)), n))
    obj = mb.to_object("Charnia", roughness=0.7)
    for v in obj.data.vertices:  # flatten the buried undersides of the mat and holdfasts
        v.co.z = max(v.co.z, -0.012)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Charnia", ground=(0.55, 0.52, 0.40), background=(0.05, 0.14, 0.18),
           views=((20, 18), (70, 30), (10, 65), (-90, 6)))
