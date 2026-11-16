"""
Procedural Endoceras giganteum (Late Ordovician endocerid nautiloid) for map colonies.

The longest shelled cephalopod known from the fossil record: an incomplete conch from
the Late Ordovician of New York (Museum of Comparative Zoology, Harvard) is about 3 m
long as preserved and has been reconstructed at roughly 5.7 m (Teichert & Kummel 1960,
whose own first estimate of over 8 m was too high; a second-hand 9 m report from Flower
1955 is unverified).

How it differs from the Cameroceras model:
  * a longer, slimmer, more evenly tapering conch (almost no swelling) whose cross
    section is slightly depressed (wider than high), as in the genus diagnosis;
  * low, closely spaced transverse annulations (Endoceras conchs are annulated, from
    low and close to well raised), fading towards the aperture;
  * a large siphuncle hugging the ventral margin (dark line on the belly);
  * a "cancellated" colour pattern - a grid of dark transverse and longitudinal lines,
    as preserved in Endoceras proteiforme - in warm chestnut over cream, instead of
    Cameroceras's olive flame stripes. Real colours are unknown;
  * soft body after modern reconstructions (Incertae Sedis): no Nautilus-like hood,
    ten roughly equal arms, big simple eyes and the funnel underneath.

Usage:
  blender --background --python tools/blender/endoceras_giganteum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Endoceras.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

CREAM = (0.88, 0.80, 0.64)
BELLY = (0.93, 0.89, 0.78)
CHESTNUT = (0.46, 0.22, 0.12)
FADED = (0.78, 0.74, 0.64)
ENCRUST = (0.88, 0.86, 0.78)
SUTURE = (0.50, 0.38, 0.26)
FLESH = (0.58, 0.30, 0.22)
FLESH_LIGHT = (0.86, 0.64, 0.50)

LENGTH = 1.95
R_AP = 0.115
R_APEX = 0.028
BODY = 0.30          # body chamber ~30% of the length (the assumption behind the 5.7 m estimate)
ANNULI = 30          # annulations along the conch (spacing grows with the shell's diameter)
DEPRESS = 0.90       # height / width of the cross section


def annulus(s):
    """0..1 crest profile of the annulations (rounded crests, wide troughs)."""
    r = R_AP + (R_APEX - R_AP) * min(1.0, s)
    phase = ANNULI * math.log(r / R_AP) / math.log(R_APEX / R_AP)
    return 0.5 + 0.5 * math.cos(phase * math.tau)


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.7, 0.5, math.sin(a))
    col = nh.lerp(BELLY, CREAM, dorsal)
    # cancellated pattern: longitudinal lines crossed by transverse lines on the crests
    lon = nh.smoothstep(0.45, 0.85, math.cos(a * 8.0 + 0.3 * math.sin(s * 30.0)))
    tra = nh.smoothstep(0.75, 0.98, annulus(s))
    grid = max(lon, tra * 0.6)
    col = nh.lerp(col, CHESTNUT, grid * (0.2 + 0.6 * dorsal) * (0.85 - 0.4 * s))
    col = tuple(x * (1.03 if info["ridge"] else 0.95) for x in col)
    col = nh.lerp(col, SUTURE, info["suture"] * 0.3)
    # the old apical end: faded, with pale encrusting patches
    old = nh.smoothstep(0.6, 0.97, s)
    col = nh.lerp(col, FADED, old * 0.5)
    p = Vector((math.cos(a) * 2.0, s * 10.0, math.sin(a) * 2.0))
    col = nh.lerp(col, ENCRUST, nh.smoothstep(0.28, 0.48, noise.noise(p)) * old * 0.8)
    return tuple(min(1.0, x) for x in col)


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=300, sides=30, body_frac=BODY,
                     septum_spacing=0.5, siphuncle=-math.pi / 2, sinus=0.25,
                     growth=0.004, bulge=0.02)
    # low annulations (fading towards the aperture) and a slightly depressed section
    for v in bm.verts:
        s = v.co.y / LENGTH
        if 0.03 < s < 0.995:
            amp = 0.028 * nh.smoothstep(0.03, 0.25, s)
            k = 1.0 + amp * (annulus(s) - 0.5)
            v.co.x *= k
            v.co.z *= k
        v.co.z *= DEPRESS
    mb.add(bm, None)
    oc.soft_body(mb, 0.0, r * 0.97, FLESH, FLESH_LIGHT, arms=10, arm_len=2.0, arm_r=0.14,
                 hood=False, eye_r=0.27, spot=(0.40, 0.20, 0.14), curl=0.25,
                 spread=0.45, droop=0.35)
    obj = mb.to_object("Endoceras", roughness=0.5)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Endoceras", views=((35, 25), (-90, 8), (20, 10), (0, 90)))
