"""
Procedural tropical rat mite (Ornithonyssus bacoti), an adult female after a partial
blood meal, for map colonies.

A tiny, oval, convex mite standing high on eight long, slender legs, the first pair
held up and forward as feelers the way mesostigmatid mites walk. Its soft body is a
translucent greyish-white, with the dark red-black blood meal showing through the
middle of the back; a long, narrow dorsal shield, paler tan, covers most of the dorsum
and tapers towards the rear. Rows of fine pale setae bristle over the back and along
the legs (it is a hairy mite). In front, a small gnathosoma carries a pair of long,
slender chelicerae (blood-feeding stylets) between two short, leg-like palps. Pale
legs with paired claws. Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/ornithonyssus_bacoti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TropicalRatMite.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_acari as acari  # noqa: E402
from mathutils import noise  # noqa: E402

BODY = (0.84, 0.82, 0.77)        # translucent greyish-white
BELLY = (0.66, 0.63, 0.58)
SHIELD = (0.86, 0.78, 0.62)
GUT = (0.32, 0.03, 0.03)        # blood meal seen through the cuticle
LEG = (0.80, 0.73, 0.60)
MOUTH = (0.74, 0.64, 0.50)
SETA = (0.93, 0.91, 0.86)


def gut(xn, yn):
    """0..1 density of the lobed blood-filled gut (midgut with lateral caeca)."""
    a = math.atan2(xn, yn - 0.1)
    lobes = 1.0 + 0.25 * math.cos(a * 4)
    d = math.hypot(xn / 0.78, (yn - 0.12) / 0.72) / lobes
    return nh.smoothstep(1.0, 0.65, d)


def paint(xn, yn, r, co, n):
    c = acari.glossy(BODY, BELLY, n, 0.4)
    g = gut(xn, yn) * (n.z > -0.2) * (0.8 + 0.2 * noise.noise(co * 30))
    return nh.lerp(c, GUT, 0.85 * g)


def shield_paint(xn, yn, t, co, n):
    c = acari.glossy(SHIELD, nh.lerp(SHIELD, (0, 0, 0), 0.35), n, 0.5)
    return nh.lerp(c, GUT, 0.7 * gut(xn, yn))


ROWS = ((-0.72, 4, 0.40), (-0.50, 6, 0.70), (-0.25, 6, 0.80), (0.0, 6, 0.85), (0.25, 6, 0.80),
        (0.50, 6, 0.70), (0.74, 4, 0.45), (0.92, 2, 0.20))

SPEC = acari.Spec(
    name="TropicalRatMite", kind="mite",
    length=0.50, width=0.31, height=0.10, belly=0.04, rim=0.02, egg=0.06, hump=0.05, clearance=0.075,
    body_color=BODY, belly_color=BELLY, paint=paint, gloss=0.4,
    scutum=(-0.08, 0.84, 0.52, 0.35), scutum_color=SHIELD, scutum_paint=shield_paint, scutum_lift=0.004,
    basis_len=0.045, basis_w=0.075, basis_h=0.035, hypo_len=0.08, palp_len=0.085, palp_w=0.011,
    palp_flare=0.012, mouth_color=MOUTH, hypo_color=(0.68, 0.56, 0.44),
    leg_y=(-0.66, -0.42, -0.15, 0.12), leg_angle=(24, 62, 112, 150), leg_len=(0.50, 0.38, 0.38, 0.46),
    leg_r=0.0105, knee=0.11, leg1_raised=0.10,
    leg_color=LEG, leg_joint=(0.88, 0.82, 0.70), claw_color=(0.45, 0.35, 0.25), leg_setae=1,
    setae=ROWS, seta_len=0.065, seta_r=0.0035, seta_color=SETA,
)


def build():
    mb, info = acari.build(SPEC, pose="walk")
    obj = mb.to_object("TropicalRatMite", roughness=0.4)
    zmin = min(v.co.z for v in obj.data.vertices)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    hip = info["hip_z"] - zmin
    print(f"height {max(zs):.3f}, hip {hip:.3f} -> mapHip {hip / max(zs):.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "TropicalRatMite", ground=(0.30, 0.26, 0.20), views=((35, 30), (0, 70), (-90, 10)))
