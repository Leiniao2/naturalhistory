"""
Procedural Doedicurus clavicaudatus (Late Pleistocene of the Argentine and Uruguayan
pampas) for map colonies: the largest glyptodont, about 3.6 m long and up to
1.5 m tall, weighing around 1.5 tonnes.

A very high, steep-sided carapace of fused osteoderms (in life largely smooth
and pitted, here with a faint rosette relief), a bony head cap on the short
head, stout pillar legs, and its famous weapon: a long tail encased in a solid
armour tube ending in a swollen mace that carried large spikes, probably swung
in fights between rivals and against predators. Dark chocolate-brown shell.
Built with nh_neo_armour.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/doedicurus_clavicaudatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DoedicurusClavicaudatus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_armour as ga  # noqa: E402

SPEC = ga.Spec(
    name="DoedicurusClavicaudatus",
    rx=0.43, ry=0.66, rz=0.50, zc=0.47, skirt=0.06, flat_top=0.03,
    head=0.95, leg=1.3, tail_len=0.62, tail_r=0.12, tail_rings=3, tail_lift=0.10,
    club=0.17, club_spikes=5,
    shell=(0.28, 0.20, 0.13), shell_pale=(0.46, 0.36, 0.25), seam=(0.13, 0.09, 0.06),
    rim=(0.18, 0.13, 0.09), skin=(0.30, 0.25, 0.21), rosette=9.0,
)

if __name__ == "__main__":
    ga.main(SPEC)
