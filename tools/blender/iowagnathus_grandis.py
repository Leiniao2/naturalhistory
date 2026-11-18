"""
Procedural Iowagnathus grandis Liu et al., 2017 (Middle Ordovician giant conodont from the
Winneshiek Shale, Iowa) for map colonies (Swim style).

A large, active predatory conodont: its feeding apparatus of fifteen big, robust tooth-like
elements (up to 1.6 cm each) points to a body several times longer than most conodonts and to
hunting larger prey. Soft parts are unknown, so the body follows Promissum and Clydagnathus: a
long, eel-like, muscular trunk with V-shaped muscle blocks, big eyes at the front and a
ray-supported fin round the tail, here deeper-bodied and darker, with a bluish back and silvery
belly for open water (colour conjectural). Built with nh_ord_agnathan.build_conodont.

Usage:
  blender --background --python tools/blender/iowagnathus_grandis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/IowagnathusGrandis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.ConodontSpec(
    name="IowagnathusGrandis", length=1.8, depth=0.10, width=0.045, eye_r=0.055,
    body=(0.36, 0.42, 0.50), body_dark=(0.16, 0.20, 0.27), belly=(0.82, 0.84, 0.82),
    fin=(0.46, 0.52, 0.58), ray=(0.22, 0.26, 0.32), eye_rim=(0.06, 0.07, 0.09),
)

if __name__ == "__main__":
    nh.run(lambda: ag.build_conodont(SPEC), SPEC.name, **ag.PREVIEW)
