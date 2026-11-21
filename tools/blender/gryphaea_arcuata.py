"""
Procedural Gryphaea arcuata (Early Jurassic oyster, Europe) for map colonies.

The "Devil's toenail": an oyster about 5-10 cm long whose thick, heavy left valve grew in a
tight, curling hook like a giant toenail, while the right valve was a small, flat lid
sitting in its mouth. Instead of cementing itself to rock like most oysters, it lay free on
soft mud, the curved weight keeping its opening clear of the sediment, and filtered plankton.
Grey-buff shell with rough growth lines; the lid darker. Fixed style: pivot on the sea
floor, faces -Y.

Usage:
  blender --background --python tools/blender/gryphaea_arcuata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gryphaea.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_ord_echino as ech  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.70, 0.66, 0.56)
SHELL_DARK = (0.48, 0.44, 0.36)
LID = (0.42, 0.38, 0.32)
FLESH = (0.82, 0.70, 0.58)


def shell_col(co, n):
    g = 0.5 + 0.5 * math.sin(Vector((co.y, co.z)).length * 90 + noise.noise(co * 8) * 2)
    c = nh.lerp(SHELL, SHELL_DARK, 0.5 * nh.smoothstep(0.6, 0.95, g))
    return nh.lerp(c, SHELL_DARK, 0.3 * nh.smoothstep(0.3, 0.7, noise.noise(co * 12)))


def one(mb, at, yaw, scale):
    """One shell: a deep, boat-shaped left valve whose beak curls up and over the hinge, with
    the small flat right valve sitting in it like a lid."""
    from mathutils import Matrix
    m = Matrix.Translation(Vector(at)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Scale(scale, 4)
    parts = [nh.ellipsoid((0, -0.02, 0.15), (0.2, 0.28, 0.15), subdivisions=3)]
    beak = kit.limb([(0, 0.16, 0.14), (0, 0.3, 0.22), (0, 0.33, 0.36), (0, 0.24, 0.45), (0, 0.13, 0.44)],
                    [0.15, 0.12, 0.08, 0.045, 0.02], sides=14)
    parts.append(beak)
    body = kit.fuse_parts(parts, 0.012, 3500, smooth=3)
    nh.transform(body, m)
    mb.add(body, shell_col)
    lid = nh.ellipsoid((0, -0.06, 0.29), (0.16, 0.2, 0.025), subdivisions=3)
    nh.transform(lid, m)
    mb.add(lid, LID)
    # a sliver of mantle where the lid gapes at the front
    fl = nh.ellipsoid((0, -0.2, 0.275), (0.12, 0.06, 0.02), subdivisions=2)
    nh.transform(fl, m)
    mb.add(fl, FLESH)


def build():
    mb = nh.MeshBuilder()
    ech.mud_patch(mb, 0.75, ((0.36, 0.32, 0.26), (0.46, 0.42, 0.34)))
    one(mb, (0.0, 0.0, 0.0), 0.0, 1.0)
    one(mb, (0.45, 0.3, 0.0), 2.2, 0.6)
    one(mb, (-0.45, 0.35, 0.0), -2.0, 0.5)
    return ech._finish(mb, "Gryphaea", roughness=0.7)


if __name__ == "__main__":
    nh.run(build, "Gryphaea", ground=None, background=(0.05, 0.15, 0.18), views=((35, 30), (-90, 5), (30, 70)))
