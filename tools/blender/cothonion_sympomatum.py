"""
Procedural Cothonion sympomatum (Cambrian operculate coral, Australia and North Greenland) for
the map: a small clustered corallum of horn-shaped cups, each capped by a hinged lid
(operculum), on a little patch of rubble.

Cothonion is one of the oldest coral-like cnidarians with a calcareous skeleton. Its corallum is
a cluster of cup-shaped corallites: new corallites bud from the side of a parent and curve up
beside it. Each cup has well-developed septa and was closed by a lid whose inner face also
carries radiating septa, a feature unknown in any living coral. Here: a tall parent corallite
with four daughters budding from its flanks, each a ring-stack (outer wall with transverse
growth wrinkles, a rounded rim, then a star-shaped calyx whose wall is fluted by the septa,
down to a dark floor). Each lid is a shallow lens hinged on the rim, shown at a different
opening: one shut, others ajar or wide open, with radial septal ridges painted and raised on
its underside. Open cups show a short ring of polyp tentacles; the soft parts are not preserved,
so these (and all colours) are a speculative reconstruction.
Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/cothonion_sympomatum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cothonion.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402

SEED = 5
SIDES = 20           # around each corallite (2 per septum)
SEPTA = 10
RINGS = 8            # outer-wall rings per corallite
LID_SEG, LID_RINGS = 20, 4
TENTACLES = 8
# daughters: (azimuth deg, bud height on parent 0..1, outward reach, rise, rim radius, lid open deg)
PARENT = dict(height=0.95, rim=0.21, lid=55)
DAUGHTERS = [
    (20, 0.30, 0.34, 0.42, 0.17, 0),
    (115, 0.22, 0.36, 0.50, 0.18, 80),
    (205, 0.38, 0.30, 0.36, 0.15, 30),
    (295, 0.18, 0.38, 0.30, 0.16, 12),
]

WALL = (0.86, 0.64, 0.40)       # warm ochre-tan epitheca
WALL_DARK = (0.60, 0.40, 0.24)  # growth wrinkles, lower corallum
RIM = (0.96, 0.86, 0.68)
CALYX = (0.34, 0.18, 0.12)      # inside the cup, between septa
SEPTUM = (0.72, 0.56, 0.42)
LID = (0.93, 0.80, 0.58)
LID_SEPTUM = (0.98, 0.93, 0.82)
LID_UNDER = (0.46, 0.28, 0.20)
TENTACLE = (1.0, 0.56, 0.50)   # soft coral-pink polyp
TENTACLE_TIP = (1.0, 0.86, 0.70)
UP = Vector((0, 0, 1))
WARP = Vector((5.3, 2.1, 7.7))


def frames_along(pts):
    """Parallel-transported (point, forward, side, up) frames along a polyline."""
    out, prev = [], None
    for i, p in enumerate(pts):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        if prev is None:
            ref = Vector((1, 0, 0)) if abs(fwd.x) < 0.9 else Vector((0, 1, 0))
            side = fwd.cross(ref).normalized()
        else:
            side = (prev - fwd * prev.dot(fwd)).normalized()
        prev = side
        out.append((p, fwd, side, side.cross(fwd).normalized()))
    return out


def corallite(pts, radii, rng):
    """Horn-shaped cup as one closed ring-stack with its own "Col" layer. Returns (bm, top frame)."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    fr = frames_along(pts)
    vcol, rows = {}, []

    def ring(f, r_of_k, offset, col_of_k):
        p, fwd, side, up = f
        vs = []
        for k in range(SIDES):
            a = k / SIDES * math.tau
            v = bm.verts.new(p + fwd * offset + (side * math.cos(a) + up * math.sin(a)) * r_of_k(k))
            vcol[v] = col_of_k(k, v.co)
            vs.append(v)
        rows.append(vs)

    n = len(pts)
    for i in range(n):
        t = i / (n - 1)
        wrinkle = (1.0 if i % 2 else -1.0) if 1 <= i <= n - 2 else 0.0   # growth wrinkles
        r = radii[i] * (1 + 0.05 * wrinkle * nh.smoothstep(0.1, 0.3, t))
        shade = nh.lerp(WALL, WALL_DARK, 0.6 * nh.smoothstep(0.3, 1.0, wrinkle) + 0.4 * (1 - t) ** 2)
        ring(fr[i], lambda k, r=r: r, 0.0,
             lambda k, co, s=shade: nh.lerp(s, WALL_DARK, 0.25 * noise.noise(co * 12 + WARP)))
    top, rt = fr[-1], radii[-1]
    # rounded rim, then the calyx: fluted by septa (every other column pokes inward)
    ring(top, lambda k: rt * 0.93, 0.025, lambda k, co: RIM)
    ring(top, lambda k: rt * 0.82, 0.02, lambda k, co: RIM)
    depth = (pts[-1] - pts[0]).length * 0.32
    for j, (f_off, dark) in enumerate(((0.0, 0.25), (-0.35, 0.6), (-0.75, 0.9))):
        ring(top, lambda k, j=j: rt * (0.78 - 0.08 * j) * (0.8 if k % 2 == 0 else 1.0), f_off * depth,
             lambda k, co, d=dark: nh.lerp(SEPTUM, CALYX, d * (0.55 if k % 2 == 0 else 1.0)))
    for a, b in zip(rows, rows[1:]):
        for k in range(SIDES):
            j = (k + 1) % SIDES
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        for lp in f.loops:
            c = vcol[lp.vert]
            lp[col] = (c[0], c[1], c[2], 1.0)
    return bm, top, rt


