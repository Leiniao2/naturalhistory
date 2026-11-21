"""
Procedural Phragmoceras ventricosum (a Silurian nautiloid, shell about 12-15 cm long,
from the Wenlock-Ludlow of Britain, Gotland and Bohemia) for map colonies.

A short, fat, curved shell (a breviconic cyrtocone), flattened from side to side: it
widens fast from a pointed, curved-down apex to a swollen ("ventricose") body chamber,
then narrows again at the mouth, which was pinched into a narrow slit with a rounded
opening at one end for the funnel - so only the tips of the arms could reach out.
Cream shell with brown growth bands, faint septal lines on the chambered part, short
arms and eyes at the aperture. Floated head-down near the sea floor.
Faces -Y (aperture), pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/phragmoceras_ventricosum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PhragmocerasVentricosum.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

NAME = "PhragmocerasVentricosum"
CREAM = (0.86, 0.78, 0.62)
BAND = (0.46, 0.28, 0.16)
SUTURE = (0.30, 0.20, 0.12)
FLESH = (0.58, 0.36, 0.30)
FLESH_LIGHT = (0.84, 0.66, 0.56)
SLIT = (0.10, 0.06, 0.05)


def centreline():
    """Aperture at y = 0, going back (+Y) and curving downward (-Z) to the apex."""
    pts = []
    n = 44
    for i in range(n + 1):
        t = i / n
        a = t * math.radians(110)
        R = 0.62
        pts.append((Vector((0, R * math.sin(a), -R * (1 - math.cos(a)))), t))
    return pts


def radius(t):
    # constricted aperture, swollen body chamber, fast taper to the apex
    if t < 0.08:
        return 0.15 + 0.08 * nh.smoothstep(0.0, 0.08, t)
    return 0.23 * (1.0 - nh.smoothstep(0.15, 1.0, t)) ** 0.85 + 0.003


def build():
    mb = nh.MeshBuilder()
    cl = centreline()
    pts = [p for p, _ in cl]
    radii = [radius(t) for _, t in cl]
    radii[-1] = 0.0

    def col(co, n):
        k = min(range(len(pts)), key=lambda i: (pts[i] - co).length)
        t = cl[k][1]
        c = nh.lerp(CREAM, BAND, 0.7 * nh.smoothstep(0.4, 0.9, math.sin(t * 46.0 + co.x * 4)))
        if t > 0.40 and math.sin(t * 90.0) > 0.93:
            c = nh.lerp(c, SUTURE, 0.6)
        return nh.lerp(c, (0.96, 0.92, 0.84), 0.35 * nh.smoothstep(0.0, -0.9, n.z))

    # laterally compressed: thinner in x than in z
    mb.add(nh.tube(pts, radii, sides=18, cap_start=False, scale_xy=(0.68, 1.0)), col)
    # constricted aperture: a cap with a long vertical slit and a round funnel opening below
    mb.add(nh.ellipsoid((0, 0.004, 0), (0.15 * 0.68, 0.02, 0.15), subdivisions=3), CREAM)
    mb.add(nh.ellipsoid((0, -0.012, 0.02), (0.016, 0.012, 0.10), subdivisions=2), SLIT)
    mb.add(nh.ellipsoid((0, -0.012, -0.09), (0.035, 0.012, 0.035), subdivisions=2), SLIT)
    oc.soft_body(mb, -0.02, 0.08, FLESH, FLESH_LIGHT, arms=8, arm_len=1.4, arm_r=0.10, eye_r=0.25,
                 spot=(0.40, 0.22, 0.18))
    obj = mb.to_object(NAME, roughness=0.45)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 25), (-90, 8), (0, 85)))
