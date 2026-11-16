"""
Procedural leafcutter ant worker (Atta cephalotes) carrying a leaf piece, for map colonies.

A rusty reddish-brown, matte media worker on long legs: a broad heart-shaped head
(deeply notched behind, with a pair of occipital spines on the back lobes), small
eyes and strong toothed mandibles; long 11-segmented elbowed antennae; a spiny
mesosoma with three pairs of spines (pronotal, mesonotal and propodeal); a
two-segmented waist; and a small gaster with no visible sting. In its mandibles
it holds a freshly cut, half-moon leaf fragment upright like a sail, leaning back
over its head and thorax, with a pale midrib and side veins.
Built with tools/blender/nh_ant.py.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/atta_cephalotes.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LeafcutterAnt.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ant  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

RUST = (0.50, 0.20, 0.07)
RUST_DARK = (0.40, 0.15, 0.055)
LEG = (0.54, 0.24, 0.09)
LEAF = (0.25, 0.56, 0.12)
LEAF_LIGHT = (0.42, 0.70, 0.20)
LEAF_VEIN = (0.58, 0.74, 0.32)

PARAMS = dict(
    base=0.15,
    head_w=0.160, head_l=0.135, head_h=0.090, head_pitch=-10.0, head_z=0.105, neck=1.02,
    head_heart=1.5, head_lobes=0.9, occipital_spines=0.055,
    eye_r=0.020, eye_y=-0.30, mandible=1.30, mandible_teeth=6,
    scape=0.26, funiculus=0.34, fun_segs=10, club_segs=0, ant_r=0.010,
    meso_len=0.38, meso_h=0.120, meso_w=0.85, groove=0.30,
    spines=((0.18, 0.075, (0.85, -0.35, 0.45)),     # pronotal: out and forward
            (0.44, 0.060, (0.35, 0.05, 1.0)),       # mesonotal: up
            (0.86, 0.075, (0.30, 0.65, 0.75))),     # propodeal: up and back
    waist="two", pet_h=0.048, pet_w=0.030, post_w=0.050,
    gaster_l=0.145, gaster_w=0.112, gaster_h=0.095, gaster_bands=0,
    sting=False,
    legs=1.35, knee_rise=0.12, leg_r=0.012,
    head_col=RUST, meso_col=RUST, waist_col=RUST, gaster_col=RUST_DARK,
    leg_col=LEG, antenna_col=LEG, mandible_col=(0.30, 0.11, 0.04),
    gloss=0.22,
)

LEAF_R = 0.34          # radius of the half-moon fragment
LEAF_TILT = 68.0       # held straight edge: raised high, leaning back
LEAF_SPREAD = 10.0     # the curved cut bulges back and up over the head and thorax
LEAF_ROLL = -25.0      # leaned to one side so the map camera (looking down) sees its face


def build_leaf(ant):
    """Half-moon leaf fragment gripped by its edge between the mandible tips."""
    a, b = ant.mandible_tips
    grip = a.lerp(b, 0.5) + Vector((0.0, -0.01, 0.0))
    t = math.radians(LEAF_TILT)
    roll = Matrix.Rotation(math.radians(LEAF_ROLL), 3, "Y")
    sp = math.radians(LEAF_SPREAD)
    C = roll @ Vector((0.0, math.cos(t), math.sin(t)))    # along the held edge: up
    P = roll @ Vector((0.0, math.cos(sp), math.sin(sp)))  # across: back and up over the body
    X = C.cross(P).normalized()
    m = Matrix((
        (C.x, P.x, X.x, grip.x),
        (C.y, P.y, X.y, grip.y),
        (C.z, P.z, X.z, grip.z),
        (0, 0, 0, 1),
    ))
    n = 22
    outline = []
    for k in range(n + 1):
        ang = math.pi * k / n
        u = LEAF_R * (1 - math.cos(ang))
        v = LEAF_R * 0.92 * math.sin(ang) * (1.0 + 0.04 * noise.noise(Vector((ang * 3, 0.5, 0.2))))
        outline.append((u, v, 0.03 * (v / LEAF_R) ** 2))   # gently curled
    # the straight original leaf margin, finely toothed
    for k in range(1, 8):
        u = 2 * LEAF_R * (1 - k / 8)
        outline.append((u, -0.006 * (k % 2), 0.0))
    leaf = nh.flat_panel(outline, 0.008)
    nh.transform(leaf, m)

    def leaf_col(co, nrm):
        q = co - grip
        f = noise.noise(q * 14.0) * 0.5 + 0.5
        c = nh.lerp(LEAF, LEAF_LIGHT, f * 0.45 + max(0.0, nrm.dot(nh_ant.LIGHT_DIR)) * 0.25)
        return c
    ant.mb.add(leaf, leaf_col, smooth=False)
    # midrib-like vein across the piece and two side veins, on both faces
    for side in (-1, 1):
        off = X * side * 0.0045
        for p0, p1 in (((0.15, 0.02), (1.70, 0.05)), ((0.55, 0.03), (0.85, 0.70)), ((1.10, 0.04), (1.45, 0.60))):
            pts = [m @ Vector((LEAF_R * p0[0], LEAF_R * p0[1], 0)) + off,
                   m @ Vector((LEAF_R * p1[0], LEAF_R * p1[1], 0.03 * p1[1] ** 2)) + off]
            ant.mb.add(nh.tube(pts, [0.0045, 0.002], sides=4), LEAF_VEIN)


if __name__ == "__main__":
    nh_ant.run(PARAMS, "LeafcutterAnt", extra=build_leaf, roughness=0.6)
