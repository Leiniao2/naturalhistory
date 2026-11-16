"""
Procedural Xianguangia sinica (early Cambrian, Chengjiang biota, Yunnan, ~518 Ma) for the map: a
little group of anemone-like polyps on a patch of mud, each a ribbed column on a bowl-shaped
basal disc, crowned by eighteen long, feathery tentacles.

Described by Chen & Erdtmann (1991) and long reconstructed as a sea-anemone-like stem
anthozoan; later work (Zhao et al. 2019, and a 2023 study of 88 specimens) argued it is instead
a sessile, suspension-feeding relative of comb jellies, so its affinity is debated. The anatomy
modelled here is the part both readings agree on:
  * a bowl-shaped basal attachment disc, probably partly buried in the sediment (shown sunk
    into a low mud mound);
  * a cylindrical 'column', slightly widening upward, with eighteen longitudinal ridges: the
    2023 study found that the column is formed by the sheathed lower parts of the eighteen
    tentacles, so each ridge here runs up into one tentacle;
  * a crown of eighteen long, tapering tentacles, each fringed on both sides with fine, closely
    spaced pinnules (short, three-sided cones angled toward the tip), giving them a feathery
    look; the pinnules were probably ciliated and used to sieve micro-plankton from the water;
  * the tentacle complexes could splay out ("blooming") or close up into a column, so two of
    the polyps are shown open, tentacles arching out and drooping at the tips, and one closed,
    its tentacles gathered upward into a tight bundle (pinnules hidden).
Colours are unknown; muted salmon-buff with paler, cream pinnules.
Fixed style: pivot at the base of the mud mound (z = 0).

Usage:
  blender --background --python tools/blender/xianguangia_sinica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Xianguangia.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 9
TENTACLES = 18
SIDES = 36            # column segments around (two per tentacle sheath)
COL_H = 0.55          # column height above the basal disc
COL_R0, COL_R1 = 0.075, 0.10   # column radius at the base and at the crown
DISC_R = 0.14         # basal disc radius
MOUND_Z = 0.05        # mud surface height (the basal discs sit just below it)
TENT_LEN = 0.52
TENT_STEPS = 5
PINNULES = 8          # per side, per tentacle
# polyps: (x, y, scale, open?, lean azimuth deg, lean deg)
POLYPS = [
    (0.00, 0.05, 1.00, True, 200, 6),
    (0.48, -0.10, 0.82, True, 330, 10),
    (-0.30, -0.36, 0.72, False, 240, 8),
]

COLUMN = (0.74, 0.55, 0.43)       # muted salmon-buff
COLUMN_DARK = (0.52, 0.37, 0.29)  # ridge grooves, mud-stained base
DISC = (0.50, 0.39, 0.31)         # basal disc
ORAL = (0.84, 0.66, 0.54)
MOUTH = (0.42, 0.24, 0.20)
TENT_BASE = (0.76, 0.56, 0.44)
TENT_TIP = (0.90, 0.78, 0.64)
PINNULE = (0.93, 0.86, 0.74)      # pale, cream fringe
MUD = (0.40, 0.34, 0.27)
MUD_LIGHT = (0.53, 0.46, 0.36)


def ridge(a):
    """1 on each tentacle sheath, 0 in the grooves between them."""
    return 0.5 + 0.5 * math.cos(a * TENTACLES)


def column():
    """Lathe from the basal disc up through the ridged column to a slightly domed oral disc."""
    prof = [  # (radius, z)
        (0.0, -0.035), (DISC_R * 0.85, -0.025), (DISC_R, 0.01),
        (COL_R0 * 1.15, 0.06)]
    for i in range(3):
        t = (i + 1) / 3
        prof.append((COL_R0 + (COL_R1 - COL_R0) * t ** 1.4, 0.06 + (COL_H - 0.06) * t))
    prof += [(COL_R1 * 0.75, COL_H + 0.02), (COL_R1 * 0.35, COL_H + 0.03), (0.0, COL_H + 0.015)]
    bm = bmesh.new()
    rings = []
    for r, z in prof:
        if r <= 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
            continue
        on_col = 0.05 < z < COL_H + 0.001
        ring = []
        for j in range(SIDES):
            a = j / SIDES * math.tau
            rr = r * (1.0 + (0.09 * (ridge(a) - 0.5) if on_col else 0.0)
                      + 0.03 * noise.noise(Vector((math.cos(a), math.sin(a), z * 8))))
            ring.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, z)))
        rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        if len(ra) == 1:
            for j in range(SIDES):
                bm.faces.new([ra[0], rb[j], rb[(j + 1) % SIDES]])
        elif len(rb) == 1:
            for j in range(SIDES):
                bm.faces.new([ra[j], ra[(j + 1) % SIDES], rb[0]])
        else:
            for j in range(SIDES):
                k = (j + 1) % SIDES
                bm.faces.new([ra[j], ra[k], rb[k], rb[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        z = co.z
        r = math.hypot(co.x, co.y)
        if z > COL_H + 0.005 and n.z > 0.4:
            return nh.lerp(ORAL, MOUTH, nh.smoothstep(0.05, 0.02, r))
        if z < 0.06:
            return DISC
        c = nh.lerp(COLUMN_DARK, COLUMN, nh.smoothstep(0.05, 0.25, z))
        return nh.lerp(COLUMN_DARK, c, 0.45 + 0.55 * ridge(math.atan2(co.y, co.x)))
    return bm, color


def tentacle_path(rng, a, opened):
    """Polyline and radii of one tentacle rising from the crown margin at angle a."""
    out = Vector((math.cos(a), math.sin(a), 0.0))
    side = Vector((-out.y, out.x, 0.0))
    base = out * COL_R1 * 0.92 + Vector((0, 0, COL_H - 0.01))
    length = TENT_LEN * rng.uniform(0.9, 1.08)
    if opened:
        e0, curl = rng.uniform(62, 76), rng.uniform(-95, -65)   # rise, then arch out and droop
        swirl = rng.uniform(-12, 12)
    else:
        e0, curl, swirl = 86, 0, 0
        length *= 0.85
    pts, radii = [], []
    p = base.copy()
    seg = length / TENT_STEPS
    r0 = 0.020 * rng.uniform(0.9, 1.1)
    for k in range(TENT_STEPS + 1):
        t = k / TENT_STEPS
        pts.append(p.copy())
        radii.append(r0 * (1.0 - 0.7 * t))
        if opened:
            e = math.radians(e0 + curl * t ** 1.4)
            s = math.radians(swirl * t)
            d = (out * math.cos(e) + Vector((0, 0, math.sin(e)))) * math.cos(s) + side * math.sin(s)
        else:
            # closed: lean inward so the tentacles gather into a bundle above the crown
            d = Vector((0, 0, 1)) - out * (0.17 * t + 0.05)
        p = p + d.normalized() * seg
    pts.append(p)
    radii.append(0.0)
    return pts, radii, side


def tentacle(mb, rng, a, opened):
    pts, radii, side = tentacle_path(rng, a, opened)
    total = sum((q - o).length for o, q in zip(pts, pts[1:]))
    b = pts[0]
    mb.add(nh.tube(pts, radii, sides=3, cap_start=False),
           lambda co, n: nh.lerp(TENT_BASE, TENT_TIP, nh.smoothstep(0.1, 1.0, (co - b).length / total)))
    if not opened:
        return
    # pinnules: two rows of fine cones in the plane around the crown, swept toward the tip
    for i in range(PINNULES):
        t = 0.12 + 0.84 * i / (PINNULES - 1)
        f = t * TENT_STEPS
        k = min(TENT_STEPS - 1, int(f))
        u = f - k
        p = pts[k].lerp(pts[k + 1], u)
        fwd = (pts[k + 1] - pts[k]).normalized()
        sd = (side - fwd * side.dot(fwd)).normalized()
        r = radii[k] + (radii[k + 1] - radii[k]) * u
        length = 0.08 * (1.0 - 0.5 * t) * rng.uniform(0.9, 1.1)
        for s in (-1, 1):
            d = (sd * s * math.cos(math.radians(42)) + fwd * math.sin(math.radians(42))).normalized()
            q0 = p + sd * s * r * 0.6
            mb.add(nh.tube([q0, q0 + d * length], [0.008, 0.0], sides=3, cap_start=False),
                   PINNULE)


def polyp(rng, opened):
    mb = nh.MeshBuilder()
    mb.add(*column())
    for i in range(TENTACLES):
        # one tentacle per column ridge
        a = i / TENTACLES * math.tau + rng.uniform(-0.02, 0.02)
        tentacle(mb, rng, a, opened)
    return mb.bm


def mound(rng):
    seed = Vector((rng.random() * 40, rng.random() * 40, 3.0))
    bm = nh.uv_ellipsoid((0.06, -0.12, 0.0), (0.72, 0.62, MOUND_Z), segments=28, rings=6,
                         deform=lambda n: 1.0 + 0.12 * noise.noise(n * 2.0 + seed))

    def color(co, n):
        return nh.lerp(MUD, MUD_LIGHT, 0.5 + 0.5 * noise.noise(co * 10 + seed))
    return bm, color


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(*mound(rng))
    for x, y, s, opened, az, lean in POLYPS:
        bm = polyp(rng, opened)
        axis = Vector((-math.sin(math.radians(az)), math.cos(math.radians(az)), 0))
        m = (Matrix.Translation((x, y, MOUND_Z - 0.02)) @ Matrix.Rotation(math.radians(lean), 4, axis)
             @ Matrix.Rotation(rng.uniform(0, math.tau), 4, "Z") @ Matrix.Scale(s, 4))
        nh.transform(bm, m)
        mb.add(bm)
    obj = mb.to_object("Xianguangia", roughness=0.5)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Xianguangia", background=(0.04, 0.18, 0.26), ground=(0.36, 0.33, 0.28),
           views=((20, 22), (110, 12), (10, 70)))
