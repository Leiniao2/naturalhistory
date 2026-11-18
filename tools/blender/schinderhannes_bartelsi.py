"""
Procedural Schinderhannes bartelsi for the map: a radiodont from the Early Devonian
(Emsian, about 400 million years ago) Hunsrück Slate of Germany, about 10 cm long - a
late survivor of the group of Anomalocaris, some 100 million years after its Cambrian
relatives.

A big head with large, bulging eyes on short stalks and a round, plated mouth
underneath; a pair of large grasping frontal appendages, each segment carrying a long,
inward-pointing spine, held curled under the front of the head; a short, segmented
trunk with a single pair of big, wing-like triangular swimming flaps just behind the
head (unlike the rows of flaps of Cambrian radiodonts); and a long, thin tail spine.

Built with nh_edicam.py helpers (as amplectobelua_symbrachiata.py). Colours are
unknown: dusky grey-violet with paler flap edges. Faces -Y, pivot at the body centre
(Swim).

Usage:
  blender --background --python tools/blender/schinderhannes_bartelsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Schinderhannes.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Schinderhannes"

BODY = (0.40, 0.36, 0.42)
BODY_DARK = (0.22, 0.19, 0.24)
BELLY = (0.70, 0.64, 0.66)
HEAD = (0.46, 0.40, 0.46)
FLAP = (0.48, 0.42, 0.48)
FLAP_EDGE = (0.82, 0.76, 0.74)
APP = (0.62, 0.46, 0.36)
SPINE = (0.92, 0.84, 0.70)
MOUTH = (0.80, 0.70, 0.60)
EYE = (0.04, 0.03, 0.04)
EYE_SHINE = (0.50, 0.48, 0.50)

Y_HEAD = -0.36          # head centre
Y0, Y1, SEG = -0.16, 0.30, 11   # trunk


def width(t):
    return 0.10 * (1 - 0.65 * t ** 1.1) + 0.01


def wing(sx):
    """Big triangular flap: broad root along the first trunk segment, tip swept out and back."""
    root_a = Vector((sx * 0.07, Y0 - 0.06, 0.0))
    root_b = Vector((sx * 0.07, Y0 + 0.14, 0.0))
    tip = Vector((sx * 0.62, Y0 + 0.24, -0.02))
    lead = Vector((sx * 0.36, Y0 - 0.02, 0.0))   # convex leading edge
    trail = Vector((sx * 0.30, Y0 + 0.22, -0.01))
    outline = [root_a, lead, tip, trail, root_b]
    bm = nh.flat_panel([tuple(p) for p in outline], thickness=0.012)
    if sx < 0:
        import bmesh
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return bm


def flap_color(co, n):
    r = abs(co.x)
    c = nh.lerp(FLAP, FLAP_EDGE, nh.smoothstep(0.30, 0.58, r))
    # faint radiating veins (strengthening rays)
    a = math.atan2(co.y - (Y0 + 0.04), r - 0.07)
    c = nh.lerp(c, BODY_DARK, 0.35 * (1 - nh.smoothstep(0.0, 0.35, abs(math.sin(a * 9.0)))) * nh.smoothstep(0.1, 0.2, r))
    return c


def appendage(mb, sx):
    """Frontal appendage: reaches forward from under the head then curls down and back,
    each podomere with a long spine pointing inward/backward (toward the mouth)."""
    ctrl = [(0.05, -0.47, -0.05), (0.07, -0.58, -0.02), (0.09, -0.70, -0.03), (0.10, -0.79, -0.08),
            (0.09, -0.82, -0.15), (0.07, -0.78, -0.21), (0.05, -0.70, -0.24), (0.03, -0.62, -0.23),
            (0.02, -0.56, -0.19)]
    pts = [Vector((sx * x, y, z)) for x, y, z in ctrl]
    n = len(pts)
    radii = [0.032 * (1 - 0.55 * i / (n - 1)) for i in range(n)]
    radii[-1] = 0.006
    mb.add(nh.tube(pts, radii, sides=7), APP)
    for i in range(1, n - 1):
        p = pts[i]
        mb.add(nh.ellipsoid(p, (radii[i] * 1.12,) * 3, subdivisions=1), BODY_DARK)
        d = (pts[i + 1] - pts[i - 1]).normalized()
        # spine perpendicular to the appendage, toward the inside of the curl, angled inward
        to_centre = (Vector((sx * 0.06, -0.70, -0.13)) - p)
        sp_dir = (to_centre - d * to_centre.dot(d)).normalized()
        sp_dir.x -= sx * 0.35
        L = 0.06 + 0.05 * math.sin(math.pi * i / (n - 1))
        mb.add(ec.spike(p, p + sp_dir.normalized() * L, r=radii[i] * 0.35, sides=4), SPINE, smooth=False)


def build():
    mb = nh.MeshBuilder()
    # trunk: short, segmented, tapering into the tail spine
    mb.add(ec.segmented_trunk(Y0 - 0.04, Y1, SEG, width, flat=0.6, sides=12, tip=0.012),
           ec.banded(BODY, BODY_DARK, BELLY, Y0 - 0.04, (Y1 - Y0 + 0.04) / SEG, amount=0.6))
    # long thin tail spine
    mb.add(nh.tube([(0, Y1 - 0.02, 0.0), (0, Y1 + 0.20, 0.01), (0, Y1 + 0.42, 0.02), (0, Y1 + 0.58, 0.03)],
                   [0.016, 0.011, 0.006, 0.0], sides=6), BODY_DARK)
    # head: big rounded capsule with a dorsal sclerite
    mb.add(nh.uv_ellipsoid((0, Y_HEAD, 0.0), (0.15, 0.20, 0.11), segments=18, rings=10),
           lambda co, n: nh.lerp(BELLY, HEAD, nh.smoothstep(-0.5, 0.2, n.z)))
    mb.add(nh.uv_ellipsoid((0, Y_HEAD - 0.02, 0.07), (0.10, 0.15, 0.05), segments=14, rings=6),
           lambda co, n: nh.lerp(BODY_DARK, HEAD, nh.smoothstep(0.5, 0.95, n.z)))
    # round mouth under the head: a ring of plates
    mc = Vector((0, Y_HEAD - 0.06, -0.105))
    for k in range(12):
        a = k / 12 * math.tau
        p = mc + Vector((math.cos(a) * 0.045, math.sin(a) * 0.045, 0))
        mb.add(nh.ellipsoid(p, (0.018, 0.018, 0.010), subdivisions=1), MOUTH)
    mb.add(nh.ellipsoid(mc + Vector((0, 0, -0.003)), (0.022, 0.022, 0.006), subdivisions=1), EYE)
    for sx in (-1, 1):
        mb.add(wing(sx), flap_color, smooth=False)
        # small ventral flaps along the trunk (low, so the single big pair dominates)
        for i in range(3, SEG - 1):
            t = i / SEG
            y = Y0 + (Y1 - Y0) * t
            w = width(t)
            f = ec.paddle(0.05 + 0.04 * (1 - t), 0.018, n=8, taper=0.6, thickness=0.006)
            ec.mirror(f, sx)
            nh.transform(f, nh.Matrix.Translation((sx * w * 0.8, y, -0.03)))
            mb.add(f, FLAP, smooth=False)
        appendage(mb, sx)
        # big bulging eyes on short stalks at the front corners of the head
        e0 = Vector((sx * 0.10, Y_HEAD - 0.10, 0.04))
        e1 = e0 + Vector((sx * 0.05, -0.04, 0.03))
        mb.add(nh.tube([e0, e1], [0.03, 0.026], sides=8), HEAD)
        mb.add(nh.uv_ellipsoid(tuple(e1 + Vector((sx * 0.03, -0.01, 0.01))), (0.055, 0.06, 0.05), 12, 8),
               lambda co, n: nh.lerp(EYE, EYE_SHINE, 0.7 * max(0.0, n.dot(Vector((-0.3, -0.4, 0.86)))) ** 8))
    return ec.centre(mb.to_object(NAME, roughness=0.45))


if __name__ == "__main__":
    ec.export(build, NAME)
