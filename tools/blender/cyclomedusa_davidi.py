"""
Procedural Cyclomedusa davidi (Ediacaran concentric disc) for the map: a low, flat, roughly
circular disc lying on a patch of wrinkled microbial-mat seafloor, with a smaller disc beside it.

Once taken for a fossil jellyfish (hence the name), Cyclomedusa is now usually read as the
holdfast of a frond or a microbial structure, so it is modelled as a sessile, slightly domed
pad: a raised central boss ringed by a groove, then many concentric ridges that get lower and
broader toward the margin, crossed by faint radial grooves, all a little irregular. The disc is a
polar grid displaced by that profile, with a flat buried underside; vertex colours darken the
furrows and lighten the ridge crests. Muted ochre-tan on an olive-grey mat.
Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/cyclomedusa_davidi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cyclomedusa.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

SEED = 3
RINGS = 9             # concentric ridges outside the boss
RADIALS = 28          # faint radial grooves
# (x, y, radius, radial steps, angular steps) for each disc
DISCS = [(-0.08, -0.04, 0.62, 28, 64), (0.62, 0.42, 0.22, 22, 40)]

CREST = (0.82, 0.68, 0.48)    # ochre-tan ridge crests
DISC = (0.66, 0.52, 0.36)
FURROW = (0.38, 0.28, 0.19)   # ring grooves
BOSS = (0.74, 0.58, 0.40)
MAT = (0.42, 0.40, 0.28)      # olive microbial mat
SAND = (0.66, 0.60, 0.46)


def profile(r, a, seed):
    """Height of the disc surface (in disc radii) and a 0..1 ridge-crest value at normalised
    radius r and angle a."""
    wob = 0.035 * noise.noise(Vector((math.cos(a) * 1.5, math.sin(a) * 1.5, seed)))
    re = r * (1.0 + wob)
    boss = 0.085 * nh.smoothstep(0.16, 0.0, re) ** 0.8                     # central boss
    moat = -0.018 * math.exp(-((re - 0.19) / 0.035) ** 2)                   # groove around it
    dome = 0.07 * (1.0 - re * re)                                           # gently domed pad
    t = nh.smoothstep(0.2, 0.97, re)
    phase = (t ** 0.85) * RINGS                                             # rings widen outward
    ridge = 0.5 - 0.5 * math.cos(phase * math.tau)
    ring = (0.026 - 0.012 * t) * ridge * (re > 0.2)
    rad = 0.5 + 0.5 * math.cos(a * RADIALS + 0.6 * noise.noise(Vector((re * 4, a, seed))))
    radial = -0.012 * rad ** 3 * nh.smoothstep(0.25, 0.5, re)               # faint radial grooves
    edge = nh.smoothstep(0.88, 1.0, re)
    h = (boss + moat + dome + ring + radial) * (1.0 - edge) - 0.01 * edge
    return h, ridge * (re > 0.2), rad


def disc(cx, cy, radius, nr, na, seed):
    """Polar-grid disc: displaced top surface plus a flat, buried underside."""
    bm = bmesh.new()
    vcol = {}
    z0 = mat_height(cx, cy) + 0.004                       # sit on the mat surface
    centre = bm.verts.new((cx, cy, z0 + profile(0.0, 0.0, seed)[0] * radius))
    vcol[centre] = BOSS
    rings = []
    for i in range(1, nr + 1):
        r = (i / nr) ** 0.9
        ring = []
        for k in range(na):
            a = k / na * math.tau
            h, ridge, rad = profile(r, a, seed)
            re = r * (1.0 + 0.03 * noise.noise(Vector((math.cos(a) * 2, math.sin(a) * 2, seed + 4))))
            v = bm.verts.new((cx + math.cos(a) * re * radius, cy + math.sin(a) * re * radius, z0 + h * radius))
            c = nh.lerp(FURROW, DISC, nh.smoothstep(0.0, 0.45, ridge) if r > 0.2 else 1.0)
            c = nh.lerp(c, CREST, nh.smoothstep(0.6, 1.0, ridge) * 0.8)
            c = nh.lerp(c, BOSS, nh.smoothstep(0.2, 0.1, r))
            c = nh.lerp(c, FURROW, 0.18 * rad ** 3 * (r > 0.25))
            c = nh.lerp(c, MAT, nh.smoothstep(0.9, 1.0, r) * 0.5)
            kk = 1.0 + 0.08 * noise.noise(v.co * 14.0)
            vcol[v] = tuple(min(1.0, x * kk) for x in c)
            ring.append(v)
        rings.append(ring)
    for k in range(na):
        bm.faces.new([centre, rings[0][k], rings[0][(k + 1) % na]])
    for a_, b_ in zip(rings, rings[1:]):
        for k in range(na):
            j = (k + 1) % na
            bm.faces.new([a_[k], b_[k], b_[j], a_[j]])
    bottom = []
    for v in rings[-1]:
        b = bm.verts.new((v.co.x, v.co.y, -0.03))
        vcol[b] = MAT
        bottom.append(b)
    for k in range(na):
        j = (k + 1) % na
        bm.faces.new([rings[-1][k], bottom[k], bottom[j], rings[-1][j]])
    bm.faces.new(list(reversed(bottom)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


MAT_C, MAT_R = (0.12, 0.1, -0.02), (1.0, 0.86, 0.035)   # microbial-mat patch ellipsoid


def mat_height(x, y):
    """Top of the (undeformed) mat ellipsoid at (x, y)."""
    d = ((x - MAT_C[0]) / MAT_R[0]) ** 2 + ((y - MAT_C[1]) / MAT_R[1]) ** 2
    return MAT_C[2] + MAT_R[2] * math.sqrt(max(0.0, 1.0 - d))


def seafloor(mb):
    """Low, lumpy microbial-mat patch with 'elephant skin' wrinkles."""
    bm = nh.uv_ellipsoid(MAT_C, MAT_R, 32, 8,
                         deform=lambda n: 1.0 + 0.04 * noise.noise(n * 4.0 + Vector((5.0, 2.0, 9.0))))

    def col(co, n):
        m = noise.noise(co * 5.0) * 0.5 + 0.5
        wrinkle = abs(noise.noise(co * 18.0))
        c = nh.lerp(MAT, SAND, 0.3 + 0.4 * m)
        c = nh.lerp(c, (0.30, 0.30, 0.20), nh.smoothstep(0.08, 0.0, wrinkle) * 0.5)
        return nh.lerp(c, SAND, nh.smoothstep(0.5, 0.8, math.hypot((co.x - 0.12) / 1.0, (co.y - 0.1) / 0.86)))

    mb.add(bm, col)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    seafloor(mb)
    for cx, cy, radius, nr, na in DISCS:
        bm, vcol = disc(cx, cy, radius, nr, na, rng.uniform(0, 50))
        nf.add_colored(mb, bm, vcol)
    obj = mb.to_object("Cyclomedusa", roughness=0.75)
    for v in obj.data.vertices:  # flatten the buried undersides of the mat and discs
        v.co.z = max(v.co.z, -0.012)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Cyclomedusa", ground=(0.55, 0.52, 0.40), background=(0.05, 0.14, 0.18),
           views=((20, 35), (10, 65), (0, 89)))
