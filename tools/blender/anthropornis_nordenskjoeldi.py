"""
Procedural Anthropornis nordenskjoeldi (Seymour Island, Antarctica, late Eocene, ~40-34 Ma)
for map colonies: the "Nordenskjoeld's giant penguin", about 1.7 m tall and some 90 kg.

Shown swimming: a long, torpedo-shaped body, stiff flipper wings with a slight bend
at the elbow joint, a long, dagger-like beak and short legs trailing behind.
Dark slate-blue back, white belly (living penguins' countershading).
Built with nh_pal_bird.py. Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/anthropornis_nordenskjoeldi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AnthropornisNordenskjoeldi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_bird as nb  # noqa: E402

SPEC = nb.Penguin(
    name="AnthropornisNordenskjoeldi",
    length=1.75, girth=0.26, beak_len=0.30, flipper=0.52,
    back=(0.14, 0.17, 0.24), belly=(0.93, 0.92, 0.88), beak_col=(0.22, 0.18, 0.14), foot_col=(0.40, 0.33, 0.30),
    eye_r=0.024,
)

if __name__ == "__main__":
    nb.main_penguin(SPEC)
