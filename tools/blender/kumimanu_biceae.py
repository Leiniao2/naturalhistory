"""
Procedural Kumimanu biceae (New Zealand, late Paleocene, ~60-56 Ma) for map
colonies. Built with nh_pal_bird.py (Penguin).

One of the oldest and largest penguins, about 1.6-1.8 m long and perhaps 100 kg,
already flightless and wing-propelled a few million years after the end-Cretaceous
extinction. It had a long, narrow, dagger-like beak for catching fish and squid.
Shown swimming with its flippers spread. Plumage: dark back and white front like
living penguins (unknown).
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/kumimanu_biceae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/KumimanuBiceae.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_bird as nb  # noqa: E402

SPEC = nb.Penguin(
    name="KumimanuBiceae",
    length=1.6, girth=0.27, beak_len=0.24, flipper=0.55,
    back=(0.13, 0.14, 0.17), belly=(0.92, 0.91, 0.88), beak_col=(0.16, 0.14, 0.13),
)

if __name__ == "__main__":
    nb.main_penguin(SPEC)
