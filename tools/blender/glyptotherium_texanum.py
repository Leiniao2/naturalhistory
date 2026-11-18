"""
Procedural Glyptotherium texanum (Pliocene to Pleistocene of southern North America
and Central America) for map colonies: a glyptodont about 2.5-3 m long, the only
glyptodont to reach North America in numbers.

Lower and longer than Glyptodon: a less tall, more evenly arched carapace of
fused rosette osteoderms with a flared rim, a bony cap on the short deep head,
short pillar legs with blunt claws and a thick tail armoured with rings of plates
but no club. Painted a paler sandy brown with cream rosette centres.
Built with nh_neo_armour.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/glyptotherium_texanum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GlyptotheriumTexanum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_armour as ga  # noqa: E402

SPEC = ga.Spec(
    name="GlyptotheriumTexanum",
    rx=0.40, ry=0.64, rz=0.36, zc=0.38, skirt=0.08, flat_top=0.10,
    head=0.95, leg=0.95, tail_len=0.42, tail_r=0.10, tail_rings=6,
    shell=(0.58, 0.47, 0.32), shell_pale=(0.80, 0.72, 0.56), seam=(0.30, 0.23, 0.15),
    rim=(0.40, 0.31, 0.21), skin=(0.45, 0.39, 0.32), rosette=12.0,
)

if __name__ == "__main__":
    ga.main(SPEC)
