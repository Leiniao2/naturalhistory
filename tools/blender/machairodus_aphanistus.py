"""
Procedural Machairodus aphanistus (Late Miocene Eurasia, best known from the
Cerro de los Batallones pits near Madrid; a lion-sized early machairodontine)
for map colonies.

A long-legged, lion-like build caught mid-stride: a longer, more level back than
Smilodon, slimmer limbs on long feet, a moderately thick neck and a long tail
hanging in a loose curve with the tip lifted. The head has a somewhat longer
muzzle than Smilodon's and shorter, flatter, blade-like upper sabres that reach
only to about the level of the chin. Built with nh_sabretooth.py.
Coat: plain, muted sandy tawny with a darker back line, pale belly, throat and
muzzle and a slightly darker tail tip (the real coat is unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/machairodus_aphanistus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MachairodusAphanistus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_sabretooth as st  # noqa: E402

SPEC = st.Spec(
    name="MachairodusAphanistus",
    withers=0.96, croup=0.90, length=1.12, girth=0.95,
    fore=1.02, hind=1.0, paw=0.9, neck=0.98, head=1.08, head_z=0.0, muzzle=0.03,
    sabre=0.155, sabre_depth=0.032, sabre_flat=0.28,
    tail=((0, 0.0, 0.0), (0, 0.16, -0.04), (0.02, 0.32, -0.18), (0.05, 0.42, -0.36), (0.09, 0.47, -0.52),
          (0.13, 0.46, -0.62)),
    tail_r=(0.055, 0.045, 0.038, 0.034, 0.031, 0.029),
    coat=(0.70, 0.56, 0.38), coat_dark=(0.55, 0.42, 0.27), pale=(0.88, 0.82, 0.69),
    spots=0.0, tail_tip=0.45,
)


if __name__ == "__main__":
    st.main(SPEC, ground=(0.52, 0.48, 0.32))
