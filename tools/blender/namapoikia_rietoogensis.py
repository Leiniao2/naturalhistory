"""
Procedural Namapoikia rietoogensis (latest Ediacaran, Namibia, ~548 Ma): an early skeletal
reef builder, an irregular encrusting mound up to a metre across. Lumpy dome whose surface is
pale mineral skeleton cut by a maze of dark, winding channels (labyrinthine tubules), with a
few open pores. Cream-grey with ochre staining. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/namapoikia_rietoogensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Namapoikia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

WALL = (0.88, 0.84, 0.72)
CHANNEL = (0.42, 0.34, 0.24)
STAIN = (0.74, 0.56, 0.32)
PORE = (0.18, 0.13, 0.09)


def maze(co):
    v = noise.noise(Vector((co.x * 5, co.y * 5, co.z * 5)))
    return abs(v)  # near 0 = wall crest


def build():
    mb = nh.MeshBuilder()

    def deform(n):
        lump = 1.0 + 0.16 * noise.noise(Vector((n.x * 2.2, n.y * 2.2, n.z * 2.2 + 3)))
        return lump

    mound = nh.uv_ellipsoid((0, 0, 0), (0.75, 0.62, 0.36), segments=120, rings=56, deform=deform)
    for v in mound.verts:
        if v.co.z < 0:
            v.co.z *= 0.05
        m = maze(v.co)
        v.co -= v.co.normalized() * (0.015 * (1 - nh.smoothstep(0.0, 0.05, m)))
    mound.normal_update()

    def color(co, n):
        m = maze(co) * 0.8
        c = nh.lerp(CHANNEL, WALL, nh.smoothstep(0.015, 0.06, m))
        st = noise.noise(Vector((co.x * 2.5 + 7, co.y * 2.5, co.z * 2.5))) * 0.5 + 0.5
        c = nh.lerp(c, STAIN, 0.25 * st)
        return c
    mb.add(mound, color)
    # a second, smaller lobe fused to the side and a few pores
    lobe = nh.uv_ellipsoid((0.55, 0.35, 0), (0.35, 0.3, 0.22), segments=70, rings=34, deform=deform)
    for v in lobe.verts:
        if v.co.z < 0:
            v.co.z *= 0.05
    mb.add(lobe, color)
    import random
    rng = random.Random(4)
    for _ in range(14):
        a, b = rng.uniform(0, math.tau), rng.uniform(0.3, 1.2)
        p = Vector((math.cos(a) * 0.62 * math.cos(b), math.sin(a) * 0.52 * math.cos(b), 0.36 * math.sin(b)))
        mb.add(nh.ellipsoid(p, (0.035, 0.035, 0.035), subdivisions=1), PORE)
    return ec.ground(mb.to_object("Namapoikia", roughness=0.8))


if __name__ == "__main__":
    ec.export(build, "Namapoikia", fixed=True)
