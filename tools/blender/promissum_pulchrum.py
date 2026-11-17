"""
Procedural Promissum pulchrum (Late Ordovician, Hirnantian, conodont animal from the
Soom Shale of South Africa; estimated about 40 cm long, the largest conodont known) for
map colonies (Swim style).

Conodonts were eel-like, jawless early vertebrates known mostly from their tiny tooth
elements. Soft-bodied Promissum specimens preserve a big feeding apparatus, the muscles
and sclerotic cartilages of large eyes, and V-shaped (chevron) trunk muscle blocks. The
model: a long, slim, laterally flattened body, two large eyes at the front, painted
chevron muscle blocks and a notochord line, and a rayed fin round the tail.
Pinkish-grey (colour conjectural). Built with nh_ord_agnathan.py.

Usage:
  blender --background --python tools/blender/promissum_pulchrum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PromissumPulchrum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.ConodontSpec(name="PromissumPulchrum", length=1.8, depth=0.075, width=0.035, eye_r=0.05)

if __name__ == "__main__":
    nh.run(lambda: ag.build_conodont(SPEC), SPEC.name, **ag.PREVIEW)
