"""
Procedural Swartpuntia germsi (Ediacaran petalonamid frond, Nama Group, Namibia) for the map:
a broad, leaf-like frond held up on a long, smooth stalk that rises from a small bulb holdfast on
a patch of microbial-mat seafloor.

The frond is made of three petaloid vanes joined along the stalk, which runs on through the
frond as a raised midrib: two broad, round-tipped lateral vanes form the "leaf" seen from the
front, and a narrower third vane stands out from the back (a T seen from above). Each vane is a
grid laid along its tubes - plump, transverse ribs separated by deep grooves, running out from
the midrib and curving gently upward toward the margin - with two faint seams parallel to the
midrib that divide the tubes into a quilted pattern. Unlike the rangeomorphs there is no fractal
branching, just one order of quilted tubes. Muted pinkish grey-tan with darker grooves.
Fixed style: pivot at the base (z = 0), frond upright and unbent so the map can sway it.

Usage:
  blender --background --python tools/blender/swartpuntia_germsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Swartpuntia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

STALK_H = 0.62        # stalk from the holdfast to the bottom of the frond
LEAF_L = 1.15         # frond length
ROWS_PER = 4          # grid rows per tube (groove, rise, crest, fall)
CURVE = 2.2           # how far (in tubes) a tube climbs from the midrib to the margin
SEAMS = (0.38, 0.72)  # quilting seams, as fractions of the vane width
CUP = 0.07            # the lateral vanes cup gently forward (-Y) toward their margins
# (yaw degrees, mirror, half-width, tubes, columns, cup) for each vane; yaw 0 = the right vane
VANES = [(0, False, 0.40, 18, 14, CUP), (0, True, 0.40, 18, 14, CUP), (90, False, 0.22, 15, 9, 0.0)]

CREST = (0.80, 0.68, 0.62)    # pinkish grey-tan tube crests
TUBE = (0.66, 0.54, 0.48)
GROOVE = (0.32, 0.24, 0.21)   # deep grooves between tubes
SEAM = (0.46, 0.36, 0.32)
MIDRIB = (0.58, 0.47, 0.40)
STALK = (0.56, 0.47, 0.40)
HOLD = (0.48, 0.40, 0.33)
MAT = (0.42, 0.40, 0.28)      # olive microbial mat
SAND = (0.66, 0.60, 0.46)


def vane_width(v, width):
    """Petal outline: narrow where it leaves the stalk, broad through the middle, round-tipped."""
    v = max(0.0, min(1.0, v))
    return width * (math.sin(math.pi * (0.04 + 0.96 * v) ** 0.75) ** 0.55) * (1.0 - 0.12 * v)


def vane(width, tubes, cols, thick, z0, cup):
    """One vane in the local XZ plane (x = distance from the midrib), as a closed front/back grid
    whose rows follow the tubes. Returns (bm, {vert: rgb})."""
    bm = bmesh.new()
    vcol = {}
    rows = int((tubes + CURVE + 1.0) * ROWS_PER)
    front, back = [], []
    for j in range(rows + 1):
        s = -CURVE - 0.5 + j / ROWS_PER
        frow, brow = [], []
        for i in range(cols + 1):
            u = i / cols
            p = s - math.floor(s)                                     # 0..1 across a tube
            v = (s + CURVE * u * u) / tubes
            vc = max(0.0, min(1.0, v))
            w = vane_width(vc, width)
            x = 0.02 + u * w
            z = z0 + vc * LEAF_L
            env = math.sqrt(max(0.0, 1.0 - u ** 3.0)) * (w / width) ** 0.4
            tube = math.sin(math.pi * p) ** 0.6                       # plump, round-topped tubes
            seam = max(nh.smoothstep(0.06, 0.0, abs(u - sm)) for sm in SEAMS)
            t = thick * env * (0.25 + 0.75 * tube) * (1.0 - 0.35 * seam)
            c = nh.lerp(GROOVE, TUBE, nh.smoothstep(0.0, 0.55, tube))
            c = nh.lerp(c, CREST, nh.smoothstep(0.7, 1.0, tube) * 0.8)
            c = nh.lerp(c, SEAM, seam * 0.7)
            c = nh.lerp(c, MIDRIB, nh.smoothstep(0.1, 0.0, u) * 0.6)
            k = 1.0 + 0.06 * noise.noise(Vector((x * 7, z * 7, width * 9)))
            c = tuple(min(1.0, a * k) for a in c)
            y = -cup * u * u * (w / width)
            vf = bm.verts.new((x, y - t, z))
            vb = bm.verts.new((x, y + t, z)) if i < cols else vf          # the margin is shared
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
    vcol = {v: vcol.get(v, TUBE) for v in bm.verts}
    return bm, vcol


def seafloor(mb):
    """Low, lumpy microbial-mat patch the stalk is rooted in."""
    bm = nh.uv_ellipsoid((0.0, 0.0, -0.03), (0.48, 0.44, 0.05), 24, 8,
                         deform=lambda n: 1.0 + 0.08 * noise.noise(n * 4.0 + Vector((3.0, 8.0, 1.0))))

    def col(co, n):
        m = noise.noise(co * 6.0) * 0.5 + 0.5
        wrinkle = abs(noise.noise(co * 22.0))
        c = nh.lerp(MAT, SAND, 0.3 + 0.4 * m)
        c = nh.lerp(c, (0.30, 0.30, 0.20), nh.smoothstep(0.08, 0.0, wrinkle) * 0.5)  # "elephant skin"
        return nh.lerp(c, SAND, nh.smoothstep(0.45, 0.72, math.hypot(co.x, co.y) / 0.48))

    mb.add(bm, col)


def build():
    mb = nh.MeshBuilder()
    seafloor(mb)
    thick = 0.035
    for yaw, mirror, width, tubes, cols, cup in VANES:
        bm, vcol = vane(width, tubes, cols, thick, STALK_H, cup)
        nh.transform(bm, Matrix.Rotation(math.radians(yaw), 4, "Z"))
        if mirror:
            nh.transform(bm, Matrix.Scale(-1.0, 4, (1, 0, 0)))
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        nf.add_colored(mb, bm, vcol)
    # long smooth stalk, continuing through the frond as the midrib and tapering into the tip
    top = STALK_H + LEAF_L * 0.96
    pts = [(0, 0, -0.01), (0, 0, STALK_H * 0.35), (0, 0, STALK_H * 0.75), (0, 0, STALK_H),
           (0, 0, STALK_H + LEAF_L * 0.35), (0, 0, STALK_H + LEAF_L * 0.7), (0, 0, top)]
    mb.add(nh.tube(pts, [0.045, 0.036, 0.033, 0.034, 0.03, 0.022, 0.0], sides=10), STALK)
    # small bulb holdfast, half buried in the mat
    mb.add(nh.uv_ellipsoid((0, 0, 0.0), (0.085, 0.085, 0.05), 14, 8,
                           deform=lambda n: 1.0 + 0.08 * noise.noise(n * 3.0)), HOLD)
    obj = mb.to_object("Swartpuntia", roughness=0.7)
    for v in obj.data.vertices:  # flatten the buried underside of the mat
        v.co.z = max(v.co.z, -0.012)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Swartpuntia", ground=(0.55, 0.52, 0.40), background=(0.05, 0.14, 0.18),
           views=((20, 18), (70, 30), (10, 65), (0, 89)))
