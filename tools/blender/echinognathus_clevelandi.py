"""
Procedural Echinognathus clevelandi Walcott, 1882 (Late Ordovician megalograptid eurypterid
from the Utica Shale near Utica, New York) for map colonies (Swim style).

A medium-sized sea scorpion, about 45 cm long, a close relative of Megalograptus. Known from
fragments, so the body follows Megalograptus: a squarish prosoma with small crescent eyes, a
broad preabdomen, a narrow postabdomen and a spine-like telson. What sets it apart (its name
means "spiny jaw") is the heavy armament of the front limbs: robust grasping legs bristling
with many long, sharp, paired spines, used to seize and hold prey. Dark olive-brown with a
paler rim (colour conjectural). Built with nh_ord_eurypterid.py. Faces -Y, pivot at the centre.

Usage:
  blender --background --python tools/blender/echinognathus_clevelandi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EchinognathusClevelandi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_eurypterid as eu  # noqa: E402

SPEC = eu.Spec(
    name="EchinognathusClevelandi",
    pro_w=0.21, pro_front=0.82, pro_corner=0.22, eye_x=0.12, eye_y=0.24,
    pre_w=(0.22, 0.245, 0.25, 0.24, 0.22, 0.19, 0.15),
    post_w=(0.10, 0.09, 0.08, 0.072, 0.066),
    legs=(0.58, 0.66, 0.64), leg_spines=7, spine_len=0.20, leg_v=0.28, paddle=0.14,
    cercal=0.0, telson_len=0.46, telson_w=0.028,
    shell=(0.34, 0.33, 0.20), shell_dark=(0.18, 0.18, 0.10), rim=(0.64, 0.60, 0.40),
    under=(0.66, 0.60, 0.44), leg=(0.42, 0.38, 0.22), leg_dark=(0.24, 0.22, 0.12),
    spine=(0.92, 0.86, 0.64), pattern=0.4,
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
