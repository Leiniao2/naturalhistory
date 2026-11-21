"""
Procedural Galapagos giant tortoise (Chelonoidis niger, Pleistocene to today,
Galapagos Islands) for map colonies.

The largest living tortoise, up to about 1.5 m long and over 250 kg, able to
live well over 100 years. Its ancestors floated from South America to the
islands about 2-3 million years ago; each island evolved its own form, from big
domed shells on the wet, grassy highlands to "saddleback" shells raised over the
neck on the dry islands, so that the animals could stretch up to cactus pads.
A high, domed, dull grey-black carapace of big scutes, a long neck, a blunt
head with a horny beak and thick, elephant-like scaly legs.

Reuses the giant-tortoise builder of megalochelys_atlas.py with Galapagos
proportions and colours. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/chelonoidis_niger.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChelonoidisNiger.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import megalochelys_atlas as ma  # noqa: E402

ma.SHELL = (0.17, 0.17, 0.16)
ma.SHELL_PALE = (0.32, 0.31, 0.28)
ma.SEAM = (0.07, 0.07, 0.06)
ma.SKIN = (0.36, 0.35, 0.33)
ma.SKIN_DARK = (0.20, 0.20, 0.19)
ma.PLASTRON = (0.30, 0.28, 0.24)
ma.SC = Vector((0, 0, 0.36))
ma.RX, ma.RY, ma.RZ = 0.44, 0.56, 0.52


def build():
    obj = ma.build()
    obj.name = "ChelonoidisNiger"
    # a longer, raised neck: stretch the head and neck forward and up
    for v in obj.data.vertices:
        if v.co.y < -ma.RY * 0.95:
            t = min(1.0, (-ma.RY * 0.95 - v.co.y) / 0.30)
            v.co.y -= 0.10 * t
            v.co.z += 0.08 * t
    obj.data.update()
    return obj


if __name__ == "__main__":
    nh.run(build, "ChelonoidisNiger", ground=(0.45, 0.42, 0.30), views=((35, 25), (-90, 5), (0, 10)))
