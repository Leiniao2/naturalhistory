"""
Procedural Groenlandaspis antarcticus for the map: a small arthrodire placoderm from the
Middle-Late Devonian rivers and lakes of Antarctica (Groenlandaspis is found on almost
every continent of the time); about 40 cm long.

Its trademark is the very tall, pointed, tent-shaped median dorsal plate rising from the
thoracic armour, which gives the fish a triangular "sail" on its back. A short, blunt
armoured head is hinged to a deep box-like thoracic shield; behind the armour a naked body
tapers into a long fringed tail. Small shearing jaw blades, high-set orbits.

Skin loft plus a proud armour shell and the crest pyramid. Colours unknown: grey-green
armour with pale tubercles, olive body.

Usage:
  blender --background --python tools/blender/groenlandaspis_antarcticus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Groenlandaspis.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Groenlandaspis"

ARMOUR = (0.56, 0.62, 0.54)
ARMOUR_DARK = (0.30, 0.36, 0.32)
TUBERCLE = (0.86, 0.88, 0.78)
SUTURE = (0.16, 0.13, 0.09)
BACK = (0.20, 0.24, 0.17)
FLANK = (0.40, 0.44, 0.30)
BELLY = (0.78, 0.74, 0.60)
BLOTCH = (0.13, 0.13, 0.09)
FIN = (0.32, 0.32, 0.22)
FIN_EDGE = (0.55, 0.53, 0.40)
RAY = (0.16, 0.16, 0.11)
BLADE = (0.88, 0.84, 0.72)
MOUTH = (0.07, 0.05, 0.04)

PROF = ef.Profile([
    (-0.80, 0.040, 0.050, 0.040, -0.020),
    (-0.77, 0.090, 0.100, 0.080, -0.016),
    (-0.70, 0.135, 0.150, 0.115, -0.008),
    (-0.58, 0.165, 0.190, 0.145, 0.004),
    (-0.42, 0.175, 0.205, 0.155, 0.008),
    (-0.26, 0.162, 0.190, 0.145, 0.008),
    (-0.14, 0.118, 0.140, 0.112, 0.008),
    (0.04, 0.078, 0.096, 0.080, 0.008),
    (0.22, 0.048, 0.060, 0.050, 0.008),
    (0.42, 0.027, 0.033, 0.027, 0.008),
    (0.62, 0.012, 0.014, 0.012, 0.008),
    (0.80, 0.002, 0.003, 0.002, 0.008),
], power=lambda y: 2.6 if y < -0.2 else 2.1)

Y_ARMOUR = -0.22          # back edge of the thoracic shield (dorsal midline)
Y_NECK = -0.56            # head / thoracic shield joint


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.25


def armour_end(v):
    # the shield reaches further back on the back than on the flanks
    return Y_ARMOUR - 0.10 * (1.0 - max(v, -0.2))


def armour_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(ARMOUR, ARMOUR_DARK, 0.4 * nh.smoothstep(-0.2, -0.9, v))
    c = nh.lerp(c, TUBERCLE, 0.5 * nh.smoothstep(0.15, 0.45, ef.mottle(co, 60.0, 1.0)))
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.3), (-0.62, 0.0), (-0.60, 0.6), (-0.70, 1.2), (-0.56, 1.6),
             (-0.38, 0.0), (-0.36, 0.9), (-0.40, 1.6), (-0.34, 2.4)]
    c = nh.lerp(c, SUTURE, 0.7 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    # the neck joint groove between head and thoracic shields
    c = nh.lerp(c, SUTURE, 0.9 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_NECK + 0.03 * abs(u))))))
    if co.y < -0.6 and abs(u) > 0.3:
        c = nh.lerp(c, MOUTH, 1.0 - nh.smoothstep(0.004, 0.010, abs(co.z - mouth_z(co.y))))
    return c


def skin_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.4)


def armour_shell(mb):
    """Second, slightly proud shell over the front, trimmed at the shield's back edge."""
    bm = ef.loft(PROF, PROF.y0, Y_ARMOUR + 0.02, 24, 30, grow=0.006, cap0=True, cap1=False)
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        u, v = PROF.rel(c)
        if c.y > armour_end(v):
            kill.append(f)
    import bmesh
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    mb.add(bm, armour_color)


