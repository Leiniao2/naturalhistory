"""
Procedural Palaeocoma egertoni (Early Jurassic brittle star, England) for map colonies.

A brittle star about 10-15 cm across whose fossils cover whole slabs of the "Starfish Bed"
of Yorkshire and Dorset, where storms buried crowds of them alive: a rounded, flattened
central disc with paired pale radial shields at the base of each arm, and five long,
slender, jointed arms fringed with short spines, used to row across the sea floor in
snake-like curves while picking up food particles. Painted buff with darker arm joints.
Built like furcaster_palaeozoicus.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/palaeocoma_egertoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Palaeocoma.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

NAME = "Palaeocoma"

DISC = (0.74, 0.62, 0.42)
DISC_DARK = (0.46, 0.34, 0.20)
ARM = (0.66, 0.52, 0.34)
JOINT = (0.42, 0.30, 0.18)
SPINE = (0.94, 0.88, 0.74)

R = 0.85          # arm reach from the centre
R_DISC = 0.17
ARM_W = 0.034
Z0 = 0.0

# per-arm sinuous bend (amplitude, phase) so the star looks caught mid-crawl
BENDS = [(-0.45, 0.6), (0.5, 1.8), (-0.3, 2.4), (0.65, 0.1), (-0.55, 1.4)]


def arm_path(a0, amp, ph, n=28):
    pts, dirs = [], []
    p = Vector((math.cos(a0), math.sin(a0), 0)) * R_DISC * 0.6
    ang = a0
    step = (R - R_DISC * 0.6) / (n - 1) * 1.08
    for i in range(n):
        t = i / (n - 1)
        pts.append(p.copy())
        dirs.append(Vector((math.cos(ang), math.sin(ang), 0)))
        ang = a0 + amp * math.sin(t * 3.4 + ph) * t
        p = p + Vector((math.cos(ang), math.sin(ang), 0)) * step
    return pts, dirs


def build():
    mb = nh.MeshBuilder()
    # disc: low, slightly pentagonal dome
    h = 0.05
    mb.add(nh.ellipsoid((0, 0, Z0 + h * 0.55), (R_DISC, R_DISC, h), subdivisions=3,
                        deform=lambda v: 1.0 + 0.08 * math.cos(5 * math.atan2(v.y, v.x) + math.pi / 2) * (1 - abs(v.z))),
           lambda co, n: nh.lerp(DISC, DISC_DARK, 0.5 * nh.smoothstep(-0.2, 0.6, noise.noise(co * 40))
                                 + 0.3 * nh.smoothstep(0.03, 0.0, Vector((co.x, co.y)).length)))
    for k in range(5):
        a = k / 5 * math.tau - math.pi / 2 + math.pi / 5
        for da in (-0.17, 0.17):
            c = Vector((math.cos(a + da), math.sin(a + da), 0)) * R_DISC * 0.68 + Vector((0, 0, Z0 + h * 0.85))
            mb.add(nh.ellipsoid(c, (0.035, 0.035, 0.012), subdivisions=2), SPINE)
    for k in range(5):
        a0 = k / 5 * math.tau - math.pi / 2 + math.pi / 5  # no arm pointing straight forward
        amp, ph = BENDS[k]
        pts, dirs = arm_path(a0, amp, ph)
        n = len(pts)
        radii = []
        for i in range(n):
            t = i / (n - 1)
            radii.append(ARM_W * (1.0 - 0.85 * t) + 0.004)
        centre = [p + Vector((0, 0, Z0 + r * 0.65 + 0.025 * nh.smoothstep(0.75, 1.0, i / (n - 1))))
                  for i, (p, r) in enumerate(zip(pts, radii))]
        radii[-1] = 0.0
        L = [0.0]
        for i in range(1, n):
            L.append(L[-1] + (centre[i] - centre[i - 1]).length)

        def arm_col(co, nrm, centre=centre, L=L):
            j = min(range(len(centre)), key=lambda q: (centre[q] - co).length_squared)
            s = L[j] / 0.035
            joint = 1.0 - nh.smoothstep(0.08, 0.22, abs(s - round(s)))
            return nh.lerp(ARM, JOINT, 0.75 * joint)

        mb.add(nh.tube(centre, radii, sides=8, scale_xy=(1.0, 0.7)), arm_col)
        # short spines along both sides of the arm
        for i in range(1, n - 2):
            d = (centre[i + 1] - centre[i - 1]).normalized()
            side = Vector((-d.y, d.x, 0)).normalized()
            r = radii[i]
            for sg in (-1, 1):
                b = centre[i] + side * sg * r * 0.85
                tip = b + (side * sg * 0.8 + d * 0.5 + Vector((0, 0, 0.25))).normalized() * (r * 1.3 + 0.02)
                mb.add(nh.tube([b, tip], [0.006 * (1 - i / n) + 0.003, 0.0], sides=4), SPINE)
    obj = mb.to_object(NAME, roughness=0.55)
    vs = obj.data.vertices
    xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj

if __name__ == "__main__":
    nh.run(build, NAME, background=(0.05, 0.15, 0.18),
           views=((30, 30), (0, 80), (-90, 8)))
