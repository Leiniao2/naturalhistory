"""
Procedural Allaeochelys crassesculpta (middle Eocene, ~47 Ma, the Messel lake, Germany) for
map colonies.

An extinct relative of the living pig-nosed turtle (Carettochelyidae), about 40 cm long:
a smooth, domed shell covered by leathery skin instead of horny scutes, paddle-like
forelimbs that it beat like flippers, and a short fleshy snout ending in a pig-like nose.
Messel is famous for several pairs that died while mating. Colour (after the living
species): grey-olive shell with a paler rim, greyish skin, cream underside.
Shown swimming. Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/allaeochelys_crassesculpta.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AllaeochelysCrassesculpta.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.40, 0.42, 0.34)
SHELL_DARK = (0.28, 0.30, 0.24)
SHELL_RIM = (0.58, 0.58, 0.48)
SKIN = (0.33, 0.34, 0.30)
BELLY = (0.85, 0.80, 0.66)
NOSE = (0.38, 0.32, 0.30)
EYE = (0.06, 0.05, 0.04)


def build():
    b = nh.MeshBuilder()
    b.add(nh.ellipsoid((0, 0, 0.0), (0.42, 0.55, 0.19), subdivisions=4,
                       deform=lambda v: 1.0 + 0.06 * max(0.0, v.z) ** 2 - 0.35 * max(0.0, -v.z) ** 2), SHELL)
    b.add(nh.ellipsoid((0, 0.02, -0.06), (0.36, 0.48, 0.07)), BELLY)                      # plastron
    # short neck and head with a fleshy, upturned pig-like snout
    b.add(nh.tube([(0, -0.44, 0.0), (0, -0.58, 0.01)], [0.085, 0.075], sides=12), SKIN)
    b.add(nh.ellipsoid((0, -0.66, 0.02), (0.085, 0.10, 0.07)), SKIN)
    b.add(nh.tube([(0, -0.72, 0.02), (0, -0.80, 0.03), (0, -0.84, 0.04)], [0.05, 0.04, 0.035], sides=12), NOSE)
    for sx in (-1, 1):
        # big flipper-like forelimbs, swept back
        b.add(nh.tube([(sx * 0.32, -0.30, -0.02), (sx * 0.55, -0.26, -0.04), (sx * 0.78, -0.08, -0.05),
                       (sx * 0.86, 0.06, -0.05)], [0.07, 0.07, 0.05, 0.015], sides=8, scale_xy=(1.0, 0.25)), SKIN)
        # smaller paddle hind limbs
        b.add(nh.tube([(sx * 0.28, 0.40, -0.04), (sx * 0.40, 0.56, -0.05), (sx * 0.44, 0.66, -0.05)],
                      [0.06, 0.055, 0.02], sides=8, scale_xy=(1.0, 0.3)), SKIN)
    b.add(nh.tube([(0, 0.50, -0.02), (0, 0.62, -0.04)], [0.04, 0.0], sides=8), SKIN)
    fused = b.fuse(voxel=0.012, smooth=3, smooth_factor=0.5, max_tris=6000)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            c = (c[0], c[1], c[2])
            p = l.vert.co
            e = (p.x / 0.42) ** 2 + (p.y / 0.55) ** 2
            if l.vert.normal.z > 0.15 and e < 1.08:
                # smooth leathery shell: no scutes, soft mottling and fine pits, pale rim
                m = noise.noise(p * 6.0)
                c = nh.lerp(SHELL, SHELL_DARK, 0.5 + 0.5 * m)
                c = nh.lerp(c, SHELL_DARK, 0.3 * nh.smoothstep(0.3, 0.5, noise.noise(p * 40.0)))
                c = nh.lerp(c, SHELL_RIM, nh.smoothstep(0.80, 1.0, e))
            elif l.vert.normal.z < -0.3 and e < 1.0:
                c = BELLY
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.062, -0.70, 0.055), (0.014,) * 3, subdivisions=2), EYE)
        mb.add(nh.ellipsoid((sx * 0.015, -0.855, 0.05), (0.008, 0.006, 0.01), subdivisions=1), EYE)  # nostrils
    obj = mb.to_object("AllaeochelysCrassesculpta")
    vs = obj.data.vertices
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) / 2
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "AllaeochelysCrassesculpta", background=(0.05, 0.14, 0.16), views=((35, 35), (-90, 5), (0, 80)))
