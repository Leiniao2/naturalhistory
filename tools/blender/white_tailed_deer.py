"""
Procedural low-poly white-tailed deer buck (Odocoileus virginianus) for map colonies.

Standing alert on slender legs with small dark hooves, a graceful neck, branching
antlers (main beam curving forward with upward tines), large ears, black nose,
white throat patch, muzzle band and eye ring, a tan/reddish-brown coat with a
white belly, and the tail raised a little so its white underside shows.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/white_tailed_deer.py -- [--render out.png]

Output: Assets/Resources/Models/Species/WhiteTailedDeer.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

COAT = (0.62, 0.40, 0.22)       # tan / reddish-brown
COAT_DARK = (0.46, 0.29, 0.15)  # darker back line
WHITE = (0.95, 0.93, 0.88)
HOOF = (0.10, 0.08, 0.07)
NOSE = (0.05, 0.04, 0.04)
ANTLER = (0.58, 0.47, 0.33)
ANTLER_TIP = (0.78, 0.70, 0.56)
EYE = (0.03, 0.02, 0.02)


def oriented(center, radii, pitch=0.0, yaw=0.0, segments=18, rings=12, deform=None):
    """UV ellipsoid rotated about X (pitch, degrees) then Z (yaw) and moved to center."""
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(pitch), 4, "X")
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def coat(belly=-0.45):
    """Brown coat, darker along the spine, white where the surface faces down."""
    def color(co, n):
        c = nh.lerp(COAT, COAT_DARK, nh.smoothstep(0.55, 0.95, n.z))
        c = nh.lerp(c, COAT, 0.3 * max(0.0, noise.noise(co * 12.0)))
        return nh.lerp(c, WHITE, nh.smoothstep(belly + 0.12, belly - 0.12, n.z))
    return color


def leg_color(hoof_top):
    def color(co, n):
        c = nh.lerp(nh.lerp(WHITE, COAT, 0.4), COAT, nh.smoothstep(0.08, 0.14, co.z))  # pale fetlock above the hoof
        return HOOF if co.z < hoof_top else c
    return color


def build():
    mb = nh.MeshBuilder()

    # Barrel: deeper at the chest, slimmer at the waist, rounded rump
    def body_deform(n):
        k = 1.0 + 0.14 * max(0.0, -n.y) * max(0.0, -n.z + 0.4)  # barrel chest
        k *= 1.0 + 0.08 * max(0.0, n.y) * max(0.0, n.z + 0.5)    # round rump
        k *= 1.0 - 0.06 * (1.0 - abs(n.y)) * max(0.0, -n.z)      # tucked waist
        return k
    mb.add(oriented((0, 0.0, 0.81), (0.18, 0.41, 0.225), pitch=3, segments=22, rings=16, deform=body_deform), coat())

    # Front legs: upper leg tapering to the knee, slender cannon, pastern, small hoof
    for sx in (-1, 1):
        x = sx * 0.09
        pts = [(x * 0.4, -0.24, 0.90), (x * 0.85, -0.25, 0.80), (x, -0.27, 0.68), (x, -0.29, 0.52), (x * 0.95, -0.30, 0.36), (x * 0.95, -0.30, 0.13),
               (x * 0.95, -0.315, 0.06), (x * 0.95, -0.335, 0.0)]
        mb.add(nh.tube(pts, [0.06, 0.08, 0.065, 0.042, 0.028, 0.02, 0.022, 0.021], sides=12), leg_color(0.045))
    # Hind legs: thick thigh to the stifle, back to the hock, slender cannon down to the hoof
    for sx in (-1, 1):
        x = sx * 0.095
        pts = [(x * 0.4, 0.25, 0.92), (x * 0.85, 0.25, 0.82), (x, 0.25, 0.72), (x, 0.22, 0.55), (x * 0.95, 0.36, 0.33), (x * 0.95, 0.34, 0.13),
               (x * 0.95, 0.325, 0.06), (x * 0.95, 0.305, 0.0)]
        mb.add(nh.tube(pts, [0.07, 0.095, 0.085, 0.058, 0.03, 0.02, 0.022, 0.021], sides=12), leg_color(0.045))

    # Neck: rises forward from the chest, thick at the base; white throat patch near the jaw
    def neck_color(co, n):
        c = coat(-0.7)(co, n)
        throat = nh.smoothstep(1.02, 1.08, co.z) * nh.smoothstep(0.0, -0.45, n.y + n.z * 0.3)
        return nh.lerp(c, WHITE, throat)
    mb.add(nh.tube([(0, -0.18, 0.80), (0, -0.28, 0.88), (0, -0.37, 0.98), (0, -0.43, 1.10), (0, -0.46, 1.18)],
                   [0.15, 0.13, 0.092, 0.072, 0.065], sides=16), neck_color)

    # Head: wedge tapering to the muzzle
    def head_color(co, n):
        c = coat(-0.6)(co, n)
        c = nh.lerp(c, WHITE, nh.smoothstep(-0.3, -0.7, n.z))  # white chin/jaw
        return c
    mb.add(oriented((0, -0.50, 1.24), (0.07, 0.09, 0.075), pitch=-22, segments=16, rings=12), head_color)

    def muzzle_color(co, n):
        c = coat(-0.6)(co, n)
        c = nh.lerp(c, COAT_DARK, nh.smoothstep(-0.6, -0.66, co.y) * 0.6)  # darker bridge of the nose
        band = nh.smoothstep(0.018, 0.0, abs(co.y + 0.665))                   # white band behind the nose
        c = nh.lerp(c, WHITE, max(band, nh.smoothstep(-0.25, -0.6, n.z)))
        return NOSE if co.y < -0.69 else c
    snout = nh.tube([(0, -0.47, 1.27), (0, -0.55, 1.235), (0, -0.62, 1.19), (0, -0.68, 1.155), (0, -0.705, 1.14),
                     (0, -0.715, 1.135)],
                    [0.072, 0.064, 0.048, 0.036, 0.03, 0.0], sides=14, scale_xy=(1.0, 1.15))
    mb.add(snout, muzzle_color)

    # Eyes with white rings
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.058, -0.53, 1.265), (0.012, 0.026, 0.021), subdivisions=2), WHITE)
        mb.add(nh.ellipsoid((sx * 0.065, -0.533, 1.265), (0.01, 0.017, 0.015), subdivisions=2), EYE)

    # Large ears, angled out to the sides; pale inside
    def ear_color(co, n):
        inner = nh.smoothstep(0.1, 0.6, -n.y)
        return nh.lerp(COAT, WHITE, inner * 0.8)
    for sx in (-1, 1):
        ear = nh.tube([(sx * 0.05, -0.45, 1.29), (sx * 0.09, -0.445, 1.32), (sx * 0.15, -0.44, 1.355),
                       (sx * 0.21, -0.44, 1.38), (sx * 0.235, -0.44, 1.385)],
                      [0.03, 0.055, 0.055, 0.03, 0.0], sides=10, scale_xy=(0.35, 1.0))
        mb.add(ear, ear_color)

    # Antlers: main beam sweeps back, out and up, then curves forward; tines rise from it
    def antler_color(co, n):
        return nh.lerp(ANTLER, ANTLER_TIP, nh.smoothstep(1.45, 1.62, co.z))
    for sx in (-1, 1):
        beam = [(sx * 0.035, -0.49, 1.30), (sx * 0.07, -0.47, 1.38), (sx * 0.14, -0.45, 1.46),
                (sx * 0.18, -0.50, 1.53), (sx * 0.16, -0.60, 1.57), (sx * 0.10, -0.68, 1.58)]
        mb.add(nh.tube(beam, [0.022, 0.019, 0.017, 0.015, 0.011, 0.0], sides=6), antler_color)
        # brow tine and three main tines
        for base, tip, r in (((sx * 0.06, -0.475, 1.37), (sx * 0.06, -0.52, 1.46), 0.011),
                             ((sx * 0.15, -0.455, 1.47), (sx * 0.15, -0.46, 1.62), 0.012),
                             ((sx * 0.18, -0.52, 1.54), (sx * 0.19, -0.54, 1.68), 0.011),
                             ((sx * 0.15, -0.61, 1.565), (sx * 0.15, -0.64, 1.67), 0.009)):
            mid = tuple((a + b) / 2 for a, b in zip(base, tip))
            mb.add(nh.tube([base, mid, tip], [r, r * 0.75, 0.0], sides=6), antler_color)

    # Tail: raised a little and flared; white underside ("flag"), brown on top
    def tail_color(co, n):
        top = nh.smoothstep(0.55, 0.85, n.z - n.y * 0.6) * nh.smoothstep(0.06, 0.02, abs(co.x))
        return nh.lerp(WHITE, COAT_DARK, top)
    mb.add(nh.tube([(0, 0.38, 0.88), (0, 0.44, 0.93), (0, 0.50, 1.0), (0, 0.53, 1.05), (0, 0.54, 1.07)],
                   [0.04, 0.062, 0.058, 0.035, 0.0], sides=12, scale_xy=(1.0, 0.5)), tail_color)
    # white rump patch around the tail base
    mb.add(oriented((0, 0.385, 0.84), (0.06, 0.03, 0.07), segments=12, rings=8), WHITE)

    obj = mb.to_object("WhiteTailedDeer")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "WhiteTailedDeer", ground=(0.38, 0.48, 0.26), views=((35, 25), (-90, 8), (20, 65)))