def crest(mb):
    """The tall, pointed median dorsal plate: a narrow pyramid on the thoracic shield."""
    import bmesh
    y0, y1, ya = -0.50, -0.14, -0.30
    apex = Vector((0.0, ya + 0.04, PROF.top(ya) + 0.25))
    bm = bmesh.new()
    n = 8
    left, right = [], []
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        w = 0.035 * math.sin(math.pi * i / n) ** 0.5 + 0.004
        z = PROF.top(y) - 0.012
        right.append(bm.verts.new((w, y, z)))
        left.append(bm.verts.new((-w, y, z)))
    a = bm.verts.new(apex)
    for i in range(n):
        bm.faces.new([right[i], right[i + 1], a])
        bm.faces.new([left[i + 1], left[i], a])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, nrm):
        h = nh.smoothstep(PROF.top(co.y), apex.z, co.z)
        c = nh.lerp(ARMOUR, ARMOUR_DARK, 0.3 + 0.3 * h)
        c = nh.lerp(c, TUBERCLE, 0.6 * nh.smoothstep(0.15, 0.4, ef.mottle(co, 70.0, 2.0)))
        # growth ridges radiating from the apex
        r = math.atan2(co.y - apex.y, apex.z - co.z)
        return nh.lerp(c, SUTURE, 0.35 * nh.smoothstep(0.7, 0.95, abs(math.sin(r * 18.0))))
    mb.add(bm, col, smooth=False)


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=50, na=26)
    armour_shell(mb)
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    crest(mb)
    df.web(mb, PROF, 0.00, 0.16, lambda u: (0.06 * u + 0.03, 0.07 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    # long tail fringed above and below
    df.web(mb, PROF, 0.26, 0.80, lambda u: (0.04 * u, 0.06 * df.bump(u, 0.6, 0.05) + 0.004), rays(10),
           side=1, n=ef.ray_cols(10), rows=2)
    df.web(mb, PROF, 0.14, 0.80, lambda u: (0.04 * u, -(0.07 * df.bump(u, 0.6, 0.05) + 0.004)), rays(11),
           side=-1, n=ef.ray_cols(11), rows=2)
    for s in (1, -1):
        ef.paired_fin(mb, PROF, s, -0.26, -0.18, -0.6, lambda u: 0.11 * (1 - u) ** 0.6 + 0.01,
                      0.8, 0.4, 0.8, rays(4), cols=ef.ray_cols(4), rows=2)
        ef.paired_fin(mb, PROF, s, 0.02, 0.10, -1.1, lambda u: 0.06 * (1 - u) ** 0.6 + 0.01,
                      0.6, 0.6, 0.8, rays(3), cols=ef.ray_cols(3), rows=2)
        # pale beak-like jaw blades along the gape
        pts = []
        for k in range(6):
            y = -0.795 + 0.16 * k / 5
            z = mouth_z(y)
            best = min((abs(PROF.point(y, a).z - z), a) for a in [-math.pi / 2 + q / 80 * math.pi for q in range(81)])[1]
            p = PROF.point(y, best, 0.008)
            p.x *= s
            pts.append(p)
        mb.add(nh.tube(pts, [0.004, 0.009, 0.010, 0.009, 0.007, 0.003], sides=5, scale_xy=(0.6, 1.0)), BLADE)
    # big orbits high on the head
    ef.surface_eye(mb, PROF, -0.68, 0.60, 0.032, (0.85, -0.3, 0.4), iris=(0.75, 0.60, 0.25), ring=ARMOUR_DARK)
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
