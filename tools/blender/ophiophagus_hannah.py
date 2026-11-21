"""
Procedural king cobra (Ophiophagus hannah, Pleistocene to today; forests of
India and Southeast Asia) for map colonies.

The longest venomous snake, commonly 3-4 m and up to 5.8 m: a slender, smooth
elapid that eats mainly other snakes (its genus name means "snake-eater").
When threatened it spreads a long, relatively narrow hood and can rear a third
of its body off the ground. Olive to dark brown with narrow pale yellowish
cross-bands, a cream throat, a broad head with large shields and dark eyes.
Shown with the hood spread (the game bends the body into the slither wave).
Built with nh_pal_snake.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ophiophagus_hannah.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OphiophagusHannah.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_pal_snake as sn  # noqa: E402

SPEC = sn.Spec(
    name="OphiophagusHannah",
    length=2.4, girth=0.050, head_len=0.12, head_w=0.060, neck=0.85, tail=0.22,
    base=(0.26, 0.25, 0.14), saddle=(0.78, 0.70, 0.42), belly=(0.86, 0.80, 0.58),
    saddles=26, saddle_w=0.14, side_spots=0.0, head_col=(0.30, 0.27, 0.15),
)


def build():
    obj = sn.build(SPEC)
    vs = obj.data.vertices
    ymin = min(v.co.y for v in vs)
    h0 = ymin + SPEC.head_len * 1.15            # back of the head
    h1 = h0 + 0.36                               # end of the hood
    for v in vs:
        if h0 - 0.02 < v.co.y < h1:
            t = (v.co.y - h0) / (h1 - h0)
            k = nh.smoothstep(0.0, 0.25, t) * (1.0 - nh.smoothstep(0.45, 1.0, t))
            v.co.x *= 1.0 + 2.8 * k
            v.co.z = v.co.z * (1.0 - 0.25 * k)
    obj.data.update()
    return obj


if __name__ == "__main__":
    nh.run(build, SPEC.name, ground=(0.30, 0.38, 0.24), views=((35, 30), (-90, 8), (0, 75)))
