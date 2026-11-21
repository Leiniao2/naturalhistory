"""
Procedural dire wolf (Aenocyon dirus, Pleistocene of the Americas) for map
colonies.

A wolf-like dog about as long as a large grey wolf but heavier (60-70 kg), with
a broader head, bigger teeth and stouter legs; DNA shows it was a separate
lineage from true wolves. Thick reddish-tawny coat (the ancient DNA points to a
warm-coloured coat), paler below, with pointed ears and a bushy tail.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/aenocyon_dirus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AenocyonDirus.fbx
"""

import math  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402
import nh_neo_quad as q  # noqa: E402


def nose(mb, L, surf, size=0.022, col=(0.05, 0.04, 0.04)):
    """Dark nose pad at the tip of the muzzle."""
    p, _n = surf.hit(L.h(0.8, 0, 0.02), L.F)
    mb.add(nh.ellipsoid(tuple(p), (size, size * 0.72, size * 0.72), subdivisions=2), col)


SPEC = q.Spec(
    name="AenocyonDirus",
    leg_f=0.48, leg_h=0.50, length=0.66, girth=(0.15, 0.21), belly=0.9,
    hump=0.14, hump_y=-0.40,
    leg_r=(0.055, 0.058), leg_taper=0.62, foot="paw", stride=0.14,
    neck_len=0.17, neck_angle=26, neck_r=(0.15, 0.14),
    head_len=0.29, head_r=(0.12, 0.105), snout_r=(0.036, 0.04), head_pitch=10, cranium=1.2, jaw=1.15,
    eye_t=0.40, eye_u=0.40,
    ears="point", ear_size=0.11, mane=0.045,
    tail_len=0.40, tail_r=0.07, tail_tuft=0.075, tail_droop=0.8,
    coat=(0.62, 0.47, 0.30), dark=(0.36, 0.26, 0.16), pale=(0.86, 0.78, 0.64),
    mane_col=(0.40, 0.29, 0.18),
    pattern=q.combine(q.lower_legs((0.74, 0.60, 0.42), z1=0.6, amount=0.6),
                      q.face((0.82, 0.74, 0.60), t0=0.75, amount=0.5)),
    extra_details=nose,
    shag=0.009, voxel=0.014,
)

if __name__ == "__main__":
    q.main(SPEC)
