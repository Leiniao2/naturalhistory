"""
Procedural Thylacosmilus atrox (Late Miocene - Pliocene of Argentina) for map
colonies: a sparassodont, a metatherian (marsupial relative) that evolved a
sabre-toothed cat body plan independently.

Jaguar-sized and short-legged, with a heavy neck, a short skull carrying very
long, ever-growing upper canines that are sheathed at rest by a deep bony
flange on the lower jaw, and a long, thick tail. Coat unknown: shown grey-
brown with a paler belly. Built with nh_sabretooth.py (shared machairodont
rig: the convergent silhouette is the point).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/thylacosmilus_atrox.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ThylacosmilusAtrox.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_sabretooth as st  # noqa: E402

SPEC = st.Spec(
    name="ThylacosmilusAtrox",
    withers=0.74, croup=0.74, length=1.05, girth=0.95,
    fore=1.12, hind=1.0, paw=0.9, neck=1.15, head=1.18,
    sabre=0.27, sabre_depth=0.026, sabre_flat=0.34,
    tail=((0, 0.0, 0.0), (0, 0.16, -0.10), (0, 0.30, -0.26), (0, 0.38, -0.44)), tail_r=(0.07, 0.055, 0.042, 0.03),
    coat=(0.46, 0.40, 0.33), coat_dark=(0.30, 0.25, 0.20), pale=(0.78, 0.72, 0.62),
    spot=(0.30, 0.25, 0.20), spots=0.0, tail_tip=0.4,
)

if __name__ == "__main__":
    st.main(SPEC, ground=(0.50, 0.47, 0.30))
