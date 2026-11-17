"""
Procedural Livyatan melvillei (Late Miocene of the Pisco Formation, Peru) for
map colonies: a raptorial sperm whale about 13-17 m long.

A sperm-whale-like body with a big, blunt, box-like head holding a large
spermaceti organ, but a shorter skull than the modern sperm whale and a jaw
lined above and below with the largest teeth of any animal used for eating
(up to 36 cm), with which it probably hunted baleen whales. Shown with the
mouth open. Dark grey with a paler belly and scarred skin.
Built with nh_neo_whale.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/livyatan_melvillei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LivyatanMelvillei.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_whale as q  # noqa: E402

SPEC = q.Spec(
    name="LivyatanMelvillei",
    length=2.2, radius=0.27, head_blunt=0.75, head_frac=0.30, jaw_open=0.55,
    teeth=8, tooth_len=0.08, flipper=0.26, fluke=0.62, dorsal=0.04,
    back=(0.24, 0.24, 0.26), belly=(0.62, 0.60, 0.58), scars=0.35,
)

if __name__ == "__main__":
    q.main(SPEC)
