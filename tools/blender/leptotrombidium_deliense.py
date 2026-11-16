"""
Procedural scrub-typhus chigger (Leptotrombidium deliense), the six-legged parasitic
larva, for map colonies.

Only the larva feeds on vertebrates (the eight-legged nymphs and adults are free-living
predators in the soil), so this is the larva: a tiny, plump, oval body of bright
orange-red, walking on just three pairs of legs. Near the front of the back sits a small
rectangular scutum, from which rise the two long, branched sensillae; two pairs of dark
red eyes flank it. Rows of stout, feathery (plumose) setae stand up from the back and
along the legs. In front, the gnathosoma is dominated by the stout palps, each ending in
a forked palpal claw, with the curved blades of the chelicerae between them. Faces -Y,
pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/leptotrombidium_deliense.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChiggerMite.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_acari as acari  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BODY = (0.96, 0.30, 0.08)        # bright orange-red
BELLY = (0.72, 0.18, 0.05)
SCUTUM = (0.88, 0.42, 0.16)
EYE = (0.32, 0.02, 0.02)
LEG = (0.97, 0.42, 0.15)
MOUTH = (0.92, 0.40, 0.14)
SETA = (1.0, 0.86, 0.72)


def paint(xn, yn, r, co, n):
    c = acari.glossy(BODY, BELLY, n, 0.3)
    k = 0.93 + 0.12 * noise.noise(co * 35)
    return tuple(min(1.0, x * k) for x in c)


def scutum_paint(xn, yn, t, co, n):
    c = acari.glossy(SCUTUM, nh.lerp(SCUTUM, (0, 0, 0), 0.35), n, 0.4)
    return nh.lerp(c, (0.70, 0.28, 0.10), 0.5) if noise.noise(co * 120) > 0.35 else c


# dorsal setae in transverse rows (yn, count, half-spread), roughly L. deliense's 2-8-6-6-4-2
ROWS = ((-0.30, 2, 0.80), (-0.12, 8, 0.82), (0.12, 6, 0.72), (0.36, 6, 0.62), (0.58, 4, 0.46),
        (0.78, 2, 0.24))

SPEC = acari.Spec(
    name="ChiggerMite", kind="mite",
    length=0.46, width=0.38, height=0.12, belly=0.05, rim=0.02, egg=0.10, hump=0.05, clearance=0.05,
    body_color=BODY, belly_color=BELLY, paint=paint, gloss=0.3,
    scutum=(-0.62, 0.22, 0.42, 0.0), scutum_color=SCUTUM, scutum_paint=scutum_paint, scutum_lift=0.005,
    eyes=(EYE, [(0.58, -0.62), (0.62, -0.44)]),
    basis_len=0.06, basis_w=0.12, basis_h=0.05, hypo_len=0.07, palp_len=0.10, palp_w=0.024,
    palp_flare=0.02, mouth_color=MOUTH, hypo_color=(0.85, 0.50, 0.25),
    leg_y=(-0.52, -0.25, 0.02), leg_angle=(34, 88, 140), leg_len=(0.31, 0.28, 0.33),
    leg_r=0.017, knee=0.07,
    leg_color=LEG, leg_joint=(1.0, 0.55, 0.25), claw_color=(0.45, 0.15, 0.05), leg_setae=1,
    setae=ROWS, seta_len=0.085, seta_r=0.0055, seta_color=SETA, plumose=True,
    extra={"palp_claw": True},
)


def build():
    mb, info = acari.build(SPEC, pose="walk")
    body = info["body"]
    # the two long, branched sensillae rising from the scutum
    for sx in (-1, 1):
        base = body.top_point(sx * 0.16, -0.62, 0.004)
        acari.seta(mb, base, Vector((sx * 0.35, 0.25, 1.0)), 0.20, 0.0045, SETA, plumose=True)
    obj = mb.to_object("ChiggerMite", roughness=0.45)
    zmin = min(v.co.z for v in obj.data.vertices)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    hip = info["hip_z"] - zmin
    print(f"height {max(zs):.3f}, hip {hip:.3f} -> mapHip {hip / max(zs):.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "ChiggerMite", ground=(0.30, 0.26, 0.20), views=((35, 30), (0, 70), (-90, 10)))
