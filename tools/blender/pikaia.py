"""
Procedural low-poly Pikaia gracilens (Burgess Shale, Cambrian), an early chordate.

An eel-like, laterally flattened animal about 4 cm long: a small head bearing a pair of
slender tentacles, a row of tiny gill openings behind it, zig-zag (chevron) muscle blocks
(myomeres) along the flanks and the dark line of the notochord, and a low fin fold along the
back running into a paddle-shaped tail fin. Translucent olive-tan. Faces -Y, pivot at the body
centre (Swim). Straight along Y so the map's body wave can bend it.

Usage:
  blender --background --python tools/blender/pikaia.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pikaia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402

BACK = (0.62, 0.58, 0.40)
BELLY = (0.90, 0.86, 0.72)
MYOMERE = (0.42, 0.38, 0.24)
CORD = (0.36, 0.30, 0.20)
GILL = (0.66, 0.40, 0.36)
FIN = (0.76, 0.74, 0.58)
TENTACLE = (0.70, 0.64, 0.46)


def radius(t):
    return 0.05 * math.sin(math.pi * min(1.0, 0.16 + t * 0.88)) ** 0.6 + 0.003


def build():
    mb = nh.MeshBuilder()
    n = 90
    pts, radii = [], []
    for i in range(n + 1):
        t = i / n
        pts.append((0.0, -0.5 + t, 0.0))
        radii.append(radius(t))
    radii[0], radii[-1] = 0.018, 0.0

    def col(co, nrm):
        t = co.y + 0.5
        c = nh.lerp(BELLY, BACK, nh.smoothstep(-0.03, 0.03, co.z))
        if 0.12 < t < 0.97:
            # myomeres: chevrons pointing forward
            ph = (co.y + abs(co.z) * 0.9) / 0.034
            band = nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.cos(ph * math.tau))
            c = nh.lerp(c, MYOMERE, 0.7 * band)
            # notochord showing as a dark line high on the flank
            c = nh.lerp(c, CORD, 0.45 * math.exp(-((co.z - 0.018) / 0.006) ** 2))
        if 0.05 < t < 0.12 and co.z < 0.01:
            c = nh.lerp(c, GILL, 0.7 * nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.cos(co.y / 0.012 * math.tau)))
        return c

    mb.add(nh.tube(pts, radii, sides=18, scale_xy=(0.45, 1.0)), col)
    # low fin fold along the back from mid-body into a paddle tail (both tail lobes)
    outline = []
    for i in range(13):
        t = 0.35 + 0.65 * i / 12
        h = 0.012 + 0.03 * nh.smoothstep(0.75, 0.97, t)
        outline.append((radius(t) * 0.8 + h, -0.5 + t))
    for i in range(12, -1, -1):
        t = 0.35 + 0.65 * i / 12
        outline.append((radius(t) * 0.5, -0.5 + t))
    fin = nh.flat_panel([(z, y, 0) for (z, y) in outline], thickness=0.004)
    nh.transform(fin, nh.Matrix.Rotation(math.radians(-90), 4, "Y"))
    mb.add(fin, FIN, smooth=False)
    belly = []
    for i in range(7):
        t = 0.8 + 0.2 * i / 6
        belly.append((-(radius(t) * 0.8 + 0.022 * nh.smoothstep(0.82, 0.97, t)), -0.5 + t))
    for i in range(6, -1, -1):
        t = 0.8 + 0.2 * i / 6
        belly.append((-radius(t) * 0.5, -0.5 + t))
    fin2 = nh.flat_panel([(z, y, 0) for (z, y) in belly], thickness=0.004)
    nh.transform(fin2, nh.Matrix.Rotation(math.radians(-90), 4, "Y"))
    mb.add(fin2, FIN, smooth=False)
    # two slender head tentacles curving forward and out
    for s in (-1, 1):
        ten = [(s * 0.008, -0.49, 0.012), (s * 0.02, -0.53, 0.02), (s * 0.034, -0.565, 0.022), (s * 0.044, -0.59, 0.018)]
        mb.add(nh.tube(ten, [0.005, 0.004, 0.003, 0.0], sides=4), TENTACLE)
    return ec.centre(mb.to_object("Pikaia", roughness=0.35))


if __name__ == "__main__":
    ec.export(build, "Pikaia")