def lid(top, r, open_deg, hinge_az):
    """Operculum: shallow lens hinged on the rim, opened by open_deg. Septal ridges underneath."""
    p, fwd, side, up = top
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    bmesh.ops.create_uvsphere(bm, u_segments=LID_SEG, v_segments=LID_RINGS * 2, radius=1.0)
    vcol = {}
    for v in bm.verts:
        n = v.co.normalized()
        a = math.atan2(n.y, n.x)
        s = a / math.tau * SEPTA * 2   # bi-radial: septa on every other segment column
        on = abs(s - round(s)) < 0.25 and round(s) % 2 == 0
        if n.z >= 0:
            v.co = Vector((n.x * r * 1.04, n.y * r * 1.04, n.z * r * 0.28))
            rho = math.hypot(n.x, n.y)
            growth = 0.5 + 0.5 * math.cos(rho * 18)     # concentric growth lines
            vcol[v] = nh.lerp(LID, WALL_DARK, 0.18 * growth + 0.3 * nh.smoothstep(0.4, 0.0, n.z))
        else:
            ridge = 0.06 * r if on and abs(n.z) < 0.9 else 0.0
            v.co = Vector((n.x * r * 0.98, n.y * r * 0.98, n.z * r * 0.08 - ridge))
            vcol[v] = LID_SEPTUM if on and abs(n.z) < 0.9 else LID_UNDER
    for f in bm.faces:
        for lp in f.loops:
            c = vcol[lp.vert]
            lp[col] = (c[0], c[1], c[2], 1.0)
    # hinge on the rim at azimuth hinge_az (local x), open about the rim tangent
    az = math.radians(hinge_az)
    hinge = Vector((math.cos(az), math.sin(az), 0)) * r
    tangent = Vector((-math.sin(az), math.cos(az), 0))
    m = (Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(open_deg), 4, tangent)
         @ Matrix.Translation(-hinge) @ Matrix.Translation((0, 0, 0.03)))
    basis = Matrix((side, up, fwd)).transposed().to_4x4()
    nh.transform(bm, Matrix.Translation(p) @ basis @ m)
    return bm


def tentacles(mb, top, r, rng, open_frac):
    """A ring of short polyp tentacles peeking out of an open cup, leaning away from the hinge."""
    p, fwd, side, up = top
    for i in range(TENTACLES):
        a = i / TENTACLES * math.tau + rng.uniform(-0.1, 0.1)
        radial = side * math.cos(a) + up * math.sin(a)
        base = p + radial * r * 0.55 + fwd * 0.01
        length = r * rng.uniform(0.55, 0.8) * open_frac
        pts = [base, base + fwd * length * 0.5 + radial * length * 0.15,
               base + fwd * length * 0.9 + radial * length * 0.45]
        bm = nh.tube(pts, [r * 0.12, r * 0.10, r * 0.06], sides=5)
        mb.add(bm, lambda co, n, b=base, L=length: nh.lerp(TENTACLE, TENTACLE_TIP,
                                                            nh.smoothstep(0.2 * L, L, (co - b).length)))


def bezier(p0, p1, p2, n):
    return [p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t for t in (i / (n - 1) for i in range(n))]


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # parent: slightly curved horn
    h, rim = PARENT["height"], PARENT["rim"]
    ppts = bezier(Vector((0, 0, -0.02)), Vector((0.0, -0.02, h * 0.5)), Vector((0.04, 0.02, h)), RINGS)
    pr = [0.05 + (rim - 0.05) * (i / (RINGS - 1)) ** 0.7 for i in range(RINGS)]
    cups = [(ppts, pr, PARENT["lid"], 200)]

    def parent_at(t):
        i = min(RINGS - 2, int(t * (RINGS - 1)))
        u = t * (RINGS - 1) - i
        return ppts[i].lerp(ppts[i + 1], u), pr[i] + (pr[i + 1] - pr[i]) * u

    for az, bud, reach, rise, r_rim, open_deg in DAUGHTERS:
        out = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0))
        c, r_par = parent_at(bud)
        p0 = c + out * r_par * 0.4
        p1 = p0 + out * reach * 0.9 + UP * rise * 0.15
        p2 = p0 + out * reach + UP * rise
        pts = bezier(p0, p1, p2, RINGS - 1)
        radii = [0.04 + (r_rim - 0.04) * (i / (RINGS - 2)) ** 0.6 for i in range(RINGS - 1)]
        cups.append((pts, radii, open_deg, az))

    for pts, radii, open_deg, hinge_az in cups:
        bm, top, rt = corallite(pts, radii, rng)
        mb.add(bm)
        p, fwd, side, up = top
        # hinge on the outer side, so open lids stand up at the colony's edge (cup's local frame)
        d = Vector((math.cos(math.radians(hinge_az)), math.sin(math.radians(hinge_az)), 0))
        local_az = math.degrees(math.atan2(d.dot(up), d.dot(side)))
        mb.add(lid(top, rt, open_deg, local_az))
        if open_deg >= 25:
            tentacles(mb, top, rt, rng, min(1.0, open_deg / 60))

    # small attachment lump and rubble
    base = nh.MeshBuilder()
    for x, y, s in ((0.0, 0.0, 0.16), (0.08, -0.06, 0.11), (-0.07, 0.05, 0.1)):
        base.add(nh.ellipsoid((x, y, 0.0), (s, s * 0.9, s * 0.45), subdivisions=3), WALL_DARK)
    lump = base.fuse(voxel=0.03, smooth=6, max_tris=400)
    mb.add(lump, lambda co, n: nh.lerp(WALL_DARK, (0.45, 0.40, 0.34), 0.5 + 0.3 * noise.noise(co * 10)))
    nc.rubble(mb, rng, 0.45, 0.7, count=7, size=(0.04, 0.08))
    obj = mb.to_object("Cothonion", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Cothonion", ground=(0.62, 0.58, 0.48), views=((20, 25), (110, 35), (10, 75)))
