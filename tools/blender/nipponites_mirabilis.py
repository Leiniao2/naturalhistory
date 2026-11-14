"""
Procedural Nipponites mirabilis (Late Cretaceous heteromorph ammonite) for map
colonies.

The "knotted" shell is one finely ribbed tube swept along a parametric
centreline: a small, open planispiral core (the crioconic juvenile whorls),
then a long meander that wraps around it, sweeping up and down over a ball
while slowly precessing around the vertical axis, so the shell doubles back
on itself in a chain of U-bends. Ivory with fine rib lines and rusty bands.
The animal sits in the final aperture, at the bottom of the ball, facing -Y.
Pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/nipponites_mirabilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/NipponitesMirabilis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

IVORY = (0.88, 0.82, 0.68)
RIB_DARK = (0.60, 0.47, 0.33)
RUST = (0.62, 0.34, 0.17)

SIDES = 8
CORE_TURNS = 2.0
CORE_R0, CORE_R1 = 0.04, 0.28   # open planispiral, radius per turn grows faster than the tube
BALL_R0, BALL_R1 = 0.38, 0.56   # meander distance from the centre
HALF_ARMS = 7.5                 # ends half-way through an arm, at the apex of a bottom bend
LAT = math.radians(50)          # how far the arms swing toward the poles
ARM_STEP = 0.62                 # azimuth advance per arm (radians)
TUBE_R0, TUBE_R1 = 0.012, 0.092
TILT = math.radians(55)         # the meander's axis rolls over as it grows, so later bends cross earlier ones


def centreline(n=4000):
    """Dense points along the whole shell, juvenile end first."""
    pts = []
    for i in range(n // 4):
        t = i / (n // 4)
        th = t * CORE_TURNS * math.tau
        rho = CORE_R0 + (CORE_R1 - CORE_R0) * t
        pts.append(Vector((rho * math.cos(th), 0.0, rho * math.sin(th))))
    span = HALF_ARMS * math.pi
    for i in range(n):
        t = i / (n - 1)
        ph = t * span
        # move out from the core onto the ball within the first eighth of an arm
        rho = nh.lerp((CORE_R1,), (BALL_R0,), nh.smoothstep(0.0, math.pi / 4, ph))[0]
        rho += (BALL_R1 - BALL_R0) * t
        amp = LAT * (1.0 + 0.1 * math.sin(0.7 * ph + 1.0))      # a little irregular, like the real thing
        lat = amp * math.sin(ph)
        lon = ARM_STEP * ph / math.pi + 0.08 * math.sin(1.3 * ph)
        p = Vector((rho * math.cos(lat) * math.cos(lon),
                    rho * math.cos(lat) * math.sin(lon),
                    rho * math.sin(lat)))
        pts.append(Matrix.Rotation(TILT * nh.smoothstep(0.15, 1.0, t), 3, "X") @ p)
    return pts


def resample(pts):
    """Rings spaced by the local tube radius: [(point, tangent, radius, index)]."""
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + (b - a).length)
    total = cum[-1]
    out, s, j = [], 0.0, 0
    while s < total:
        while cum[j + 1] < s:
            j += 1
        f = (s - cum[j]) / max(cum[j + 1] - cum[j], 1e-9)
        p = pts[j].lerp(pts[j + 1], f)
        tan = (pts[j + 1] - pts[j]).normalized()
        r = TUBE_R0 + (TUBE_R1 - TUBE_R0) * (s / total) ** 0.85
        out.append((p, tan, r, s / total))
        s += 0.011 + 0.33 * r
    p, tan = pts[-1], (pts[-1] - pts[-2]).normalized()
    out.append((p, tan, TUBE_R1, 1.0))
    return out


def shell():
    samples = resample(centreline())
    rings, colors = [], []
    side = None
    for i, (p, tan, r, w) in enumerate(samples):
        if side is None:
            side = tan.cross(Vector((0, 0, 1))).normalized()
        side = (side - tan * side.dot(tan)).normalized()   # parallel transport, no twist
        up = side.cross(tan)
        rib = i % 2 == 0 and w < 0.985
        k = (1.05 if rib else 1.0) * (1.0 + 0.08 * nh.smoothstep(0.988, 1.0, w))
        band = nh.smoothstep(0.6, 0.95, math.sin(w * 70.0))
        base = nh.lerp(IVORY, RUST, 0.55 * band)
        ring, cols = [], []
        for kk in range(SIDES):
            a = kk / SIDES * math.tau
            ring.append(p + (side * math.cos(a) + up * math.sin(a)) * r * k)
            cols.append(base if rib else nh.lerp(base, RIB_DARK, 0.35))
        rings.append(ring)
        colors.append(cols)
    end_p, end_t, end_r, _ = samples[-1]
    return am.grid_mesh(rings, colors), end_p, end_t, end_r


def build():
    mb = nh.MeshBuilder()
    bm, ap, tan, r = shell()
    mb.add(bm, None)
    am.soft_body(mb, ap, tan, -ap.normalized(), r * 0.9, arm_len=2.0, droop=0.5)
    obj = mb.to_object("NipponitesMirabilis", roughness=0.45)
    # turn the aperture's heading to -Y, then centre the bounds on the pivot
    heading = math.atan2(tan.y, tan.x)
    rot = Matrix.Rotation(-math.pi / 2 - heading, 4, "Z")
    for v in obj.data.vertices:
        v.co = rot @ v.co
    lo = Vector([min(v.co[a] for v in obj.data.vertices) for a in range(3)])
    hi = Vector([max(v.co[a] for v in obj.data.vertices) for a in range(3)])
    centre = (lo + hi) / 2
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "NipponitesMirabilis", views=((35, 20), (-90, 5), (0, 10), (30, 50)))
