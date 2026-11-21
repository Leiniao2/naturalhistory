"""
Procedural Palmatolepis gigas for the map: a conodont, a small eel-like early vertebrate,
from the Late Devonian (Frasnian, about 375 million years ago) seas worldwide; the animal
was a few centimetres long. Palmatolepis, with its broad palm-shaped feeding elements, is
the classic index fossil of the Late Devonian and swarmed in the open sea until the end-
Frasnian extinction.

Only its tooth-like elements fossilised; the body follows the soft-bodied conodonts known
from other species: an eel-like trunk with chevron muscle blocks, a small head with very
large eyes and a rayed fin round the tail. Colours unknown: translucent blue-grey, darker
back. Built with nh_ord_agnathan.build_conodont.

Usage:
  blender --background --python tools/blender/palmatolepis_gigas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Palmatolepis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.ConodontSpec(
    name="Palmatolepis", length=1.7, depth=0.062, width=0.040, eye_r=0.042,
    body=(0.58, 0.66, 0.74), body_dark=(0.34, 0.42, 0.54), belly=(0.86, 0.88, 0.90),
    fin=(0.64, 0.72, 0.80), ray=(0.32, 0.40, 0.50), eye_rim=(0.06, 0.08, 0.12),
)

if __name__ == "__main__":
    nh.run(lambda: ag.build_conodont(SPEC), SPEC.name, **ag.PREVIEW)
